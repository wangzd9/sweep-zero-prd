# 回执：TASK-08 attempt-1（模块联调、故障与兼容）

- task/attempt：TASK-08 / attempt-1
- owner：执行者B（2号）
- 状态：**REVIEW_PENDING**（联调报告已交付；发现 2 类真实根因需协调者回派最小修复，本单不改业务代码）
- 被测 base：main `62a85bf`（= origin/main，ACK 时 fetch 双核一致）
- worktree/分支：`wt-04a-t08` @ `scene/task-08-integration`（HEAD=base，零业务代码改动）
- 环境：真实 MySQL 8.4.11 隔离库（`rosbag-catalog-local-mysql-1` 容器 STRICT_TRANS_TABLES），每文件独立新库 + 会话 FK off + create_all（对齐 `r2i6_mysql.py` 口径）；主仓 `.venv` Python 3.10.12
- 交付：报告 `reports/TASK-08/attempt-1.md`

## 核心结果

- **全链路联调 PASS**（真 MySQL）：迁移 upgrade/downgrade 回滚链 RC=0（31 表 + `alembic_version` 单头）；05 消费链空跑全零无副作用；场景核心文件 `test_scene_result_report.py` 35/35、`test_scene_result_storage.py` 25/25 真 MySQL 全绿。
- **文件级全量真 MySQL**：64 可跑文件 **55 PASS / 10 FAIL**（对照 SQLite 10 红文件全绿）。
- **I-1 回归验证项完成**：以 1号 `6823f2d`（wt-01-i1）真 MySQL 跑 `test_scene_slice_scheduling.py` = **36 passed RC=0**，确认 I-1 修复有效且止于该文件。

## 发现（需回派，非本单引入，未自行改码）

- **C1（4 文件）** DATETIME(0) 秒精度截断 vs 内存微秒时间比较（`source_service.deleted_at`/web 秒边界/pipeline 时间断言）——06B 缺陷3 已修域的同型未覆盖残留。
- **C2（5 文件）** 乐观并发/重试 UPDATE 命中 0 行 → `StaleDataError`（bag_cleanup/source/pipeline/clone）——与 06B 缺陷3（reconcile 幂等二次 UPDATE）同根因家族。
- **C3（2 文件）** 夹具 `bag_uid` 超 VARCHAR(26) 1406：`test_scene_slice_scheduling.py` 3 failed = **I-1 精确范围**（I-1 合入后消失）；`test_scene_slice_lineage.py` 10 errors = **I-1 未覆盖新同型**（T02 前缀 27 字符 uid，`tests/test_scene_slice_lineage.py:74-75`）。

## 越界申报 / 未执行

- 业务代码 0 改动（`git status` 仅 `.venv` 软链；HEAD=base）；C1/C2/C3 仅定位+最小复现。
- 未跑十万/百万压测；`test_bag_cleanup_mysql.py`/`test_mysql_operations.py`（独占容器入口）/`test_devflow.py`（沙箱环境性）skip，与 main 基线同集。
- 生产/真实样本（TASK-09/10/11）未触发（独立门禁）。
- 隔离库 0 残留（drop 全部 t08* 库 + drop `t08` 用户，after=[] user=0）。

## 证据

- 全量文件级真 MySQL：`~/.hermes/cache/scratch/t08-e2e/fkoff/allfiles_summary.txt`（55/10 逐文件）
- 根因隔离：`fkoff/isol2_*.log` + `sqlite_*.log`（对照全绿）
- 迁移/回滚：`t08-e2e/migrate-up.log` / `migrate-down1.log` / `migrate-up2.log`
- I-1 复测：`fkoff/i1_scheduling.log`（36 passed RC=0）
- 复现脚本（scratch 不进仓库）：`t08_mysql_e2e.py`/`t08_fkoff4.py`/`t08_isolate2.py`/`t08_allfiles.py`/`t08_i1check.py`/`t08_cleanup.py`

## 下一步（等协调者）

协调者按报告 §F 裁决回派：①C3-lineage 最小夹具单（建议 1号连续）②C2 是否扩展 06B 缺陷3 同源到清理/来源域（独立单+真 MySQL A/B）③C1 与 C2 合并"秒精度时间戳"专项。本单交付冻结，等待审查结果，不占第二个开发槽。