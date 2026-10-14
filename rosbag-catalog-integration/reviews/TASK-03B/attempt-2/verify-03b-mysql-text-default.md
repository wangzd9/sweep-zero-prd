---
task: TASK-03B
item: verify-03b-mysql-text-default
owner: 测试者
status: TEST_REPORT_PENDING
base: b3280c9（派单指定 HEAD）；实测工作区 8bd5618，`git diff b3280c9 8bd5618 -- alembic/ requirements.txt` = 空 → 被测迁移文件逐字节一致
target: main 的 alembic/versions/20261008_02_ingest_config.py（L47-49 三列 sa.Text() server_default="[]"/"[]"/"{}"）
env: MySQL 8.4 docker（镜像 6ea90827b110，mysql:8.4）+ python:3.10-slim（6ff506466f8b），同 docker network test-mdnet；pymysql 1.1.1/sqlalchemy 2.0.41/alembic 1.16.4（容器内 `pip install -r requirements.txt` 锁定核实）
updated: 2026-10-09 20:5x CST
verdict: **PASS（#1 critical = 误报）**——干净 MySQL 8.4 完整升级链 RC=0 成功，general_log 实抓 CREATE TABLE ingest_profile 三个 TEXT 列真实 DDL 为 `TEXT NOT NULL`（无 DEFAULT 子句），MySQL 未报 1101，迁移完好
---

# 03B 迁移 TEXT server_default 真实 MySQL 8.4 终测（TESTER attempt-1）

## 被测快照（ACK 回写）
- 目标仓库 /home/wang/work/rosbag-catalog，被测 commit = b3280c9（派单指定 HEAD）。
- 当前 main = 8bd5618（06A 合入）。`git diff b3280c9 8bd5618 --stat -- alembic/ requirements.txt` = **空**，
  即被测迁移文件与依赖锁在 b3280c9 与 8bd5618 下逐字节一致 → 在 8bd5618 工作区执行，快照等价 b3280c9。
- 被测对象 = alembic/versions/20261008_02_ingest_config.py：
  - L47 `default_purposes_json` sa.Text() nullable=False server_default="[]"
  - L48 `default_scenes_json` sa.Text() nullable=False server_default="[]"
  - L49 `default_scene_parameters_json` sa.Text() nullable=False server_default="{}"
- 完整升级链 base → … → 20261008_01 → 20261008_02（head），非单独 02。
- 环境为**独立新建**隔离库（test-md-*，前缀 test-），未复用协调者/3号既有容器。

## 环境说明（如实记录，不影响 DDL 证据）
- MySQL 8.4 已**卸载 mysql_native_password** 插件（`ALTER USER ... IDENTIFIED WITH mysql_native_password`
  → ERROR 1524 Plugin not loaded）。root@'localhost' 走 unix socket（CLI）认证可用；
  容器间/跨机 TCP 与 PyMySQL URL 解析路径的 caching_sha2 全认证在本网络下被 1045 拦截
  （PyMySQL 显式 `pymysql.connect(unix_socket=...)` 则稳定成功，`current_user()` = tuser@%）。
- 为让**标准 `alembic upgrade head` CLI** 跑通且不碰仓库任何文件，测试者自建临时 alembic 配置
  （scratch tempalembic/：env.py 用已验证的 unix_socket 连接 + `versions` 软链到真实 /work/alembic/versions）。
- **核心证据是服务端 general_log 里【实际下发】的 CREATE TABLE 原文，与客户端认证/连接方式无关**，
  故上述连接机制差异不影响本裁决的有效性。

## 执行步骤与真实结果
1. 干净 mysql:8.4 容器（MYSQL_ROOT_PASSWORD=testpw，MYSQL_DATABASE=testdb）+ python:3.10-slim 容器
   同 docker network；python 容器 `pip install -q -r requirements.txt`（锁定版本核实）。
2. `SET GLOBAL general_log='ON'; SET GLOBAL general_log_file='/tmp/glog.log';`
3. **完整升级链**（`alembic upgrade head`，base→head，非单独 02）：
   - 第一遍（testdb）：**RC=0，成功**，head=20261008_02，`SHOW TABLES` 落地 31 张表（含 ingest_profile / ingest_submission / purpose_schedule_event 三张新表）。
   - 第二遍（全新 testdb2，general_log 已开）：**RC=0，成功**。
   - 两遍均无 1101 / 无任何 DDL 报错。
4. general_log 实抓 `CREATE TABLE ingest_profile` 原文（两遍一致，以下为 12:41 那遍，line 1260）：
   ```sql
   CREATE TABLE ingest_profile (
   	id BIGINT NOT NULL AUTO_INCREMENT,
   	profile_id VARCHAR(64) NOT NULL,
   	version INTEGER NOT NULL,
   	display_name VARCHAR(128) NOT NULL,
   	incoming_prefix VARCHAR(255) NOT NULL,
   	default_purposes_json TEXT NOT NULL,
   	default_scenes_json TEXT NOT NULL,
   	default_scene_parameters_json TEXT NOT NULL,
   	enabled BOOL NOT NULL,
   	created_at DATETIME NOT NULL,
   	PRIMARY KEY (id),
   	CONSTRAINT uq_ingest_profile_id_version UNIQUE (profile_id, version)
   )
   ```
   **三个 TEXT 列真实下发 DDL = `TEXT NOT NULL`，无 DEFAULT 子句。** → 强模型 "fresh compile 得
   `TEXT NOT NULL DEFAULT '[]'`" 是对 `literal_binds`/方言编译的过读；真实 MySQL 8.4 执行路径未下发
   TEXT 默认值，**未触发 1101**，迁移完好。
5. 功能侧 INSERT 佐证（testdb2）：
   - S1：`INSERT INTO ingest_profile (profile_id, version, display_name, incoming_prefix, enabled, created_at) VALUES (...)`
     （补齐其余 NOT NULL 列、**只省略三个 TEXT 列**）→
     `ERROR 1364 (HY000): Field 'default_purposes_json' doesn't have a default value`。
   - 即 DB 层这三个 TEXT 列**确实无默认值**，与 general_log DDL 一致。业务写入不受影响：
     ingest_service.py L197-199 创建路径**显式赋值**三列（`json.dumps(["self_built"])` 等）、
     L85-87 读取路径 `or "[]"`/`or "{}"` 兜底。
6. 静态编译（sa.inspect/literal_binds）未采用——那正是强模型与旧实验矛盾来源，只认 general_log 实际执行 DDL。
7. 收尾：`docker rm -f test-md-mysql test-md-py` + `docker network rm test-mdnet` + `docker volume rm mdsockvol`，
   `docker ps -a --filter name=test-md` = **0 残留**（测试者自建前缀，未碰他人容器）。

## 关键发现（如实报告，供协调者裁决口径）
- **gate 结论**：#1 critical = **误报**。干净 MySQL 8.4 完整升级链真实执行成功（RC=0），
  general_log 铁证三个 TEXT 列 DDL 无 DEFAULT，未触发 1101。03B 迁移（20261008_02）**在 DDL 层面完好**。
- **一处系统性现象（非本 gate 阻塞，但值得记录）**：02 迁移 `op.create_table` 里**所有** server_default 列
  （三个 TEXT、`status`、`row_version`、`source`、`enabled`、`display_name`）真实下发 DDL **均未渲染 DEFAULT 子句**；
  而同库 01 迁移 `op.add_column` 的 `bag_role`（server_default="ORIGINAL"）**保留了** `DEFAULT 'ORIGINAL'`。
  差异指向 SQLAlchemy 2.0.41 MySQL 方言对 create_table 列 server_default 的 DDL 渲染行为
  （literal_binds/编译路径下 TEXT 列默认被省略或整体 server_default 未进 DDL）。
  影响面：所有 NOT NULL + server_default 的 02 新表列在 DB 层无默认值，**业务依赖 ORM 显式赋值**
  （已核 ingest 创建路径显式赋值，无裸 INSERT 依赖 DB 默认 → 无功能回归）。
  若协调者希望 DB 层真正具备列默认值（防御 ORM 外的直接 SQL），属**业务/迁移变更**（回派 3号改迁移或补 server_default 渲染），
  不在本测试者 gate 裁决范围；本 gate 只回答"当前 main 迁移是否产生非法 DDL / 是否损坏" = **否**。

## 交付
- 报告：reviews/TASK-03B/attempt-2/verify-03b-mysql-text-default.md（本文件）
- 回执：test-receipts/TEST-03B-mysql-text-default/attempt-1.md
- 证据：~/.hermes/cache/scratch/tester_03b_md/glog.log（general_log 全文，1583 行，含两遍 CREATE TABLE ingest_profile）
- 未改任何业务代码/迁移；未跑 OCR；未动生产/处理机/部署。