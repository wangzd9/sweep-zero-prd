# 派单：TASK-07B attempt-4-r4 迁移 downgrade 最小返修（单文件两项）

- 派单时间：2026-10-13 06:54:26 +08:00（协调者 r130）
- 任务：TASK-07B attempt-4-r4（R3 增量 OCR r3-1 medium 正式裁决 CORRECTION 的最小返修）
- owner：B（`wt-04a-t07b` 原分支 `scene/task-07b-manual-revision-withdraw` 续 commit）
- base：`4baf79f`（attempt-3-r3 交付冻结 HEAD，续 commit；原 base `502bf8e` 不变）
- 审查来源：协调者串行 OCR R3 增量批 r3-1 `alembic/versions/20261012_01_scene_manual.py` rc=0 session `01543c81-27c2-4290-b192-895cb291ac40`（06:11-06:21，2 findings），log `~/.hermes/cache/scratch/t07b_r3_ocr/r3-1_alembic_versions_20261012_01_scene_manual.py.log`；R3 增量 6/6 全收口余 5 批 0 findings（账 `reviews/TASK-16/16A-16B-ocr-batches.md` r130 段）。

## 一、返修范围（仅 1 文件 2 项，零 app 代码面）

**R4-1（r3-1 medium，CORRECTION）：downgrade 表存在性守卫口径回归。**
- 现状：R3 把原 `if TABLE in get_table_names(): drop_table` 内的 drop 结构改为先无条件 `drop_column("corrected_label")` 再判表存在。原（`68b5188`）downgrade 对表不存在的库是 no-op 安全；R3 后 `drop_column` 在表缺失时抛异常（SQLite NoReferencedTableError / MySQL 1146），**部分应用重入安全**（该迁移 docstring 自述目标）在 downgrade 面失去保证。
- 最小修复：`drop_column(TABLE, "corrected_label")` 移回 `TABLE in sa.inspect(bind).get_table_names()` 判定内；index 循环维持 `name in idx_names` 守卫（`_indexes_of` 对缺表的行为与原始口径一致，不改）。
- 验证：真 MySQL 8.4 隔离库 downgrade→upgrade 往返复跑（正常态）+ 表缺失态 SQLite 内存探针 downgrade 不抛异常。

**R4-2（r3-1 low，documentation）：downgrade 往返风险 docstring 同步。**
- 现状：R3 对 `bag_scene_label_evidence` 增 `drop_column("corrected_label")` 后单独回滚再重新 upgrade，期间 MANUAL 行 corrected_label 值被静默清除恒 NULL，与 `20261009_02_ingest_frozen.py` docstring 已文档化的同型往返风险口径不一致。
- 最小修复：迁移模块 docstring 补一段等价说明（引用 20261009_02 先例 + 按 07B 未合入迁移口径接受的处置边界），不改变列结构。

## 二、边界（冻结）

- 允许文件：仅 `alembic/versions/20261012_01_scene_manual.py`。
- 禁：新表/新迁移文件、app 代码、tests、07A/16A/16B 文件面、upgrade 面改动（R3 已审 0 findings 的 upgrade 结构不动）。
- AC 不变量冻结=审查包 `reviews/TASK-07B/attempt-2-r2/strong-review/SR-07B-A2R2-20261013-pack.md` §2（1-6），R4 只关闭 r3-1 两项，不新增需求。

## 三、自测口径

- 定向：`pytest tests/test_task07b_r3_revision.py tests/test_task07b_manual_revision.py tests/test_task07b_r2_revision.py -q` 0 红（迁移面无新增用例要求）。
- 真 MySQL 8.4 隔离库：fresh upgrade→downgrade→upgrade 往返 RC=0 复跑（口径同 R3 交付申报），容器 0 残留；新增 SQLite 内存探针=表缺失态 downgrade 不抛异常（守卫生效断言）。
- ruff 改动文件绿；`alembic heads` 单头 `20261012_01_scene_manual` 不变。

## 四、交付与后续

- 交付：commit（`4baf79f` 之上）+ 回执 `receipts/TASK-07B/attempt-4-r4.md`（REVIEW_PENDING）+ 报告 `reports/TASK-07B/attempt-4-r4.md`。
- 交付后：协调者机械核验（diff 限单文件）→ R4 增量 OCR（单批迁移）→ 强审查增量复审（授权 grant `31dcbabe…` 期限 2026-10-13 11:33:12 内，范围=R3-1~R3-4+R4-1/R4-2 问题 ID 与修复 diff，冻结原 AC）→ TESTER 07B-post-r 独立验证单（SR-05 口径不变，target 以 R4 收口后固定 HEAD 为准）→ 全绿合入（07B 整链先于 16A 迁移 rebase 双头）→ 07B DONE → 派 07C/16C。
- 同根因两轮失败（R4 增量复审再出同位 CORRECTION）=升级用户，不无限返修。

- 已 ACK 前请回复 ACK（`inbox/2号/TASK-07B/attempt-4-r4-ack.md`）；开工不催单。
