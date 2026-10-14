# ACK：TASK-07B attempt-4-r4 迁移 downgrade 最小返修

- status: ACKED
- 派单路径：`inbox/2号/TASK-07B/attempt-4-r4-dispatch.md`
- task/attempt：TASK-07B / attempt-4-r4（R4-1 r3-1 medium CORRECTION 守卫回归 + R4-2 r3-1 low 文档同步，问题 ID 单）
- owner：B（前端功能开发群，cron poll `6f7471d8747c`）
- base：`4baf79f`（attempt-3-r3 交付冻结 HEAD，续 commit；原 base `502bf8e` 不变）
- 分支/worktree：`scene/task-07b-manual-revision-withdraw` @ `/home/wang/.local/state/rosbag-scene/wt-04a-t07b`（HEAD 实测 `4baf79f`，洁净，仅 `.venv`/`scratch/` 未跟踪）
- 时间：2026-10-13 07:02 +08:00（claim owner `cron-b-poll-6f7471d8747c-20261013-065753`）
- 范围确认：仅 `alembic/versions/20261012_01_scene_manual.py` 单文件 2 项（R4-1 `drop_column` 移回表存在判定内、R4-2 docstring 补 downgrade 往返风险段）；禁新表/新迁移文件、app 代码、tests、07A/16A/16B 文件面、upgrade 面改动；AC 不变量冻结=强审包 §2（1-6）
- 自测口径：定向 pytest 3 文件 0 红 + 真 MySQL 8.4 隔离库 fresh upgrade→downgrade→upgrade 往返 RC=0 + SQLite 内存探针表缺失态 downgrade 不抛异常 + ruff 单文件绿 + `alembic heads` 单头不变；容器 0 残留
- 交付口径：commit（`4baf79f` 之上）+ 回执 `receipts/TASK-07B/attempt-4-r4.md` + 报告 `reports/TASK-07B/attempt-4-r4.md`，REVIEW_PENDING
- 停止条件：R4 收口 r3-1 两项；同根因两轮失败（R4 增量复审再出同位 CORRECTION）升级用户，不无限返修