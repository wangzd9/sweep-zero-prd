# TASK-11S-BATCH-1012 / A / attempt-1 — 执行回执（23:3x 增量，随 op/裁决接续更新）

owner=A（A-batch-1012），唯一上传/正式提交 owner。生产业务 `3c9c496`，batch `spray-production-1012-20261013`，profile `scene-spray`，车辆 `test`。
本回执记录截至 2026-10-13 23:3x 的真实执行面；TESTER 独立验收口径见 `test-receipts/TASK-11S-BATCH-1012/attempt-1.md`。

## 已完成（8 包逐包）

| 包 | 内容落位 | 正式提交 | 现状（A 23:2x DB/物理实测） |
|---|---|---|---|
| 15_58_23（首包） | 复用既有 ready，本机↔ready 逐字节 SHA 一致（metadata `5a3cb296…`=manifest） | 复用 `9949d1a7…`（不重提交） | SCENE_DONE attempt2 PASS 冻结 |
| 16_00_13 | A flat 落位（staging+SHA+原子rename+移后复验） | A `99615748…` SCHEDULED | run `scene-604c0896…` SUCCESS 21:43 |
| 16_31_25 | A flat 落位 | A `e5649055…` SCHEDULED | run `scene-bc8c1d1c…` NOT_APPLICABLE 21:43（零模型，与 B 一致） |
| 16_33_10（空包） | A flat 落位（0B×2，SHA `e3b0c442…`） | A `7a71e404…` PENDING_INPUT（仅记录意图） | scanner 日志实测反复 `FAILED … missing rosbag2_bagfile_information`，零 run 创建=拒绝/隔离可追溯（待 TESTER 核） |
| 16_02_03（10.1GB） | 第二写者 flat 文件 21:26-21:52 间落 incoming；**A 22:5x op 逐文件 SHA 全量核验 REUSE_INCOMING_SHA_MATCH**（metadata `e40a8d86…`/db3 `b352cde3…`/`bceda7fe…`） | `24d60fee…`（第二写者行，全列快照实测 source_metadata 完整含 vehicle_code=test）23:05:30 被 scanner SCHEDULED：source `91FFEEC1…`（source_copy id122，10,105,905,152 B）→ run `scene-4acf689f…` SCENE_SLICE_QUEUE | A 不重复提交（目标态=每包一条 flat submission，已有且有效）；**A 未拷贝 10GB（无必要，文件先于 A op 到位）** |
| 14_42_48（725MB） | flat 已在 ready（724,637,738 B 全尺寸，source_copy id116/119 fingerprint `fa86215e…` 同源） | 409 根因 `13dc398c…` **A 23:0x 按裁决删除**（备份 `polluted-submission-13dc398c-backup-2300.json`，flat claim 删前唯一占用→删后零占用实测）；**A 23:0x 正式重提交 `a65a25a7…` HTTP 201 PENDING_INPUT**（stable key `spray1012:…0195a14f`，source_metadata 按 manifest） | 待 scanner 绑定（见「观察项」：同 source 被 date-grouped 行先行占位，409 恢复路径反复） |
| 16_37_47（7.3GB） | A 22:5x op 全量源 SHA 核验 REUSE_READY_SHA_MATCH（`fdbec007…`/`8532ce81…`/`bc7ad38c…`，ready 平铺 7,321,525,005 B） | **A 23:0x 正式提交 `87dfebaa…` HTTP 201 PENDING_INPUT**（stable key `spray1012:…ef68da1f`，台账原缺条目已补） | 同上待绑定 |
| 16_58_28（6.8GB） | A flat 落位（6,794,992,397 B，source_copy id120 `8a2af8e0…`） | A `518089ed…` PENDING_INPUT（21:43） | 同上待绑定 |

## 本回合执行（21:52 BLOCKED 解除后，ruling-doublewrite-2210 授权面）

1. **op 收口**：冻结 op `…-bigbags-copy`（worker 2520120 身份实测消失+unit inactive）→ `RECONCILED`（四包逐包对账记录落 result.json）。
2. **新 op `…-finalbag-160203-163747verify`**：22:53:47 start，23:0x **SUCCEEDED** step1 exit 0（16_37_47 REUSE_READY_SHA_MATCH / 16_02_03 REUSE_INCOMING_SHA_MATCH，零重拷、台账 22:56/22:59 更新）。
3. **污染 submission 清除（收窄执行）**：
   - 已删：`13dc398c…`（14_42_48 flat，A 409 根因）。删时断言 PENDING_INPUT 零绑定零 run 全过，SELECT 全列备份+删后 claim 释放核验在 receipt。
   - **保留/暂停（ruling 前提实测失效，详见下）**：`24d60fee…`（16_02_03，23:05 已 SCHEDULED 绑定 run，现为该包唯一有效提交）；3 条 date-grouped `03281a51…`/`5e08e73d…`/`7f4e7b75…`（其 run 23:0x 自动 attempt-2：`scene-a4824f1c…` attempt-2 **SCENE_RUNNING** 活租约、`scene-eb4397c3…`/`scene-24ab78bb…` attempt-2 SCENE_SLICE_QUEUE，23:27 仍在更新）。
4. **NAS date-grouped 清理：PAUSED**（与在途 attempt-2 run 纠缠，等待终态+更新裁决）。

## 与 ruling 前提的事实偏差（申报，不自行扩权处置）

- ruling ③/第16行：`13dc398c`/`24d60fee`「无 source_metadata（缺 vehicle_code）」——A 23:0x 全列快照实测**两行 source_metadata 均完整**（vehicle_code=test，hash `9e6f0c69…`，与 manifest 固定值一致）；attempt-1 三 run fail-closed 的「缺车辆绑定」真实根因待协调者/C 从代码面核（12S-A 门禁读的是 schedule event 冻结快照而非 submission 行，猜测不采信）。
- ruling ②/§四：3 个 date-grouped run「均终态 SCENE_FAILED 保留不删」——23:01 实测已**自动 attempt-2** 且一个 SCENE_RUNNING（`platform-local` 活租约，proxy active_runs ACCEPTED），自动重试机制与「零模型零产物」结论不再成立；attempt-2 有完整车辆元数据，**可能真实跑成 SUCCESS 烧模型**（14_42_48 attempt-2 绑定的 flat ready 源 `FFDEE943…` 与 A `a65a25a7…` 指向同一物理源）。
- ruling ③第20行：16_02_03「文件全域失踪」——23:0x 实测 flat 文件已在 incoming/ready（第二写者 cp 完成时间介于 21:52 与 22:5x 之间，非在途新写者；A op SHA 核验锚定）。

## 2338 续跑回合（2026-10-13 23:52–00:05，ruling-duprun-2338，夜间静默不群报）

1. **D2 完成（cancel 未执行=已终态，按裁决口径留证报协调者）**：只读核 3c9c496 确认正式 cancel 端点存在（`POST /api/v1/scene-analysis-runs/{id}/cancel`，排队→CANCELLED / 运行→CANCELLING，app/api/scene_analysis_runs.py:41 + scene_slice_service.cancel_scene_run）。**处置前 23:5x DB 实测 dup `scene-a4824f1c3ea64a5dba9e67bfc353` attempt-2 已 23:54:41 终态 SCENE_DONE**（event 链 RETRY_REQUESTED 22:53:02→CLAIMED→STEP_DONE×8→SCENE_RUN_SCENE_DONE 23:54:41→RESOURCE_RELEASED；lease 已 NULL）。终态=**SUCCESS**：`scene_outcomes.spray.outcome=SUCCESS`（recorded_at 23:54:41）、4 段 scene_segment publish_target=1（15s 切片）、bag FFDEE943… READY（=A `a65a25a7` 同物理 flat 源，fingerprint `fa86215e…` 同源在案）——**裁决预设情形「终态 SUCCESS=重复烧模型实证」成立：同一物理源被 dup 链与 A flat 链各烧一次模型（dup 侧 22:53–23:54 ~61min 窗口）**。cancel 已无对象（非排队非运行），未调用端点，run 行保留不删。证据 `dup-a4824f1c-done-evidence-2338.json` + `scan2-dupruns-409-evidence-2338.json`。
2. **D3 面只读核**：dup `scene-eb4397c3…`（16_37_47）00:01:30 SCENE_DONE outcome **NOT_APPLICABLE**（无 iv topic，与 B 一致，零模型）；dup `scene-24ab78bb…`（16_58_28）00:02:34 **SCENE_RUNNING**（platform-local 活租约）——D4 删 3 date-grouped submission 的时序前提「3 dup 全终态」未满足，**D4 保持暂停**等 `scene-24ab78bb` 终态。
3. **409 根因实测（新事实，供协调者）**：scanner 3h 窗口 FAILED recovering 409 持续行全部指向 `ready/spray/20261012/rosbag2_2026_10_12-16_00_13`（**16_00_13 date-grouped 副本**，非 14_42_48）；A flat 三包（14_42_48/16_58_28/16_37_47）3h 窗口零绑定行，submission 仍 PENDING_INPUT。即 D4 删除范围需补含 `ready/spray/20261012/` 下 16_00_13 残留（裁决 D4 已含该目录整体删除，口径一致，此处仅申报 409 实测指向）。
4. **D1 完成**：`24d60fee` 未动（00:02 实测仍 SCHEDULED 绑 `scene-4acf689f`，该 run 00:02:44 在 queue 推进，跨夜不 kill/retry）。
5. **D6 完成**：16_33_10 拒绝痕迹补入 `upload-ledger.json`（scanner 日志 17+ 行 `missing rosbag2_bagfile_information` 持续 + scan_job 计数 failed:2 持续 + 零 source 绑定零 run；证据 `d6-163310-rejection-trace-2338.json`）。

## D4 执行回合（2026-10-14 00:14–00:38，ruling-duprun-2338 D4 时序，夜间静默不群报）

1. **前提解锁实测**：3 dup run 全终态+lease 全 NULL——`scene-a4824f1c` 23:54:41 SUCCESS（上轮已报）/`scene-eb4397c3` 00:01:30 NOT_APPLICABLE/`scene-24ab78bb` 00:07:46 NOT_APPLICABLE（outcome 快照实测，缺 iv topic 与 B 定性一致，零模型）。
2. **删 3 条 date-grouped submission**：备份全列→`d4-dategrouped-subs-backup-0016.json`；删前断言全过（SCHEDULED×3、path_claim_key NULL×3、绑定源 FFDEE943/9C9456B6/205E5054 对应 run 全 SCENE_DONE）→DELETE（带 `AND status='SCHEDULED' AND path_claim_key IS NULL` 条件）→post 零残留，A 四提交（a65a25a7/87dfebaa/518089ed/24d60fee）未受影响（`d4-dategrouped-subs-delete-0017.json`）。
3. **删 NAS `ready/spray/20261012/`（14G）**：10 文件逐文件 SHA256+size 留证；删前 flat 七包完好断言 + dated/flat 四包逐包**总字节全 MATCH**（14_42_48 724637738 / 16_00_13 89664966 / 16_37_47 7321525005 / 16_58_28 6794992397）；同盘（cifs 设备 71）`rename` 移入 `.upload-staging/d4-dategrouped-delete-20261014/`（非 rm -rf，留暂存待处置）；post flat 七包文件数完好；`incoming/spray/20261012/` 残留实测 **absent**（`d4-nas-delete-evidence-0021.json`）。
4. **释放核验**：删除前 scanner 循环 `FAILED recovering …/ready/spray/20261012/…16_00_13: HTTP 409` 持续；删除后 00:28/00:33/00:36 三个窗口 **409 循环停止**，仅剩空包 16_33_10 `missing rosbag2_bagfile_information` 拒绝行（既定拒绝路径，D6 台账已记）。
5. **绑定面观察（未收敛，下回合核）**：A flat 三提交删除后 ~13min 仍 PENDING_INPUT 未绑定——SCENE_EXEC_HOST 串行占用（`scene-4acf689f` 16_02_03 10.1GB 大包 SCENE_RUNNING 心跳 30s 正常推进至 00:36:58）+scanner 恢复绑定排队；预期 4acf689f 终态后依次收敛，跨夜不 kill/retry。

## 观察项（下回合接续，A 权限内）

- 14_42_48 / 16_37_47 / 16_58_28 三新提交绑定面：scanner 日志反复 `FAILED recovering …/ready/spray/20261012/…: HTTP 409`，flat 恢复疑似被 date-grouped 副本占位 409 拖累；date-grouped 文件清理授权到位后应自动收敛，A 下回合核。
- attempt-2 三 run 终态：预期 16_37_47/16_58_28 NOT_APPLICABLE（无 iv_* topic，B 取证）、14_42_48 NEEDS_RUNTIME；任一 SUCCESS=重复烧模型实证，第一时间报协调者（保留现场不自行 cancel）。
- 16_02_03 run `scene-4acf689f…` 推进（跨 DB3 包，~9min 处理时长，TESTER 面验真实时间戳边界）。

## 未执行项（待协调者）

- date-grouped 3 submission + `ready/spray/20261012/*` NAS 清理：ruling 前提失效，已按收窄口径暂停，等更新裁决（尤其 attempt-2 在途窗口的删除时序）。
- 13dc398c 之外第二写者行处置确认（24d60fee 保留口径）。
- BATCH-STATUS 逐包表更新（协调者单写）。

## 证据文件

- `upload-ledger.json`（8 包全量 state/src_sha/idempotency_key/submission HTTP 响应，22:59 后含 16_37_47/16_02_03 核验条目）
- `polluted-submission-13dc398c-backup-2300.json` / `flat-144248-claims-before|after-2300.json` / `polluted-submission-backup-2300.json`（5 行 23:00 快照）/ `polluted-cleanup-execution-2300.md.json`（删除执行摘要+保留理由）
- op：`operations/A/…-bigbags-copy/result.json`（RECONCILED）+ `operations/A/…-finalbag-160203-163747verify/result.json`（SUCCEEDED，result.log 含两包逐文件 SHA）
- event：`a-batch1012-attempt1-reconcile-finalbag-op-running-20261013`；本轮 23:3x 新增 event 见 sessions/A.md
- DB 只读实测时间线：22:2x（全量 submissions/sources/runs）/ 23:0x（删前删后）/ 23:2x（绑定核验）
## 1017 绑定更正回合（2026-10-14 10:2x，A 只读核实 Codex 完成结果）

- **派单/裁决**：`resume-ruling-binding-1017.md`（10:17）D4③「等 4acf689f 终态后 flat 三提交自动收敛绑定」口径作废（代码因果：绑定发生在 source 登记 `bind_ingest_for_registration`，`create_submission` 不主动绑、SCENE_EXEC_HOST 释放≠触发登记）；`codex-direct-repair-20261014.md`（10:18）明确 **flat 三提交重登记恢复由 Codex 单写经正式 Backend API 执行，A 暂勿再上传/重提/trigger retry**。
- **A 本回合动作=只读核实，不重复执行绑定**（两裁决时间线交叉，A 未对三提交做任何写/重试/上传，无冲突）。
- **核实结论**（处理机 MySQL 只读 NOW 10:29:25 + backend 日志 + Codex `binding-repair.jsonl` 10:23）：
  1. flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 已于 **10:23:08–09 绑定 SCHEDULED**（backend 日志 02:23:08 UTC ×3 `POST /api/v1/sources/register 200`，此前 02:18:28 一 409=Codex 幂等预检）。
  2. **绑定身份合法**：`bound_ready_path` 全为 flat 路径 `ready/spray/<bag>`，`source_id` 指向 flat source_copy 行（id119 `FFDEE9435C`/id120 `205E505412`/id121 `9C9456B6EF`，登记 10-13 21:45–22:05、`deleted_at` NULL），**非** date-grouped dup 行（id116/117/118，路径 `ready/spray/20261012/<bag>`）；register 响应 `created:false`=复用既有 flat 源身份、`matched:true`/`scheduled_purposes=[scene_slice]`，无新源行、无直接改库。
  3. **未重烧模型/未新建 run**：最近 40min `pipeline_run` 零新建（与 Codex `created_runs=0/reused_runs=3/errors=[]` 一致）；4acf689f 仍 SCENE_RUNNING（heartbeat 10:29:12 30s 连续，INFER 跨夜继续不 kill/retry）；其余 6 scene run 全 SCENE_DONE 无变化；scan_job 4095/4094（10:16）SUCCESS 幂等，scanner state 现仅旧 dated 16_00_13 MOVE_CONFLICT 残留（flat 三包零恢复记录，1017 口径一致）。
- **绑定 outcome**：三包 **SCHEDULED**（非保留），逐包 source_id 实测 `FFDEE9435C4547…`/`9C9456B6EFEA…`/`205E50541256…`，generation=1。
- **是否触发新 run 创建**：否（created_runs=0，SCHEDULED 待 SCENE_EXEC_HOST 串行排程；14_42_48 正式验收以 `a65a25a7` 绑定 run 为准）。
- **证据**：`/home/wang/work/doc/analysis/spray-batch-progress-20261014/binding-repair.jsonl`（Codex 10:23 重登记前后快照+3 register 响应）/`recovery-review-background.md`；处理机 backend 日志 02:18–02:23 register 行 + MySQL source_copy id116-121 + ingest_submission 10:23:08-09 绑定行（A 只读实测）；`sessions/A.md` 10:2x 核实条目。
- **下一步**：等 4acf689f 终态（任一 outcome）→核 flat 三提交是否按 SCHEDULED 依次创建正式 run（TESTER 验收面）；若协调者要求 A 独立复核绑定契约（entry_relative/claim 释放/为何 10-13 登记时 bind 漏匹配），再逐包深挖根因。
### 1017 更正补充（2026-10-14 10:4x，A 只读核实终态）

- **`resume-ruling-binding-1017.md` 对 A 已 STOP**（协调者 10:2x，消费 `codex-direct-repair-20261014.md` 10:07 用户「直接处理问题」授权）：flat 三提交的重登记恢复 **owner 由 A 转 Codex**（隔离树 `fix/spray-progress-20261014` 单写经正式 Backend API），A 停对 `a65a25a7`/`87dfebaa`/`518089ed` 再上传/重提/retry。**A 本回合「只读核实、不重复执行绑定」的决策与 STOP 方向一致，未产生任何 A 侧重登记写/重试，无冲突。**
- **Codex 10:23 已完成绑定（复用既有终态 run，非新建）**：`a65a25a7`(14_42_48)→`scene-a4824f1c`(SUCCESS)/`87dfebaa`(16_37_47)→`scene-eb4397c3`(NOT_APPLICABLE)/`518089ed`(16_58_28)→`scene-24ab78bb`(NOT_APPLICABLE)，全 SCHEDULED gen1、事件 CONSUMED、`created_runs=0/reused_runs=3/errors=[]`（复用既有终态 run，未重烧模型，全批仍 7 run）；证据 `doc/analysis/spray-batch-progress-20261014/binding-repair.jsonl`（register `created:false` 与 A 实测一致）。
- **A 只读核实与 Codex 回执相互印证**：① `bound_ready_path` 全 flat 路径、`source_id` 指向 flat source_copy 行（id119/120/121，非 date-grouped dup 行 id116-118）；② register `created:false` 无新源行/无直接改库；③ 最近 40min `pipeline_run` 零新建；④ 4acf689f 仍 SCENE_RUNNING（heartbeat 10:29:12）未动。**A 侧无剩余绑定动作。**
- **A 剩余面=只读观察**：等 4acf689f 终态（任一 outcome）→配合 TESTER 全链增量验收（14_42_48 正式验收以 `a65a25a7` 绑定 run=`scene-a4824f1c` 复用结果为准，含既有切片两次 reconcile 幂等核账，归 TESTER 域）；不重上传/不改库/不重烧 dup/不 kill 4acf689f。
## 收尾增补回合（2026-10-14 10:5x，A 只读核实 + 台账补录，D4③/D6 回执）

**消费** `post-release-closeout-20261014.md`（10:49 协调者收尾增补，入口 `inbox/control/POST-SPRAY-CLOSEOUT-20261014.md`）：生产 `3c9c496` 已上线 main `63bfcf8`；10:23 正式 API 已恢复三提交（复用既有终态 run，created_runs=0/reused_runs=3）；首要=核三份恢复提交 source/generation/flat ready 路径、outbox CONSUMED、复用 run/attempt，补 upload-ledger 及 D4③/D6 回执；不上传/不重新 submit/register/不 retry/不直接写库；交付协调者后释放槽。A 已有 10:29 独立只读核实（见上 1017 节），本轮补 outbox/复用 run 实测 + 台账收口，不重跑已证事实。

**逐包收口实测（处理机 MySQL NOW 10:55:47）**：

| 包 | submission | source_id（flat） | gen | flat ready 路径 | outbox 事件 | 复用 run（attempt/终态） |
|---|---|---|---|---|---|---|
| 14_42_48 | `a65a25a70b…` SCHEDULED | `FFDEE9435C4547…` | 1 | `ready/spray/rosbag2_2026_10_08-14_42_48` | `purpose_schedule_event` id8 **CONSUMED** 10:23:08 | `scene-a4824f1c…` attempt2 SCENE_DONE（23:54:41，既有终态非新建） |
| 16_37_47 | `87dfebaa5b…` SCHEDULED | `9C9456B6EFEA…` | 1 | `ready/spray/rosbag2_2026_10_12-16_37_47` | id9 **CONSUMED** 10:23:09 | `scene-eb4397c3…` attempt2 SCENE_DONE（00:01:30，NOT_APPLICABLE 零模型） |
| 16_58_28 | `518089ed6f…` SCHEDULED | `205E50541256…` | 1 | `ready/spray/rosbag2_2026_10_12-16_58_28` | id10 **CONSUMED** 10:23:09 | `scene-24ab78bb…` attempt2 SCENE_DONE（00:07:46，NOT_APPLICABLE 零模型） |

- **source/generation 实测**：三 submission `source_generation=1`、`row_version=1`、`path_claim_key=NULL`（claim 已释放）、`updated_at` 10:23:08-09；`source_id` 均指向 flat source_copy 行（deleted_at NULL），非已删 date-grouped dup 源。
- **outbox CONSUMED**：`purpose_schedule_event` id8/9/10 三行 `status=CONSUMED`、`error_reason=NULL`、frozen_at 10:23:08-09，`scene_code=spray`/`capability_version=spray-v1`/`profile scene-spray` 与正式提交一致。
- **复用 run/attempt**：三 reuse 目标 run 全 `SCENE_DONE attempt2`、`updated_at` 停在本批既有终态时刻（23:54/00:01/00:07），**非 10:23 新建**——与 Codex `created_runs=0/reused_runs=3` 一致，全批仍 7 run、attempt 不变、未重烧模型。
- **16_02_03（D1 保留链）**：`24d60fee44…` SCHEDULED 绑 `91FFEEC1…` gen1（source_copy id122 flat ready 路径），run `scene-4acf689f…` attempt1 仍 **SCENE_RUNNING**（PRECHECK/EXTRACT DONE、INFER RUNNING、余 QUEUED；10:23 Codex 经正式步骤 API 补报真实阶段，不改 checkpoint/不重启/不 cancel/retry），跨夜继续，完成帧数/ETA 未知。
- **空包 16_33_10（D6 回执维持）**：scanner 拒绝可追溯（日志反复 `missing rosbag2_bagfile_information` + scan_job 每 10min failed:2），但 submission `7a71e404…` **仍 PENDING_INPUT、无 source/run**——保护有效≠提交层终态已收口，**不写提交终态已完成**（台账 `rejection` 条目已记，结论=真实输入校验拒绝闭环、拒绝可追溯、零 source 零 run）。

**台账补录**：`upload-ledger.json` 三条 flat 包追加 `binding_closeout`（source_id/flat_ready_path/outbox CONSUMED/复用 run+attempt+终态时刻/evidence），`16_02_03` 补 `submission_note`（24d60fee SCHEDULED 绑 91FFEEC1 run 4acf689f SCENE_RUNNING）。

**A 侧收口**：1017/D4③ 绑定恢复面对 A 已 STOP（owner 转 Codex，已完成）；A 本回合只读核实 + 台账补录，未做任何重登记/重试/上传/写库。剩余 A 面=只读观察 `scene-4acf689f` 终态（任一 outcome）配合 TESTER 全链增量验收；不 kill/retry 大包、不重烧 dup、不自行扩大修复。交付本回执后释放槽。
