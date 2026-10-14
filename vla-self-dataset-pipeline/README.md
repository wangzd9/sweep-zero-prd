# VLA 自建数据集处理链路

需求标识：`vla-self-dataset-pipeline`。本包归集自建 ROS 2 Bag 从稳定接收、处理机 Phase0、A100 后续处理，到质量校验、帧索引和 NAS 发布的 V1 设计与任务追踪。

- 文档根：`/home/wang/work/doc/prd/vla-self-dataset-pipeline/`。
- 需求设计：[PRD.md](PRD.md)。PRD 描述设计与目标，不能作为任务已完成的证据。
- 唯一任务状态源：[TODO.md](TODO.md)。具体状态、证据、未完成项和执行顺序均以该文件为入口；本导航不复制任务状态。
- 平台代码：[rosbag-catalog](/home/wang/work/rosbag-catalog)。正式自建脚本：[proj_self_dataset_builder_scripts](/home/wang/work/dataset_build/self_built_route/code/proj_self_dataset_builder_scripts)。
- 代码事实与架构入口：[当前架构](/home/wang/work/rosbag-catalog/docs/current_architecture.md)、[项目状态](/home/wang/work/rosbag-catalog/docs/project-status.md)、[仓库交接](/home/wang/work/rosbag-catalog/HANDOFF.md)。

## 需求边界

本包维护自建路线自身的需求和验收。NVIDIA 路线、水雾场景识别、独立 A100 扩容需求分别归属各自需求包；共享 Backend、资源池、代理或代码仓不意味着共用一个 TODO。跨包契约与证据通过链接引用。

自建 PRD 与 NVIDIA V1 PRD 的路线设计优先于早期无人化概念方案。当前能力和执行许可仍需读取任务条目、代码及验收证据，不从 PRD 的目标叙述推断。

## 关联需求

- [NVIDIA PhysicalAI 处理链路](../vla-nvidia-dataset-pipeline/README.md)：复用平台公共能力，任务状态独立维护。
- [无人化与 Agent 长期方案](../vla-unattended-workflow/README.md)：长期设计背景，不能覆盖路线实际契约。
- [场景目录集成](../rosbag-catalog-integration/README.md)：场景链路入口；水雾等拆分归属以其当前导航为准。
- [需求总索引](../README.md)。

## 兼容与接续

旧入口 `/home/wang/work/doc/prd/vla_self_dataset_pipeline_v1_prd.md` 和 `/home/wang/work/doc/todo/vla_self_dataset_pipeline_v1_todo.md` 保留为兼容入口，均指向本包唯一正文，不维护第二份状态。旧 PRD、TODO 内的历史路径与文件名保留用于追溯。

此次整理只调整文档归属与导航，不改变任务编号、业务状态、生产授权或执行节奏。本轮未核实或建立本包五角色运行绑定；执行前按权威 TODO 和实际运行配置确认工作入口。
