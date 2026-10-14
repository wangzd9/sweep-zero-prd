# NVIDIA PhysicalAI 数据集处理链路

需求标识：`vla-nvidia-dataset-pipeline`。本包归集 NVIDIA PhysicalAI 的 chunk 提交、下载与解压、处理、质量校验、可选 NAS 回传及血缘的 V1 设计与独立任务追踪。

- 文档根：`/home/wang/work/doc/prd/vla-nvidia-dataset-pipeline/`。
- 需求设计：[PRD.md](PRD.md)。
- 唯一任务状态源：[TODO.md](TODO.md)。具体完成范围、测试证据、故障验证、正式目录切换条件和剩余项以该文件为入口。
- 平台代码：[rosbag-catalog](/home/wang/work/rosbag-catalog)。正式 NVIDIA 脚本：[proj_nvidiadata_builder_scripts](/home/wang/work/dataset_build/nvidia_physicalai_route/code/proj_nvidiadata_builder_scripts)。
- 代码事实与架构入口：[当前架构](/home/wang/work/rosbag-catalog/docs/current_architecture.md)、[项目状态](/home/wang/work/rosbag-catalog/docs/project-status.md)、[仓库交接](/home/wang/work/rosbag-catalog/HANDOFF.md)。

## 需求边界

本包是复用既有数据平台的独立路线，原始数据为 NVIDIA PhysicalAI 数据集，不是 ROS 2 Bag。自建路线提供的 Backend、编排器和资源池是关联依赖；NVIDIA 的任务、脚本版本、验收和生产切换分别维护。

PRD 顶部的历史校准说明与后续 TODO 进展记录属于不同时点。不得仅依据其中的“暂停”或目标态表述判断当前完成情况，也不得把测试根验收解释为正式目录已切换。当前事实需要按 TODO 的证据与实际代码、运行结果核实。

## 关联需求

- [自建数据集处理链路](../vla-self-dataset-pipeline/README.md)：平台公共能力与路线基线来源。
- [无人化与 Agent 长期方案](../vla-unattended-workflow/README.md)：长期设计背景，不能替代两条路线的实际契约。
- [场景目录集成](../rosbag-catalog-integration/README.md)：独立场景链路及关联能力导航。
- [需求总索引](../README.md)。

## 兼容与接续

旧入口 `/home/wang/work/doc/prd/vla_nvidia_dataset_pipeline_v1_prd.md` 和 `/home/wang/work/doc/todo/vla_nvidia_dataset_pipeline_v1_todo.md` 保留为兼容入口，均指向本包唯一正文。历史文件名和路径保留，不产生第二份任务状态。

此次整理不重新裁定完成状态、不启动下载、不切换 A100 或 NAS 正式目录。本轮未核实或建立本包五角色运行绑定；执行前读取权威 TODO、仓库规则和实际运行配置。
