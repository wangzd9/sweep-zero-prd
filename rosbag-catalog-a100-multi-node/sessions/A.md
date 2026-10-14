# 开发角色A恢复入口

角色A=开发者1，不是执行服务器A。状态UNBOUND；无派单、无ACK、无owner/worktree。
Skill：complex-task-executor。先读[启动](../SESSION-START.md)→[协议](../inbox/PROTOCOL.md)→[TODO](../TODO.md)→[DESIGN](../DESIGN.md)→[HANDOFF](../HANDOFF.md)，共享根`/home/wang/work/doc/prd/rosbag-catalog-a100-multi-node`。

未来首波候选MN-01，供应接受后的候选MN-04；具体task/attempt/base/允许文件以inbox/A实际派单为准。自行建立专属分支/worktree，只做派单开发、自测、返修，不改共享TODO，不派单、不跑OCR、不合入或部署。公共models/迁移/config/schema按TODO单写。

领取前创建独立ACK；交付receipts/<实际task>/attempt-N.md，含commit/命令/AC证据/未知项及停止条件。读到此文件不启动任务。
