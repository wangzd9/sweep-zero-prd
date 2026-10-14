# R2 终测 attempt-2：S1 复测 + 夹具三用例真 MySQL（main 0f6aa87）

- 派单：`inbox/TESTER/TASK-06/r2-final-mysql-e2e.md`（协调者 17:15 下达；attempt-1 17:18 ACK / 18:16 交付 6 PASS/1 FAIL）
- 本次范围（= attempt-1 FAIL 项复测 + 明确归 TESTER 的复测项）：
  - S1 R2-01 迁移链（attempt-1 FAIL 高）三 AC：AC1 全新库 upgrade head / AC2 已有库增量 / AC3 幂等
  - 仓库不变式套件 40 用例真 MySQL（含 attempt-1 缺陷2 指认的 3 个夹具 FAIL 用例）
- 被测快照：`main 0f6aa87`（`git rev-parse --short=7 HEAD`=0f6aa87，`git status` 迁移目录+两测试文件 CLEAN，核对一致）
  - 相对 attempt-1 被测 `74ba3bf` 的增量：`c2dbe91`（2号 fixture `6ee858b`：`tests/test_scene_result_report.py::_parent` uid hex12→hex10 + `assert len<=26`）+ `ceeac16`/`0f6aa87`（1号 S1 `attempt-6-rework`：迁移 revision `20261009_02_ingest_frozen_columns`(33) 改短为 `20261009_02_ingest_frozen`(25) + 链宽度/一致性回归；`git diff c2dbe91..0f6aa87`=2 文件 +58/-2，零 app 代码面）
- 结论：**S1 三 AC 全 PASS（迁移 1406 阻塞已解除）；夹具 3 用例 2 转 PASS、1（reconcile 幂等二次）仍 FAIL——该 FAIL 经探针证实与 UID 宽度无关，系 06B reconcile 幂等重放路径在 MySQL 下的真实缺陷（attempt-1 对其归因为"child uid 截断"系误诊，见 §纠正）**。本单 TEST_REPORT_PENDING。

## 环境（真实 MySQL 口径，SQLite 未替代）

- MySQL **8.4.11**（`mysql:8.4` 镜像 `6ea90827b110`，容器 `tester-r2-mysql`，独立网络 `tester-r2net2` 172.22.0.2:3306、宿主 33070；默认 sql_mode，与 attempt-1 口径一致）。**跑完随容器销毁，0 残留（本轮已执行清理核实）**
- S1 隔离库：`t_s1fresh`（AC1 全新库）、`t_s1exist`（AC2 已有库增量）、`t_r2app3`（不变式套件）
- 驱动链：`pymysql 1.1.1 / SQLAlchemy 2.0.41 / alembic 1.16.4`（主仓 `.venv`）；caching_sha2 走 SSL 连接（机制不影响服务端 DDL/SQL 证据）
- 迁移执行：标准 `alembic upgrade` CLI（仓库 `alembic/env.py` + `DATABASE_URL`），未改仓库任何文件
- 不变式套件：`pytest tests/test_scene_result_report.py tests/test_scene_r2_rework_1.py` 绑定真实 MySQL（自写插件 `tester_r2_mysql`：creator 引擎 + 会话级 `FOREIGN_KEY_CHECKS=0`——仅用于仓库 `_purge` 拆除顺序兼容，应用写路径仍走真实 InnoDB 约束）

## S1 复测：R2-01 迁移链（attempt-1 FAIL → **attempt-2 PASS**）

真实 MySQL 8.4.11，脚本 `tester_r2_a2_s1.py`，证据 `tester_r2_a2_s1.log`（每阶段独立建库、跑完销毁）：

| AC | 命令 | RC | 结果 |
|----|------|----|------|
| AC1 全新库 | `t_s1fresh`（空库）`alembic upgrade head` | 0 | `current`=`20261009_02_ingest_frozen`（head，25 字符）落 `version_num` varchar(32)，**无 1406** |
| AC2 已有库增量 | `t_s1exist` `upgrade 20261009_01`（RC=0，停 `20261009_01_scene_identity_key`）→ `upgrade head` | 0/0 | 停步→head，`final`=`20261009_02_ingest_frozen`，**无 1406**（attempt-1 正是此步中断） |
| AC3 幂等 | `t_a2_wide` `upgrade 20261009_01` 后先 `ALTER alembic_version MODIFY version_num VARCHAR(255)`（模拟已加宽库）→ `upgrade head` | 0/0 | 改短 revision 不触碰 `alembic_version` 结构，已加宽库再 upgrade head 不报错，`final`=head |

- R2-01 原目标复核（`t_s1exist` 终态 `SHOW CREATE TABLE`）：`ingest_profile` 三 TEXT 列 + `ingest_submission.selection_json` 均 `text NOT NULL`（**无 DEFAULT 子句**），`version_num` 已含新 25 字符 head → 去 TEXT server_default 防 1101 + 链尾不越宽，两者在真实 MySQL 均成立。
- 影响面收敛：attempt-1 指认"任何 MySQL 库从 20261009_01 upgrade head 必 1406"已被 S1 三 AC 全 PASS 推翻——**06 聚合唯一高阻塞（迁移链）解除**。

## 仓库不变式套件（真实 MySQL 8.4.11，t_r2app3）：40 用例 = **39 PASS / 1 FAIL**

attempt-1 = 37 PASS / 3 FAIL；本次 3 个原 FAIL 中 **2 转 PASS、1 仍 FAIL**：

1. `test_identity_gates` — **PASS**（attempt-1 FAIL：`_parent("gate-other")` 27 字符 uid 1406 → fixture `6ee858b` 收敛 hex10 + assert 后转绿）。
2. `test_multi_scene_run_partial_complete_does_not_deadlock` — **PASS**（attempt-1 FAIL：`_parent("multi-scene")` 28 字符 uid 1406 → 同上转绿）。B8a 核心不变式（部分场景 complete 不 finish、末场景切 current）真 MySQL 成立。
3. `test_reconcile_backfills_after_publish_without_report` — **FAIL**（见 §纠正：非 UID 宽度，为 06B reconcile 幂等重放真实缺陷）。

## §纠正：attempt-1 缺陷2 对 reconcile 用例的归因有误

attempt-1 §仓库不变式套件总账第 3 项将该 FAIL 归因："`_child_uid()` 27 字符 uid 被 MySQL 截断为 26 后落库，二次调用 ORM 按内存 27 字符值更新 0 行——非应用缺陷，为夹具口径问题"。

**本轮 fixture `6ee858b` 已合入（uid 收敛 + assert），该用例仍 FAIL，且经独立探针证实原归因不成立：**
- 实测该用例 child uid = `T06Bc-` + 19 hex = **22 字符**（`<26`，`assert len<=26` 通过）；parent uid = `T06Brec-` + 10 hex = **18 字符**。无越宽、无截断。
- 最小复现（单用例、单全新库 `t_dbg5`、`with TestClient(app)` 触发 app lifespan = pytest 行为）：reconcile 1 返回 200（补登记 + 子包推进 AVAILABLE）；**reconcile 2（幂等二次）在 `scene_result_report_service.py:928 db.commit()` 抛 `StaleDataError: UPDATE statement on table 'bag_record' expected to update 1 row(s); 0 were matched`**，失败语句 echo 原文 = `UPDATE bag_record SET updated_at=... WHERE bag_record.id = 2`（param `bag_record_id=2`）。
- **关键探针（区分 ORM id 错配 vs DB 行不可见）**：reconcile 2 异常后，用**全新 root 连接** `SELECT id,bag_uid,availability,row_version FROM bag_record WHERE bag_role='SCENE_SLICE'` → 行**确实存在**（`id=2, T06Bc-..., AVAILABLE, row_version=1`）；同连接直接 `UPDATE bag_record SET updated_at=NOW() WHERE id=2` → **affected rows = 1**。即：DB 行在、可更新，但 app ORM 会话内同语句（同 id=2）匹配 0 行。
- 定性：**06B reconcile 幂等重放路径在 MySQL 下的真实 app 层缺陷**（违反既定 AC"再次 reconcile 不重复登记 / 幂等重放应收敛成功"），与测试夹具 UID 宽度无关。SQLite 全绿遮坑（与 attempt-1 R2-02 同类）。**我 attempt-1 将该用例归为"夹具口径问题、非应用缺陷"系误诊，予以更正**；回派口径应从"改测试夹具"改为"回派 06B owner 根因 app reconcile 幂等重放路径"。

## 缺陷/回派建议（供协调者裁决）

- **缺陷3（新，中，06B app 代码面）**：`test_reconcile_backfills_after_publish_without_report` 幂等二次 reconcile 在 MySQL 下 `StaleDataError`（`_mark_children_available`/`register_manifest` 重放路径 commit 时 `UPDATE bag_record ... WHERE id=2` 匹配 0 行，而探针证实该行存在且新连接可更新）。建议回派 **2号**（06B app owner）根因：reconcile-2 重放事务内子包 ORM 对象的 flush 谓词/身份与 DB 实际行不一致（疑似 `expire_all`/`begin_nested` 重查后主键身份或版本状态在 MySQL InnoDB 下未对齐；SQLite 不暴露）。最小复现 + 探针 + echo 原文见下证据索引。**该项阻塞 06 聚合不变式套件 40/40，是 attempt-2 唯一残留 FAIL**。
- S1（迁移链）已随 `ceeac16`/`0f6aa87` 解除，无需再派。
- 观察（沿用 attempt-1，信息不派单）：`_scene_row` 并发首建 1062 低概率竞态边缘，与本次七场景无因果。

## 影响 AC / 门禁

- S1 复测三 AC **PASS** → 06 聚合"迁移链 MySQL"高阻塞**解除**；03 聚合（03B）MySQL 路径验收缺口随本项收口。
- 不变式套件 **39/40**：残留 1 FAIL（缺陷3）为 06B app 代码面幂等重放，**06 聚合放行业务门禁仍不通过**（需缺陷3 修复 + 本用例真 MySQL 复测 PASS）。
- 强模型增量复审（R2-01/02/03 必附 MySQL 结果）前置：缺陷3 未收口前，reconcile 幂等重放属 R2-04/06 一致性面，建议纳入复审范围。

## 清理（本轮已执行核实）

- S1 隔离库 `t_s1fresh/t_s1exist/t_r2app3` + 调试库 `t_dbg1~t_dbg5` 全 `DROP`；容器 `tester-r2-mysql` `docker rm -f`、网络 `tester-r2net2` 删除——`docker ps -a --filter name=tester-r2-mysql` 与 `docker network ls --filter name=tester-r2net2` 均空，**0 残留**。
- 未改仓库任何业务文件；测试材料（插件/探针/脚本/日志）在 `~/.hermes/cache/scratch/`（`tester_r2_a2_*` 前缀 + `tester_r2_mysql.py`）。

## 证据索引（~/.hermes/cache/scratch/）

- `tester_r2_a2_s1.py` / `tester_r2_a2_s1.log`（S1 三 AC 全命令 + RC + current + `SHOW CREATE TABLE` TEXT 列摘录；OVERALL PASS）
- `tester_r2_a2_run.sh` / `tester_r2_a2_suite.log`（不变式套件 40 用例总账 39 PASS/1 FAIL，t_r2app3）
- `tester_r2_a2_single_tb.sh` / `tester_r2_a2_single_tb.log`（reconcile 单用例全新库最小复现，`--tb=short`：`test:899 → service:928 → StaleDataError`）
- `tester_r2_a2_t5_run.sh` / `tester_r2_a2_t5_echo.log`（pytest + app lifespan + SQL echo：INSERT child id=2 / reconcile-1 多字段 UPDATE id=2 / reconcile-2 `UPDATE bag_record SET updated_at WHERE id=2`）
- `tester_r2_a2_dbg_reconcile2.py`（探针版复现：reconcile-2 异常后新连接 `SELECT` 证实行存在 + 直接 `UPDATE WHERE id=2` affected rows=1）
- `tester_r2_mysql.py`（MySQL 绑定插件：creator SSL 引擎 + FK 拆除兼容说明）
- 建库/清理脚本：`tester_r2_a2_mkt_db{3,4,5}.py` / `tester_r2_a2_cleanup.py`