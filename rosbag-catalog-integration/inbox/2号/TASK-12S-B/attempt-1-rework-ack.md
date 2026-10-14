# ACK：TASK-12S-B attempt-1-rework（16 findings 一次最小返修）

- status: ACCEPTED
- ACK 时间：2026-10-13 14:23 +08:00
- 派单路径：`inbox/2号/TASK-12S-B/attempt-1-rework-dispatch.md`（协调者 r158，14:2x）
- task/attempt：TASK-12S-B / attempt-1-rework（base `f62a29c` 续 commit，不新开分支/attempt 号）
- owner：执行者 B（2号），cron 会话 `cron-b-poll-6f7471d8747c-20261013-142228`
- base：`f62a29c`（wt-04a-t12sb 当前 head，12S-B attempt-1 交付冻结）
- 分支/worktree：`c/task-12s-b-spray-adapter` @ `/home/wang/.local/state/rosbag-scene/wt-04a-t12sb`（复用本任务专属 worktree，返修延续既有分支口径）
- 边界确认：只动 `app/scene/spray/*` 与 `tests/test_spray_*`；LOW 项最小修+书面取舍；不扩需求、不改契约语义
- 计划：17 条（S1–S8、T1–T8）逐条实现 → 定向用例 → 全仓回归（口径同 attempt-1）→ ruff → 冻结 commit → 回执 `receipts/TASK-12S-B/attempt-1-rework.md`
