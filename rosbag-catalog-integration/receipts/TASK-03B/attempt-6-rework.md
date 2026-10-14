# 回执：TASK-03B / attempt-6-rework（S1 迁移链 1406，revision 改短）

- status: REVIEW_PENDING
- output_commit: ceeac16
- branch: t03b-attempt-6-s1
- base: main 74ba3bf
- 交付时间: 2026-10-10 18:58 +08:00
- owner: 1号

## 处置口径
按协调者裁决=**改短 revision ID**（非 ALTER 列宽）。核实无"已有库已存旧 ID"反例：
- 旧 ID `20261009_02_ingest_frozen_columns` 仅在迁移文件 `revision=` 处定义，全仓 grep 无代码/测试引用。
- 1406 恰发生在"写入该 33 字符 ID 到 alembic_version"那一步，故无任何 MySQL 库成功应用过本 revision，改短零兼容风险。

## 改动（2 文件，零越界）
1. `alembic/versions/20261009_02_ingest_frozen_columns.py` → 改名 `20261009_02_ingest_frozen.py`
   - `revision` 由 33 字符 `20261009_02_ingest_frozen_columns` 改短为 **25 字符** `20261009_02_ingest_frozen`
   - `down_revision` 不动（仍指 `20261009_01_scene_identity_key`，30 字符合规）
   - 加注释说明改短理由与零兼容前提；补文件末尾换行
   - 未改 upgrade/downgrade 逻辑、未改 app 代码
2. `tests/test_scene_slice_scheduling.py`：新增定向回归
   `test_migration_head_revision_id_within_alembic_version_width`
   - 断言迁移链**所有** revision ID 长度 ≤32（防再踩同坑）
   - 断言 down_revision 链一致性（单 head 不分裂）
   - 隔离 SQLite `alembic upgrade head` RC=0 且 `current` 含新 head

## 真实 MySQL 8.4.11 证据（隔离容器 host 网络，默认 sql_mode，跑完 DROP 销毁）
证据 log：`/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/TASK-03B/attempt-5/s1-attempt6-mysql-evidence-1hao.log`

| AC | 命令 | RC | 结果 |
|----|------|----|------|
| AC1 全新库 | s1_fresh `alembic upgrade head` | 0 | `current`=20261009_02_ingest_frozen (head)，`version_num` varchar(32) 落新 ID |
| AC2 已有库 | s1_existing `upgrade 20261009_01`(RC=0) → `upgrade head` | 0 | 停步 `20261009_01_scene_identity_key` → 头 `20261009_02_ingest_frozen`，无 1406 |
| AC5 revision 长度 | grep revision | — | 新 ID 25 字符 ≤32 |

AC3（幂等：version_num 已 VARCHAR(255) 时新迁移不报错）——本方案不改列宽、不新增迁移，
幂等由"改短 revision 本身不触碰 alembic_version 结构"保证，测试者新 attempt 复测覆盖。

## 自测
- 定向新测：`test_migration_head_revision_id_within_alembic_version_width` PASS
- 迁移链相关既有 + 场景回归（scheduling/r2_rework/nvidia_contract/migration_lineage/china_standard_time/dataset_frame_indexes）：52 passed
- 全量 SQLite（`env -u DATABASE_URL`，排除 test_devflow 沙箱环境性 3 例，与基线一致）：**800 passed, 10 skipped**
- ruff check + format（改动 2 文件）：全绿
- 未跑 OCR、未合入 main（OCR 与合入归协调者）

## 边界声明
- 仅改动 alembic 迁移文件改名+revision 字符串、新增 1 条测试，零 app 代码改动、零契约变更。
- 隔离 MySQL 容器 `a-s1-mysql` 已 `docker rm -f` 销毁；未触碰生产/本地栈数据库。