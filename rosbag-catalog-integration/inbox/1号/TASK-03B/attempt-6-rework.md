---
task: TASK-03B
item: attempt-6-rework
owner: 1号
status: REVIEW_PENDING
dispatched_by: 协调者
updated: 2026-10-10 18:37
base: main 74ba3bf
round: R2 终测 S1 FAIL 返修（有界 2 轮内）
---
# 1号返修：S1 迁移链 1406（version_num 列宽 vs 33 字符 revision ID）

TESTER MySQL 终测（reports/TASK-06/r2-final-mysql-e2e.md，18:17 交付）**S1 FAIL**：
`alembic_version.version_num` 默认 VARCHAR(32)，revision `20261009_02_ingest_frozen_columns`
= 33 字符 → 任何 MySQL 库 `upgrade head` 到该 revision 必 1406 卡死（全新库+已有库双路径真实复现，
最小复现脚本 ~/.hermes/cache/scratch/tester_r2_r1_repro.py）。R2-01 原目标（4 TEXT 列无 DEFAULT）
已验证成立（SHOW CREATE TABLE 证据），败在链尾 revision ID 越宽。

## 处置（协调者已核实，裁决=改短 revision ID，不是 ALTER 列宽）

TESTER 报告建议"改短不推荐（已有库兼容差）"——**该前提不成立**，协调者已核实：
1. `20261009_02_ingest_frozen_columns` 这个字符串**仅在迁移文件 `revision=` 处定义**，
   全仓 grep 无任何代码/测试引用它（已核）。
2. TESTER 自身证据：**没有任何 MySQL 库成功应用过 20261009_02**——1406 恰好发生在
   "写入这个 33 字符 ID 到 alembic_version"那一步，故不存在已存该 ID 的库，改短无兼容风险。

**改法（实现面最小）**：
- 把 `alembic/versions/20261009_02_ingest_frozen_columns.py` 里 `revision = "..."` 改为
  **≤32 字符**的新 ID（如 `20261009_02_ingest_frozen`，25 字符），**down_revision 不动**（仍指
  `20261009_01_scene_identity_key`，30 字符合规）。文件名同步改以对齐（可选卫生，alembic 按
  文件内 revision 属性发现迁移、不依赖文件名）。
- 全仓再 grep 确认无第二处引用旧 ID（含 HANDOFF/文档里的 revision 提及，改一致）。
- 若你核后认为存在"已有库已存旧 ID"的反例（应不存在），改用 ALTER 列宽方案并在回执说明。

## 验证（真实 MySQL 必交，不得只 SQLite）
- 干净 MySQL 8.4 库 `alembic upgrade head` 全程 RC=0 + `alembic current` 输出 = 新短 ID。
- 已有库停在 20261009_01 的库 `upgrade head` RC=0。
- SQLite 全量 823 passed 不回归 + ruff 绿。
- 交付：commit + receipts/TASK-03B/attempt-6-rework.md（含上述真实 MySQL RC 证据）+ 群内通报；OCR 不自跑。