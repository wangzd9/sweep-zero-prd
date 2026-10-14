---
task: TASK-03B
attempt: 3
status: ACCEPT_MERGED
decided_by: 协调者 cron（scene-coordinator-poll，2026-10-09 14:1x）
updated: 2026-10-09 14:1x
base: 8e97ef1
output_commit: a8fac99（覆盖 14b7a64，amend 历史）
merge_commit: b3280c9（--no-ff，a8fac99 已在 main 祖先链，**禁止再合**）
pushed: origin/main = b3280c9（GitLab 已推；05 四 commit dccc867/1946718/d1f2eba/2d4a6fa 同批上 origin）
---

# TASK-03B attempt-3 验收结论：ACCEPT（已合入 b3280c9 + push origin）

> ⚠️ 给主协调者会话：本 cron 已在 14:0x 完成 03B 合入与推送（main=b3280c9，
> origin 已同步）。TODO.md 中 03B 的 VERIFYING/B1 描述是本合入**之前**的快照——
> a8fac99 已在 main 祖先链，**请勿对 a8fac99/14b7a64 再执行 merge**。
> B1 增量 OCR（14:06 起的进程）如需补跑可继续，作为覆盖性证据补记即可，
> 不再阻塞合入（F1/F2/F3 已逐条对照代码独立核实，见下）。

## 协调者 cron 独立验收（不信任自报）

### 范围核对
- `git diff 8e97ef1 a8fac99 --stat` = 13 文件 +2382/-8，与 attempt-2 同范围，零扩散。
- 无 .venv/环境产物入 commit（`--name-only | grep -i venv` = 空）；worktree `.venv`
  为 untracked 软链（指向主仓，回执已申报）。base 8e97ef1 正确且在 main 线上（是 b3280c9 祖先）。
- a8fac99 相对 14b7a64 增量仅 2 文件（ingest_service.py +74/-25、test_ingest_config.py +72），符合派单"只含核心文件+对应测试"。

### 测试复跑（wt-03b 独立跑，借主仓 venv）
- 定向 ingest 三文件 → **33 passed**（含 2 条新回归）。
- 全量 → **666 passed, 10 skipped, 3 failed**；3 failed 全部
  `tests/test_devflow.py` 沙箱用例，**同一 3 例在 main 工作区独立跑 = 3 passed**
  → 坐实为 worktree `.git` 文件态沙箱环境问题（非本任务回归），与 attempt-2 结论一致。
- ruff format --check + ruff check（改动 2 文件）→ 全绿。
- 合入后 main（b3280c9，含 03B+05）全量复跑 → **730 passed, 10 skipped**，零回归。

### F1/F2/F3 逐条对照 a8fac99 代码核实（非盲信回执）
1. **F1 [high] 活动版本折叠**：`_active_profiles(db)` helper（ingest_service.py:64-77）
   max-version-per-profile_id 折叠 + profile_id 排序；`match_profile_for_incoming`（L110）
   与 `list_profiles`（L215）统一走该 helper，第二份折叠逻辑已删（diff 核实 list_profiles
   原内联折叠 7 行删除）。回归 `test_match_profile_collapses_to_active_version` 独立跑 GREEN。✅
2. **F2 [medium] row_version DB 强制**：patch_submission L425-444 —— flush 并入同事务后
   `sa_update(IngestSubmission).where(submission_id==, row_version==expected,
   status=='PENDING_INPUT').values(row_version=IngestSubmission.row_version+1)`，
   `rowcount==0 → db.rollback() + 409 ROW_VERSION_CONFLICT`；`row_version` 未再在 ORM 属性上
   手动 +1（diff 核实 `submission.row_version += 1` 已删）。`PENDING_INPUT` 字面量与同文件
   L259/308/495/529 既有用法同口径。回归 `test_patch_concurrent_generation_rejected` 独立跑 GREEN。✅
   **残余风险**：真并发行锁语义 SQLite 无法实证（回执如实申报，隔离 MySQL 补测）。
3. **F3 [low] 死代码**：`_ensure_system_submission` 首个不可达查询已删，保留
   relative_path+PENDING 兜底；docstring 重写为可达性论证（diff 核实 -14 行/+6 行）。✅

### OCR 覆盖度记录（如实）
- 本轮 cron 代跑 a8fac99 全量 OCR 遇 vLLM 饱和（4 running/7-9 waiting，3 号 1 号 OCR
  争用）：r1（--from/--to 模式 31m5s）8/10 文件超时失败；r2（-c 模式）全 cancel。
  cron 侧 kill 全量重跑（冗余），移交主会话 B1 增量 OCR（14b7a64..a8fac99，14:06 起）收口。
- **合入依据**：F1/F2/F3 逐条代码核实 + 2 条回归独立 GREEN + 666/730 全量零回归 +
  ruff 全绿。B1 收口后若有新 finding 按协议处理（同因两轮上限已到：若为**同因**升级用户裁决；
  若为增量新发现则最小返修）。

## 下游
- 05 四 commit 随 b3280c9 上 origin（05 验收另见 attempt-1-decision.md）。
- 03B 合入后 `purpose_schedule_event` outbox 表在 main → 05 的 poll 通道从恒空转为真实读表，
  TASK-08 联调前置条件达成。03 聚合验收由主协调者按 TODO 继续。
- 06A attempt-2（e92ef17）已在主会话 VERIFYING，B2 后合入。