---
task: TASK-03B
item: attempt-4-ocr-rework
owner: 3号
status: ACCEPTED
dispatched_by: 协调者
updated: 2026-10-10 00:58
target: 03B B5b OCR（86baad5，session 40910526）：1 medium + 2 low（docstring/迁移文档），核心逻辑 0 发现
round: OCR 返修第 1 轮
---
# 03B B5b OCR 返修（3 条，全部 documentation 级，核心逻辑无发现）

B5b 对你 86baad5（冻结列 7 文件）审查 5 文件 3 条，**无 high/critical**——冻结 hash/行锁/
用途门控核心逻辑零发现。以下 3 条都是文档与实现漂移，但你那条 medium 涉及 05 消费端依赖的
契约语义，必须修。从 main b5efba2 新建修复 commit（同分支或新 hotfix），交付报 commit。

## medium（必修）：ingest_service.py:643-648 docstring 与实现矛盾
现 docstring 仍写**旧降级契约**："registry 漂移时事件以 capability_config_hash=None 落 outbox，
登记事务不抛错（§3.2 降级语义）"。但你 #4 返修已改成**显式失败**：冻结缺失/与有效配置版本
不一致时 raise CapabilityError → 整个登记事务回滚，函数内注释明言"绝不允许 NULL-hash 事件流出
本服务"。docstring 与实现直接冲突，且 05 消费端的 SCENE_UNAVAILABLE 降级依赖的正是"带接受时刻
hash 的事件 + 消费端 registry.get→None"，**不是**生产端 NULL-hash 事件——下一读者/维护者会被
旧 docstring 误导，以为还能收到 NULL-hash 事件。
**改法**：OCR 建议的替换文本（已核实与你的实现一致，可直接用）——
> scene_slice 事件只携带"接受时刻"持久化在 submission 上的冻结 hash，不重新从当前 registry 计算；
> registry 此后漂移（能力被禁用/移除）时事件仍带接受时刻 hash，由 05 消费端 registry.get→None
> 落 SCENE_UNAVAILABLE 失败运行。冻结缺失或与有效配置版本不一致（数据异常）时显式 raise
> CapabilityError，登记事务回滚——绝不允许 NULL-hash 事件流出本服务。

## low（建议顺手）：20261009_02 迁移 downgrade→upgrade 往返风险文档化
backfill 只在升级把 NULL 置 '{}'，未门控：生产库升级后已有新提交写入真实冻结 hash，再
downgrade(drop 列)→upgrade(add 列全 NULL + backfill 无条件置 '{}')，这些行冻结值被静默覆写为
'{}'，其后续 bind 命中"冻结缺失"raise → 登记 500 + Scanner 重试同一 bag。OCR 自己更正了：
drop 列丢数据是固有的、gate 挡不住，**不改列结构**。可行缓解=在迁移 docstring ⚠️ 段补一句记录该
风险 + 运维处置（对受影响 PENDING_INPUT 提交重新 PATCH 恢复冻结值）。与既有 20261009_01 的
drop-数据列口径一致，仅文档化即可。

## low（风格，与 05 的 20261009_01 同类）：20261009_02 import 位置 E402
你 20261009_02 的 4 个 E402（import 在 revision/down_revision 属性之后）。既有 20261008_02
是 All checks passed（import 在顶）。门禁路径 `ruff check app scripts tests` 不含 alembic 不阻塞，
但为与 03B 既有迁移风格一致，**把 import 移到文件顶部**（revision 属性后无需 import 也能定义，
或按 20261008_02 的组织方式）消除 E402。1号的 20261009_01 同样有 4 个 E402，协调者另行回派 1号，
你只管 20261009_02。

## 交付
- 修复 commit（medium 必修 + 2 low 建议），定向 test_ingest_frozen_hash/test_source_register_purpose
  必须全绿 + `ruff check alembic/versions/20261009_02_ingest_frozen_columns.py` 无 E402
- receipts 追加交付段（commit/测试/状态 REVIEW_PENDING），群内按新通报格式
- OCR 不自跑，等协调者对修复 commit 复审（有界 2 轮，本单是第 1 轮）