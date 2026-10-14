# 回执：TASK-12S-B attempt-1-rework（c01+c02 OCR 16 findings 一次最小返修 + S9b 帧映射契约）

- status: REVIEW_PENDING（交付冻结，**非通过**）
- 交付时间：2026-10-13 15:20 +08:00（16 条返修段）；**S9b 交付标记：2026-10-13 17:5x +08:00**
- 派单路径：`inbox/2号/TASK-12S-B/attempt-1-rework-dispatch.md`（协调者 r158）+ `attempt-1-rework-s9b-dispatch.md`（r163，两份 S9 单合并口径）
- owner：执行者 B（2号）
- base → head：`f62a29c` → `f76e2a9b403577b791ca3688e0da5e574c4c272a`（**s9_head = `f76e2a9`**，续 `0320a8e`；`f62a29c` 未移动）
- 分支/worktree：`b/task-12s-b-spray-adapter` @ `/home/wang/.local/state/rosbag-scene/wt-04a-t12sb`（返修延续本任务分支，续 commit，未新开分支/attempt 号）
- 变更面：8 文件，+980/-78（7 个 `app/scene/spray/*` + 新增 `tests/test_spray_rework_16s.py` 40 用例）

## 一、文件清单

| 文件 | findings | 变更 |
|---|---|---|
| `app/scene/spray/adapter.py` | S1/S2/S5/S8 + T4 消费 | 模型面 valid_frames、work_dir 守卫前置、死分支注释、auto 缺 topic 口径、SOURCE_COMMIT 消费、decoder env 化 |
| `app/scene/spray/decode.py` | S3/S6 | 全读越界守卫、point_step/offset 布局守卫、路线层 DECODE_FAILED 收敛、cancel_check 透传 |
| `app/scene/spray/render.py` | S4/S7 | intensity 先 mask 再上色、_intensity_color np.select 向量化 |
| `app/scene/spray/precheck.py` | T1/T2/T3 | ldd 探针 fail-closed、SPRAY_DECODER_PATH env、错误码按前缀传播 |
| `app/scene/spray/pcd_io.py` | T5/T6/T7 | header 解析收敛 PcdError、COUNT 缺省全 1、compressed 头层拒绝、ASCII 头行计数修正 |
| `app/scene/spray/references.py` | T4 | REF_ORDER/NORMAL_ORDERS/ABNORMAL_ORDERS 死代码删除 |
| `app/scene/spray/time_map.py` | T8 | 最近候选 tie 显式拒绝 |
| `tests/test_spray_rework_16s.py` | 新增 | 40 定向用例 |

`config/scene_capabilities.yaml` 无改动（派单口径）。

## 二、17 条逐项处置（16 findings + T8 补列；全部修复，无取舍豁免）

| ID | 级别 | 处置 | 关键断言/证据 |
|---|---|---|---|
| S1 | HIGH·CORRECTION | **修复**：模型循环、`cache.hit(expected_frame_count)`、`model_storage_ns`、render_log 计数统一改用 `report.valid_frames` | `TestS1`：7 选中帧+第 0 帧 <500KiB → run 不炸，`filtered_small=1`/`valid_frame_count=6`/`len(model_storage_ns)=6`/模型调用 6 次；全小图 → `RENDER_INSUFFICIENT` |
| S2 | MED·CORRECTION | **修复**：`if not work_dir.is_absolute():` 无条件拒绝，前置于 mkdir | `TestS2`：相对 `work_dir` → `WORK_DIR_INVALID`，且 `Path("spray_rel_work")` 未创建（守卫在 mkdir 前） |
| S3 | HIGH·CORRECTION | **修复**：`_p2_read`/`_p2_read_byte` 越界守卫（slope `cdr._read_struct` 口径）；`_P2_DT_SIZE` point_step/offset 布局守卫；`decode_pointcloud_route` 逐帧收敛 `DECODE_FAILED`（带帧索引+storage_ns 上下文） | `TestS3`：blob 截断→`P2_TRUNCATED`；字段区截断→`P2_TRUNCATED/P2_LAYOUT`；point_step=0→`P2_LAYOUT`；intensity offset=100>point_step=16→`P2_LAYOUT`；路线层截断消息→`DECODE_FAILED` |
| S4 | HIGH·CORRECTION | **修复**：`read_intensity` 全点序列先应用同一 ROI mask 再上色（长度不齐=无法对齐，跳过上色不猜） | `TestS4`：mask 后长度=cropped=12；render 集成口径（最小 open3d stub 仅替代不可用渲染后端、真实代码+真实 numpy 走到上色行）`_intensity_color` 入参 len=6=ROI 内点数且值=[0..5] |
| S5 | LOW | **修复**：`pcd_path is None` 注明两路线恒填 pcd_path 不变式（保留 False 口径，不删行为） | `TestS5`：None → False |
| S6 | LOW | **修复**：pointcloud 解码循环透传 `cancel_check`（签名与 packet 路线对齐） | `TestS6`：`cancel_check=lambda: True` → `CANCELLED`；False → 12 帧正常 |
| S7 | LOW·perf | **修复**：`_intensity_color` 逐点循环改 np.select 分箱向量化（逐段 t 公式 t1/t2/t3/t4） | `TestS7`：5 组随机 1000 点 + 常值序列与旧逐点实现 `np.allclose(atol=1e-12)` 全等价 |
| S8 | LOW | **修复**：auto 双缺 topic → 缺 topic 口径 NOT_APPLICABLE（reason 含两个 topic 名与实际列表）；显式非法 route 仍报未知路线 | `TestS8`：`"未知路线" not in reason`、`"缺少水雾输入 topic" in reason`；`route=laser` → 仍报未知路线 |
| T1 | MED·CORRECTION | **修复**：`_ldd_missing_libs` 返回 `(missing, probe_error)`；探针失败/非零 rc → `DECODER_DEPS_UNKNOWN` fail-closed | `TestT1`：OSError mock、rc=127 mock → `ok=False`/`reason=DECODER_DEPS_UNKNOWN`；libseyond not found → 仍 `DECODER_DEPS_MISSING` |
| T2 | LOW | **修复**：`resolve_decoder_path()` 读 `SPRAY_DECODER_PATH`（对齐 `SPRAY_REFERENCE_DIR` 口径）；未配置 → `DECODER_UNAVAILABLE`；`check_decoder`/adapter 生产路径同步（删硬编码机器路径） | `TestT2`：env 未配置 → `DECODER_UNAVAILABLE` 且 detail 含 env 名；指向缺失文件 → 同；adapter packet 路线无 env → `DECODER_UNAVAILABLE` |
| T3 | LOW | **修复**：`check_references` 按前缀优先级 UNDECODABLE→MISMATCH→MISSING 传播 | `TestT3`：三类 ReferenceError mock → 错误码各自透传 |
| T4 | LOW | **修复**（单一来源路线）：删 `REF_ORDER`/`NORMAL_ORDERS`/`ABNORMAL_ORDERS`（全仓零引用已 grep 核）；`adapter._write_render_log` 改 import `SOURCE_COMMIT`（原 `be23177…` 硬编码删除） | `TestT4`：三常量不存在；render_log `refs.source_commit` == `SOURCE_COMMIT` 全值 |
| T5 | LOW·CORRECTION | **修复**：`_pcd_int`/`_pcd_field_parts`，SIZE/COUNT/WIDTH/HEIGHT/POINTS 非数值或缺第二 token 全部收敛 `PcdError` | `TestT5T6`：`SIZE 4 4 foo`→PcdError；`WIDTH`（无值）→PcdError；`POINTS abc`→PcdError |
| T6 | LOW | **修复**：① COUNT 行缺失 → 默认全 1（`count_line_seen`）；② `binary_compressed` 在 header 层即报不支持（与 `read_intensity` 能力口径对齐） | `TestT5T6`：无 COUNT 行 → `counts=(1,1,1,1)`；compressed → `PcdError` 含 `binary_compressed`；COUNT 长度不符仍拒 |
| T7 | MED·CORRECTION | **修复**：头行数 = `raw[:data_start].count(b"\n")`（旧 `split("\n")` 尾随 `\n` 多一个空元素 → 多跳一行、首条数据静默丢弃） | `TestT7`：合成 ASCII PCD 4 点往返 `vals==[0.11,0.22,0.33,0.44]`（首值不丢）；头内含空行仍正确 |
| T8 | LOW·CORRECTION | **修复**：最近候选 tie（等距双候选）显式拒绝；唯一最近 <50ms 命中；过远仍拒 | `TestT8`：t±25ms 等距 → ValueError 含"等距/tie"；975/1025 唯一最近 25ms → 命中；60ms → 拒 |

**取舍说明（书面）**：S5 保留 `return False` 行为并注明不变式（两路线解码均恒填 pcd_path，删行为等价但保留防御口径更稳）；其余 16 条全部实质修复，无豁免。

## 三、自测证据（真实执行）

| 命令 | 环境 | 结果 |
|---|---|---|
| `.venv/bin/python -m pytest tests/test_spray_rework_16s.py -q` | wt-04a-t12sb，venv Python 3.10.12 + pytest 8.4.1（临时装 numpy 2.2.6 供 S4/S7 定向用例） | **40 passed** |
| `.venv/bin/python -m pytest tests/test_spray_adapter.py tests/test_spray_rework_16s.py -q` | 同上 | **94 passed**（spray 域：54 既有 + 40 新增） |
| `.venv/bin/python -m pytest tests/ -q` | 同上 | **977 passed, 4 failed, 10 skipped**；4 failed = base 既有（`test_devflow.py` ×3、`test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time` ×1），与 attempt-1 回执口径一致（937+4 base 既有），**零新增失败** |
| `.venv/bin/python -m ruff check app/scene/spray/ tests/test_spray_rework_16s.py tests/test_spray_adapter.py` | 同上 | **All checks passed**（clean） |

- 真实 decode/render/VLM：**NOT_RUN**（本机依赖缺失口径不变，与 attempt-1 一致）；S4 集成用例用最小 open3d stub（仅替代不可用的渲染后端 `read_point_cloud`/`OffscreenRenderer`，被测的上色/mask/会计逻辑为真实代码+真实 numpy）。
- 1012 只读 bag 探针：`TestApplicability.test_real_bag_packet_route`（既有）随回归通过（packet 路线适用判定不变）。
- git：`git rev-parse HEAD` = `0320a8e96c76e126de15c61d0671afb88ae8988f`；`git status` 干净（仅 untracked `.venv`，非交付物）；commit 只含 8 个本单文件。

## 三-B、S9b 追加段：packet 路线帧映射契约（17:51 交付，s9_head = `f76e2a9`）

**派单**：`attempt-1-rework-s9b-dispatch.md`（r163，两份 S9 单 r159/r160 合并口径）+ `attempt-1-rework-s9b-nudge2.md`（17:3x 催办：只做验证+冻结，不重做已完成工作）。**变更面**：`app/scene/spray/decode.py` +205/−54、`tests/test_spray_adapter.py` +218/−54（`0320a8e..f76e2a9` 共 2 文件 +369/−54），仅 2 个文件，未越出 S9b 边界。

**映射设计**（替换 `decode.py:270` 错误契约 `len(pc_ds) != len(src_msgs)`）：
- 新增 `@dataclass(frozen=True) ScanFrameMapping`：`scan_end_storage_ns`（帧源时间 = scan 结束消息整数 storage_ns，**非 ms×1e6 伪造**）、`scan_end_message_id`/`scan_end_db3`（帧边界消息身份）、`first_message_id`/`first_db3`（该帧首个参与消息）、`packet_count`（CDR 声明 packet 数）、`scan_timestamp_f64`（对照用）。`DecodedFrame` 增 `scan_mapping` 字段（packet 路线填、pointcloud 路线保持 1:1 不变）。
- `_read_front_mid`：只读（`sqlite3 mode=ro`）逐 DB3 读 front_mid 全部消息，**保留 message_id 与来源 db3**（不复用 `slope.bag_io.read_messages`——它丢弃这两项，无法支撑可追溯映射），全局 `(storage_ns, message_id)` 升序。
- `_seyondscan_is_last`/`_seyondscan_head`：SeyondScan CDR 封装头感知（LE/BE 4 字节封装、无封装 base 0），只读 `is_last_scan`（u8@base+12）与 timestamp/size，不展开 packet 体；长度不足 → False 交由上层完整性守卫。
- `_build_scan_frames`：以 `is_last_scan=true` 为帧边界建帧；完整性矩阵——n>1 全 `is_last=false`（首尾均不完整）→ `DECODE_FAILED` 拒绝冒充；尾部非 is_last 残尾 → 完整帧发布 + `tail_truncated.json` 证据（残尾消息数）；跨 DB3 拼接 scan 的 `first_db3 != scan_end_db3` 可追溯；decoder 输出 PCD 数与 scan 数不符 → 帧级失败（不糊过长度断言）。

**自测证据（17:41–17:50 本轮真实执行，wt-04a-t12sb，venv Python 3.10.12 + pytest 8.4.1）**：

| 命令 | 结果 |
|---|---|
| `.venv/bin/python -m pytest tests/test_spray_rework_16s.py tests/test_spray_adapter.py -q` | **98 passed**（含 6 条 S9b 新增真实锚定/完整性用例），1.32s |
| `…pytest "tests/test_spray_adapter.py::TestPacketDecode::test_real_bag_1184_to_44_mapping" -v` | **1 passed**（真实锚定单跑复核） |
| `.venv/bin/python -m ruff check app/scene/spray/ tests/test_spray_adapter.py tests/test_spray_rework_16s.py` | **All checks passed** |

**真实小包 1184→44 断言**（`REAL_SMALL_BAG=/home/wang/下载/1012/rosbag2_2026_10_12-15_58_23`，只读，**已实际执行 PASSED**）：`decode_packet_route` 输出 **44 帧**；独立 `_read_front_mid` 复算 **1184 消息**；首 scan 结束 `message_id=4`、`storage_ns=1791791903804001823`；末 scan 结束 `message_id=2285`、`storage_ns=1791791908105918599`；44 帧 storage_ns 升序、无重复（44 个唯一值=无重复帧）。（注：该用例 decoder 子进程为 fake（按 is_last 边界写 PCD），被测的是**真实 bag 只读 + 真实帧映射/完整性逻辑**；真实 seyond decoder 渲染仍属下方 NOT_RUN 面。）

**S9b 新增用例（6 条，`TestPacketDecode`）**：
| 用例 | 断言 |
|---|---|
| `test_decoder_pcd_count_mismatch_scan_failed` | PCD 数 ≠ scan 数 → 帧级失败（不删断言糊过） |
| `test_decoder_success_maps_scan_not_message` | 帧=scan 边界（4 帧非 12 消息），mapping 身份对齐 |
| `test_no_is_last_scan_rejected` | n>1 全无 is_last → `DECODE_FAILED`（detail 含 `is_last_scan`） |
| `test_tail_truncated_emitted_as_evidence` | 3 完整 scan+尾部 2 残 → 3 帧 + `tail_truncated.json` 记 2 |
| `test_multi_db3_scan_mapping_traceable` | 4 scan 拆 2 库 → 4 帧；跨库帧 `first_db3 != scan_end_db3` 存在 |
| `test_real_bag_1184_to_44_mapping` | 上表真实锚定 |

**催办合规**：本轮未重做 16:58 前已完成工作（diff 与协调者 17:33 实测一致 +368/−54，仅 ruff E501 一处拆分 +1 行→+369/−54）；真实断言只跑一次（98 回归内 + 单用例复核），17:45 目标顺延至 17:51（顺延因：冻结 commit 前 ruff 复扫抓到新 E501，拆行后重跑回归确认绿才冻结——验证上未多轮）。

**git**：`f76e2a9`（branch `b/task-12s-b-spray-adapter`，parents `0320a8e`，仅 2 文件）；`f62a29c` 未移动；status 干净（仅 untracked `.venv`）。

## 四、未执行项 / 越界申报

- 未执行：真实处理机 decode/render/VLM（依赖缺失，NOT_RUN 口径）；TESTER 独立验证（收口链下一步，B 不代跑）。
- 越界申报：无。未动 12S-A DTO/16B scripts/16C 冻结面/旧 slope；无新迁移；能力注册 `enabled=false` 状态未改；未改契约语义（`bag_storage_ns`/整数 ns/双路线选择逻辑不变）。
- 环境变化申报：wt-04a-t12sb 的 `.venv` 临时 `pip install numpy`（attempt-1 时 venv 无 numpy，真实渲染口径 NOT_RUN 依赖缺失面不变——numpy 仅使 S4/S7 定向用例可跑，open3d 仍缺失，`test_real_render_unavailable_fail_closed` 等 NOT_RUN 口径用例行为不变）。

## 五、下一步（收口链，B 侧无动作）

交付冻结（s9_head `f76e2a9`）→ 协调者机械核验 → **增量 OCR 一次覆盖 `f62a29c..f76e2a9`**（16 条+S9 同一次审，固定入口排队 12S-A OCR 后）→ TESTER 增量复验（S9 真实解码/渲染探针+16 条受影响项，镜像在库实跑，B 侧快照更新为 `f76e2a9`）→ 合入 main → 12S-B DONE → 重算 12S-C 依赖。