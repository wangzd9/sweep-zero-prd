---
task: TASK-06B
item: attempt-1-defect3-reconcile-replay
owner: 2号
status: ACK
dispatch_path: inbox/2号/TASK-06B/attempt-1-defect3-reconcile-replay.md
attempt: 1（缺陷3 单，base main 0f6aa87）
ack_time: 2026-10-10 20:19 +08:00
worktree: /home/wang/.local/state/rosbag-scene/wt-04a（任务分支自 0f6aa87 新建）
next: 核实 :928 根因（MySQL rowcount 语义）→ 最小单 commit 修复 → 自测 → 回执
---
# ACK：缺陷3 reconcile 幂等二次 MySQL StaleDataError

收到派单（20:13 落盘，协调者 20:1x decision 裁决 2=缺陷3 CORRECTION 回派本侧），确认 base `main 0f6aa87`、
范围 `app/services/scene_result_report_service.py` app 代码面、AC 三条件（真 MySQL 幂等二次 PASS /
SQLite 定向+全量+ruff / 单 commit 零越界）。开工顺序：先按根因线索实测 rowcount 语义（含
`updated_at` 微秒假设核验），再选修复方向并说明选择依据；禁止改测试断言语义/删用例。