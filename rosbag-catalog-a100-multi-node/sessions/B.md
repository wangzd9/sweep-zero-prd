# 开发角色B恢复入口

角色B=开发者2，不是执行服务器B。状态UNBOUND；无派单、无ACK、无owner/worktree。
Skill：complex-task-executor。先读[启动](../SESSION-START.md)→[协议](../inbox/PROTOCOL.md)→[TODO](../TODO.md)→[DESIGN](../DESIGN.md)→[HANDOFF](../HANDOFF.md)，共享根`/home/wang/work/doc/prd/rosbag-catalog-a100-multi-node`。

未来首波候选MN-02，供应接受后的候选MN-05；具体task/attempt/base/允许文件以inbox/B实际派单为准。自行建立专属分支/worktree，只做派单开发、自测、返修；代理/环境/恢复及两路线接线按TODO归属，不改models/迁移或抢平台配置owner。

领取前创建独立ACK；交付receipts/<实际task>/attempt-N.md，含commit、节点/路径/故障证据和未执行项。不更新共享TODO、不跑OCR、不合入、远端安装或部署。读到此文件不启动任务。
