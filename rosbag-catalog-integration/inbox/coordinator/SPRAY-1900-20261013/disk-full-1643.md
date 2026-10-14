# Codex介入：根分区满导致G4副本恢复失败

2026-10-13 16:43 +08:00。当前机器根分区100%、/home另盘351G可用，命令已报ENOSPC。A在途g4r2.log刚报`ERROR 1114 (HY000) at line 1768: The table 'dataset_frame' is full`。本次G4副本恢复未完成，不得判升级证据齐。

Codex已开始只清理可重建闲置Docker build cache，保留容器/镜像/卷。已给A事实通知：失败副本需确认写者退出后重建，datadir显式bind到/home私有目录并恢复同一已验sha备份，复核实际行数再升级；A仍owner，不重复恢复或迁移。此项属于用户要求介入加速下的环境阻塞排除，不修改业务派单或TODO。
