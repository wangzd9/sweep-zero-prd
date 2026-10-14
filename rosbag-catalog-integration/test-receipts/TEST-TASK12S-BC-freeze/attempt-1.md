# TEST REPORT：TASK-12S-BC-freeze attempt-1（12S-B `0320a8e` + 12S-C `92dcb52` 冻结产物前置验证）

- owner：TESTER（cron 会话 `cron-tester-poll-20261013-161953`）
- 时间：2026-10-13 16:2x–16:5x +08:00（A 面中期证据 16:4x 落盘，晚于 16:45 截止约数分钟，如实申报）
- 派单：`inbox/TESTER/TASK-12S-BC-freeze/attempt-1-dispatch.md`（ACK `attempt-1-ack.md`）
- 被测冻结快照（不可移动）：
  - A 面：`wt-04a-t12sb` @ `0320a8e96c76e126de15c61d0671afb88ae8988f`（12S-B 16 条返修，**不含 S9**），base `f62a29c`
  - B 面：`wt-03b-t12sc` @ `92dcb52ded2a112df514bc7d323e64315db7fe2e`（12S-C 接线前置），base `22ffb71`
- 环境：开发机 docker 镜像 `rosbag-spray-runtime:20261013`（RootFS id `e3fe73534ad8`，复用未重装，`--network none`、`--user 1000:1000`、2CPU/6GiB）；真实只读包 `/home/wang/下载/1012/rosbag2_2026_10_12-15_58_23`（56MB）；pytest 用 `wt-04a-t12sb/.venv`
- **总体：A 面 PASS（S9 除外，口径见 §A.3）；B 面 PASS（模块级）。交协调者裁决 TEST_REPORT_PENDING。正式 12S-D 联调不在本单。**

## 快照身份核对（独立证据）

- A 面：`wt-04a-t12sb` HEAD=`0320a8e`，但**工作区有未提交 S9b 增量**（`M app/scene/spray/decode.py` + `M tests/test_spray_adapter.py`，B 16:0x ACK S9b 后在途）。为保证被测身份纯净，**新建只读 detach worktree** `/home/wang/work/.local/spray-runtime/t12sbc-a-0320a8e`（`git worktree add --detach`，HEAD 双核 `0320a8e`，status 干净）作为 A 面全部 pytest/探针的代码源；`wt-04a-t12sb` 本体只借 `.venv`，未改动。
- `git show 0320a8e:app/scene/spray/decode.py` 独立核：`decode.py:270` 仍为旧断言 `len(pc_ds) != len(src_msgs)`，全文件 `is_last_scan` 零命中——与 r164 机械核验一致，**`0320a8e` 不含 S9 修复**（S9b 修复只存在于 B 工作区未提交面）。
- B 面：`wt-03b-t12sc` HEAD=`92dcb52`，status 干净（仅 `?? .venv`），无在途改动。
- 探针脚本（本角色自建，非被测代码）：`/home/wang/work/.local/spray-runtime/t12sbc-probe-a.py`、`t12sbc-probe-b.py`；探针产物：`/home/wang/work/.local/spray-runtime/work/t12sbc-probe-a/`（`probe-a-result.json` + 12 JPEG + PCD 解码输出）。

## A 面：12S-B `0320a8e`

### A.1 16 条受影响项（S1–S8 + T1–T8）定向复验 — **PASS**

- `pytest tests/test_spray_rework_16s.py -q`（干净 `0320a8e` worktree）→ **40 passed**（RC=0）。该文件即 16 条 finding 的逐条锚定用例（S1 valid_frames 模型面/S2 相对 work_dir/S3 截断 P2 收敛/S4 ROI mask 先于上色/S8 auto 双缺 topic/T1 ldd fail-closed/T7 ASCII 首值/T8 tie 拒绝等）。
- spray 域相关（`-k "spray or scene_spray or scene_capability or ingest_submissions or scene_config"`）→ **166 passed**（RC=0）。
- 回归口径（派单 §A.4）：全仓 `pytest tests/ -q` → **977 passed, 10 skipped, 4 failed**；4 失败 = `test_devflow.py`×3 + `test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time`，与 r164 协调者机械核验的 base 既有失败集**逐项一致，零新增**（日志 `/home/wang/.hermes/cache/scratch/t12sbc-a-fullreg.log`）。

### A.2 真实 decode/render 探针（镜像内实跑，NOT_RUN → 有据）— **PASS（解码链真实执行成功）**

容器命令（可复跑）：

```text
docker run --rm --user 1000:1000 --cpus 2 --memory 6g --network none \
  --mount type=bind,src=/home/wang/work/.local/spray-runtime/t12sbc-a-0320a8e,dst=/code,readonly \
  --mount type=bind,src="/home/wang/下载/1012/rosbag2_2026_10_12-15_58_23",dst=/source,readonly \
  --mount type=bind,src=/home/wang/work/.local/spray-runtime,dst=/verification,readonly \
  --mount type=bind,src=/home/wang/work/.local/spray-runtime/work/t12sbc-probe-a,dst=/work \
  rosbag-spray-runtime:20261013 python /verification/t12sbc-probe-a.py
```

关键断言（`probe-a-result.json` 摘录，全部来自实际执行）：

| 项 | 结果 | 证据 |
|---|---|---|
| 独立消息计数（探针自建 rclpy 反序列化，与代码无关） | **1184 条消息 / 44 条 is_last_scan** | `independent_msgs=1184, independent_scan_ends=44` |
| decoder 真实执行（`/opt/spray/bin/packet2pointcloud`） | **rc=0，输出 44 PCD** | `decoder_rc=0, decoder_pcd_count=44` |
| 冻结代码 select/render/account/finalize 链 | **12 帧选中 `[10,13,…,43]`（10 起每 3 取 1），12/12 渲染 OK，0 render_failed，0 filtered_small，valid_frames=12 ≥ MIN_VALID 3，finalize OK** | `report={selected:12, rendered_ok:12, filtered_small:0, valid_frame_count:12}` |
| **S4 强度上色生效** | 12/12 真实 PCD：`read_intensity` 全点序列长度 == open3d 点数（`aligned=true`，如 `n_points=123641, n_intensity=123641, roi_masked=84043`）；渲染 JPEG 非灰度（`mean_channel_sat≈27.7`，`mean_rgb=[28.6,2.2,2.6]` 红主导=低强度端配色） | `s4_detail[]` 全 aligned、`color_stats[]` |
| 时间覆盖 | 44 scan 帧覆盖包 4.38s（topic ts `1791791903803034259`→`1791791908182909013`，与 14:35 环境交接证据一致） | 1012 小包 metadata |
| 只读包不变 | 原包文件 sha256 前后一致 | `source_unchanged=true` |
| 全链耗时 | **27.1s**（1184 消息解码 + 12 帧 3840×2160 渲染，2CPU/6GiB 限额） | `t1-t0` |

**17:30 停止点输入（真实首包预算）**：小包（1184 消息/44 帧）镜像内**无模型面**全链 27s；模型面（每有效帧 1 次双 pass 请求，12 帧）未在本单执行（VLM 付费留 12S-D），按 14:35 环境交接"两机器各一次真实 8 图请求 HTTP200"口径估算，单包模型请求时间另计——**结论：环境解码/渲染预算不是 19:00 首包瓶颈，瓶颈在模型请求次数×单次延迟**。

### A.3 S9 不预占 + 真实缺陷复现证据（派单 §A.3 口径执行）

- 冻结代码 `decode_packet_route` 对真实包实跑：**抛 `DecodeError(DECODE_FAILED)`，detail=`PCD 数 44 != 源消息数 1184，序号映射歧义（重复/缺失），拒绝冒充`**（`probe-a-result.json: code_decode=RAISED, code=DECODE_FAILED`）。
- 这正是 S9b 待修缺陷（`decode.py:270` 旧断言）在真实有效包上的**最小复现**：一切真实 packet 包（消息数≠scan 数）必 DECODE_FAILED，packet 路线在 `0320a8e` 上对真实数据**不可用**；pointcloud 路线不受影响（其映射按帧文件 1:1）。
- 按派单口径**不判 S9 FAIL**：S9 修复（is_last_scan 帧边界映射 + 1184→44 断言）随 B 在途 S9b 提交（`s9_head`），冻结 `0320a8e` 的 S9 面待新 head 增量复验（本探针的 1184/44 独立计数与 44 PCD 序列可直接复用为该复验的输入证据，口径 `frame-mapping-contract-note.md` 在案）。
- **风险通报（交协调者）**：S9b 冻结前，packet 路线不可用于任何真实包——19:00 首包依赖线（12S-B 合入 → 12S-C 消费 → 12S-D 联调）的关键路径在 `s9_head` 增量 OCR + 复验，建议停止点判断时以此为硬约束。

### A.4 结论

A 面 **PASS**（16 条返修面全部锚定 + 真实解码/渲染/上色链路在冻结 `0320a8e` 上实际执行成功，零新增回归）；S9 缺陷真实复现证据在案，随 `s9_head` 增量复验。

## B 面：12S-C `92dcb52`

### B.1 接线模块验证（前置，非联调）— **PASS**

- `pytest tests/test_scene_spray_wiring.py -q`（干净 `92dcb52` worktree）→ **11 passed**（RC=0）。覆盖：dispatch→SprayAdapter 全链 SUCCESS 发布到 spray 场景子树并 register、`bag_storage_ns` offset=0 复用分支、NO_MATCH 只 complete 不发布、缺 front topic 终态 NOT_APPLICABLE、7 图缺 PRECHECK fail-closed 不烧模型、恢复幂等 manifest 复用不二次计费、MODEL_FAILED 归 INFER、旧坡道 header 轴恢复回归（spray import 在场）、12S-A 车辆绑定消费面（spray 缺车 fail-closed 不猜/slope lenient 不回归）。
- 回归口径：`-k "wiring or scene or ingest or orchestrator"` → **345 passed**；全仓 `pytest tests/ -q` → **1005 passed, 10 skipped, 4 failed**，4 失败同为 base 既有集（devflow×3 + web×1）**零新增**。
- 接线固定 SHA 消费核：`92dcb52` 的 `git show --stat` = 27 行业务增量（orchestrator +18 / proxy +9）+ 470 行测试，与派单口径一致；`git diff 22ffb71 92dcb52 -- config/scene_capabilities.yaml` = **0 行**（yaml spray 段为 12S-B `f62a29c` 产物已在其 base，`92dcb52` 未改 yaml，事实记录）。

### B.2 disabled spray 回退风险（REPORT 点名）独立证据 — **PASS**

自建探针 `t12sbc-probe-b.py`（不依赖被测仓测试，独立构造 resolve 场景）：

| 项 | 结果 |
|---|---|
| `CapabilityRegistry.from_file(真实 config).resolve("spray")`（spray `enabled=false` 起步） | **拒绝**：`CapabilityDisabledError: 场景 spray 没有启用版本`——不存在"错误调度为坡道"路径（resolve 按 scene_code 精确匹配，拒绝即 fail-closed，不落入任何其它场景） |
| `resolve("slope")`（spray disabled 在场） | **OK slope-v1**（默认版本解析不受 spray 影响） |
| yaml slope 段对 base `22ffb71` 逐字段对比 | **完全一致**（diff_keys=[]，entries 相等） |
| 场景能力集合 | 与 base 相同 `{slope, spray, test-capability}`，spray 段 additive 在场零侵入 |

### B.3 结论

B 面 **PASS（模块级）**：接线不破坏 slope 默认（零回归 + 逐字段一致），disabled spray fail-closed 不落入坡道。正式联调（真链冒烟+发布+入库）归 12S-D；与 C 16B-r2 的关系按派单 §B.4：本证据对 `92dcb52` 快照有效，r2 若改 proxy 则受影响项增量复验。

## 交付状态与未执行项

- 状态：**TEST_REPORT_PENDING**，交协调者裁决（本单 PASS 不构成 12S-B/12S-C 合入放行，合入门禁=各自 OCR 收口 + 协调者核验）。
- NOT_RUN（派单口径内不做）：VLM 付费双 pass 模型面（留 12S-D）；53s 大包（14404 消息）真实解码（14:35 环境交接已有 PASS 证据 `local-53s-v1`，本单小包口径够用，如需预算证据另行派单）；12S-D 联调。
- 资源清理申报：本角色新建 detach worktree `t12sbc-a-0320a8e`（测试后已 `git worktree remove`）；探针脚本与产物保留于 `/home/wang/work/.local/spray-runtime/`（.local 工作区，非业务仓）；docker `--rm` 无容器残留；未触碰 OCR/`ocr.lock`/他人 worktree/生产路径。