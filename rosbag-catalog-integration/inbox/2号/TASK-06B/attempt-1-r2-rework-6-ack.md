---
task: TASK-06B
item: attempt-1-r2-rework-6
owner: 2号
status: ACCEPTED
ack_by: 执行者B（cron poll）
ack_at: 2026-10-11T09:07:00+08:00
dispatch_path: inbox/2号/TASK-06B/attempt-1-r2-rework-6.md
base: main 6d30a68
branch: scene/task-06b-codex-rework6
worktree: /home/wang/.local/state/rosbag-scene/wt-04a-r6
---
# 2号 ACK：codex 全链合审 REWORK 回派（R-01 medium 阻塞 / R-02 low / R-03 low，同单 3 项）

已接收并开工。执行者 B 独立分支/worktree（wt-04a-r6，base main 6d30a68），不占第二任务、不 reset 他人工作。

计划最小行为（逐条对应裁决 reviews/codex-r6-fullchain-20261010-verdict.md）：
- R-01 [medium 阻塞] scene_result_report_service.py:582：der.start_ns / 1e9（浮点秒，纳秒末近秒边界已进位）改为 datetime.fromtimestamp(der.start_ns // 1_000_000_000, tz=timezone.utc).replace(tzinfo=None)（整数除法先求秒，构造即整秒）。补 3 个秒末边界回归用例断言完整 started_at 值：ns末=0（保持）、ns末=500_000_000（向下截断非四舍五入）、ns末=999_999_999（进前秒），各自二次 reconcile 重放仍零 UPDATE / 零 StaleDataError。
- R-02 [low] test_scene_slice_scheduling.py（test_migration_head_revision_id_within_alembic_version_width）：用 ScriptDirectory 动态取 heads 断言单 head + 单独断言本次 revision 20261009_02_ingest_frozen 仍在迁移链中 + 全 ID ≤32 字符宽度断言保留（未来加合法后继迁移不再 :1204 误失败）。
- R-03 [low] test_scene_result_report.py 精度回归用例补强：同秒重放 + 跨秒重放中监听 UPDATE 语句（SQLAlchemy 事件计数），明确断言目标行 UPDATE 零次（registered=True 不能证明 no-op）。

验证口径（按裁决 info 条写清边界）：真 MySQL A/B 证据沿用无 CLIENT_FOUND_ROWS 隔离库口径，回执注明"生产默认建连带该 flag"、不宣称生产默认连接语义；SQLite 全量不回归 + ruff 绿。交单单 commit（6d30a68 之上）+ 回执 + 群内通报；OCR 不自跑。