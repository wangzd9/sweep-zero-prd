# 回执：TASK-16A attempt-2-r1 最小返修（OCR 收口后合并）

- status: REVIEW_PENDING（**非通过**，待协调者增量 OCR + TESTER 独立验证 + 07B 合入顺序裁决）
- task/attempt：TASK-16A / attempt-2-r1（attempt-1 交付冻结后的合并返修，沿 07B r102 先例）
- owner：A（执行者A·数据处理链路）
- 交付时间：2026-10-13 04:09 +08:00
- 固定 base：`c30f048`（attempt-1 交付冻结 HEAD，`wt-01-t16a` 续 1 笔 commit，未 rebase/reset）
- 新 HEAD：`3aee4d1`（`git rev-parse HEAD` 实测）
- 分支/worktree：`a/task-16a-scene-intake` @ `wt-01-t16a`，.venv 软链主仓，porcelain 干净（仅 `.venv` 未跟踪既定）
- 派单：`inbox/1号/TASK-16A/attempt-2-r1-dispatch.md`（协调者 r116 03:48 派发）；ACK `attempt-2-r1-ack.md` 03:54

## 6 项返修落地（全部 low/2 行量级，零扩面）

| 项 | 文件 | 变更 |
|---|---|---|
| R1-1（runner M2） | `app/scanner/runner.py` | `_scene_context()` 启用条件由 `settings.scene_roots_configured()`（三根任一非空）收紧为显式 `settings.scene_nas_scan_root and settings.scene_nas_ready_root`（scanner 实际只消费这两根），半配置 fail closed 返回 None。`scene_roots_configured` 本身保留（config 校验 `:137`/`:196` + `ingest_service:844` + `bootstrap:223` 仍在用，零语义外溢） |
| R1-2（runner L1） | `app/scanner/runner.py` | `_recover_moves` 恢复路径 cross-check `marker["root_id"]` vs `ctx.root_id`：缺失（None）=旧 journal（TASK-16A 写入前）兼容放行；矛盾=该条标 `ROOT_MISMATCH`、记 `stats["failed"]`、跳过、字段保留（重启保持快照口径 DESIGN §1.5/§7.3.1），不 KeyError、不静默吞 |
| R1-3（ingest L1） | `app/services/ingest_service.py` | `list_profiles` 改走 `_active_profiles(db, "__all__")` 私有 all-roots 哨兵，使 scene 入口出现在 `GET /api/v1/ingest-profiles`；列表项补 `intake_root_id` 字段（DESIGN.md:157 契约已含）。**匹配路径 `match_profile_for_incoming`→`_active_profiles(db, root_id)` 只传 scene/self_built/None，跨根隔离语义不动**（哨兵仅 list 使用，不入匹配分支） |
| R1-4（scene_intake L1+L2） | `app/services/scene_intake.py` | `validate_register_root` docstring 显式注 `incoming_path` reserved（不读取、不影响 root 派生，刻意 API 面）；补文件尾换行 |
| R1-5（迁移） | `alembic/versions/20261013_01_scene_intake.py` | 补文件尾换行（零逻辑改动） |
| R1-6 | 无 | R7-M1（CLI 出口码）已裁决 OUT_OF_SCOPE 不改；无其他 |

## 文件清单（5 文件，+122/-7）

```
alembic/versions/20261013_01_scene_intake.py |  2 +-
app/scanner/runner.py                        | 24 +++++++-
app/services/ingest_service.py               | 12 +++-
app/services/scene_intake.py                 |  6 +-
tests/test_scene_intake_isolation.py         | 85 +++++++++++++++++++++++++++-
```

## 定向测试（新增 3 条，tests/test_scene_intake_isolation.py）

- `test_scene_context_requires_scan_and_ready_roots`（R1-1）：只设 `SCENE_SLICE_PUBLISH_ROOT`（scan/ready 空）→ `_scene_context()` 返回 None；scan+ready 同时给出 → 建 scene RootContext。
- `test_recover_moves_root_mismatch_skipped_and_missing_passes`（R1-2）：journal `root_id=self_built` 与 `ctx.scene` 矛盾 → `ROOT_MISMATCH`+failed 跳过+字段保留+不登记；缺 `root_id` 旧兼容条 → 恢复登记携当前上下文 `scene`（未 KeyError）。
- `test_list_profiles_all_roots_and_matching_isolated`（R1-3）：`list_profiles` 含 scene+self 入口且返回正确 `intake_root_id`；`match_profile_for_incoming` 对 self_built incoming root_id=self_built 命中、root_id=scene 不命中（隔离不变）。

## 自测命令 / 退出码 / 环境 / 关键断言

- 环境：`wt-01-t16a` 本地 SQLite（`.venv` python3.10 + 主仓依赖），非生产、未操作生产数据
- 定向 16A 隔离：`.venv/bin/python -m pytest tests/test_scene_intake_isolation.py -q` → **22 passed**（既有 19 + 新增 3），RC=0
- scanner 稳定性（`_scene_context` 面）：`tests/test_scanner_stability.py -q` → **6 passed**，RC=0
- 接收入口列表口径：`tests/test_ingest_config_api.py tests/test_ingest_config.py -q` → **28 passed**，RC=0
- ruff：`ruff check` 五个变更文件 → **All checks passed!**（零新增违规）
- alembic 单头：`alembic heads` → **`20261013_01_scene_intake (head)`**（单头不变，R1-5 零逻辑改动）
- 全量：`.venv/bin/python -m pytest -q` → **872 passed / 3 failed / 10 skipped**（57.70s）
  - 3 failed = `tests/test_devflow.py::{test_external_sandbox_hides_home..., test_worker_resolves_codex..., test_external_sandbox_binds_main_repo_git...}`（worktree 沙箱：`主仓库缺少 .git`/codex binary/bubblewrap 环境性）
  - **非回归证明**：`git stash` 本单 5 文件后在同 worktree 复跑 `tests/test_devflow.py` → 同 3 条失败、21 passed（base `c30f048` 口径一致），已 `stash pop` 还原。与 attempt-1 申报的 3 个 test_devflow 固有问题同一组，非本单引入
  - 10 skipped = `tests/test_bag_cleanup_mysql.py`（MySQL 独占容器门控，本单不涉）

## 未执行项

- 真 MySQL 8.4 STRICT 并发/迁移往返：本单零 DDL/迁移逻辑改动（R1-5 仅尾换行，`alembic heads` 单头已在案），真 MySQL 面随 attempt-1 既有验证 + 协调者合入面复跑，本轮不重复起容器
- real 栈双根冒烟：attempt-1 已全断言通过，本单为 6 项 low 收口（含 scanner 双根启用条件收紧），real 栈面由 TESTER 16D 前独立验证承接
- 07B 合入顺序对 16A 迁移链位置裁决（`down_revision=20261009_02`，若 07B `20261012_01` 先合入需 rebase 双头）：协调者合入面执行，本单不动

## 越界申报

- 无：零新表/零新迁移文件/零新依赖；`app/scanner/clients.py` 未触碰（medium 已裁决随合入备注）；07B 冻结文件集零触碰；`scene_roots_configured` 保留未删（多调用点在用）
- 未部署、未操作生产数据、未改生产 compose 实际值

## 停止条件核对

- 6 项全部完成 + 自测全绿（定向/稳定性/列表口径/ruff/alembic 单头/全量非回归）→ 交付冻结 REVIEW_PENDING
- 无单项需扩面（>2 行/新文件/语义变化），未触发停止回报

## 后续（协调者链）

机械核验 → 增量 OCR（`--from c30f048 --to 3aee4d1`）→ 合入（07B 整链先合入后 16A 迁移 rebase 双头，协调者执行）→ TESTER 16D 前独立验证。本角色交付后等 OCR 增量收口，不自行合入。