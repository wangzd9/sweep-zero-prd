# ACK：t10-defect2-storage-offset —— 06B 域 derive_storage_offset 真实 rosbag2 jitter 口径（TASK-10 缺口 #2 最小返修，优先）

- status: ACCEPTED
- ACK 时间：2026-10-12 00:09 +08:00（B cron poll 00:07:53 回合，claim 成功）
- 派单路径：`inbox/2号/TASK-06B/t10-defect2-storage-offset.md`
- task/attempt：TASK-10 缺口 #2 / t10-defect2-storage-offset（最小返修单，优先）
- owner：2号（B）
- base：main `ca8730d`（= origin/main，本回合 rev-parse 双核一致实测）
- worktree：新建 `wt-04a-t10d2` @ 新分支（base `ca8730d`，.venv 软链主仓），待开工建立
- 范围确认：`app/services/scene_publish_service.py` derive_storage_offset 放宽口径（众数/中位数+有界容差，fail-closed 保持）+ 真实 7 袋复验 + 定向/全量测试 + ruff；不改 03B、不改 04B 判定语义
- 回执路径：`receipts/TASK-06B/t10-defect2-storage-offset.md`
- 前置事实：TASK-10 取证单已交付冻结（00:0x 协调者 ACCEPT_REPORT），本单为 #2 回派；#1 由 1号并行，文件集无冲突
