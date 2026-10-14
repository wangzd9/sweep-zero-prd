# TASK-11S-BATCH-1012 / 协调者裁决 — dup-run attempt-2 处置 + 24d60fee 保留 + date-grouped 清理时序（ruling-duprun-2338）

时间：2026-10-13 23:38 +08:00，owner=COORDINATOR（批次唯一状态单写者）。
消费：A 23:2x 回执 `receipts/TASK-11S-BATCH-1012/a-attempt-1.md`（23:28 增量）四项「未执行项（待协调者）」+ TESTER 23:0x 增量验收申报的 dup run 冲突取证。
取代：`ruling-doublewrite-2210` 中与 attempt-2 事实冲突的前提（③第16/20行 source_metadata 缺失判定、④「3 dup run 均终态 SCENE_FAILED 保留不删」——22:53:02 三 dup run 已自动 RETRY_REQUESTED 重入，其一 SCENE_RUNNING）。其余 2210 裁决（15_58_23/16_00_13/16_31_25 保持、16_33_10 拒绝路径、禁止事项）继续有效。

## 一、裁决前提（以 23:2x 在案证据为准）

- A 23:0x 已删 `13dc398c`（14_42_48 第二写者 flat，备份在案）并正式重提交 `a65a25a7`（HTTP 201 PENDING_INPUT）、`16_37_47` 正式提交 `87dfebaa`（HTTP 201 PENDING_INPUT，台账已补）；`518089ed`（16_58_28 flat）维持 PENDING_INPUT 待绑定。
- `24d60fee`（16_02_03 flat，第二写者行）23:05:30 被 scanner SCHEDULED，绑定 run `scene-4acf689f` SCENE_SLICE_QUEUE；A 全列实测其 source_metadata 完整（vehicle_code=test，与 manifest 固定值一致）——2210 裁决「缺 vehicle_code」前提对该行不成立。
- 3 个 date-grouped dup run 22:53:02 收自动 RETRY（retry_mode=normal）：`scene-a4824f1c`（14_42_48，NEEDS_RUNTIME_RESULT 有真实 iv 数据）attempt-2 **SCENE_RUNNING** 持 SCENE_EXEC_HOST 活租约（23:27 仍在更新）；`scene-eb4397c3`（16_37_47）/`scene-24ab78bb`（16_58_28）attempt-2 SCENE_SLICE_QUEUE。attempt-2 带完整车辆元数据，**不再天然 fail-closed**。
- A flat 三提交 409 绑定受阻根因=scanner `recovering …/ready/spray/20261012/…: HTTP 409`，date-grouped 副本占位拖累；date-grouped 清理是 A flat 链解锁条件。
- RETRY 发起方身份未定：22:53:02 早于 A finalbag op 22:53:47 起跑，A op 仅 SHA 核验不写 run 表；疑似系统自动重试机制（3c9c496 行为），需代码面归因。

## 二、逐项裁决

**D1 — `24d60fee`（16_02_03）：确认保留，不删不重提。** 现为该包唯一有效 flat submission（SCHEDULED 绑定 `scene-4acf689f`），source_metadata 实测完整；2210 对其的清除指令**作废**。A 台账口径（22:56 事件+23:2x 回执）成立。

**D2 — 14_42_48 dup run `scene-a4824f1c` attempt-2（SCENE_RUNNING）：授权 A 最小处置。** A 先只读确认 3c9c496 是否存在正式 run cancel 端点（API 清单/代码只读）：
- 存在 → 执行 cancel，先留证（cancel 前 run 状态/事件链/slices 目录计数），cancel 后核 run 终态+资源释放；run 历史记录保留不删行。
- 不存在 → **不得直删 runs 表/强杀**，让其自然收敛；若终态 SUCCESS（重复烧模型+发布同数据第二份切片的实证）第一时间申报协调者，保留现场不自行处置，TESTER 将该 dup 子包记为双写事件产物。
- 无论哪条路径，14_42_48 的**正式验收以 A flat `a65a25a7` 绑定的 run 为准**（NEEDS_RUNTIME_RESULT 全链）。

**D3 — 16_37_47/16_58_28 dup（`scene-eb4397c3`/`scene-24ab78bb`）attempt-2：不 kill，自然收敛。** B 已独立确认两包零 iv_* topic，预期路由 NOT_APPLICABLE 快速拒绝（零模型零切片）；TESTER 核收敛终态+无伪切片即可。不占 cancel 预算，不拖延 A flat 链（其 409 解锁依赖 D4 的 submission 删除而非 run 状态，见 D4 时序）。

**D4 — date-grouped submission 删除 + NAS 清理时序（授权 A，顺序固定）：**
1. 等 3 dup run 全部终态（D2 cancel 或自然收敛）且对应 source/path_claim 释放（A 只读核 SELECT）。
2. 备份后删除 3 条 date-grouped submission：`03281a51…`/`5e08e73d…`/`7f4e7b75…`（`ingest_submission`，逐行全列备份到 receipt）。
3. 核 A flat 三提交（`a65a25a7`/`87dfebaa`/`518089ed`）409 是否释放、scanner 能否正常绑定。
4. 删除 `ready/spray/20261012/`（4 包目录，删前 du -sb+逐文件 SHA 留证，确认 flat 顶层同名文件完好）；`incoming/spray/20261012/` 残留一并清。
5. 大包/删除类机械操作仍走 runtime_tools 冻结 op 跨回合，不占模型回合。

**D5 — RETRY 发起方归因（C 只读）：** 查 3c9c496 代码/scheduler 是否存在对 SCENE_FAILED run 的自动 RETRY（retry_mode=normal）机制及触发点（22:53:02 三 run 同刻 RETRY_REQUESTED 的事件源），结论落 C 观察事件报协调者。**不因此新开任务**；若证实系统自动重试设计，作为既有行为记录，不扩需求。

**D6 — 16_33_10 空包：** 维持 scanner 拒绝路径（TESTER ② 已 PASS），A 将正式拒绝痕迹补进 `upload-ledger.json` 落账（BATCH-STATUS 23:07 行「拒绝痕迹未见」由此闭合）。

## 三、23:5x 增补（消费 A 23:33 / C obs11 23:41 / TESTER 23:12+23:48 四事件）

- **C obs11 定性更正**：`scene-a4824f1c`（14_42_48 dup）attempt-2 非 EXECUTING 待推进，**EXTRACT 产物已全量落盘（171 jpg/534 pcd，树 2.4GB）+ INFER 阶段活跃在途**（VLM 192.168.2.45:8002 Running=4、容器渲染线程活跃，23:41 实测）。**D2 执行时序增补：A 下一动作=立即只读核正式 cancel 端点，存在则尽快 cancel 止血（不再等 dup 自然收敛）；无端点维持 D2 原口径自然收敛 + TESTER 记烧模型证据。** 该 dup 与新 flat `a65a25a7` 同物理源双链并存（TESTER 23:48 核 ingest_submission 11 行全集在案）。
- **C obs11 ②**：3 排队 run 的 attempt-1 均 FAILED at RESOLVING（缺车辆绑定 fail-closed 根因与 2210 一致），但 `/api/v1/sources` 四 source 现均 vehicle_code=test READY（A 正式提交已补绑定）——排队 run（含合法 `scene-4acf689f`）被串行队列取走后 attempt 预期过 RESOLVING，C 下轮核。
- **A 23:33 事件确认**：ruling 2210 授权面收窄执行完毕（删 `13dc398c`/重提交 `a65a25a7`+`87dfebaa`/`24d60fee` 保留申报/date-grouped PAUSED）与本裁决一致；A「date-grouped 删除时序待更新裁决」由 **D4 正式解除**（A 按 D2 处置 dup→终态后依 D4 时序执行，无需再等）。
- 资源面（C obs11）：NAS 98T/71% 余 29T、load 0.47、18000 production ready、proxy active_runs=1，无风险。

## 四、范围与禁止（沿用 2210 + 本裁决）

- 严禁触碰保持行（`15_58_23`/`16_00_13`/`16_31_25` 的 submission/run/文件）；不重提交已 PASS 包；不改业务代码/部署；kill 仅限 D2 的正式 cancel 端点路径。
- 本批无代码变更，不起 OCR；强审 REVOKED 不续；夜间静默照常（工作与落盘继续，不主动群报）。

## 五、TESTER 增量范围（按 D 项更新）

① `scene-4acf689f`（16_02_03 flat，D1 保留链）SCENE_DONE 后核八步/跨DB3 真实时间戳边界/两次 reconcile 幂等；② 维持已 PASS 项；③ A flat 四包（14_42_48=`a65a25a7` 为准 run / 16_37_47=`87dfebaa` / 16_58_28=`518089ed` / 16_02_03 见①）逐包终态+产物+reconcile；④ D2 cancel 证据（或自然收敛终态+dup 子包处置记录）+ D3 两 dup NOT_APPLICABLE 无伪切片 + D4 claim 释放核验。全批齐后 TEST_REPORT_PENDING 交协调者。回执 `test-receipts/TASK-11S-BATCH-1012/attempt-1.md`。