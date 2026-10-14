# NVIDIA数据集清理

本需求从旧场景目录拆为独立同级包，原`NC`编号、任务状态、契约与证据保留。角色/群/cron仍未绑定；目录迁移不启动开发、安装或生产操作。

本需求绝对根：`/home/wang/work/doc/prd/rosbag-catalog-nvidia-cleanup`。代码仓：`/home/wang/work/rosbag-catalog`。

阅读顺序：[PRD](PRD.md) → [DESIGN](DESIGN.md) → [唯一TODO](TODO.md) → [ACCEPTANCE](ACCEPTANCE.md) → [HANDOFF](HANDOFF.md) → [角色入口](SESSION-START.md)。[协议](inbox/PROTOCOL.md)与[绑定元数据](ROLE-BINDINGS.json)属于本包，不复制旧场景任务。

关联：[场景基础](/home/wang/work/doc/prd/rosbag-catalog-scene-foundation/README.md)、[自建路线](/home/wang/work/doc/prd/vla-self-dataset-pipeline/README.md)、[NVIDIA路线](/home/wang/work/doc/prd/vla-nvidia-dataset-pipeline/README.md)。A100纳管只覆盖自建/NVIDIA；场景非模型执行均在处理机。旧路径保留为指向本包的兼容链接，见 [迁移说明](/home/wang/work/doc/prd/MIGRATION-20261014.md)。
