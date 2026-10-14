# ACK：TASK-16A attempt-1 场景接收隔离

- status: ACCEPTED
- ACK 时间：2026-10-12 22:41 +08:00
- owner：A（执行者A·数据处理链路）
- 派单路径：`inbox/1号/TASK-16A/attempt-1-dispatch.md`（2026-10-12 22:40，status=DISPATCHED）
- task/attempt：TASK-16A / attempt-1
- base：main 本地 `c2018dd`（= origin `502bf8e` + 1 纯文档 commit；ACK 时 rev-parse 双核在案，07B `f4bfcf2` 未合入，按派单口径不携带 07B 文件）
- 分支/worktree：`wt-01-t16a` @ `/home/wang/.local/state/rosbag-scene/wt-01-t16a`，任务专属分支自 base `c2018dd` 新建，.venv 软链主仓
- 开发主 worktree `wt-01`（HEAD `ceeac16`）与 `wt-01-t10def1`（HEAD `1b92ce6`）保持冻结不动
- 声明：不碰 07B 冻结文件集；新迁移 revision 命名 `20261013_01_scene_intake` 系独立，down_revision 指届时 alembic 单头（07B 若先合入则链在其后，报告说明）；不改生产 compose 实际值；不实现 16B/16C
- 长任务说明：开工后按 §8.2 验收口径自测（双根/不重叠/迁移往返/real 栈冒烟），阶段进展记 `sessions/A.md` 与 events，交付冻结 commit + 回执 `receipts/TASK-16A/attempt-1.md`（REVIEW_PENDING）