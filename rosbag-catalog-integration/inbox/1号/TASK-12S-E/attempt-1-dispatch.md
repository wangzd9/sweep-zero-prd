# TASK-12S-E 接收/登记/绑定自动闭环 attempt-1 派单（协调者，2026-10-14 20:2x +08:00）

## 状态：PENDING 待 ACK（V04_CLOSEOUT 已解除）

- **owner：A（执行者1号，数据处理链路开发）**；建议开发槽 A。
- 父任务 TASK-12S；REQ-20 / AC-20，细化 REQ-01/02/06/08/14/18。
- 唯一规划入口 [SPRAY-POST-V04.md §1](../../../SPRAY-POST-V04.md)；本派单补实际 base/owner/attempt。
- **base（固定开发起点）：main `16a154fff6f23e20b15498d1285a783713859647`**（v0.4 已合入，20:02，ls-remote github 一致）。从该 SHA 建专属 worktree/branch；禁止改 seed/旧冻结树/主仓用户脏文件（HANDOFF/devflow/ocr SKILL 等未提交内容保留）。

## 范围（文件 owner，越界即停）

- 独占：`app/services/ingest_service.py`、`app/services/source_service.py`、必要 `scene_schedule_consumer.py` 与对应 ingest/source/schedule 测试；仅确需请求接线时触及 `app/api/ingest_submissions.py`。
- **不碰**：场景算法/代理/UI/ros2_slice/models/迁移头/部署；不复制旧恢复脚本为正式旁路。

## 契约（必须达成，来自规划 §1）

1. 登记前提交、先登记后提交、二者并发、登记后崩溃重启都必须收敛到「单份用途事件/运行 + 已有结果复用」。
2. 复用既有登记绑定与 outbox 业务服务；后提交必须从**冻结 root/profile/version + 相对 ready 映射**定位已登记源，不能只按 basename/快指纹匹配。
3. 快指纹仅作候选索引；验证准确原包路径/root/已有 ORIGINAL/source/代次后，允许合法原包携快指纹重登记（即使子包同指纹）；绝不能把子包当原包、覆盖父路径、归并 UID 或移除派生围栏。歧义/越界/无法证明准确源 → 409 + 可追溯原因。
4. 幂等身份：`source_id + source_generation + 冻结场景/能力/参数身份`一致才复用已有 run；相同重放不分配新分析版本、不新增 attempt/outbox 消费副作用或模型调用；新代次/配置冲突/不同车辆按既有冲突规则区分，不为「幂等」吞掉显式合法新分析。
5. 采用现有后台恢复/有界对账补事务空隙，不新建通用调度平台；时限沿现有扫描/消费配置取证，不能无限等待或依赖模型执行槽释放。资料不齐仍待补，不制造成功绑定。

## 自测 + TESTER 交接

- 自测：MySQL 隔离库固定 SHA 验证两种先后、交错并发、commit/响应丢失、重启/重复扫描/重复提交/重复恢复；构造同指纹父子、同名跨根/跨车辆、歧义源、错误代次、不同配置；对重复路径核 source/run/attempt/分析版本/outbox 及模型调用计数不增加（不能仅断言 HTTP200）；无真实模型的机械用例可记调用计数/桩，真实已接受结果复用单独取证，**不再烧历史生产三包**；旧自建/NVIDIA/坡道与派生保护必要回归。
- 交付冻结后由 TESTER 独立验证、协调者经唯一 ocr_runtime 串行 OCR 裁决、适用强审/合入。

## 停止条件

发现需 schema/状态机/算法变化、生产写需求、未知在途写者或文件冲突 → 存证据交协调者，继续独立无冲突项。

## 完成产物

`receipts/TASK-12S-E/attempt-1.md`；AC-20 通过 + 独立验证 + OCR findings 裁决 + 合入证据齐后接受。接受事件解除 F 公共文件前置，并为 D2 最终集成候选提供基线。

## ACK 要求

领单后在 `inbox/1号/TASK-12S-E/attempt-1-ack.md` 落盘 ACK（记录 base、专属 worktree 路径/分支、.venv 软链、控制租约释放），再开工。