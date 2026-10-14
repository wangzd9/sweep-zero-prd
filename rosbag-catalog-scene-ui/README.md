# 场景最小界面闭环

- 需求ID：`CATALOG-SCENE-UI`。
- 代码仓：`/home/wang/work/rosbag-catalog`；水雾算法来源`/home/wang/work/ros2_slice`。
- 本需求文档根：`/home/wang/work/doc/prd/rosbag-catalog-scene-ui`。
- 范围：REQ/AC-16、REQ-05界面部分与原07界面任务；TASK-16C-A/B/C、16D、16R及聚合16。
- 文档已按需求拆分；本包未建立独立五角色运行绑定。
- 当前活跃协作根仍为`/home/wang/work/doc/prd/rosbag-catalog-integration`。本包 [TODO](TODO.md) 是定位入口，状态唯一维护在 [原运行TODO](../rosbag-catalog-integration/TODO.md)，不复制第二份状态。

阅读顺序：[需求](PRD.md) → [设计](DESIGN.md) → [验收](ACCEPTANCE.md) → [本包任务](TODO.md) → [交互记录](INTERACTIONS.md) → [交接](HANDOFF.md)。

公共契约唯一源：[场景基础设计](../rosbag-catalog-scene-foundation/DESIGN.md)。关联需求：[基础](../rosbag-catalog-scene-foundation/README.md)、[界面](../rosbag-catalog-scene-ui/README.md)、[水雾](../rosbag-catalog-spray-pipeline/README.md)、[A100](../rosbag-catalog-a100-multi-node/README.md)、[NVIDIA清理](../rosbag-catalog-nvidia-cleanup/README.md)。

当前角色继续按原有效派单工作；本次只迁移文档归属，不重新领取、不改REQ/AC、不重置任务状态、不激活后续阶段。运行根、inbox、回执、租约和会话暂留原位是兼容过渡；切换运行根须在安全检查点统一核对工具与绑定，见 [迁移记录](../MIGRATION-20261014.md)。
