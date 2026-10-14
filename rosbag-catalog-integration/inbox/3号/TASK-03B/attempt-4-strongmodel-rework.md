---
task: TASK-03B
item: strongmodel-rework
owner: 3号
status: ACCEPTED
dispatched_by: 协调者（强模型审查 #3/#4-生产端/#6 high，全部已代码核实成立）
updated: 2026-10-09 16:5x
round: 1（强模型审查返修，独立于 F2 f11e617 并发返修）
depends: f11e617 交付中——先完成 F2 并发返修（等测试者 verify-f11e617-f2 PASS）再领本单，避免同文件冲突
---
# 03B 强模型审查返修（3 条 high，生产端）

## 前置
本单 3 条都落在 ingest_service.py / source_service.py，与你进行中的 F2 f11e617 同文件。
**先完成 F2 并发返修**（测试者 verify-f11e617-f2 报告 PASS 后我确认合入），再领本单；
从 main 合入后的 HEAD 新建返修分支，勿在主工作区改。

## #3 high：用途配置没有控制 Phase0 创建（source_service.py:178-190，已核实）
现状：`_find_or_create_pipeline_run` 在**解析冻结用途之前**就无条件 `or_` 匹配/创建
`PHASE0_QUEUE` 的 run，绑定到 200 行才发生。因此**仅选 scene_slice 的包也会启动 self-built 链**，
违反 DESIGN 用途替换规则（REF-DESIGN line58）。且既有 run 查询**未按 pipeline_type 过滤**，
恢复登记可能把 scene run 当 self-built run 返回。
修复：
- 先解析并冻结用途，再**按用途分别**创建对应 pipeline_type 的运行（scene_slice→不建 PHASE0_QUEUE；self_built→建）。
- 所有既有 run 查询必须带 `pipeline_type` + `source_generation` 双过滤，杜绝跨类型误配。

## #4 生产端（强模型跨任务契约，见下方协调者裁决）
修复：提交**接受时**冻结单能力 hash 并持久化到 submission；绑定时**不得**重新从当前 registry 计算。
CONFIG_REQUIRED（接受时能力未解析成功）的 submission **不发射 scene 事件**（停在 PENDING_INPUT 等用户补配置）。
即：任何 scene 事件都必须带有效冻结 hash，绝不允许 NULL-hash 事件。

## #6 high：PATCH 与 Scanner bind 没有共享行锁（已核实，全文件无 with_for_update）
`_find_pending_submission`（499）和 `patch_submission`（362）都按普通 SELECT 读快照、无 FOR UPDATE/条件更新。
Scanner 读到旧快照后，PATCH 可并发成功，随后 bind 覆盖状态 → 用户收到"修改成功"但运行用了旧配置。
修复：
- PATCH 与 bind 使用**同一行锁**（`with_for_update()` 读 pending submission，或锁同一个稳定键）。
- PATCH 更新的条件包含 `status='PENDING_INPUT' AND row_version=:expected`（乐观锁 + 行锁双保险）。

## 协调者裁决（#4 契约，两端同一策略）
DESIGN §11.2 冻结的 purpose-schedule-event/v1 规定：scene 事件**必带** capability_version + capability_config_hash。
策略 = **接受时冻结**：
- 能力 hash 在 submission 接受（用户给出有效 scene 选择、registry 当时可用）时计算并持久化。
- bind（source_service）阶段只读已冻结 hash，不重算；registry 若此后漂移，事件仍带接受时的 hash，
  由 05 消费端 `registry.get(scene_code, capability_version)` 返回 None → 走 SCENE_UNAVAILABLE → **失败运行留痕**（不是丢弃）。
- 接受时能力未解析（CONFIG_REQUIRED）→ 不发 scene 事件，submission 停 PENDING_INPUT。
- 05 的 CONTRACT_VIOLATION 丢弃路径保留为**真正的不变式违约**（我们自己的生产端永远不该触发它）。
此裁决同步给 1号（消费端），两端实现一致。

## 验收（协调者）
- 我代码核实 3 条 + 定向/全量测试；
- #4 与 1号 消费端联调（真实 outbox 事件走通：接受冻结→bind 不重算→漂移失败运行留痕）；
- 合入 main + push。