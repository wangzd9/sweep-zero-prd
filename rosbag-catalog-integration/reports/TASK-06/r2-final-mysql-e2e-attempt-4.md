# r2-final-mysql-e2e attempt-4：M-1 微秒回归 + 生产默认连接语义复测（PASS）
> **连接语义纠错（2026-10-11 13:55 协调者，据 codex 第七轮 B-01）**：本文件所称
> "PyMySQL 生产默认连接/生产默认语义"均指**无 CLIENT_FOUND_ROWS 隔离连接**（裸 pymysql.connect 无 client_flag，changed-rows 语义）；生产实际默认建连
> （SQLAlchemy 2.0.41 + PyMySQL 1.1.1）默认 client_flag=2 带 FOUND_ROWS，同值 UPDATE 返回
> matched rows=1。本文件证据只验证 changed-rows 连接下的修复行为，**不外推生产默认连接**。
> 详见 reviews/codex-r10-finalstate-20261011-verdict.md。


- 被测 base：main `6d30a68`（= origin/main，2026-10-10 22:46:03 推送；开工前 git 复核 HEAD 一致）
- 派单：`inbox/TESTER/TASK-06/r2-final-mysql-e2e-attempt-4.md`（22:50 下达，22:51 ACK，23:0x 交付）
- 执行者：TESTER（cron-tester-poll-2249），零业务代码改动（只读 + 测试材料在 scratch）
- 环境：真实 MySQL 8.4.11 隔离容器（本地镜像 `6ea90827b110`，不拉取），网络 `tester-r2net4`（172.22.0.2），宿主 33072，隔离库 `t_r4app`/`t_r4dbg`（新库名不串旧库），主仓 `.venv` Python 3.10，PyMySQL 经 SQLAlchemy `creator` 连接（`ssl={"ca": None}`，无 flag 参数）

## 连接语义实测（生产默认口径）

- `pymysql.connections.Connection.__init__` 的 `client_flag` 默认参数为 **0**（调用方未传时 pymysql 内部补 `DEFAULT`）
- 实测裸连接协商 flag = `0x3AAA0D`，**`CLIENT_FOUND_ROWS` 位 = False**
- 即本复测与 2号自测、生产默认连接同语义：**无 CLIENT_FOUND_ROWS**，rowcount 反映"实际变化行数"，缺陷3/M-1 触发路径成立

## AC1：M-1 微秒回归（核心新增）— PASS

套件：`tests/test_scene_result_report.py` 全文件，`R2_MYSQL_DB=t_r4app` + 真 MySQL 8.4.11，
命令 `.venv/bin/python -m pytest -p tester_r2_mysql -p no:cacheprovider -q --tb=short tests/test_scene_result_report.py`
→ **32 passed, RC=0**（3.75s；含新增微秒回归用例 `test_reconcile_fractional_second_start_ns_starts_at_truncated_to_second`）。
（日志 `~/.hermes/cache/scratch/tester_r4_suite.log`）

探针（`~/.hermes/cache/scratch/tester_r4_probe.py`，t_r4dbg 全新库，app lifespan + TestClient 真实调用链，日志 `tester_r4_probe.log`）：

- reconcile-1 带小数秒 `start_ns`（BASE_S+2 秒 + 500ms 纳秒偏移）→ **200**，落库子包行
  `started_at = 2023-11-14 22:13:22`（**microsecond=0，库内整秒**）；
- reconcile-2 同 body 幂等重放 → **200，无 StaleDataError**；
- 两次后 `started_at`/`updated_at`/`row_version` 三元组逐值相等（**均未推进，row_version 不变**）——
  与 attempt-3 探针口径对齐，并按派单扩展了 `started_at` 列断言；
- 修复前行为（attempt-2 已实证）：同形状微秒输入在 MySQL 下二次重放抛
  `StaleDataError: UPDATE bag_record ... expected 1 row 0 matched`——本次同链路同连接语义下不再出现。

## AC2：不回归（整秒口径抽查 1 例）— PASS

探针 AC2-int：整秒 `start_ns`（BASE_S+2 到 BASE_S+4，缺陷3 原始复现形状）同流程
reconcile-1/2 均 **200 无 StaleDataError**，`started_at` 整秒、三元组不推进、`row_version` 不变。
M-1 一行改动未碰坏整秒路径。

## AC3：口径核对（5f0124b..6d30a68 diff）— PASS

`git diff --stat 5f0124b..6d30a68` = 3 文件 +72/-5：

- `app/services/scene_result_report_service.py` +6/-1：**行为面仅 M-1 一行赋值**
  `:582 started_at = ...replace(tzinfo=None, microsecond=0)`，其余为注释；
- `alembic/versions/20261009_02_ingest_frozen.py` +8/-4：纯 docstring 适用边界（M-2，revision 未改）；
- `tests/test_scene_result_report.py` +58/-2：新增微秒回归用例 + 注释纠偏（M-3）。

**确认无 app 行为面越出 M-1 一行赋值**，与派单口径一致。

## 结论

- **PASS 3/3**（AC1/AC2/AC3），缺陷3 同根因（DATETIME(0) 秒精度 + 无 CLIENT_FOUND_ROWS 的
  no-op 单列 UPDATE）第二列 `started_at` 修复在**生产默认连接语义**下独立复测成立。
- 已交付证据复用说明：S1/S2/S3/S4/B8c/B8a/r6 按派单不重跑（attempt-1/2/3 已 PASS，且 AC3
  确认 6d30a68 对它们无行为面变更，仅 M-1 一行 + docstring + 测试）。
- 强模型增量复审包 R2I-20261010-06（target 已更新 6d30a68）维持 **READY_FOR_USER_TRIGGER**，用户手动触发，本角色不代跑。
- 隔离资源：容器 `tester-r2-mysql-a4` + 网络 `tester-r2net4` 已 `docker rm -f` / `docker network rm`，
  宿主 33072 无监听、`docker ps -a` 无 tester-r2 残留，**0 残留**。

## 交付物

- 报告：`reports/TASK-06/r2-final-mysql-e2e-attempt-4.md`（本文件）
- 回执：`test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-4.md`
- 证据：`~/.hermes/cache/scratch/tester_r4_suite.log`、`tester_r4_probe.log`、`tester_r4_probe.py`