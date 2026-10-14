# TEST-03B-mysql-text-default attempt-1

- task_id: TASK-03B
- item: verify-03b-mysql-text-default（派单 inbox/TESTER/TASK-03B/verify-03b-mysql-text-default.md，PENDING，CRITICAL gate #1）
- owner: TESTER
- status: **TEST_REPORT_PENDING**（ACK 17:1x → 执行 → 交付 20:5x CST）
- verdict: **PASS（#1 critical = 误报）**
- 被测快照（ACK 回写）：
  - 目标仓库 /home/wang/work/rosbag-catalog
  - 被测 commit = b3280c9（派单指定 HEAD）；当前 main = 8bd5618（06A 合入），`git diff b3280c9 8bd5618 -- alembic/ requirements.txt` = **空**，即被测迁移文件与依赖锁两 commit 下逐字节一致 → 以 8bd5618 工作区执行，快照等价于 b3280c9
  - 被测对象 = alembic/versions/20261008_02_ingest_config.py（L47-49 三列 sa.Text() server_default="[]"/"[]"/"{}"）
  - 升级链：base → 20261008_01 → 20261008_02（head）
- 环境（一次性 test-* 前缀，已清理 0 残留）：
  - MySQL 8.4：docker 本地镜像 mysql:8.4（6ea90827b110，不拉取远端）；注：8.4 已卸载 native 插件
  - Python 3.10-slim：本地镜像 6ff506466f8b，`pip install -q -r requirements.txt`（pymysql==1.1.1 / sqlalchemy==2.0.41 / alembic==1.16.4 锁定核实），挂载 -v /home/wang/work/rosbag-catalog:/work
  - 同 docker network test-mdnet；unix socket 经命名卷 mdsockvol 桥接
- 验收项（照派单 7 步）：全过
  1. general_log 全链 upgrade（base→head）×2 遍，**均 RC=0 成功**，无 1101
  2. 抓实际下发 CREATE TABLE ingest_profile 全文，三个 TEXT 列原文 = `TEXT NOT NULL`（**无 DEFAULT 子句**）
  3. 判定：DDL 无 DEFAULT + upgrade 成功 → **#1=误报，迁移完好**
  4. 功能侧 INSERT 只省略三 TEXT 列 → 1364 无默认值（DB 层确无默认），业务创建路径显式赋值不受影响
  5. 静态编译不做（矛盾来源）
- 报告：reviews/TASK-03B/attempt-2/verify-03b-mysql-text-default.md
- 证据：~/.hermes/cache/scratch/tester_03b_md/glog.log（general_log 1583 行全文，含两遍 CREATE TABLE ingest_profile）
- 附加发现（如实报告，非本 gate 阻塞）：02 create_table 所有 server_default 列真实 DDL 均未渲染 DEFAULT（01 add_column 的 bag_role 却保留）→ SQLAlchemy 2.0.41 方言行为；业务依赖 ORM 显式赋值无功能回归。若需 DB 层真默认值属业务/迁移变更，回派 3号。
- 禁止项确认：未改迁移/任何业务代码，未跑 OCR，未动生产/处理机/部署