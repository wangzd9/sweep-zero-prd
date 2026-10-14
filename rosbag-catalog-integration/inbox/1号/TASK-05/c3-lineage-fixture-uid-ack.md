# ACK：C3-lineage 夹具 bag_uid 越宽最小修复（TASK-08 联调发现回派）

- status: ACCEPTED
- 派单：`inbox/1号/TASK-05/c3-lineage-fixture-uid-dispatch.md`（2026-10-11 16:50）
- task/attempt：C3-lineage / c3-1
- owner：1号（A），cron 会话 `a-poll-20261011-165153-c3-1`
- 固定 base：main `f9bafb0`（ACK 时 git fetch 核实 = origin/main，零前移，与派单一致）
- 分支/worktree：新建 `scene/task-08-c3-lineage-fixture` + 独立 `wt-01-c3`（不动在冻 `wt-01`/`wt-01-i1`）
- ACK 时间：2026-10-11 16:53 +08:00
- 范围确认：仅 `tests/test_scene_slice_lineage.py` uid 构造点（27 字符→≤26 + len assert），零 app 变更；同文件其余 24 hex 用法逐处核对同族越宽一并收敛；`_purge`/断言/业务逻辑不动
- AC：真 MySQL 8.4.11 STRICT 隔离库文件级全绿 + 隔离库 0 残留 + SQLite 定向不回归 + ruff 绿；停止条件=上述全绿+回执 REVIEW_PENDING