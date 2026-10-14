# TASK-11S-BATCH-1012 / B / attempt-1 — 独立输入适用性/算法证据检查（回执）

- **owner:** B　**task/attempt:** TASK-11S-BATCH-1012 / attempt-1
- **时间:** 2026-10-13T21:12:47+08:00　**状态:** DONE（独立只读取证完成，交协调者；无代码变更、无提交、无模型调用）
- **固定输入:** 本机只读 `/home/wang/下载/1012`（8 包，manifest `total_bytes`=25,119,612,157 与逐包实测一致）；`input-manifest.json`；适配契约 `wt-04a-t12sb`（HEAD `f76e2a9`，`app/scene/spray/decode.py` `PACKET_TOPIC=/iv_packets_front_mid`、`POINTCLOUD_TOPIC=/iv_points_front_mid_transformed`）
- **方法:** 纯 stdlib `sqlite3` 以 `file:...?mode=ro` 只读连接各 `.db3`，直查 `topics`/`messages` 表的 topic 名/类型/消息计数/时间戳区间；跨 DB3 包核对两文件时间戳边界与包内顺序。**未复制输入、未调模型、未改码。**

## 一、逐包实测（topic/类型/消息计数/时长）

| bag | DB3 | 总消息 | 时长(s) | 水雾输入 topic | 判定 |
|---|---|---|---|---|---|
| `rosbag2_2026_10_08-14_42_48` | 1 | 39,711 | 53.429 | `/iv_packets_front_mid` SeyondScan **14,404**（rear 3,732） | **APPLICABLE（packet）** |
| `rosbag2_2026_10_12-15_58_23` | 1 | 2,325 | 4.380 | `/iv_packets_front_mid` **1,184**（rear 307） | **APPLICABLE（packet）**＝已完成首包 |
| `rosbag2_2026_10_12-16_00_13` | 1 | 2,595 | 4.747 | `/iv_packets_front_mid` **1,262**（rear 330） | **APPLICABLE（packet）** |
| `rosbag2_2026_10_12-16_02_03` | **2** | 410,669 | 537.246 | `/iv_packets_front_mid` **144,971**（db3_0:77,134 / db3_1:67,837；rear 37,607） | **APPLICABLE（packet，跨 DB3）** |
| `rosbag2_2026_10_12-16_31_25` | 1 | 734 | 3.577 | **无**（无任何 iv_* topic，20 topic 全为相机/感知/IMU/tf 等） | **NOT_APPLICABLE** |
| `rosbag2_2026_10_12-16_33_10` | 1（**0 字节**） | 0 | — | **无**（空 DB3，无 topics 表数据） | **INVALID_EMPTY_INPUT** |
| `rosbag2_2026_10_12-16_37_47` | **2** | 218,570 | 1,049.019 | **无**（无任何 iv_* topic，20 topic） | **NOT_APPLICABLE** |
| `rosbag2_2026_10_12-16_58_28` | **2** | 218,488 | 1,048.598 | **无**（无任何 iv_* topic，20 topic） | **NOT_APPLICABLE** |

- 逐包总消息数、时长与 `input-manifest.json` 完全一致（39711/2325/2595/410669/734/0/218570/218488），manifest 消息口径可信。
- **全批无水雾 PCD 路线输入**：无一包含 `sensor_msgs/msg/PointCloud2`；所有水雾输入均为 `seyond/msg/SeyondScan`（packet 路线）。`POINTCLOUD_TOPIC` 路线本批无命中。

## 二、关键独立发现（manifest 口径需修正）

1. **manifest 将 `16_31_25` / `16_37_47` / `16_58_28` 标 `initial_classification=NEEDS_RUNTIME_RESULT` 不实**：三包均**不含** packet 或 pointcloud 水雾输入 topic（`16_37_47`/`16_58_28` 的 manifest 自身 topic 列表也未列 `iv_packets_*`）。按 `adapter.check_applicability`（packet 优先，缺则 pointcloud，双缺 → `NOT_APPLICABLE`），三包在**路由阶段即判定 NOT_APPLICABLE**，不会进入解码/模型/分段，预期无伪切片。**无需等待 runtime 结果**，属输入层面可直接定性。
2. `16_31_25` 的 manifest 亦未列 `iv_packets_*`（17 图相机 + 感知，无雷达），与实测一致 → NOT_APPLICABLE。
3. **跨 DB3 包（3 个）时间戳边界正常，无乱序、无缺口重叠**：每包 db3_1.min_ts ≥ db3_0.max_ts（gap 4.73µs / 10.93µs / 1.55µs，均为正向衔接），且每 DB3 内按 id 递增的 timestamp 逆序数 = 0。多 DB3 的帧拼接需以**真实源时间戳**为准（不能按单文件行号），此为本批 packet 路线大包的真实边界证据，供 A 提交/TESTER 血缘核对。
4. 空包 `16_33_10`：`metadata.yaml` 与 `.db3` 均 0 字节，实测无 topics/messages 内容 → 输入校验应拒绝/隔离并可追溯（`INVALID_EMPTY_INPUT`），与 manifest 一致。
5. **无任何包含后雷达 `/iv_packets_rear_mid` 可替代前雷达**（适配契约 RAW-DATA §1：后雷达不能替代前雷达；缺前雷达=不适用）——`16_31_25/16_37_47/16_58_28` 连后雷达也无，纯缺输入。

## 三、适用性汇总（交协调者）

- **可处理（packet 路线，4 包）:** `14_42_48`(53s) / `15_58_23`(4.38s,已完成) / `16_00_13`(4.75s) / `16_02_03`(537s 跨DB3)。
- **NOT_APPLICABLE（3 包，路由阶段定性，非算法失败）:** `16_31_25` / `16_37_47` / `16_58_28`。
- **INVALID_EMPTY_INPUT（1 包，应输入校验拒绝/隔离）:** `16_33_10`。
- **本单范围无真实算法/解码缺陷证据**：只读 topic/类型/计数/时间戳层，未解包 SeyondScan 点云、未跑模型；若后续 runtime 出现具体解码/分段失败，按协调者最小返修单再取证。

## 四、命令与证据

- 探针脚本（只读 stdlib，未调模型）：`/home/wang/.hermes/cache/scratch/b11s_topics_probe.py`、`b11s_crossdb3_probe.py`、`b11s_verify_16_02.py`、`b11s_verify_noiv.py`；结果 `b11s_topics_probe.json` / `b11s_crossdb3.json`。
- `git status`（`wt-04a-t12sb`）：干净，仅 untracked `.venv`；HEAD `f76e2a9` 未动（**零提交**）。
- 环境：Linux 6.8.0-138，python3.11.16 stdlib sqlite3；全部 `mode=ro`，源包未被写。
- 未执行项：SeyondScan 点云解包/帧映射验证（属 runtime/TESTER 面，本单只读输入证据范围内不做）；模型调用；生产提交。

## 五、越界申报

- 无越界：仅写自身 ACK/session/receipt/event；未改 manifest/TODO/其他角色目录/生产；未复制输入、未调模型。
- 发现 manifest `NEEDS_RUNTIME_RESULT` 口径对 3 包不适用（见二.1），**只申报、不擅改 manifest**，由协调者决定是否更正清单。

## 六、上线后收尾增补（post-release-closeout-20261014.md，B 接续 2026-10-14 10:56 +08:00）

- **owner/attempt:** B / TASK-11S-BATCH-1012 attempt-1 沿用（原输入适用性任务 DONE 保持，本段只补缺失证据，不重跑模型、不改算法/UI、不增加契约）
- **核对基准:** 生产 API 只读快照 `doc/analysis/spray-batch-progress-20261014/production-snapshot.json`（`checked_at` 2026-10-14T10:37:40+08:00）+ 10:23 Codex 正式 API 绑定恢复回执口径（`codex-repair-receipt-20261014.md`：三 flat 提交复用既有终态 run，created_runs=0/reused_runs=3）
- **原 attempt-1 结论维持不变:** 4 包 packet 路线可处理 / 3 包 NOT_APPLICABLE 路由定性 / 1 包 INVALID_EMPTY_INPUT；本段以当前 run outcome 对该分类做 runtime 佐证核对，**无一处被推翻**。

### 6.1 逐包 source/run/attempt 与实际 outcome（B 面登记）

| 包 | B 输入分类 | run / attempt / 终态 | outcome（recorded_at +08:00） | 佐证关系 |
|---|---|---|---|---|
| `15_58_23` | APPLICABLE(packet) | `scene-c4a88c07…` / a2 / SCENE_DONE | SUCCESS 2026-10-13 20:24:04 | 首包，已独立验收 PASS |
| `16_00_13` | APPLICABLE(packet) | `scene-604c0896…` / a1 / SCENE_DONE | SUCCESS 2026-10-13 21:43:28 | TESTER PASS |
| `14_42_48` | APPLICABLE(packet) | `scene-a4824f1c…` / a2 / SCENE_DONE | SUCCESS 2026-10-13 23:54:41 | 正式提交 `a65a25a7` 10:23 绑定恢复后**复用**该终态 run（created_runs=0）；复用结果待 TESTER 独立核 |
| `16_02_03` | APPLICABLE(packet,跨DB3) | `scene-4acf689f…` / a1 / **SCENE_RUNNING**（heartbeat 10:37:13） | INFER 在途，余步 QUEUED | 跨 DB3 边界 B 已证（见 6.2-3）；终态验收归 TESTER |
| `16_31_25` | NOT_APPLICABLE | `scene-bc8c1d1c…` / a1 / SCENE_DONE | NOT_APPLICABLE 21:43:38 | error_detail「缺 /iv_packets_front_mid 与 /iv_points_front_mid_transformed」与 B 实测（无任何 iv_* topic）一致 |
| `16_37_47` | NOT_APPLICABLE | `scene-eb4397c3…` / a2 / SCENE_DONE | NOT_APPLICABLE 2026-10-14 00:01:29 | 同上口径；`87dfebaa` 10:23 绑定恢复复用该终态 run |
| `16_58_28` | NOT_APPLICABLE | `scene-24ab78bb…` / a2 / SCENE_DONE | NOT_APPLICABLE 2026-10-14 00:07:46 | 同上口径；`518089ed` 10:23 绑定恢复复用该终态 run |
| `16_33_10` | INVALID_EMPTY_INPUT | 无 source / 无 run；submission `7a71e404…` 恒 PENDING_INPUT | scanner 拒绝持续（scan_jobs 4097/4099 `failed:2`，10:36 实测） | 输入校验拒绝可追溯已成立；**提交层无失败终态**=缺陷事实（Codex 隔离树 `fix/spray-progress-20261014` 修复范围，未部署前不声称生效） |

### 6.2 12S-D 适用性/真值缺口清单（只补缺失证据与上游资料引用，不改契约）

1. **真阴性缺口（外部素材，B 无法在本批补齐）:** 三个 NOT_APPLICABLE 包（`16_31_25`/`16_37_47`/`16_58_28`）是**输入路由不匹配**（缺 `/iv_packets_front_mid`，且 B 21:12 实测连后雷达 `iv_packets_rear_mid` 也无），属「路由阴性」，**不能当真实阴性（算法对含水雾输入判无水雾）的证据**。真阴性需要「有水雾输入 topic、但内容无水雾」的真实包——本批 8 包与既有素材均无此样本，上游需补采集资料；12S-D 该项保持缺证。
2. **真实采集车辆缺口:** 全部 8 包 source 均绑定 `vehicle_id=1`（`vehicle_code=test`，用户指定受控车辆）。快照 originals 中 `vehicle_link_status`：MATCHED×4（15_58_23/16_00_13/16_02_03/16_31_25）、**MANUAL×3（14_42_48/16_37_47/16_58_28）**——MANUAL 三包对应 10:23 正式源登记恢复链（历史 MANUAL 绑定操作归因见 C 侧 D5 交付），其车辆身份可追溯但**非自动匹配证据**。「test 不能当真实采集车辆」→ 真实车映射验收保持缺证。
3. **多 DB3 实采拼接缺口（在途可收）:** 唯一跨 DB3 阳性包 `16_02_03`（10.1GB，db3_0:77,134 / db3_1:67,837 packet 条）仍在 SCENE_RUNNING（INFER）；B attempt-1 已交付真实时间戳边界证据（db3_1.min_ts ≥ db3_0.max_ts、gap 1.55µs 正向衔接、逆序 0），可作为其终态后跨 DB3 验收的输入侧锚点。另 `16_37_47`/`16_58_28`（各 ~1049s 跨 DB3）零模型 NOT_APPLICABLE 终态，可作为**多 DB3 包路由面**证据，仍不作算法阴性。
4. **空包提交层终态缺口:** 见 6.1 末行——拒绝可追溯已证、提交层 PENDING_INPUT 无失败终态为事实，修复在 Codex 隔离树、部署前不生效；验收材料引用 `receipts/TASK-11S-BATCH-1012/d6-163310-rejection-trace-2338.json`（A 侧 D6 痕迹）与快照 scan_jobs 口径。
5. **批量规模/容量缺口:** 本批为单机 CIFS 串行 8 包（先短后长），无并行批量容量证据；属 TESTER/协调者收口面，B 不代判。

### 6.3 B 面已证/缺证小结

- **已证（本段新增）:** B 输入分类与 7 个有效 run outcome 逐一 runtime 佐证一致（4 阳性包 3 SUCCESS + 1 在途、3 路由阴性包 NOT_APPLICABLE 零模型、1 空包拒绝可追溯）；NOT_APPLICABLE error_detail 与 B 实测 topic 缺失口径一致；MANUAL 绑定三包身份列明。
- **缺证（交 12S-D 保留，不冒充完成）:** 真阴性样本（需上游素材）、真实采集车辆映射、跨 DB3 阳性终态（待 `scene-4acf689f` 收敛）、空包提交层终态（待隔离树修复部署）、批量容量。
- **未执行项:** 模型重跑、算法/UI 改动、契约扩展、生产写——全部未做（本段纯只读取证+材料引用）。
- **下一步:** B 交付本段后释放槽、IDLE_WAITING；缺口 1/2/5 为外部素材/协调者收口面，缺口 3 随大包终态由 TESTER 面核收，缺口 4 随 Codex 隔离树按既有门禁（OCR/测试/按需强审）处置；B 不新开任务。
