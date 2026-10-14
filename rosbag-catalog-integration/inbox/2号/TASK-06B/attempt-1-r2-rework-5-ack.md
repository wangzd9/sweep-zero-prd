---
task: TASK-06B
item: attempt-1-r2-rework-5
owner: 2号
status: ACKED
acked_by: 2号（B cron，owner b-cron-rework5-20261010）
ack_time: 2026-10-10 22:30 +08:00
dispatch: inbox/2号/TASK-06B/attempt-1-r2-rework-5.md
base: main 5f0124b
---
# ACK：codex 审查 3 项返修（M-1 微秒精度 / M-2 迁移边界 docstring / M-3 测试注释）

- 范围确认：
  1. M-1 [medium]：`scene_result_report_service.py:577` started_at 赋值统一 `replace(microsecond=0)` + MySQL 语义回归（纳秒 start_ns 带小数秒 + 同秒重放，注明连接是否 CLIENT_FOUND_ROWS）。
  2. M-2：`alembic/versions/20261009_02_ingest_frozen.py:40` docstring 补适用边界（核实范围 + 人工升级语句），不改"零兼容风险"结论。
  3. M-3 [low]：`tests/test_scene_result_report.py:119` 注释纠偏（SQLite 未校验列宽）。
- 单 commit 交付（5f0124b 之上）+ 回执 + 群内通报；OCR 不自跑。
- 分支/worktree：沿用本任务分支惯例新建 `scene/task-06b-codex-rework5`，worktree `/home/wang/.local/state/rosbag-scene/wt-04a`（当前冻结分支 defect3 已合入，无冲突）。
- rework-4 关单确认：无需动作。