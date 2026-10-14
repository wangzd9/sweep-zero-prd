# 回执：TEST-TASK16A-post-merge attempt-1（TASK-16A rebase 链合入后独立验证）

- 时间：2026-10-13 09:32 +08:00（TESTER cron poll 167580c0500b，会话 `cron-tester-poll-167580c0500b-20261013-091953-t16a`）
- 派单：`inbox/TESTER/TASK-16A/t16a-post-merge-verify-dispatch.md`（协调者 r138）；ACK `inbox/TESTER/TASK-16A/t16a-post-merge-verify-ack.md`
- 被测基线：main **`6fb42c4821bc5dfa54531c88fbc0ef1578715748`**（开工前主仓 `/home/wang/work/rosbag-catalog` 实测 `git rev-parse HEAD`=origin/main=`6fb42c4`，checkout 一致；结束核 HEAD 仍 `6fb42c4`，tracked 0 改动）
- 环境（独立取证，不复用 A 回执/协调者机械核验作本单证据）：
  - 真 MySQL 8.4 = 隔离容器 `tester-t16a-mysql`（镜像 `docker.m.daocloud.io/mysql:8.4`，本地缓存 `6ea90827b110`，容器内 `SELECT VERSION()` 实测 **8.4.11**），独立 docker 网络 `tester-t16a-net`，宿主仅 loopback `127.0.0.1:3386` 映射（无公网/无共享栈端口），隔离库 `t16a`（MYSQL_DATABASE 新建空库）；用完即毁
  - 迁移执行：主仓 `.venv`（alembic 1.16.x / SQLAlchemy 2.x / PyMySQL），`DATABASE_URL=mysql+pymysql://…@127.0.0.1:3386/t16a`
  - 探针脚本 `~/.hermes/cache/scratch/tester_t16a_mig_probe.py`，全程日志 `~/.hermes/cache/scratch/tester_t16a_mig.log`（最终 **PROBE RESULT: PASS**）
- 结果：**PASS（3/3 范围项全过）**

## 一、真 MySQL 8.4 全链迁移往返（本单核心）

- fresh 空库 `alembic upgrade head`（链起点 `20260911_01` → `20261013_01_scene_intake`）**RC=0**；`alembic heads` 实测**单头** `20261013_01_scene_intake (head)`（25 字符短名，无 1406 长 revision 截断风险）。
- `alembic downgrade -1` **RC=0** → `alembic_version`=`20261012_01_scene_manual`（精确落到 07B 单头）；两列（`intake_root_id`/`intake_snapshot_json`）SHOW COLUMNS 实测**均已 drop**。
- 再 `alembic upgrade head` **RC=0** → `alembic_version`=`20261013_01_scene_intake`；双列恢复（`varchar(16) NOT NULL DEFAULT 'self_built'` / `text NULL`）。
- `alembic_version` 值序列取证：`20261013_01_scene_intake → 20261012_01_scene_manual → 20261013_01_scene_intake`（探针 `ROUND-TRIP SUMMARY: rc1=0 rc2=0 rc3=0`）。
- 全链（含 07B `20261012_01` 与更早既有迁移）在真 MySQL 8.4.11 一次通，无 1101/1071 类 DDL 方言错误。

## 二、AC-14/08 面（迁移承载字段，MySQL 口径）

- DDL 实测（`SHOW CREATE TABLE ingest_profile`）：`` `intake_root_id` varchar(16) NOT NULL DEFAULT 'self_built' `` + 索引 `` KEY `ix_ingest_profile_root_enabled` (`intake_root_id`,`enabled`) `` 在列（SHOW INDEX 两键实测）；`ingest_submission.intake_snapshot_json` text 可空列在列。
- **历史行回填**（真实路径，无应用层）：downgrade 至 `20261012_01`（列 drop）后 raw SQL 插入 pre-migration 行（`profile_id='tester_t16a_hist'`，无 intake_root_id 列可写）→ upgrade head → 实测该行 `intake_root_id`=`self_built`，且全表 `intake_root_id IS NULL` 计数=**0**；行身份不变（id/profile_id/version 原样）。回填 SQL 幂等口径（只置 NULL 行）成立。探针行事后 DELETE，0 残留。
- 说明：双根同名/跨盘 rename 拒绝、intake 快照绑定、场景异常不回退自建属应用层行为面（A 链 56 测试 + OCR 已闭环范围）；本单按派单口径只取**迁移承载字段**（列存在 + 默认/回填 + 索引）MySQL 证据，未越界重跑应用层语义。

## 三、SQLite 定向不回归（主仓 .venv 独立复跑）

- 16A 面 4 文件：`pytest tests/test_scene_intake_isolation.py tests/test_scanner_stability.py tests/test_ingest_config_api.py tests/test_ingest_config.py -q` → **56 passed, RC=0**（4.62s，口径与 A 回执/协调者复跑一致）。
- 07B 面 3 文件：`pytest tests/test_task07b_manual_revision.py tests/test_task07b_r2_revision.py tests/test_task07b_r3_revision.py -q` → **12 passed, RC=0**（07B 合入后主仓不回归维持）。
- 合计 7 文件 **68 passed, RC=0**（5.57s）。

## 四、已知观察项（按派单口径申报，非 16A 回归）

- `tests/test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time` **单跑失败**（实测复现，0.64s，顺序依赖夹具态）；**全模块口径 `pytest tests/test_web.py -q` = 41 passed（含该用例）RC 面正常**——与协调者 r138 独立二分结论（`502bf8e` 基线即存在、与 16A/07B 无关）一致，按派单「勿判 16A 回归」口径申报，不阻塞。

## 五、清理与残留核

- 容器 `tester-t16a-mysql` `docker rm -f` + 网络 `tester-t16a-net` `docker network rm` 实测完成：`docker ps -a --filter name=tester-t16a` **0 残留**、`docker network ls --filter name=tester-t16a` **0 残留**；宿主 loopback 3386 随容器销毁释放。
- 主仓 `git status` 无 tracked 改动，HEAD 仍 `6fb42c4`——零业务代码改动；测试材料仅在 `~/.hermes/cache/scratch/`。

## 六、结论与未执行项

- **结论：PASS**——TASK-16A rebase 链合入后独立验证（真 MySQL 8.4.11 全链迁移三趟 RC=0 + 单头 + 双列/索引/回填取证 + SQLite 56/12 定向复跑）全部独立取证成立；按派单收口链，PASS 即 16A DONE，请协调者裁决。
- 未执行项：应用层 AC-14/08 语义面（双根同名/跨盘 rename/快照绑定/异常不回退——属 A 链已 OCR 闭环范围，本单口径只取迁移字段）；16B（合入门禁冻结，proxy OCR 4/4 连败待用户裁决）/16C（B 开发中）面不越界；生产启用（TASK-11 门禁仍 **PRODUCTION BLOCKED** 待用户授权）。
- 普通测试 PASS ≠ OCR/强审查/生产门禁通过；16A 链 OCR（v2 14/14 + attempt-2-r1 增量 3 批 + 接线批 0 findings）已由协调者 r138 收口，本回执不覆盖。