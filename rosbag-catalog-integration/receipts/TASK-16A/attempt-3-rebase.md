# TASK-16A attempt-3-rebase 回执（REVIEW_PENDING）

- **owner/attempt**：执行者 A（1号）/ attempt-3-rebase（07B 整链合入后的既定 rebase 双头接线，口径=r107/r119 双头裁决+A 申报一致）
- **dispatch**：`inbox/1号/TASK-16A/attempt-3-rebase-dispatch.md`（协调者 r136，2026-10-13 08:4x）
- **ACK**：`inbox/1号/TASK-16A/attempt-3-rebase-ack.md`
- **worktree/branch**：`wt-01-t16a`@`a/task-16a-scene-intake`（复用任务专属 worktree，返修延续本任务分支）
- **base（rebase 目标）**：派单落盘时 main=`4b9f30a`；ACK 时 main 已前移 `3d2a075`（=origin/main 双核，纯文档 changelog F-040，在 `4b9f30a` 之上，零代码面）。**按「rebase 到新 main」意图 rebase 到当前 main `3d2a075`**（比派单文字多一个纯文档 commit，无代码面冲突风险，merge-tree 预核 0 冲突）。
- **状态**：**REVIEW_PENDING（非通过）**——待协调者机械核验 + 增量 OCR + TESTER 16A 独立验证（真 MySQL 8.4 全链迁移往返）→ 16A DONE。

## rebase 后 commit 映射（16A 链 base `c2018dd` 不动，3 commit 重放 + 1 接线 commit）

| 旧（rebase 前） | 新（rebase 后） | 说明 |
|---|---|---|
| `79f6889` | `995e351` | 场景接收隔离基础层（三根配置契约、Scanner 双根上下文、登记身份防线） |
| `c30f048` | `bed9006` | IngestProfile/IngestSubmission 扩展 + 身份防线接线 + 用途路由边界 |
| `3aee4d1` | `24d934e` | attempt-2-r1 OCR 合并返修（_scene_context 收紧 / _recover_moves cross-check / list_profiles all-roots / 尾换行） |
| —（新增） | `da304e2` | **迁移双头接线**：`20261013_01_scene_intake` down_revision `20261009_02` → `20261012_01_scene_manual` + docstring |

- **HEAD（新）**：`da304e2a1f9599974533173c79292175d28d3b76`，基于 `3d2a075`。
- rebase 执行 `git rebase 3d2a075`，rc=0，无冲突（`app/models.py` 按派单口径自动合并）。

## 迁移双头接线（本单唯一代码面）

- 接线前双头：`20261009_02_ingest_frozen` ← `20261012_01_scene_manual`（07B 新 main 单头）和 ← `20261013_01_scene_intake`（16A）均指其下。
- 接线后单头链：`20261009_02_ingest_frozen → 20261012_01_scene_manual → 20261013_01_scene_intake`。
- 改动文件：`alembic/versions/20261013_01_scene_intake.py`（1 文件 +4/-4：`down_revision` + docstring 两段）。零新功能零语义变更（upgrade/downgrade 函数体不动，仍为 add_column/index 幂等 gate + backfill）。

## 自测（wt-01-t16a，.venv=主仓软链，SQLite 口径）

| 项 | 结果 |
|---|---|
| `alembic heads` | **单头 `20261013_01_scene_intake`**（双头已消除） |
| `alembic history` 顶部 | `20261009_02 → 20261012_01_scene_manual → 20261013_01_scene_intake (head)` 口径正确 |
| 真 SQLite 三往返（upgrade head → downgrade -1 → upgrade head） | **全 RC=0**：head=`20261013_01_scene_intake` → downgrade=`20261012_01_scene_manual` → upgrade=`20261013_01_scene_intake`（临时库 `/tmp/t16a_rebase_mig.db` 已删） |
| 16A 定向 56 passed 口径（test_scene_intake_isolation/test_scanner_stability/test_ingest_config_api/test_ingest_config） | **56 passed**（4.42s，无回归） |
| ruff 变更文件（迁移 + 16A touched scene_intake/runner/ingest_service） | **All checks passed** |
| 全量 SQLite | **883 passed / 4 failed / 10 skipped** |

## 全量 4 failed 逐条归因（如实申报，非本单回归）

1. `tests/test_devflow.py::test_external_sandbox_hides_home_and_only_binds_task_dirs`
2. `tests/test_devflow.py::test_worker_resolves_codex_without_interactive_path`
3. `tests/test_devflow.py::test_external_sandbox_binds_main_repo_git_for_worktree`
   → 3 条均为 **test_devflow worktree 沙箱环境性**（派单既定 base 复现口径，历史各轮同 3 条）。
4. `tests/test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time`（`/bags` 执行 9 条 SQL，assert ≤8 N+1）
   → **本单新观察项，非 16A 回归**：独立在纯 main `3d2a075`（07B 在案、无 16A）复跑 `tests/test_web.py` 全模块得**完全相同 1 failed, 40 passed**；且 `git diff --name-only 3d2a075 da304e2` 证实 16A 链**零触碰** `app/web/bags.py` / `app/templates/bags.html` / `detail.html`（`/bags` 页面=07B 域）。判为 **07B 合入 main（08:28）后在 main 上的既有失败**，与派单「3 failed」基线（07B 合入前口径）相差这条，属 07B/B/协调者域，供协调者核，本角色不代修不代判。

## 未执行项

- **真 MySQL 8.4 全链迁移 upgrade→downgrade→upgrade 往返**：留 TESTER/独立验证口径（本单仅 down_revision 指针变更，SQLite 三往返已验证链拓扑正确；MySQL STRICT 语义面由 TESTER 16A 独立验证承担）。
- 增量 OCR：rebase 后迁移单文件 + models 自动合并面小批（协调者串行执行）。
- 07B 强审增量 / TESTER 16D 前 16A 独立验证：协调者/TESTER 域。

## 越界申报

- **无越界**：仅改本任务迁移 `20261013_01_scene_intake.py` 的 down_revision + docstring；未触碰 07B 冻结文件（app/web/bags.py、templates、scene_manual_* 等）、未改生产 compose、未部署、未操作生产数据。rebase 未触碰 07B 面（merge-tree 0 冲突、git diff 核 16A 仅 16A 域文件 + 1 迁移接线）。

## 停止条件达成核对

- rebase 完成 ✅（rc=0 无冲突）
- 迁移接线 ✅（单头链验证）
- 自测全绿 ✅（定向 56 + ruff + SQLite 三往返；全量仅既定 test_devflow 环境性 + 1 条 07B 域既有失败，均非本单引入）
- 交付冻结 ✅（HEAD `da304e2`）