# VLA 无人化工作流与 Agent 监督方案

需求标识：`vla-unattended-workflow`。本包保存跨自建与 NVIDIA 路线的无人化工作流、确定性编排、质量与发布、Agent 监督等长期目标设计。

- 文档根：`/home/wang/work/doc/prd/vla-unattended-workflow/`。
- 设计正文：[PRD.md](PRD.md)。本文是长期方案，不代表已完成无人值守系统。
- 关联平台代码：[rosbag-catalog](/home/wang/work/rosbag-catalog)；算法和处理脚本边界以 PRD 及各路线文档为准。
- 本包没有新增权威 TODO。已落地路线的任务状态分别由[自建 TODO](../vla-self-dataset-pipeline/TODO.md)与[NVIDIA TODO](../vla-nvidia-dataset-pipeline/TODO.md)维护。

## 使用边界

需要实施无人化方案中的新目标时，先明确本期范围与验收，确认它是既有路线补充还是可独立交付的新需求，再建立对应任务。不得直接把长期设计章节解释为当前派单或执行许可。

路线实际执行位置、Worker、资源调度、状态与验收契约优先读取[自建 V1 设计](../vla-self-dataset-pipeline/PRD.md)和[NVIDIA V1 设计](../vla-nvidia-dataset-pipeline/PRD.md)。当前实现事实读取[当前架构](/home/wang/work/rosbag-catalog/docs/current_architecture.md)、[项目状态](/home/wang/work/rosbag-catalog/docs/project-status.md)、[仓库交接](/home/wang/work/rosbag-catalog/HANDOFF.md)及对应任务证据。

## 兼容与接续

旧入口 `/home/wang/work/doc/prd/vla_unattended_workflow_prd.md` 保留为指向本包 PRD 的兼容入口。历史正文中的旧文件名和路径继续用于追溯。

此次整理只归集长期方案，未激活该方案的开发、群、cron 或五角色运行绑定，未复制其他路线的 TODO。[返回需求总索引](../README.md)。
