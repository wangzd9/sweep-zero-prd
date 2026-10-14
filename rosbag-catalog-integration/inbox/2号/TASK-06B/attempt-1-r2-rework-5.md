---
task: TASK-06B
item: attempt-1-r2-rework-5
owner: 2号
status: REVIEW_PENDING
dispatched_by: 协调者
updated: 2026-10-10 22:25
base: main 5f0124b
round: codex 独立审查 REWORK 回派（2 medium + 1 low，同单 3 项）
裁决: reviews/codex-r2final-20261010-verdict.md
---
# 2号返修：codex 审查 3 项（M-1 微秒精度 / M-2 迁移边界 docstring / M-3 测试注释）

codex CLI 对 74ba3bf..5f0124b 独立审查（read-only 快照+探针验证），裁决已落
reviews/codex-r2final-20261010-verdict.md，3 项回你：

1. **M-1 [medium] started_at 微秒使缺陷3 no-op 检测失效（真 bug，必修）**：
   `scene_result_report_service.py:577` `datetime.fromtimestamp(der.start_ns/1e9, tz=utc).replace(tzinfo=None)`
   保留微秒；`started_at` 列 MySQL DATETIME(0) 秒精度。二次 reconcile 从库读回整秒 → old 元组（:566-573）
   判"变化" → 写微秒值被截断回同整秒 + updated_at 同秒 → 无 CLIENT_FOUND_ROWS 连接 rowcount=0 →
   StaleDataError 复发。现有回归/探针均整秒数据漏掉此条件。
   **修复**：:577 赋值统一 `replace(microsecond=0)`（写入与持久化精度对齐，比较口径随之正确）；
   **回归**：纳秒 start_ns 带小数秒 + 同秒重放，MySQL 语义下二次 reconcile 零 StaleDataError。
2. **M-2 [medium→边界记录]**：协调者已驳回"需版本映射"（全量核实 5 类存活库无旧 33 字符 ID，
   TESTER 隔离库已销毁——codex 反例前提不成立），但"零兼容风险"改**记录适用边界**：
   `alembic/versions/20261009_02_ingest_frozen.py:40` docstring 补——核实范围（开发机 3 SQLite +
   本地栈 MySQL 20260928_02 + 处理机生产库，2026-10-10 22:23 全无旧 ID）+ 若未来出现存旧 ID 库的
   人工升级语句（UPDATE alembic_version SET version_num='20261009_02_ingest_frozen' WHERE
   version_num='20261009_02_ingest_frozen_columns'）。
3. **M-3 [low] 注释纠偏**：`tests/test_scene_result_report.py:119` "SQLite 静默截断"改为
   "SQLite 未校验列宽（VARCHAR(26) 写 28 字符读回仍 28），掩盖超长问题"（codex 探针实证）。

验证：M-1 带 MySQL 语义回归（注明连接是否 CLIENT_FOUND_ROWS）+ SQLite 全量不回归 + ruff 绿。
交单 commit（5f0124b 之上）+ 回执 + 群内通报。OCR 不自跑。

另：attempt-1-r2-rework-4（夹具 uid 收敛）已被 6ee858b 覆盖交付并合入，该单关单，无需动作。