# 独立验证报告：TEST-TASK12S-B-s9b / attempt-1（S9b 增量独立复验）

- 状态：**TEST_REPORT_PENDING**（交协调者裁决；普通测试 PASS ≠ OCR/强审/生产门禁通过）
- 验证时间：2026-10-13T18:45~19:05+08:00
- owner：TESTER
- 派单：`inbox/TESTER/TASK-12S-B-s9b/attempt-1-dispatch.md`（r2 短定向单之后按序接续）
- 固定快照：base=`0320a8e96c76e126de15c61d0671afb88ae8988f`，head=`f76e2a9b403577b791ca3688e0da5e574c4c272a`
- 独立隔离：新建 `git worktree --detach` `/home/wang/.local/state/rosbag-scene/wt-tester-s9b` @ `f76e2a9`（不动开发树 `wt-04a-t12sb`，其 HEAD 实测=`f76e2a9`、porcelain 仅 `.venv`，冻结干净）
- diff 越界核对：`git diff --stat 0320a8e..f76e2a9` = `app/scene/spray/decode.py` + `tests/test_spray_adapter.py`，2 文件 +369/-54，与派单 S9b 增量口径一致，**零越界**

## 一、真实包独立探针（镜像内实跑，替换旧 DECODE_FAILED 确证）

容器命令（可复跑，`rosbag-spray-runtime:20261013`，`--network none`、2CPU/6GiB、原包只读挂载）：

```text
docker run --rm --user 1000:1000 --cpus 2 --memory 6g --network none \
  --mount type=bind,src=/home/wang/.local/state/rosbag-scene/wt-tester-s9b,dst=/code,readonly \
  --mount type=bind,src="/home/wang/下载/1012/rosbag2_2026_10_12-15_58_23",dst=/source,readonly \
  --mount type=bind,src=/home/wang/.hermes/cache/scratch,dst=/verification,readonly \
  --mount type=bind,src=/home/wang/work/.local/spray-runtime/work/s9b-tester-f76e2a9,dst=/work \
  rosbag-spray-runtime:20261013 python /verification/s9b-tester-probe.py
```

**rc=0**，输出（独立 rclpy 解析期望 vs 代码 `decode_packet_route` 实际，逐项相等）：

| 检查 | 结果 |
|---|---|
| `message_count_1184`（独立反序列化 1184 条 `/iv_packets_front_mid`） | true |
| `boundary_and_pcd_count_44`（44 个 is_last_scan 边界 = 44 PCD = 44 帧） | true |
| `all_frame_mapping_exact`（每帧 scan_mapping 首/末 message_id、首/末 db3、packet_count 逐字段相等） | true |
| `all_storage_ns_exact`（帧 storage_ns = scan 结束消息**原始整数** storage_ns） | true |
| `non_ms_precision_retained`（storage_ns 非 ms×1e6 伪造，含亚毫秒位） | true |
| `all_real_pcd_exists`（44 个真实非空 PCD 落盘） | true |
| `source_sha256_unchanged`（原包前后摘要一致） | true |

首末帧锚：`frames[0].scan_end_message_id=4 / storage_ns=1791791903804001823`、`frames[-1].scan_end_message_id=2285 / storage_ns=1791791908105918599`（与 TEST-TASK12S-BC-freeze 独立计数一致）；decode 0.54s；尾部 20 条消息属未结束残缺 scan（tail 证据口径）。**旧 `DECODE_FAILED: PCD 44 != 消息 1184` 在 `f76e2a9` 上确已替换为成功**（`0320a8e` 同探针必抛，16:5x 报告在案）。

## 二、定向回归（受影响矩阵一次）

| 命令（`wt-tester-s9b`，`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`） | 结果 |
|---|---|
| `pytest tests/test_spray_adapter.py -q` | **58 passed**，rc=0 |
| `pytest tests/test_spray_rework_16s.py -q`（旧 16 条锚定） | **40 passed**，rc=0 |
| `pytest tests -q -k "spray or scene_spray or scene_capability"` | **124 passed**，rc=0 |
| `ruff check app/scene/spray/decode.py tests/test_spray_adapter.py` | All checks passed，rc=0 |

新增矩阵断言独立核（读实际断言非用例名）：3 scan/9 消息→`len(frames)==3`（不是消息数）；尾部残缺→`tail_truncated_messages==2` 且不算帧；多 DB3→`len(dbs)==2` + `first_db3 != scan_end_db3` 可追溯；重复/歧义→`DECODE_FAILED` 且 detail 含 is_last_scan 口径；映射 ns 升序无重复；取消在写前停止。

## 三、复用证据（按派单口径，未重跑）

- 旧 16 条 40 用例 PASS：本单已定向复跑确认（上表），非仅快照复用。
- 真实小包独立计数 1184/44/44 PCD、源包 sha256、镜像身份：`f76e2a9` 本探针实测复核（第一节），与 16:5x 探针一致。
- 未重复 534 PCD/全批渲染/VLM 模型面（派单明确本轮不做）。

## 四、结论

- **S9b 增量：PASS**——真实包 packet 路线解码成功、逐帧映射与源口径精确一致、源包不变、旧缺陷替换确证、受影响矩阵零回归、ruff 全绿。
- 未执行项（派单口径）：VLM 付费模型面/真实渲染（留 12S-D 与 53s 包观察）；OCR（协调者门禁，`01407cec` 2 批在途不插手）；生产写入/NAS 发布（无授权）。
- 边界：未改任何业务实现；探针脚本/产物在 `.local/spray-runtime` 与 scratch（本角色自建）；FAIL 回 B 最小修复。
- 状态 **TEST_REPORT_PENDING**，交协调者裁决；本 PASS 不构成 S9b 合入放行（合入门禁=OCR 收口+协调者核验）。