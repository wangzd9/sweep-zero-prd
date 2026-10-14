# 当前机Docker迁移维护窗口

用户要求Codex将当前机Docker/containerd存储迁到home以排除根分区满；即将短暂停服务，保留全部镜像/卷，恢复后补通知。采样无测试探针容器运行，请暂勿启动新探针。处理机生产服务不变；已有测试证据保留，避免迁移期间启动失败误判业务缺陷。

**16:54恢复通知**：Docker迁移完成并恢复原五容器；Backend/Web/MySQL healthy，水雾镜像ID保持e3fe73534ad8，DockerRootDir=/home/docker。可继续真实探针，不需重建环境；模型/业务契约没有更改。
