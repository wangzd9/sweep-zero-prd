# 场景文档旧入口：DESIGN.md

2026-10-14已按独立需求拆分正文。这里保留旧路径和章节锚点，便于现有任务/历史链接接续；新需求请在对应包规划。

- [场景基础](../rosbag-catalog-scene-foundation/README.md)
- [最小界面闭环](../rosbag-catalog-scene-ui/README.md)
- [水雾流水线](../rosbag-catalog-spray-pipeline/README.md)
- [A100双节点](../rosbag-catalog-a100-multi-node/README.md)
- [NVIDIA清理](../rosbag-catalog-nvidia-cleanup/README.md)
- [迁移前原文（历史，不是另一份当前契约）](archive/pre-reorganization-20261014/DESIGN.md)

当前状态仍以 [运行TODO](TODO.md) 和原派单/decision为准；本次不改状态或原REQ/AC。公共契约权威在基础DESIGN，UI和水雾各自维护专项正文。

# Bag 场景处理服务技术设计

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

## 1. 当前结构与复用边界

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

## 2. 场景能力注册与适配器（沿用已接受 P0 契约）

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

### 2.1 注册契约

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

### 2.2 统一适配器协议

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

## 3. 接收配置、每包提交与自动调度（已有契约，v0.4 根隔离见 §7.3）

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

### 3.1 配置来源和覆盖

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

### 3.2 绑定、冻结与竞争

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

## 4. 数据契约与 CSV 对应（沿用已接受 P0 契约）

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

### 4.1 数据分层

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

### 4.2 替换 CSV 的业务对应

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

## 5. 异步执行与结果状态（已有状态机，v0.4补正式代理）

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

## 6. 发布、幂等与当前版本（沿用已接受P0契约）

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

## 7. 服务接口与客户端（已有接口及v0.4扩展目标）

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

### 7.1 P0 API 契约

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

### 7.2 页面与写接口

本节按需求归属查看 [rosbag-catalog-scene-ui/DESIGN.md](../rosbag-catalog-scene-ui/DESIGN.md)。

### 7.3 v0.4 场景专用接收、执行与界面补齐

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

#### 7.3.1 NAS 根与用途路由

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

#### 7.3.2 处理机执行与远端模型

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

#### 7.3.3 页面查询与步骤映射

本节按需求归属查看 [rosbag-catalog-scene-ui/DESIGN.md](../rosbag-catalog-scene-ui/DESIGN.md)。

### 7.4 v0.5 水雾接入与原始信息契约

本节按需求归属查看 [rosbag-catalog-spray-pipeline/DESIGN.md](../rosbag-catalog-spray-pipeline/DESIGN.md)。

## 8. 容量、归档与统计设计

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

### 8.1 P0 必要容量基础

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

### 8.2 批量扩张前容量门禁

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

### 8.3 冷热归档与完整性

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

### 8.4 P3 分布统计

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

## 9. 清理、迁移、兼容与回滚

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

## 10. 验证层次与建议默认值

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

## 11. 有界开发与并发集成

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

### 11.1 范围边界

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

### 11.2 模块子任务与可并行边界

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

### 11.3 文件责任与隔离

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

## 12. 共享文档与证据更新契约

本节按需求归属查看 [rosbag-catalog-scene-foundation/DESIGN.md](../rosbag-catalog-scene-foundation/DESIGN.md)。

## A100 双节点纳管独立专项入口

本节按需求归属查看 [rosbag-catalog-a100-multi-node/DESIGN.md](../rosbag-catalog-a100-multi-node/DESIGN.md)。

## 12. v0.4之后的水雾生产收尾契约

本节按需求归属查看 [rosbag-catalog-spray-pipeline/DESIGN.md](../rosbag-catalog-spray-pipeline/DESIGN.md)。

