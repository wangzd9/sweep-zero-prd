# ACK：TASK-07B attempt-3-r3 强审查返修

- status: ACKED
- 派单路径：`inbox/2号/TASK-07B/attempt-3-r3-dispatch.md`
- task/attempt：TASK-07B / attempt-3-r3（R3-1~R3-4，问题 ID 单）
- owner：B（前端功能开发群，cron poll `6f7471d8747c`）
- base：`68b5188`（续 commit，原 base `502bf8e` 不变）
- 分支/worktree：`scene/task-07b-manual-revision-withdraw` @ `/home/wang/.local/state/rosbag-scene/wt-04a-t07b`（HEAD 实测 `68b5188`，洁净，仅 `.venv`/`scratch/` 未跟踪）
- 时间：2026-10-13 02:11 +08:00（claim owner `cron-b-poll-6f7471d8747c-20261013-020753`）
- 范围确认：改未合入原迁移 `alembic/versions/20261012_01_scene_manual.py` 加 `corrected_label` 列（含 downgrade drop）；禁新表/新迁移文件/新依赖；`app/api/scene_manual_revision.py` 尾换行+`raise from exc` 顺带小修；SR-05 真 MySQL 双连接并发取证不属本单（TESTER post-r3 单）
- 交付口径：commit（`68b5188` 之上）+ 回执 `receipts/TASK-07B/attempt-3-r3.md` + 报告 `reports/TASK-07B/attempt-3-r3.md`，REVIEW_PENDING