---
task: TASK-03B
item: attempt-5-rework-2
owner: 1号
status: ACCEPTED
base: wt-01 f088c2b
branch: t03b-r2-rework（本任务分支续做）
ack_at: 2026-10-10 16:27 +08:00
---
# ACK：attempt-5-rework-2（f088c2b OCR 2 findings 小修）

- 派单：inbox/1号/TASK-03B/attempt-5-rework-2.md（16:26 PENDING，已读全文）
- worktree：/home/wang/.local/state/rosbag-scene/wt-01，HEAD=f088c2b，工作区干净（仅 .venv 未跟踪）
- 范围：① `_mark` 检查 rowcount 返回值，0 行计 errors+warning 并附 1 定向回归；② 终态 UPDATE 改 Core `update()` 表达
- 不动：不跑 OCR，不合入，不扩范围