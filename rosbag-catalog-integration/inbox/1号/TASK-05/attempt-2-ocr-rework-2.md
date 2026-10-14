---
task: TASK-05
item: attempt-2-ocr-rework-2
owner: 1号
status: ACCEPTED
dispatched_by: 协调者
updated: 2026-10-10 00:56
target: alembic/versions/20261009_01_scene_identity_key.py 的 4 个 E402（import 位置）
round: 风格小单（非 B6 两轮返修计数内；B6 的 high 你已修复合入 b5efba2）
---
# 05 风格小单：20261009_01 迁移 import 位置 E402

你的 backfill high 修复（db4bec7）已合入 main b5efba2（00:55，验收通过：去重逻辑核实 +
33 定向 + 778 全量 + 真实 alembic 子进程 upgrade 测试）。

剩一个小风格问题：20261009_01 有 4 个 E402（hashlib/json/sqlalchemy/alembic import 在
revision/down_revision 属性之后）。既有 20261008_02（03B）是 import 在顶部、All checks
passed。门禁路径 `ruff check app scripts tests` 不含 alembic 不阻塞，但 3号的 20261009_02
同类问题我正在让她一并修，保持两个新迁移风格统一。

**改法**：把 4 个 import 移到文件顶部（shebang/docstring 之后、revision 属性之前），
跑 `ruff check alembic/versions/20261009_01_scene_identity_key.py` 无 E402 +
定向 tests/test_scene_slice_scheduling.py 全绿（import 顺序不影响迁移逻辑，
但务必重跑确认）→ commit + 回执追加 + 群内通报。

## 顺带并入 2 条 B3 low（orchestrator 观测质量，低优先，非功能 bug）
B3（d1f2eba 05 主体 OCR）对当前 HEAD 核出 2 条仍在的 maintainability/observability 低项，
都落在 app/orchestrator.py:170-174 的 purpose-events 消费 print，一并修掉（不单独唤醒）：
- **errors 未 log**：print 只打 consumed/dropped/pending/created/reused，`stats['errors']`
  完全没输出——单事件失败（保持 PENDING 每轮重放）两边都无日志痕迹。加 errors 计数 +
  非空时打第一条 event_id/message。
- **空轮次无限打 0 行**：outbox 合入前（或无事件时）每 10s 轮询都打一行全 0 日志，
  刷屏。改为**仅当任一计数非 0 或 errors 非空时才 print**（OCR 已给示例：
  `if any(stats.get(k,0) for k in (...)) or stats.get('errors'): print(...)`）。
两条都是纯 print 逻辑调整，不碰业务正确性（已由 6ce7b7a 修复 + outbox 联调 PASS 6/6 保证）；
改完 `ruff check app/orchestrator.py` + 相关定向测试全绿即可，与 E402 同一 commit 交付。
