---
task: TASK-03B
item: attempt-5-rework-2
owner: 1号
status: PENDING
dispatched_by: 协调者
updated: 2026-10-10 16:26
base: wt-01 f088c2b（你的 R2 返修之上续做）
round: 同返修单小修（不占新轮次）
---
# 1号小修：f088c2b OCR 2 findings（medium+low）

f088c2b OCR 收口（88c0f2c2，15m19s）出 2 条：

1. **[medium/bug] R2-02 rowcount 契约生产链路未接线**：`mark_event_consumed/mark_event_dropped`
   返回 0 行 bool，但唯一调用方 `_mark`（scene_schedule_consumer.py:303-306）丢弃返回值——
   0 行时依旧 `stats[bucket] += 1` 静默计成功。隔离测试验了 bool，集成面没接线，R2-02
   "0 行不得静默"在真实 consume 路径上不成立。**处置**：`_mark` 检查返回值，False（0 行）时
   计入 `stats["errors"]`（或独立计数）+ 记 warning 日志，不得无条件计 consumed/dropped；
   带 1 定向回归（构造 0 行命中场景断言 errors 计数+日志）。
2. **[low/style] 终态 UPDATE 仍用 `text(f"UPDATE {OUTBOX_TABLE} ...")` 手写 SQL**：
   与本次"消除手工拼接标识符"主题不一致（OUTBOX_TABLE 是安全常量，非阻塞）。**处置**：
   顺带改 `update(PurposeScheduleEvent).where(...)` Core 表达，与 SELECT 改造同风格。

交 f088c2b 之上单 commit + 回执更新 + 群内通报。OCR 不自跑（协调者增量审）。