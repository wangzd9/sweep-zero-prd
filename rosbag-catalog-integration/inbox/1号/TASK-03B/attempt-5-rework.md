---
task: TASK-03B
item: attempt-5-rework
owner: 1号
status: ACCEPTED
dispatched_by: 协调者
updated: 2026-10-10 11:43
base: main eff0479（11:31）
round: R2 第二轮强模型返修第 1 轮（有界 2 轮）
---
# 1号返修：R2-01 / R2-02 / R2-05-create 侧（R2 强模型 11:31 裁决，全部 HIGH，均已有独立 MySQL 复现证据）

R2 审查结论：REWORK_REQUIRED（10 HIGH + 1 MEDIUM，裁决文件 reviews/strongmodel/R2-20261010-verdict.md，
复现证据 R2-20261010-evidence/）。你负责接收/调度侧 3 条。核心教训：**SQLite 全绿 ≠ MySQL 放行**
（SQLite 双引号=标识符 fallback、允许自引用 UPDATE，系统性遮坑）——此前 outbox 联调 6/6 是 SQLite 口径。

## R2-01：已有库增量迁移 1101（阻断生产升级）
- 位置：alembic/versions/20261008_02_ingest_config.py:39（create 分支）+ :47-49 三个 TEXT server_default
- 缺陷：**表尚不存在的已有库**升级到该迁移时，`op.create_table` 对 TEXT 下发 `DEFAULT '[]'/'{}'`，
  MySQL 8.4 拒绝（1101）。强模型用真实 MigrationContext/Operations 执行实际迁移函数抓到 1101。
- 此前裁决收窄：#1"误报"只成立于**空库路径**（空库 base 起始时首迁移 import 当前 ORM create_all 提前建表，
  02 的 `_table_exists` 分支跳过）——不全面排除。
- 修复：去掉 3 个 TEXT 字面量 server_default（保持写入侧显式赋值不变——现有业务路径已是）；
  **已应用实例的处理按发布策略**：不擅自重写历史迁移状态，方案写进回执（新迁移修正 vs 最小重写 02），
  最终裁决归协调者。
- 回归：旧 schema（无表）快照 `20261008_01 → head` upgrade 用例 + 空库用例，两条路径分别报告。

## R2-02：outbox 投影 MySQL 方言 bug（阻断调度）
- 位置：app/services/scene_schedule_consumer.py:57 `columns = ", ".join(f'"{c}"' for c in _EVENT_FIELDS)`
- 缺陷：`SELECT "event_id", "purpose", ...`——MySQL 默认 sql_mode（无 ANSI_QUOTES）双引号是**字符串字面量**，
  投影的是字面量不是列 → 事件当"未知用途"drop、终态更新用字面量 event_id 命中 0 行、
  **真实事件永久 PENDING 占 LIMIT 50 头部**、stats 误报已处理。
- 修复：用 SQLAlchemy Core 列对象生成 SELECT（或 `sa.text` + 正确的标识符引用）；
  同时终态 UPDATE（consumed/dropped）检查真实 rowcount，0 行按真实错误处理（不得静默）。
- 回归：双方言单测（至少 MySQL 默认 sql_mode 下的编译/投影断言）；MySQL 真实链路证据见下。

## R2-05 create 侧：自动路径创建时分配版本行（跨 owner 契约，两端逐字一致）
- 位置：app/services/scene_slice_service.py create_scene_run（显式路径 :259 已分配）
  + app/services/scene_schedule_consumer.py:234（自动事件路径建 run 未分配 SceneAnalysisVersion）
- 缺陷：自动路径**首次回报才分配**版本行；晚到旧任务回报时换版按版本行 created_at 排序，
  旧任务晚回报会覆盖用户显式新分析的 current（强模型复现 test_late_old_event_run_overwrites_new_current）。
- 契约（协调者裁决，2号负责 switch 侧）：**所有 scene run（自动事件路径 + 显式 API 路径）在创建时
  （同一事务内）即分配并绑定 SceneAnalysisVersion 行；换版比较用版本行提交时点顺序
  （分配时刻的持久 id 序号），不用回报时点。**
- 修复：create_scene_run 对自动路径（spec.idempotency_key 以 purpose-event: 前缀）也同事务分配 av 行
  （显式路径分配逻辑已有，统一入口）；2号会把 switch 侧比较字段改为 av 行 id/分配序。
- 回归：交错用例——自动旧→显式新、两次自动（不同配置版本）、显式旧→自动新（各含旧先完成/后完成）。

## 门禁事实
main 当前 HEAD=**eff0479**（06B 已于 2e674b2 合入——**不得回退/重做该合入**，返修直接在 main 新建
worktree 分支开发）。R2-01/02 的 **MySQL 真实结果必交**：独立 MySQL 8.4 容器实测
（已有库 20261008_01→head upgrade RC=0 + 默认 sql_mode 下 bind→poll→consume 真实 CONSUMED/建 run，
查 DB 终态不是 stats）——可自测（方法见 2号历史派单环境备忘）或交付后由测试者补测，但回执必须附真实结果。

## 交付
- commit + receipts/TASK-03B/attempt-5-rework.md（status REVIEW_PENDING，列出 R2-xx、测试数字、MySQL 证据）
- 群内按通报格式；OCR/强模型复审不自跑（协调者交付后串行）
- 定向：tests/test_ingest_config_api.py + tests/test_ingest_frozen_hash.py + tests/test_scene_slice_scheduling.py + 新增回归；全量 SQLite；ruff 全绿