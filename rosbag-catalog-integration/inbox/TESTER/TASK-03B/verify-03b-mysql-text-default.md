---
task: TASK-03B
item: verify-03b-mysql-text-default
owner: 测试者
status: ACCEPTED（2026-10-09 20:5x 已执行并交付 TEST_REPORT_PENDING；报告 reviews/TASK-03B/attempt-2/verify-03b-mysql-text-default.md，回执 test-receipts/TEST-03B-mysql-text-default/attempt-1.md，结论=误报迁移完好）
priority: CRITICAL（gate：决定 main b3280c9 的 03B 迁移是否真损坏）
dispatched_by: 协调者
updated: 2026-10-09 16:5x
target: main 的 alembic/versions/20261008_02_ingest_config.py（HEAD b3280c9）
---
# 验证派单（CRITICAL）：03B 迁移 TEXT server_default 在真实 MySQL 8.4 是否产生非法 DDL

## 为什么测这个（强模型审查 + 协调者此前裁决矛盾，必须一锤定音）
强模型审查判 critical：`default_purposes_json/default_scenes_json/default_scene_parameters_json`
三个 sa.Text() 列设了字面量 `server_default="[]"/"{}"`，用当前 SQLAlchemy/MySQL dialect 编译得
`... TEXT NOT NULL DEFAULT '[]'`，而 **MySQL 不允许 TEXT/BLOB 列带 DEFAULT**（应报 1101）。
协调者此前用 general_log 隔离库实测判过"误报（实际 DDL 无 DEFAULT、迁移成功）"，
但该实验在 a8fac99 时期做、未在合入后的 main 版本复核，且强模型独立编译结果与之矛盾。
**结论必须以"当前 main 迁移 + 干净 MySQL 8.4 真实执行路径"为准，不能静态编译、不能凭旧实验。**

## 验证步骤（MySQL 8.4，docker 隔离环境，容器/网络前缀 test-*）
1. 干净 mysql:8.4 容器 + python:3.10-slim 容器**同 docker network**；
   python 容器 `pip install -q -r requirements.txt`（pymysql 锁 1.1.1），挂载 main 工作区
   `-v /home/wang/work/rosbag-catalog:/work -w /work`。
2. **开 general_log**：`SET GLOBAL general_log=1; SET GLOBAL general_log_file='/tmp/glog.log';`
3. 跑**完整升级链**（不是单独 02）：`DATABASE_URL='mysql+pymysql://root:[REDACTED_PASSWORD]@<mysql容器>:3306/testdb' alembic upgrade head`
   从 base 一路升到 head（含 20261008_01 → 20261008_02）。记录 exit code。
4. **抓 general_log 里实际下发的 CREATE TABLE ingest_profile** 全文，定位三个 TEXT 列：
   - 若 DDL 为 `... TEXT NOT NULL`（无 DEFAULT）→ 强模型的"fresh compile"是 literal_binds 风格过读，#1 = 误报，迁移完好；
   - 若 DDL 为 `... TEXT NOT NULL DEFAULT '[]'` 且 upgrade 报 1101/失败 → #1 = 真 bug，main 迁移损坏。
5. **功能侧佐证**：upgrade 成功后，`INSERT INTO ingest_profile (profile_id, version, incoming_prefix, default_purposes_json, default_scenes_json, default_scene_parameters_json, enabled, created_at) VALUES ('t','1','p', ... )`
   不显式给三个 TEXT 列默认值，看是否报错 / 值是否为空串；再 `SELECT default_purposes_json` 确认。
6. **补充**：对 `sa.inspect`/`literal_binds` 不做静态编译（那正是矛盾来源），只认 general_log 实际执行 DDL。
7. 收尾：`docker rm -f test-*` + `docker network rm`，确认 0 残留。

## 交付
- 报告 `reviews/TASK-03B/attempt-2/verify-03b-mysql-text-default.md`：
  环境/命令/upgrade exit code/**general_log 实际 CREATE TABLE 三个 TEXT 列原文**/INSERT 结果/结论（#1=真 bug 或 误报，附 general_log 铁证）。
- group 通报"测试者：03B TEXT DEFAULT 终测报告已交付（真 bug / 误报）+ general_log 关键行"。
- 禁止改迁移/任何代码。若判定真 bug，报告写清即可，协调者回派 3号。