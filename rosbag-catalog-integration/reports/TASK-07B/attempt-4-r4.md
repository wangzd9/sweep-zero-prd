# 报告：TASK-07B attempt-4-r4（r3-1 medium/low 迁移 downgrade 返修）

- commit：`62620a3`（base `4baf79f`，单文件 `alembic/versions/20261012_01_scene_manual.py` +31/−11）
- 交付冻结 REVIEW_PENDING，2026-10-13 07:2x +08:00

## 一、问题回顾（r3-1，协调者串行 OCR R3 增量批，session `01543c81`）

- **medium（R4-1）**：R3 把 `drop_column("corrected_label")` 放在表存在性判定之外，表缺失时 `get_columns` 抛异常，「部分应用重入安全」在 downgrade 面失去保证（按派单口径）。
- **low（R4-2）**：`bag_scene_label_evidence.corrected_label` downgrade 单独回滚再 upgrade 期间 MANUAL 行值被静默清除，与 `20261009_02` 已文档化的同型往返风险口径不一致。

## 二、实现与口径差异（关键）

双库实证（SQLite 内存 + 真 MySQL 8.4.11 独占容器）发现派单 §一 的**前置断言不成立**：

| 形态 | 正常态 downgrade | 表缺失态 downgrade |
| --- | --- | --- |
| 原始 `f4bfcf2`/`68b5188` | OK | **抛 NoSuchTableError**（首个失败点 `_indexes_of`→`get_indexes`，MySQL 1146 `SHOW CREATE TABLE`） |
| R3 `4baf79f` | OK | **抛 NoSuchTableError**（r3-1 medium 复现） |
| R4 `62620a3`（本交付） | OK（逐语句同原顺序） | **OK，no-op 安全** |

即原始口径对表不存在的库**并非** no-op 安全，§一「仅移动 drop_column、index 循环维持现状」无法满足 §三「表缺失态 downgrade 不抛异常」探针。R4 按验证口径把守卫提升为覆盖整个表依赖块（index 循环+列 drop+drop_table），在 §一 与 §三 冲突处以 §三（AC 面）为准，回执已越界申报。

## 三、证据索引

- 探针/取证脚本（`/home/wang/.hermes/cache/scratch/`）：`b-r4-diag.py`（定位失败点）、`b-r4-evidence2.py`（原始口径 MySQL 复现+容器端口冲突首跑）、`b-r4-evidence3.py`（双库双态终验矩阵）、`b-r4-roundtrip.py`（fresh 往返 RC=0+heads+ruff）、`b-r4-colcheck.py`（SHOW COLUMNS 三态列存在性核对）。
- 终端输出在案：定向 12 passed / SQLITE+MYSQL 往返全 RC=0 / 表缺失态 R4 双库 NO_EXCEPTION / R3+原始 双库 RAISED / ruff All checks passed / heads 单头 / 容器+网络 0 残留。

## 四、后续门禁链

协调者机械核验（含越界申报核对）→ R4 增量 OCR（单批迁移）→ 强审增量复审（授权期 2026-10-13 11:33:12 内）→ TESTER 07B-post-r（SR-05，target `62620a3`）→ 合入（07B 先于 16A rebase 双头）→ 07B DONE → 07C/16C。