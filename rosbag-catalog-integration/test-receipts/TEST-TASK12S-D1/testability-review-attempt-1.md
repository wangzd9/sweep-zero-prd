# TASK-12S-D1 可测试性复核 attempt-1 回执（TESTER，2026-10-15 10:10 +08:00）

- **状态**：TEST_REPORT_PENDING。owner=TESTER；task/attempt=TASK-12S-D1 / attempt-1；派单 `inbox/TESTER/TASK-12S-D1/testability-review-dispatch.md`（协调者 09:50）。
- **定位**：可测试性复核，**非真实验收**。D2 维持 BLOCKED（缺五材料不因本单解锁、不编造准确率）；本单纯只读资料面。
- **被测对象**：C 部分交付 `receipts/TASK-12S-D1/attempt-1.md` + `attempt-1-samples.md`（协调者机械核验已通过 10-14 20:5x）；只读参照 `input-manifest.json`（协调者 10-13 冻结）、`ruling-4acf-stuck-cancelling-1840.md`。
- **环境/边界**：处理机 `rosbag-catalog_mysql_1` 只读 SELECT（与 11S-BATCH-1012 同源、3c9c496 生产业务库）+ 本地冻结 manifest bytes 抽查。**零写业务库/NAS/A100，零新流水线，VLM 调用=0，未碰 1012 大包取消链**；未新建隔离环境（不需可写库）。
- **探针**：`/home/wang/.hermes/cache/scratch/t12sd1_probe{,2,3,4}.py`（只读，保留供复核）。

## 6 项逐条结论（可测 / 不可测 / 证据链断点 + owner）

### ① 已证阳性×4（受控 test 车）— **可测（PASS，标识真实存在且终态一致）**
C 引用的 run / parent / child 标识在测试库只读核全部命中且终态一致：

| 包 | parent(source) | run 终态 | child(SCENE_SLICE) | 核对 |
|---|---|---|---|---|
| 15_58_23 | `615A4A7B…` ORIGINAL | `scene-c4a88c07` SCENE_DONE a2 | `16Bc-51ac3e1fa53dbdd6b2` READY test | ✅ 三标识全命中 |
| 16_00_13 | `051768B1…` | `scene-604c0896` SCENE_DONE a1 | `16Bc-4654d41f86d36f5c4b` READY test | ✅ |
| 14_42_48 | `FFDEE943…` ORIGINAL(1行) | `scene-a4824f1c` SCENE_DONE a2 | `16Bc-0c0695/94a9db/491286/7a95e7`×4 READY test | ✅ 双写 4 份 child 实测在位 |
| 16_02_03 | `91FFEEC1…` | `scene-4acf689f` **SCENE_CANCELLING** | 无已发布 child | 见 ④ |

- 4 个阳性 run/parent/child 均在 `pipeline_run` / `bag_record`（bag_role=ORIGINAL/SCENE_SLICE，vehicle_id=1=test）真实存在，终态与 C 回执一致；`ingest_submission` 8 行状态核对：flat 三提交 `a65a25a7`/`87dfebaa`/`518089ed` 均 SCHEDULED+bound（FFDEE943/9C9456B6/205E5054），`24d60fee`(16_02_03) SCHEDULED bound 91FFEEC1，`9949d1a7`(15_58_23) SCHEDULED bound 615A4A7B。
- **轻微口径注记（非断点，不影响结论）**：C 把 16_00_13 切片写成 NAS 形态 `051768B1_16Bc-4654d41f86d36f5c4b`，实际 `bag_uid=16Bc-4654d41f86d36f5c4b`（parent source `051768B1…`）——同一对象、两种记法，与 `slices/test/spray/` 物理路径一致，终态结论不受影响。

### ② 输入适用性×3（NOT_APPLICABLE，缺 `/iv_packets_front_mid`）— **可测（PASS，判定=topic 清单实证非推断）**
- run `scene-bc8c1d1c`(16_31_25 a1)/`scene-eb4397c3`(16_37_47 a2)/`scene-24ab78bb`(16_58_28 a2) 实测均 **SCENE_DONE**（零模型零伪切片）。
- NOT_APPLICABLE 判定依据=**冻结 manifest topic 清单实证**：16_31_25 topic 表无 `/iv_packets_front_mid`/`rear_mid`；16_37_47 与 16_58_28 topic 表**均无 iv_* 任一**（manifest `classification_note` 明确「manifest 自身 topic 列表亦未列 iv_*」）。→ 判定非推断、可复证，符合派单口径「不算正常阴性」。

### ③ 无效输入×1（16_33_10 0B 空包）— **可测（scanner 拒绝 PASS）+ 证据链断点（已登记）**
- **可测面（PASS）**：scanner 拒绝闭环实证在位——submission `7a71e404` 实测 **PENDING_INPUT、source_id=NULL**（`COUNT(source_id IS NOT NULL)=0`）、无 source 登记、无 scene run、无伪切片；manifest `initial_classification=INVALID_EMPTY_INPUT`、`bytes=0`、`metadata_sha=e3b0c442…`(空文件指纹)。scanner `missing rosbag2_bagfile_information` 10min 周期拒绝 + `scan_job` incoming `failed:2`（TESTER 11S-BATCH-1012 既有独立核 PASS）。
- **证据链断点**：缺的是**提交层终态**——`7a71e404` 恒 PENDING_INPUT，无「输入被拒绝」的可追溯终态行（scanner 层拒了但 submission 状态机不翻终态）。**补齐路径 = 12S-F INPUT_REJECTED 修复对象**（C 已标），即空包 submission 转明确拒绝终态后可追溯。本单**只登记不补跑**（12S-F 非本角色/非本单范围）。

### ④ 16_02_03 跨 DB3 取消终态未证 — **不可测（断点，标为 D2 材料缺口）**
- 实测 `scene-4acf689f` 仍 **SCENE_CANCELLING attempt1**（heartbeat 停 16:21:55、lease 16:22:22 起 stale），steps：EXTRACT DONE / **INFER RUNNING** / PRECHECK DONE / PUBLISH+REGISTER+VALIDATE+WRITE+SEGMENT QUEUED。
- 与 `ruling-4acf-stuck-cancelling-1840` 口径**一致**：取消已实际发生（编排退出、INFER 中断、零 PUBLISH 产物），但 DB run 行滞留 SCENE_CANCELLING=确认写被过期租约守卫（`security.py:39` 409）挡回后的**状态收口缺口**，非业务未取消。
- **断点**：① DB run 未推到 CANCELLED 终态（滞留，缺陷候选入 16R，不代修）；② **跨 DB3 边界消息时间未定位**（双 DB3 5.37G+4.74G，537s），跨边界命中/顺序**均未证**。1012 不能凭文件数/包名认定跨边界（派单明示）。
- **D2 材料缺口 owner**：需 D2 当次授权重跑（不重烧 4acf 大包）或上游另提供跨边界包——**owner=TESTER D2 + 协调者授权**。本单不复跑、不触取消链。

### ⑤ 五项 BLOCKED_MATERIAL — **可测（阻塞原因=上游材料缺失，非测试方法缺陷；无「材料已可取但没人取」项）**
逐条确认阻塞根因，均为**上游材料缺失**（非本角色方法缺陷），且**无一属于「材料已可取但没人取」**：
1. 输入有效真实正常阴性（含水雾 topic、内容无水雾）— 上游采集/算法未提供（本批 8 包无此形态，三个 NOT_APPLICABLE 缺 iv topic 只算输入适用性）。
2. 业务人工真值区间（storage ns + 标注来源，全部样本）— 业务/算法 owner 未书面提供；模型 outcome 不当真值，不编造准确率。
3. 业务质量接受阈值及适用范围 — 无书面数值在案，待业务/算法 owner 确认。
4. 真实采集车辆映射（非 test）+ 父/子继承实车实证 — 全批 vehicle_code=test（用户指定受控车），实车映射=缺；上游/用户未指定实车。
5. 跨 DB3 阳性命中与顺序验证 — 唯一候选 16_02_03 取消终态未证（见 ④）；需 D2 授权重跑或上游另供跨边界包。
- 结论：五项阻塞均**方法面可测**（复核能定位缺什么、缺在哪、owner 是谁），缺的是**材料面**（上游/授权），非测试方法缺陷；**无「材料已可取但没人取」项**，不列返修单派回 C。

### ⑥ 批次总量口径（25,119,612,157 B）— **可测（PASS，抽查 2 包 bytes 与冻结 manifest 一致）**
- 冻结 `input-manifest.json` 实测：`total_bytes=25119612157`；抽查 2 包 bytes：15_58_23=`57689621`、16_02_03=`10105917670`，与 C 回执/manifest 逐项一致；`sum_of_bags=25119612157`==`total_bytes`（8 包 bytes 求和自洽）。
- 派单口径「协调者已全量核过，复核只验口径不重跑」——本轮仅本地 manifest 只读抽查，未重跑 A 的 SHA/拷贝验证。

## 发现的证据链问题清单（供协调者裁决）

| # | 问题 | 面 | 影响 | owner | 处置 |
|---|---|---|---|---|---|
| 1 | 16_33_10 空包 submission 恒 PENDING_INPUT 无提交层终态 | 断点 | 无效输入拒绝在提交层不可追溯（scanner 层已证） | **12S-F**（C/协调者） | 只登记，随 12S-F INPUT_REJECTED 落地补齐 |
| 2 | 16_02_03 run 滞留 SCENE_CANCELLING 未收口 + 跨 DB3 边界未定位 | 断点/材料缺口 | 跨 DB3 阳性不可测（取消已证实、终态对账待缺陷修复） | **16R 盘点（缺陷候选）+ TESTER D2/协调者授权** | 不代修/不复跑；D2 当次授权重跑或上游另供跨边界包 |
| 3 | C 把 16_00_13 切片记为 NAS 形态 `051768B1_16Bc-4654…` 而非 `bag_uid=16Bc-4654…` | 口径注记（非断点） | 不影响终态结论（同一对象两记法） | C（可选更正） | 记录在案，无需返修 |

## 边界与未执行项
- **零越界**：全部动作=处理机只读 SELECT + 本地 manifest 只读 + 本角色 ACK/回执/sessions 写入。未写业务库/NAS/A100、未起新流水线、VLM 调用=0、未碰 1012 大包取消链、未补跑空包/未修滞留行、未编造准确率。
- 五项 BLOCKED_MATERIAL 因材料缺失维持 BLOCKED（不因本单解锁）；D2 真实验收仍缺材料。
- 普通测试 PASS ≠ OCR/强审查/生产门禁通过；本单为可测试性复核结论，交协调者裁决「D1 部分交付接受（真实面维持 BLOCKED）」正式口径。