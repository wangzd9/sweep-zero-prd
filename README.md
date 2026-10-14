# 需求文档总索引

本目录是需求文档容器。独立需求按可单独交付、验收或发布的业务目标建立同级需求包；同一代码仓、执行角色或模型服务不构成合并需求的理由。

本页只做导航，不复制实时进度。每个包的 README 说明范围与权威任务入口；是否完成、是否允许接续或发布，读取对应 TODO、有效裁决与实际证据。

## 独立需求包

| 需求包 | 目标与边界 | 任务入口 |
|---|---|---|
| [VLA 自建处理链路](vla-self-dataset-pipeline/README.md) | 自建 ROS 2 Bag 的接收、Phase0/A100 后续处理、质量与发布 | [唯一 TODO](vla-self-dataset-pipeline/TODO.md) |
| [NVIDIA PhysicalAI 处理链路](vla-nvidia-dataset-pipeline/README.md) | NVIDIA chunk 下载、处理、质量与可选 NAS 回传 | [唯一 TODO](vla-nvidia-dataset-pipeline/TODO.md) |
| [VLA 无人化与 Agent 监督](vla-unattended-workflow/README.md) | 长期无人化方案；当前路线任务分别在自建与 NVIDIA 包维护 | [方案与接续边界](vla-unattended-workflow/README.md) |
| [场景接收、执行与发布基础](rosbag-catalog-scene-foundation/README.md) | 场景公共能力、源身份与代次、配置冻结、执行与发布契约 | [任务定位](rosbag-catalog-scene-foundation/TODO.md) |
| [场景最小界面闭环](rosbag-catalog-scene-ui/README.md) | 切片/原始数据/全部视图、流水线详情、查询追溯与界面收尾 | [任务定位](rosbag-catalog-scene-ui/TODO.md) |
| [水雾识别与生产自动化](rosbag-catalog-spray-pipeline/README.md) | 水雾接收、绑定、识别、切片、发布入库及生产收尾 | [任务定位](rosbag-catalog-spray-pipeline/TODO.md) |
| [A100 双节点纳管](rosbag-catalog-a100-multi-node/README.md) | 自建/NVIDIA 路线的 A100 双节点资源与调度；场景非模型执行仍在处理机 | [唯一 TODO](rosbag-catalog-a100-multi-node/TODO.md) |
| [NVIDIA 数据集清理](rosbag-catalog-nvidia-cleanup/README.md) | NVIDIA 数据集清理的独立契约、任务与验收 | [唯一 TODO](rosbag-catalog-nvidia-cleanup/TODO.md) |

场景基础、界面、水雾已按业务文档拆包；三包当前任务状态和五角色交互仍由[旧运行根](rosbag-catalog-integration/README.md)接续。上述三份任务定位页链接原件，不构成第二份可写 TODO。

## 历史方案

- [VLA 数据平台早期方案](archive/vla-data-platform/README.md)：保留产品背景，原 PostgreSQL/个人处理电脑方案不作为当前实现基线。
- [VLA 可迁移处理早期 MVP](archive/vla-processing-mvp/README.md)：保留最初流程设计，不覆盖当前编排与代理契约。

## 运行兼容入口与整理规则

[rosbag-catalog-integration](rosbag-catalog-integration/README.md) 继续保存当前活跃角色的 TODO、派单、ACK、开发/测试/审查回执、会话、事件与锁。旧专项路径以兼容链接接续；旧混合 PRD、DESIGN、ACCEPTANCE 已改为章节导航，原文保存在历史快照中。详见[迁移说明](MIGRATION-20261014.md)。

后续独立需求在 `doc/prd/<独立需求名>/` 同级建包。既有需求的缺陷、补验与后续阶段留在所属包；一次测试或生产批次使用包内 `runs/<批次编号>/`，例如[1012 水雾批次](rosbag-catalog-spray-pipeline/runs/1012-20261013/README.md)。单个 TASK 不另建独立需求根。

需求文档归属与运行角色绑定分别维护。建包、归档、路径迁移均不代表角色已启动、任务已完成或获得生产发布授权。
