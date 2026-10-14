# 场景旧协作根与兼容入口

本目录原来同时保存基础、界面、水雾和独立专项。2026-10-14业务文档已拆到同级需求包：

- [场景基础](../rosbag-catalog-scene-foundation/README.md)：公共接收、能力、执行、身份与发布契约。
- [场景界面](../rosbag-catalog-scene-ui/README.md)：三视图、八步详情、查询/追溯和原OCR遗留。
- [水雾流水线](../rosbag-catalog-spray-pipeline/README.md)：水雾能力、输入资料、发布/批次及后续生产收尾。
- [A100双节点](../rosbag-catalog-a100-multi-node/README.md)与[NVIDIA清理](../rosbag-catalog-nvidia-cleanup/README.md)：完整独立包已移出，原目录只保留兼容链接。

## 当前运行兼容区

五角色继续以本目录作为实际运行根。[TODO](TODO.md)仍是当前任务唯一可写状态；[SESSION-START](SESSION-START.md)、[协议](inbox/PROTOCOL.md)、[绑定](ROLE-BINDINGS.json)、[HANDOFF](HANDOFF.md)、inbox/receipts/test-receipts/reviews/sessions/events和锁保持原运行入口。新包任务页和交互索引只链接这些原件，不复制状态或运行身份。

旧PRD/DESIGN/ACCEPTANCE保留章节跳转，新契约在对应需求包维护；水雾旧文件名及两个独立专项目录均为兼容入口。历史原文见 [拆分前快照](archive/pre-reorganization-20261014/README.md)。scratch、review-bundle、历史sessions和事件仍按证据引用保留，目录整理不删除它们。

新独立需求在[需求容器](../README.md)同级建包。当前运行状态在安全检查点迁移前，不更改注册表/cron/租约或多包复制群绑定。迁移详情见 [MIGRATION](../MIGRATION-20261014.md)。
