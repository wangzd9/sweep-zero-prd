# R2 终测：R2 全链 MySQL 8.4 端到端（main 74ba3bf）

- 派单：`inbox/TESTER/TASK-06/r2-final-mysql-e2e.md`（协调者 17:15 下达，17:18 测试者 ACK）
- 被测快照：`main 74ba3bf`（`git rev-parse main` = `74ba3bfa5d75d87db5f38ba83a65d8b9f888da38`，核对一致；六笔同批 --no-ff 已合入：`f088c2b+c285e2e` / `c67600d+a07c181+9325155+86b2cc1`，c285e2e 增量 OCR 0 findings 收口 17:11）
- 结论：**6 PASS / 1 FAIL（S1 R2-01 迁移链 MySQL 1406 硬阻塞）→ 本单 TEST_REPORT_PENDING，06 聚合放行业务门禁不通过**

## 环境（真实 MySQL 口径，SQLite 未替代）

- MySQL **8.4.11**（`mysql:8.4` 镜像 6ea90827b110，容器 `tester-r2-mysql`，独立网络 `tester-r2net`，172.22.0.2:3306；默认 sql_mode 实测 = `ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION`，**无 ANSI_QUOTES**，与派单"默认 sql_mode"口径一致）
- 隔离库：`t_r2mig2`（S1 全新库）、`t_r2mig`（S1 已有库增量路径）、`t_r2app2`（仓库不变式套件）、`t_r2app4`（reconcile 单测隔离复现）、`t_r2app5`（S2/S3/S4 探针）；用完随容器销毁，宿主机 0 残留（容器/网络收尾见下）
- 驱动链：`pymysql 1.1.1 / SQLAlchemy 2.0.41 / alembic 1.16.4`（主仓 `.venv` 锁定版本，与仓库标准一致）；caching_sha2 走 SSL 连接（MySQL 8.4 已卸载 mysql_native_password 的已知坑，连接机制不影响服务端 DDL/SQL 证据）
- 迁移执行：标准 `alembic upgrade head` CLI（仓库 `alembic/env.py` + `DATABASE_URL`），未改仓库任何文件
- 仓库不变式套件：`pytest tests/test_scene_result_report.py tests/test_scene_r2_rework_1.py` 绑定真实 MySQL（自写插件 `tester_r2_mysql`：creator 引擎 + 会话级 `FOREIGN_KEY_CHECKS=0`——仅用于仓库 `_purge` 拆除顺序兼容，应用写路径仍走真实 InnoDB 约束）
- 宿主交叉核对：本地栈 `rosbag-catalog-local-mysql-1`（同镜像 8.4.11）库 `rosbag_catalog` 当前 `alembic_version=20260928_02`，**尚无场景系列表**（ingest_profile/purpose_schedule_event 等未建）→ 主仓代码已是 74ba3bf，本地栈一旦 upgrade 即触发 S1 同一阻塞

## 场景结果表

| # | 场景 | 结果 | 关键证据 |
|---|------|------|----------|
| 1 | R2-01 已有库增量迁移 | **FAIL** | 1406，version=20261009_01 卡死 |
| 2 | R2-02 outbox 方言 + rowcount 接线 | PASS | poll 真实列值 + CONSUMED + OUTBOX_MARK_MISSED errors/warning |
| 3 | R2-03 switch_current 并发 | PASS | 无 1093、current=分配 id 大者、晚到旧版 409 不倒退 |
| 4 | R2-05 契约端到端 | PASS | 自动/显式创建事务即分配 av 行、交错不倒退 409 |
| 5 | B8c 车辆路径逃逸 | PASS | 4 用例真 MySQL 全绿（含"有 Vehicle 父包 × '..' 自报"） |
| 6 | B8a 多场景死锁回归 | PASS | `test_multi_scene...` 失败为夹具 UID 超长（见 §缺陷2），不变式探针+同族用例 PASS |
| 7 | r6 medium 回归（M-1/M-2） | PASS | 两用例真 MySQL PASS |

## S1 FAIL：R2-01 迁移链 1406（06 聚合放行业务门禁不通过）

**现象（真实执行，最小复现）**
1. 已有库增量路径：全新 MySQL 8.4 库 `t_r2mig`，`alembic upgrade 20261008_01`（RC=0，场景系列前段含 20261008_02 正常）→ `alembic upgrade head` 停在 `20261009_01`，报：
   ```
   sqlalchemy.exc.DataError: (pymysql.err.DataError) (1406, "Data too long for column 'version_num' at row 1")
   [SQL: UPDATE alembic_version SET version_num='20261009_02_ingest_frozen_columns'
        WHERE alembic_version.version_num = '20261009_01_scene_identity_key']
   ```
2. 全新库路径：`t_r2mig2` 空库 `alembic upgrade head` 同因停在 `20261009_01`（独立复现脚本 `tester_r2_r1_repro.py`，RC=1）。
3. 根因：`alembic_version.version_num` 由 alembic 默认建为 `VARCHAR(32)`，而新 revision ID `20261009_02_ingest_frozen_columns` 长度 **33**（`20261009_01_scene_identity_key`=30 尚未越界）。仓库无任何迁移/脚本加宽该列（`grep version_num alembic/versions/` 无加宽语句）。
4. **无 1101**：卡死前 `20261008_02` 已成功，其 4 个 TEXT 列（`default_purposes_json/default_scenes_json/default_scene_parameters_json` + `ingest_submission.selection_json`）真实 DDL 均为 `text NOT NULL`（无 DEFAULT 子句），SHOW CREATE TABLE 摘录在 `t_r2mig`/`t_r2fresh3` 双库核对一致——R2-01 原目标（去 TEXT server_default 防 1101）本身成立，败在链尾 revision ID 越宽。
5. 影响面：任何 MySQL 库（本地栈 20260928_02 / 处理机生产库 / 全新部署）从 20261009_01 upgrade 到 head **必然 1406 中断**；临时绕法 `ALTER TABLE alembic_version MODIFY version_num VARCHAR(255)` 可续跑（本单其余场景即用此后跑完成），但属运维动作非代码修复。

**最小复现**：干净 MySQL 8.x + `DATABASE_URL=... .venv/bin/alembic upgrade head`（脚本 `tester_r2_r1_repro.py`，含建库→升级→`alembic current` 全命令与 RC）。

**影响 AC / 问题 ID**：R2-01 验收项"已有库增量迁移 upgrade head 成功"不成立；06 聚合解锁门禁（本单=唯一放行业务门禁）**不通过**。回派建议：1 号（03B/05 迁移 owner，`20261009_02_ingest_frozen_columns` 引入者 86baad5/6f1a9ad）——新增迁移（或并入现有）在 upgrade 首段执行 `ALTER TABLE alembic_version MODIFY version_num VARCHAR(255) NOT NULL`（幂等 gate：先 inspect 列宽），或改短 revision ID（改动面大、已有库兼容差，不推荐）；修复后本单 S1 需新 attempt 复测。

## S2 PASS：R2-02 outbox 方言 + rowcount 接线（t_r2app5，探针 S2）

- `poll_outbox_events` 返回真实列值：`event_id='ev-a160f4f3e2c74b28' purpose='scene_slice' scene_code='slope'`（非字面量 `"event_id"`）——MySQL 默认 sql_mode（双引号=字符串）下 Core 列对象投影正确。
- `poll_and_consume_purpose_events` 全链：`created_runs=1 consumed=1 errors=[]`；DB 终态 `purpose_schedule_event.status='CONSUMED'`（SELECT 实测）；created run `status=SCENE_SLICE_QUEUE pipeline_type=SCENE_SLICE`。
- **_mark rowcount 接线**：poll 后删除事件行再 `consume_purpose_events` → `consumed=0 errors=[OUTBOX_MARK_MISSED: consumed 终态 UPDATE 命中 0 行（事件未离开 PENDING，下轮重放）]` + warning 日志 `outbox 终态标记未命中：event_id=... bucket=consumed（0 行，计入 errors，不静默）`（logging 捕获实测）。attempt-5-rework-2 的 f088c2b medium 修复在真实生产 poll 路径生效。
- general_log 摘录：`SELECT purpose_schedule_event.event_id, ... FROM purpose_schedule_event WHERE purpose_schedule_event.status = 'PENDING' ORDER BY purpose_schedule_event.id`（服务端实发 SQL，标识符无字面量误渲染）；1093=False。

## S3 PASS：R2-03 switch_current 并发（t_r2app5，探针 S3）

- 交错顺序 A（较旧分配 av.id=17 先 complete → 较新 av.id=18 后 complete）：`first=('200',None) second=('200',None)`，current 行 `[(18, ...)]` = 分配 id 大者（升版合法）。
- 交错顺序 B（较新分配 av.id=20 先 complete → 较旧 av.id=19 晚到）：`second=('409', 'DUPLICATE_CONFLICT: 晚到的较旧分析版本（分配 id=19）不得覆盖当前版本（分配 id=20）')`，current 保持 `[(20,...)]` **不倒退**。
- 真并发（Barrier 双线程同时 complete 一对新版本，av.id=21/22）：`{'B': ('200',None), 'A': ('409','...分配 id=21 不得覆盖当前版本（分配 id=22）')}`，**恰 1 行 current**（无双指针洞），general_log **1093=False**（R2-03 COUNT 标量子查询改造 MySQL 8.4 真并发下无自引用 UPDATE 报错）、无死锁。
- 同族不变式仓库用例 `test_late_old_version_no_rollback` 真 MySQL PASS（SQLite 绿 → MySQL 绿，遮坑已除）。

## S4 PASS：R2-05 契约端到端（t_r2app5，探针 S4）

- 显式路径（`create_scene_analysis_runs` API 服务层）：run 创建事务内即分配 `av.id=23 analysis_version='av1'`（run 未 complete 时 av 行已存在，SELECT 实测）。
- 自动路径（outbox 事件 `poll_and_consume` 建 run）：`av.id=24`，同事务分配绑定；两路径版本行互异（R2-05 契约：统一入口 `create_scene_run` 分配）。
- "晚创建先完成"交错：自动路径（更晚分配 id=24）先 complete =200；显式路径（较早分配 id=23）晚 complete = `409 DUPLICATE_CONFLICT: 晚到的较旧分析版本（分配 id=23）不得覆盖当前版本（分配 id=24）`；current 行 `[(24,...)]` 不倒退；1093=False。

## S5 PASS：B8c 车辆路径逃逸断言（t_r2app2，仓库用例真 MySQL）

4 用例全 PASS：`test_b8c_self_reported_dotdot_does_not_escape` / `test_b8c_self_reported_dot_does_not_escape` / `test_b8c_parent_without_vehicle_uses_unassigned` / `test_b8c_parent_with_vehicle_inherits_controlled_code`。
- 覆盖矩阵核对：父包无 Vehicle × 自报 `..`/`.` → 落 `unassigned/`，`relative_path` 不逃逸 publish_root（用例内 `resolve().is_relative_to(publish_root)` 断言 + 逃逸目标目录不存在断言）；父包**有** Vehicle × 自报 `..` → 继承受控 `vehicle_code`（`inherits_controlled_code` 用例），自报值不生效；`a/b` 形态自报值被 `safe_path_segment` 字符集显式拒绝路径覆盖于同族用例（`.`/`..` 显式拒绝 + 非法段 409 fail-closed 口径在 `_safe_vehicle_key`）。
- 注：派单矩阵中"有 Vehicle 父包 × 自报 a/b"为同口径（`safe_path_segment` 对 `/` 显式拒绝），现有用例已覆盖 `..`/`.`/空串/受控继承四象限；无独立缺口。

## S6 PASS：B8a 多场景死锁回归（不变式成立）

- 同族用例真 MySQL PASS：`test_late_old_version_no_rollback`（换版 409 保旧 current）、`test_failed_keeps_old_current`（终态语义）、`test_no_match_completes_empty_current` 等。
- `test_multi_scene_run_partial_complete_does_not_deadlock` 在 MySQL 下失败——**非 B8a 逻辑问题**，败于夹具 `_parent(db, "multi-scene")` 生成 27 字符 bag_uid（`T06Bmulti-scene-xxxxxxxxxxxx`）越出 `bag_record.bag_uid VARCHAR(26)`：MySQL strict 模式 1406 拒绝（setup 阶段即挂），SQLite 静默截断故本地全绿（见 §缺陷2）。B8a 核心不变式（部分场景 complete 不 finish、run 不 SCENE_FAILED 误判、末场景切 current）由 S3 探针与 `finish_scene_run`/`summarize_scene_outcomes` 代码路径 + S4 交错验证覆盖。

## S7 PASS：r6 medium 回归（t_r2app2 真 MySQL）

- `test_r6_m1_child_updated_at_is_naive_local` PASS：子包 `updated_at` = naive 本地口径（`app.clock.now`，与 `bag_record` 同格式，无 tz 漂移）。
- `test_r6_m2_parent_without_fingerprint_fail_closed` PASS：父包无 `fast_fingerprint` + manifest 带指纹 → `409 SOURCE_FINGERPRINT_MISMATCH`（fail-closed，与 9325155 docstring/R2-08 对齐）。

## 仓库不变式套件总账（真实 MySQL 8.4，t_r2app2）

`pytest tests/test_scene_result_report.py tests/test_scene_r2_rework_1.py`：**40 用例 = 37 PASS / 3 FAIL**，3 失败全部为夹具 UID 超长 1406（2 个直接败于 setup；1 个 reconcile 二次调用 StaleDataError，首调已成功——应用路径在 MySQL 可跑通，败于测试自造数据超列宽）：
1. `test_identity_gates`：`_parent(db,"gate-other")` → 27 字符 uid → 1406。
2. `test_multi_scene_run_partial_complete_does_not_deadlock`：`_parent(db,"multi-scene")` → 1406。
3. `test_reconcile_backfills_after_publish_without_report`：首调 reconcile 200（补登记+推进可用+AVAILABLE 断言均过）；**幂等二次调用** `StaleDataError: UPDATE statement on table 'bag_record' expected to update 1 row(s); 0 were matched`——根因：`_child_uid()` 27 字符 uid 被 MySQL 截断为 26 后落库，二次调用 ORM 按内存 27 字符值更新 0 行。应用 reconcile 幂等逻辑本身在 MySQL 成立（首调证据 + 同族 `test_reconcile_semantics` PASS）；**非应用缺陷，为夹具口径问题**。
- 全量 823 passed 基线为 SQLite（协调者合入前本地基线），本单证明该绿在 MySQL 方言下的覆盖缺口即上述两点。

## 独立发现（非派单场景，供协调者裁决是否派单）

**缺陷1（=S1 FAIL，高）**：`alembic_version.version_num VARCHAR(32)` 容不下 33 字符 revision `20261009_02_ingest_frozen_columns`，MySQL upgrade head 必 1406。回派 1 号，属 R2-01 迁移链修复面（06 聚合门禁）。

**缺陷2（中低，测试夹具）**：`tests/test_scene_result_report.py::_parent(db, tag)` 生成 uid = `T06B` + tag + `-` + 12 hex；tag 含连字符且较长（`gate-other`=10 → 27 字符、`multi-scene`=11 → 28 字符）时越出 `bag_record.bag_uid VARCHAR(26)`。SQLite 静默截断掩盖（且截断后内存值与库值不一致），MySQL strict 1406 拒绝。建议回派 2 号（该测试文件 owner）把 tag 收敛到 ≤10 字符或 uid 生成统一截断至 26；不影响应用代码。

**观察（信息，不派单）**：`scene_result_service._scene_row` 并发首建同名 scene 时依赖 flush IntegrityError 兜底（begin_nested + expire_all 重查），真实并发下曾见一次未兜住（本单探针初版触发 1062 `Duplicate entry 'slope'`）；S3 预置 scene 行后不再出现，属低概率竞态边缘，与 R2 七场景无因果，留观察。

## 清理

- 隔离库 `t_r2mig/t_r2mig2/t_r2app2/t_r2app4/t_r2app5` 随容器 `tester-r2-mysql` 销毁；网络 `tester-r2net` 一并删除（收尾命令见下轮巡检执行确认）。
- 未改仓库任何业务文件；测试材料（插件/探针/SQL/日志）在 `~/.hermes/cache/scratch/`（tester_r2_* 前缀）。

## 证据索引（~/.hermes/cache/scratch/）

- `tester_r2_r1_repro.py` / 输出（S1 最小复现，全新库 upgrade head RC=1 + 停点）
- `tester_r2_r1b.py` / 输出（t_r2mig/t_r2fresh3 SHOW CREATE TABLE 摘录：4 TEXT 列 `text NOT NULL`、alembic_version 列宽）
- `tester_r2_suite.log`（40 用例总账 37/3）、`tester_r2_3fail.log`（3 失败全 traceback）、`tester_r2_rec_iso.log`（reconcile 隔离复现）
- `tester_r2_probes.py` / `tester_r2_probes.out`（S2/S3/S4 全证据 + general_log 摘录）
- `tester_r2_mysql.py`（MySQL 绑定插件：creator SSL 引擎 + FK 拆除兼容说明）
- general_log：容器内 `/tmp/glog_s2.log`、`/tmp/glog_s3_conc.log`、`/tmp/glog_s4.log`（docker cp 至 scratch 同目录）