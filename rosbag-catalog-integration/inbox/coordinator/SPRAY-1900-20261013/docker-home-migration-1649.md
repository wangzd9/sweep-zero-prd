# 当前机Docker迁移维护窗口（Codex环境owner）

2026-10-13 16:49 +08:00。用户已明确要求释放根分区，包括将Docker迁到home。Codex即将短暂停当前机Docker/containerd，迁移 `/var/lib/docker` 约21GB 与 `/var/lib/containerd` 约6GB 到 `/home/docker`、`/home/containerd`，保留全部镜像/卷，验证后才清旧副本。处理机生产服务不变。

当前实际运行仅本地catalog五容器，无A副本MySQL/TESTER探针容器。迁移过程中请A/TESTER暂勿新建Docker容器或再跑副本恢复，已失败副本不算G4 PASS。Codex结束后在本收件箱追加实测结果；原业务owner不变。

C已16:44:55冻结16B-r2 `e152465`，可由协调者按原门禁接续增量OCR/强审，无需等本机Docker恢复才准备审查材料。

**16:54恢复通知**：迁移于16:52:14完成，DockerRootDir=/home/docker，containerd root=/home/containerd；原五容器恢复，Backend/Web/MySQL均healthy，原数据库卷Mountpoint已=/home/docker/volumes/...。镜像ID及全部原卷名清单保持一致。A隔离t11sp_g4已在/home私有datadir重新启动。TESTER/A可继续Docker操作；旧副本由Codex在健康核验后清理，不需重复安装镜像。迁移不代表G4实验通过。

**最终空间实测16:54:34**：旧副本清理完成，根分区51%，可用约31GB；home剩324GB。已补Docker/containerd systemd对/home的挂载依赖、旧路径兼容软链；宿主Backend ready及Web live均HTTP200。完整证据见`doc/analysis/spray-runtime-install-20261013/REPORT.md`新增16:54节。
