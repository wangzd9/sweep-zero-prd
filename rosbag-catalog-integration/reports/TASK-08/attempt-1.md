# TASK-08 attempt-1 联调报告（模块联调、故障与兼容）

- task/attempt：TASK-08 / attempt-1
- owner：执行者B（2号，cron `cron_6f7471d8747c_20261011_152753`）
- 被测 base：main `62a85bfb6b3791ebfa706cce0125bb217635126f`（ACK 时 fetch 实测 = origin/main 双核一致）
- worktree/分支：`/home/wang/.local/state/rosbag-scene/wt-04a-t08` @ `scene/task-08-integration`
- 环境：主仓 `.venv`（Python 3.10.12 / PyMySQL 1.1.1 / SQLAlchemy 2.0.41）；**真实 MySQL 8.4.11 隔离库**（本地栈 `rosbag-catalog-local-mysql-1` 容器，STRICT_TRANS_TABLES）；每测试文件独立新库、FK 会话级 off + `Base.metadata.create_all`（对齐 TESTER/强复审 `r2i6_mysql.py` 口径）
- 交付物：本报告 + 回执 `receipts/TASK-08/attempt-1.md`（REVIEW_PENDING）
- 业务代码改动：**0**（`git status` 仅未跟踪 `.venv` 软链；HEAD=base）——按派单"不改业务代码，失败记录回派"

---

## 结论（先说重点）

**全链路联调与故障/兼容主链在真实 MySQL 8.4.11 下通过；但在"全量 pytest 真 MySQL 隔离库"口径下暴露 10 个测试文件 / 两类真实根因（SQLite 全绿遮坑），其中一类正是 06B 已修缺陷3 的同型问题在 bag_cleanup/source/pipeline/clone 域的未覆盖残留。** 这些是 TASK-08 应报告的"旧流程回归 + 故障并发"缺口，非本单引入，需协调者回派最小修复。

## A. 全链路联调（接收→调度→结果回报）：PASS

- **迁移链**：真 MySQL `alembic upgrade head` RC=0（31 表 + `alembic_version=20261009_02_ingest_frozen`，单头核实）；`downgrade -1 → upgrade head` 回滚链 RC=0。
- **05 消费链空跑**：`poll_and_consume_purpose_events` 真 MySQL 无 outbox 行时全零统计（consumed/dropped/pending/created_runs/reused_runs=0、errors 空、affected_run_ids 空），**无副作用**——契约"03B outbox 未合入时返回全零"在真 MySQL 成立。
- **场景核心文件真 MySQL（FK-off 隔离）**：`test_scene_result_report.py` **35 passed**、`test_scene_result_storage.py` **25 passed**、`test_scene_slice_scheduling.py` 33/36（3 failed=I-1 范围，见 D）、05↔03B outbox e2e 已在 TESTER attempt-1 真 MySQL/SQLite 双核 PASS 6/6（证据不失效）。
- 三用途/配置冻结/子包不递归：对应 AC 的核心断言文件全绿（见 B 文件级）。

## B. 文件级全量真 MySQL 8.4.11（55 PASS / 10 FAIL）

64 个可跑测试文件（skip `test_devflow.py` 沙箱环境性、`test_bag_cleanup_mysql.py`/`test_mysql_operations.py` 独占容器入口）逐文件独立新库跑，**同批文件 SQLite 全绿**（对照 `t08_sqlite_baseline` 10 文件 10 全绿）。红文件与失败数：

| 文件 | 真 MySQL | SQLite | 根因类 |
|---|---|---|---|
| test_bag_cleanup_api.py | 3 failed / 21 passed | 全绿 | C2 |
| test_bag_cleanup_concurrency.py | 1 failed / 10 passed | 全绿 | C2 |
| test_bag_cleanup_worker.py | 4 failed / 15 passed | 全绿 | C2 |
| test_clone_published_dataset_records.py | 1 failed / 1 passed | 全绿 | C2 |
| test_source_register_purpose.py | 2 failed / 6 passed | 全绿 | C2 |
| test_pipeline_api.py | 1 failed / 24 passed | 全绿 | C2 |
| test_lineage_lifecycle.py | 2 failed / 1 passed | 全绿 | C1 |
| test_web.py | 1 failed / 40 passed | 全绿 | C1 |
| test_scene_slice_lineage.py | 10 errors / 1 passed | 全绿 | C3 |
| test_scene_slice_scheduling.py | 3 failed / 33 passed | 全绿 | C3(=I-1) |

## C. 两类真实根因（SQLite 全绿遮坑，需回派）

### C1 — DATETIME(0) 秒精度截断 vs 内存微秒值比较（4 文件：lineage_lifecycle / web / pipeline_api / 06B已修的对照）
- 现象：`assert '2026-10-11T16:15:53.438020' == '2026-10-11T16:15:53'`（`deleted_at`/时间字段回读比较）；`test_web.py::test_bag_time_filter_supports_second_precision` 秒边界过滤断言。
- 机制：`app/clock.py now()` 产微秒 `datetime`；模型 `DateTime`（如 `source_copy.deleted_at`、`pipeline_run`/`bag_record` 时间列）落 MySQL 为 `DATETIME(0)` 截断整秒，读回与内存微秒值 `isoformat()` 不等，或秒边界过滤语义偏移。SQLite 无列宽/精度约束，静默全绿。
- 这正是 06B 缺陷3/M-1（`5c854ea`/`4e2158e`）在 06B 回报 reconcile 域已修的**同型问题**，但 `source_service`（`deleted_at`）/web 时间过滤/pipeline 时间断言**未覆盖**。

### C2 — 乐观并发/重试 UPDATE 命中 0 行 → `StaleDataError`（5 文件：bag_cleanup_api / _concurrency / _worker / clone / source_register_purpose / pipeline_api 部分）
- 现象：`StaleDataError: UPDATE statement on table 'bag_cleanup_operation' expected to update 1 row(s); 0 were matched.`（`pipeline_run` / `bag_record` 同型）
- 机制：claim/重试/幂等流程用带 `updated_at`（微秒 `now()`）或秒级时间戳做 WHERE 条件二次 UPDATE；MySQL 落 `DATETIME(0)` 后整秒，二次同值 UPDATE 匹配 0 行 → SQLAlchemy `check_rowcount` 抛 StaleDataError。SQLite 保微秒故全绿。与 06B 缺陷3（reconcile 幂等二次 UPDATE）同根因家族。
- 注：`test_pipeline_api.py` 唯一失败 `test_scanner_input_unstable_stops_queued_pipeline` 为 C1/C2 的连带（`order_by(created_at.desc())` 秒精度并列取到不同 run_id），非独立新根因。

### C3 — 测试夹具 `bag_uid` 超 VARCHAR(26) → MySQL strict 1406（2 文件：scene_slice_scheduling / scene_slice_lineage）
- `test_scene_slice_scheduling.py` 3 failed = **I-1 精确范围**（T05 前缀 28 字符 uid）。**已用 I-1 的 `6823f2d`（wt-01-i1）真 MySQL 复测 = 36 passed 全绿**，确认 I-1 修复有效且止于该文件。
- `test_scene_slice_lineage.py` 10 errors = **I-1 未覆盖的新同型**：该文件 `BAG_PREFIX="T02"`，`parent_uid=child_uid="T02"+24hex=27 字符`（`tests/test_scene_slice_lineage.py:74-75`），真 MySQL strict 下 setup 1406 拒插。I-1 派单明确"不处理 T06 等其他前缀族"，故 lineage 属新缺口。

## D. I-1 回归验证项（派单要求）

- I-1（`i1-fixture-uid-dispatch.md`，1号 `6823f2d` @ `scene/task-05-i1-fixture-uid`）ACK 时（15:31）**未合入 main**（HEAD 仍 `62a85bf`）。
- 本单已按派单口径执行：以 I-1 交付 commit `6823f2d` 在独立 worktree `wt-01-i1` 真 MySQL 8.4.11 隔离库跑 `tests/test_scene_slice_scheduling.py` = **36 passed 0 failed（RC=0）**，**文件级全绿确认 I-1 修复有效**。
- I-1 合入 main 后，TASK-08 base `62a85bf` 的 `test_scene_slice_scheduling.py` 3 failed（C3）将消失；`test_scene_slice_lineage.py`（C3 新同型）**不因 I-1 合入而解决**，仍需独立修复。

## E. 越界申报 / 未执行项

- **零业务代码改动**（`git status` 仅 `.venv` 软链；HEAD=base `62a85bf`）；C1/C2/C3 均为**发现+定位+最小复现**，未自行修复（派单边界）。
- 未跑十万/百万压测（派单边界：小规模 SQL/索引/查询检查）；`test_bag_cleanup_mysql.py`/`test_mysql_operations.py` 走独占容器验收入口（skip，非本单口径）；`test_devflow.py` 沙箱环境性（skip，与 main 基线同集）。
- **生产/真实样本（TASK-09/10/11）未触发**（独立门禁，不在本单）。
- 真实坡道样本/VLM 核验不在 P0 联调范围。

## F. 建议回派（供协调者裁决，本单不擅自扩做）

1. **C3-lineage**（新，优先，最小）：`tests/test_scene_slice_lineage.py:74-75` uid 收敛 ≤26（同 I-1 `6823f2d` hex 口径 + 长度 assert）。owner 建议 1号（05/夹具域，I-1 连续）。
2. **C2**（同根因家族第二轮）：bag_cleanup/source/pipeline/clone 域乐观并发/重试 UPDATE 的 `updated_at` 秒精度 no-op 匹配问题——06B 缺陷3 已在回报域修（`5c854ea`），需协调者裁定是否扩展同源到清理/来源域（涉 app 行为面，超出 I-1/夹具最小单，建议独立单 + 真 MySQL A/B 复现）。
3. **C1**（同型）：`source_service.deleted_at` / web 秒边界时间过滤 / pipeline 时间断言的 DATETIME(0) 微秒比较，与 C2 同根因（微秒 now() 入秒列），可合并为"秒精度时间戳"专项最小修复。

> 回派前请协调者确认 C1/C2 是否为**既有 SQLite 遮坑**（非 06 聚合 DONE 后新引入）——本单证据显示 06B 核心文件（`test_scene_result_report.py` 35/35、`test_scene_result_storage.py` 25/25）真 MySQL 全绿，C1/C2 集中在 bag_cleanup/source/pipeline/clone 的**旧流程**路径，符合 TASK-08 "旧流程回归/故障并发" 报告目标，非 06 收口缺口。

## 证据

- 全量文件级真 MySQL：`~/.hermes/cache/scratch/t08-e2e/fkoff/allfiles_summary.txt` + `allfiles/af_*.log`（55 PASS/10 FAIL 逐文件）
- 根因隔离：`fkoff/isol2_*.log`（独立新库，排除共享库污染）+ `sqlite_*.log`（对照全绿）
- 迁移/回滚：`t08-e2e/migrate-up.log`、`migrate-down1.log`、`migrate-up2.log`（RC=0，alembic_version 核实 31 表）
- I-1 真 MySQL 复测：`fkoff/i1_scheduling.log`（36 passed RC=0 @ `6823f2d`）
- 05 消费链空跑：`fkoff/t08_chain_probe` 输出（全零无副作用）
- 隔离库 0 残留：`t08_cleanup.py` 输出（drop 全部 t08* 库 + drop `t08` 用户，after dbs=[] user=0）
- 复现脚本（scratch，不进仓库）：`t08_mysql_e2e.py` / `t08_fkoff4.py` / `t08_isolate2.py` / `t08_allfiles.py` / `t08_i1check.py`