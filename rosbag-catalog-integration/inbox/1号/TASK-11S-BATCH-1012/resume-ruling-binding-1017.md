> **⛔ 本派单已被 10:2x 协调者 STOP 取代，勿执行（见下方 STOP 块）。**

# TASK-11S-BATCH-1012 / A / 协调者裁决更正（binding 等待口径）

时间：2026-10-14 10:17 +08:00（协调者消费 09:54 Codex 只读纠正审计）。owner=A，attempt-1。
**本裁决替代/收窄 resume-ruling-2338.md 的 D4③「等 4acf689f 终态后 flat 三提交自动收敛绑定」口径——该口径无代码/运行证据支持，作废。**

## ⛔ STOP：本派单作废（2026-10-14 10:2x 协调者，消费 `codex-direct-repair-20261014.md` 10:07）

**A 不得执行本文件下方任何绑定恢复动作。** 用户已明确「直接处理问题」，协调者 10:07 收到 Codex 直接修复范围（`/home/wang/work/doc/prd/rosbag-catalog-integration/inbox/coordinator/SPRAY-BATCH-1012-20261013/codex-direct-repair-20261014.md`）：

- 三份 flat 提交 `a65a25a7`/`87dfebaa`/`518089ed` 的**重登记恢复由 Codex 单写**，在隔离树 `fix/spray-progress-20261014`（分支已存在）通过正式 Backend API 执行。
- **A 暂勿对这三份提交再上传、重提或触发 retry**（避免与 Codex 单写形成第二写者）。
- 本文件下方「A 本回合执行范围」整段作废；其幂等原则仍有效但 owner 已转移给 Codex。

**A 维持面（不改动）**：大包 `scene-4acf689f` 跨夜继续不 kill/cancel/retry（Codex 同口径「保持运行不重启」）；已 PASS/收口三包（15_58_23/16_00_13/16_31_25）不动；A 唯一上传/提交 owner 身份不变，但**本批 flat 三提交的绑定恢复本轮由 Codex 代行**，待 Codex 修复回执收口后 A 再按协调者新口径接续（若有）。A 侧本轮只读观察即可，不重复领取本文件。

（下方原绑定执行范围保留作历史，owner=Codex，A 不执行。）

## 纠正后的事实（只读核实 + 代码因果）

Codex 只读审计（`/home/wang/work/doc/analysis/spray-batch-progress-20261014/REPORT.md` + `production-snapshot.json` 09:52）实测：

1. 三份 flat 正式提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 至 09:53 仍 **`PENDING_INPUT`、`source_id=NULL`、`source_generation=NULL`、`bound_ready_path=NULL`**，尚未创建各自正式 run。
2. 它们对应的**物理 flat 源已在 ready**（flat 布局 `ready/spray/<bag>`），旧 date-grouped 重复 run 全 `SCENE_DONE`（a4824f1c SUCCESS / eb4397c3·24ab78bb NOT_APPLICABLE 零模型）。
3. **代码因果**（生产 `3c9c496`）：`ingest_service.create_submission` 只建 `PENDING_INPUT` 就 commit，**不主动绑定已存在 ready 源**；绑定发生在 **`source_service.register_source` → `bind_ingest_for_registration`**（登记时按 profile + entry_relative 经 `_find_pending_submission` 找 PENDING 行并置 `SCHEDULED`）；资源排队（SCENE_EXEC_HOST）发生在绑定/outbox **之后**。
4. **SCENE_EXEC_HOST 释放 ≠ 触发登记绑定**。Scanner `_recover_moves` 只重放 `MOVING`/`MOVED_PENDING_REGISTER`；当前生产 `/data/scanner-state-scene.json` **仅有旧 dated `…/20261012/…16_00_13` 的 MOVE_CONFLICT 项，三个 flat 包零恢复记录**。
5. 09:45:58 场景 scan `created=0/updated=0/failed=2`，三包绑定无推进——**不是串行推理占槽造成的执行队列等待**。

**结论：不要再以「等 4acf689f 终态自动推进」为由挂起。三份 flat 提交停在「接收绑定之前」，属登记/绑定面问题，独立于在途大包，可立即推进。**

## A 本回合执行范围（唯一上传/提交/绑定 owner，机械操作走 runtime_tools 冻结 op 跨回合，不并发第二条模型线）

**先核幂等身份，再操作。** 逐包（a65a25a7 / 87dfebaa / 518089ed）：

1. **只读取证**：flat 源是否已登记为 source（查 sources 表 flat ready 路径对应的 source_id / 是否存在）、scanner journal/state 对这三个 flat 包是否有 move/register 痕迹、submission 行的 `path_claim_key` 是否已释放。
2. **判定根因**：为何 `bind_ingest_for_registration` 未命中这三份 PENDING 提交（源未登记？entry_relative 口径？claim 未释放？）。
3. **恢复合法绑定**（择一，按实测最小区间）：
   - 若 flat 源已登记但 bind 漏匹配 → 触发 Scanner 对该源**恢复登记**（`_recover_moves` 口径或等价重登记），让 bind 走既有幂等路径置 `SCHEDULED`；
   - 若 flat 源未登记 → 确认 scanner 将其 flat incoming→flat ready 并登记（**复用既有物理源身份，不重新上传**）；
   - 复用既有源/run 身份：正式 flat 提交必须绑到 **flat 源**，不得绑到已删除的 date-grouped dup 源（FFDEE943/9C9456B6/205E5054）。
4. **硬禁止**（违反即保留现场报协调者，不自行处置）：
   - **不重复上传**（flat 物理源已在 ready，不重拷）；
   - **不直接改库**（不手写 UPDATE submission.source_id / 不插 source 行）；
   - **不新建 reanalysis / 不重烧已完成的 dup 模型 run**（旧 dup 已终态，正式链走自己身份）；
   - 不动 4acf689f（16_02_03）在途 run，不 kill/cancel/retry；
   - 不动已 PASS/收口三包（15_58_23 / 16_00_13 / 16_31_25）。
5. **若三包无法经既有幂等路径自动绑**（如 entry_relative 契约与 flat 布局不匹配=真实业务缺陷）→ **保留现场，逐包如实记录**（source_id 实测、claim 状态、bind 未命中点、根因），报协调者定最小纠错范围/收口规则，**不硬造绑定、不改代码**。

## 交付回执

`receipts/TASK-11S-BATCH-1012/a-attempt-1.md` 增『1017 绑定更正回合』节：逐包 源登记状态 / 绑定 outcome（SCHEDULED 或保留原因）/ 证据文件路径 / 是否触发新 run 创建。落 `events/A/` 实质事件（带稳定 event_id + occurred_at + task/attempt + 证据 + 下一步）。

**大包 4acf689f 独立跨夜继续（C 只读观察、TESTER 验收面不变）；本 binding 更正不等待它。**