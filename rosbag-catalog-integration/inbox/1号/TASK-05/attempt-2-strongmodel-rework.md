---
task: TASK-05
item: strongmodel-rework
owner: 1号
status: ACCEPTED
dispatched_by: 协调者（强模型审查 #5/#7 high + #4-消费端，已代码核实成立）
updated: 2026-10-09 16:5x
round: 1
note: 05 已在 main（d1f2eba 等），本单返修后 hotfix 合入；强模型另指出 05-review.md 是未提交中期快照不作验收回执，本次以 main 实际 commit 为准
---
# 05 强模型审查返修（2 条 high + 1 条契约消费端，均落在 scene 消费/运行路径）

## 前置
从 main 当前 HEAD 新建返修分支（勿在主工作区改，协议 v1 起主工作区 commit 红线）。
05 核心 3 文件的 OCR 完整覆盖我另行串行补审，本单返修与 OCR 可并行推进，但**合入以两者都过为准**。

## #7 high：业务身份只保证"活动期唯一"（scene_slice_service.py:170-178 + pipeline_service.py:414/416/424，已核实）
现状：`create_scene_run` 只按 `active_identity_key` 查重，而该键在**所有**场景终态（SCENE_FAILED 不可重试、
SCENE_DONE、及其他）都会被 `= None` 清空。于是相同业务身份（source+generation+purpose+scenes）
**以新 event_id 重发时，active_identity_key 已空 → 查重命中不了 → 新建 run**，
违反 purpose-schedule-event/v1 的"只创建一次"（§11.2）。
修复：
- 自动调度身份需要**持久唯一键**：新增/复用一列（如 `scene_identity_key`，区别于活动租约的 active_identity_key），
  由 source+generation+purpose+scenes 确定性计算，**不随终态释放**，加唯一约束（scene run 域内）。
- create_scene_run 改为先按持久身份键查重命中（含终态 run）→ 复用/幂等返回；
- **显式重新分析**应另带 `analysis_version`/`reanalysis_id`（新身份维度），走新 run，不与自动调度身份混淆。
- 注意与 06A 已合入的 scene 结果表身份口径不冲突（06A 用 run+bag 维度，这里是 run 创建身份）。

## #5 high：dropped 事件仍保持 PENDING（scene_schedule_consumer.py:_mark 242-245，已核实）
现状：`_mark(...,"dropped")` 只 `stats["dropped"] += 1`，**只有 consumed 才 `mark_event_consumed` 更新 outbox**。
未知用途、缺字段、旧源事件等永久错误的事件不离开 PENDING → 永远占据 `ORDER BY id LIMIT 50` 头部，
**50 条坏事件即可阻塞后续全部正常事件**。
修复：
- outbox 增加 `DROPPED`/`FAILED_PERMANENT` 终态 + 错误原因列（或复用现有 status + error 字段，看你表结构）；
- 永久错误（CONTRACT_VIOLATION、SCENE_UNAVAILABLE 终判、源身份失效）**必须原子离开 PENDING**：
  在 `_consume_one` 的事务里同步写 outbox 终态，再 commit，不能只改内存 stats。
- 瞬时错误（源未 READY）保持 PENDING 下轮重试不变。
- 迁移：若 outbox 表是 03B 的（20261008_02），字段变更走 3号 的迁移链或你新迁移，注意 migration 链顺序（我协调）。

## #4 消费端（契约，见 3号 单内协调者裁决，两端一致）
- 接受时冻结 hash 后，05 对 scene 事件：`registry.get(scene_code, capability_version)` 为 None（漂移）
  → 走 SCENE_UNAVAILABLE → **建失败运行留痕**（已有此路径，确认它真的建 run 而非丢弃）。
- 事件缺 hash（capability_config_hash 为空）→ 保留 CONTRACT_VIOLATION 丢弃，但**必须落 outbox 终态**（与 #5 联动，
  不能只丢内存），且我们生产端修好后此路径不应再被触发。

## 验收（协调者）
- 我代码核实 3 条 + 定向/全量测试（05 调度 25 passed 基线 + 新增回归）；
- #4 与 3号 生产端真实 outbox 联调；
- 合入 main + push（合入顺序：先 03B 返修合入，再 05 rebase 到最终 03B 上联调——强模型裁决也如此）。