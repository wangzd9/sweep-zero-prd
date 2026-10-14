# 水雾设计入口

本包的算法/输入/模型/时间轴/缓存契约唯一正文是 [SPRAY-INTEGRATION](SPRAY-INTEGRATION.md)；生产接收自动收敛、拒绝恢复和质量补验唯一正文是 [SPRAY-POST-V04](SPRAY-POST-V04.md)。本页不复制另一套算法或状态机。

- 公共能力、源代次、冻结hash、幂等、租约和current发布：[场景基础DESIGN](../rosbag-catalog-scene-foundation/DESIGN.md)。
- 上游车辆/采集时区/批次/传感器资料：[RAW-DATA-REQUIREMENTS](RAW-DATA-REQUIREMENTS.md)。
- 参考图内容身份：[SPRAY-REFERENCES.json](SPRAY-REFERENCES.json)。
- 发布G1～G6与旧功能保护：[SPRAY-RELEASE](SPRAY-RELEASE.md)。
- UI依赖与回归范围：[场景界面包](../rosbag-catalog-scene-ui/README.md)。

跨包集成沿原TASK依赖：12S-A依赖16A/03；12S-B依赖04A/04B/09；12S-C依赖16B与12S-A/B的固定接受产物。后续接续按V04_CLOSEOUT→E→F、V04_CLOSEOUT→D1、E+F+D1→D2；本次不激活新阶段或运行绑定。
