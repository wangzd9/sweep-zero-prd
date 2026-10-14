# r2-final-mysql-e2e attempt-5：R-01 秒末截断边界 + R-03 零 UPDATE 真 MySQL 独立复测（PASS）

- 被测 base：main `4697be0`（= origin/main，09:44:51 合入推送；开工前 git 复核 HEAD 一致，工作树无 app/tests 未提交改动）
- 派单：`inbox/TESTER/TASK-06/r2-final-mysql-e2e-attempt-5.md`（09:44 下达，09:52 ACK，10:07 交付）
- 执行者：TESTER（cron-tester-poll-0950），零业务代码改动（只读 + 测试材料在 scratch）
- 环境：真实 MySQL 8.4.11 隔离容器（本地镜像 `6ea90827b110`，不拉取），网络 `tester-r2net5`（172.22.0.2），宿主 33072，隔离库 `t_r2app5`/`t_r5dbg`/`t_r5ac2`（新库名不串旧库），主仓 `.venv` Python 3.10.12，PyMySQL 裸连接（无 client_flag 参数，**无 CLIENT_FOUND_ROWS**，changed-rows 语义；**非生产默认连接**——生产默认建连带 FOUND_ROWS，见 :13 边界说明）

## 连接语义实测（无 CLIENT_FOUND_ROWS 隔离连接口径）

- 连接方式：`pymysql.connect(host, port, user, password, database, ssl={"ca": None}, charset="utf8mb4")`，**无 `client_flag` 参数**
- `pymysql.connections.Connection.__init__` 的 `client_flag` 默认参数 = **0**（调用方未传时 pymysql 内部补 `DEFAULT`）
- 实测裸连接协商 flag = **`0x3AAA0D`**，**`CLIENT_FOUND_ROWS` 位 = False**
- **注意**：本复测与 2号自测为**无 CLIENT_FOUND_ROWS 隔离连接**语义（rowcount 反映"实际变化行数"，R-01/R-03 触发路径成立）；**与生产默认连接语义不同**——生产走 app/database.py 的 SQLAlchemy 默认建连（codex 第四轮 11:05 无网络探针实测 client_flag=2，FOUND_ROWS=True，同值 UPDATE 返回 matched rows=1，no-op 天然不触发 StaleDataError）。本单证据**只验证 changed-rows 连接下的修复行为，不外推生产默认连接**
- 环境口径说明：派单文字 `R2_MYSQL_DB=<隔离库>` 在仓库 grep 无定义，`app/config.py` 实际读 `DATABASE_URL`——本轮经 pytest 插件 `tester_r5_mysql`（scratch）将 `DATABASE_URL` 指向隔离库，等效口径

## AC1：R-01 秒末边界（核心新增）— PASS

套件：`tests/test_scene_result_report.py` 全文件，`R2_MYSQL_DB=t_r2app5` + 真 MySQL 8.4.11，
命令 `.venv/bin/python -m pytest -p tester_r5_mysql -p no:cacheprovider -q --tb=short tests/test_scene_result_report.py`
→ **35 passed, RC=0**（4.19s；含新增 `test_reconcile_start_ns_truncates_toward_zero_at_second_boundary` ns末=0/500_000_000/999_999_999 三参数）。
（日志 `~/.hermes/cache/scratch/tester_r5_suite.log`）

探针（`~/.hermes/cache/scratch/tester_r5_probe.py`，`t_r5dbg` 全新库，app lifespan + TestClient 真实调用链，日志 `tester_r5_probe.log`）：

- **AC1-999m**（R-01 核心）：`start_ns` = (BASE_S+2) 秒 + **999_999_999 ns**（纳秒末贴近秒边界）→
  reconcile-1 **200**，落库子包行 `started_at = 2023-11-14 22:13:22`（**microsecond=0，完整值 = BASE_S+2 整秒，向下截断，不进位到 BASE_S+3**；旧码 `/1e9` 浮点秒在 999_999_999 会进位到 +3）；
  reconcile-2 同 body 幂等重放 → **200，无 StaleDataError**；
  `started_at`/`updated_at`/`row_version` 三元组逐值相等（**均未推进，row_version 不变**）→ `PROBE_PASS`。
- **AC1b-frac**（0.5s 小数秒，M-1 回归形状）：同流程 reconcile-1/2 均 **200 无 StaleDataError**，`started_at = 22:13:22` 整秒、三元组不推进 → `PROBE_PASS`。
- attempt-4 时代旧码 `22:13:23`（进位）错口径已消除。

## AC2：R-03 零 UPDATE 直接断言 — PASS

独立口径 = **连接层/数据库 general_log 等价验证**（非 2号 的 ORM `before_cursor_execute` 监听计数），
脚本 `~/.hermes/cache/scratch/tester_r5_ac2b.py`（`t_r5ac2` 全新库，日志 `tester_r5_ac2b.log`）：

- 方法：先走 initial registration（PENDING→AVAILABLE，合法产生 `UPDATE bag_record`），随后 **`TRUNCATE mysql.general_log`**，只让两次幂等重放的 SQL 落日志，再计数。
- start_ns 取 R-01 最坏形状 (BASE_S+2)s + 999_999_999 ns。
- **same-second replay**：reconcile-2 **200** registered=True，落日志 total=36 行，**`UPDATE bag_record` = 0**，三元组不推进。
- **cross-second replay**（monkeypatch 服务内 `local_now` +1s）：reconcile-3 **200** registered=True，累计落日志 total=72 行，**`UPDATE bag_record` = 0**，三元组不推进。
- 两次 replay 全窗口无任何 `UPDATE` 语句（`argument LIKE 'UPDATE %'` 计数=0），**AC2_PASS**：幂等重放零 UPDATE，no-op 与墙钟同秒/跨秒无关。

## AC3：不回归（attempt-4 已 PASS 项抽查）— PASS

- **微秒回归** `test_reconcile_fractional_second_start_ns_starts_at_truncated_to_second`：真 MySQL **passed**（R-01 一行改动未碰坏 M-1 路径）。
- **整秒口径** 探针 AC2-int（defect3 原始复现形状，BASE_S+2→BASE_S+4 整秒）：reconcile-1/2 均 **200 无 StaleDataError**，`started_at` 整秒、三元组不推进、`row_version` 不变 → `PROBE_PASS`。

## AC4：口径核对（6d30a68..4697be0 diff）— PASS

`git diff --stat 6d30a68..4697be0` = **3 文件 +156/-8**：

- `app/services/scene_result_report_service.py` +7/-1：**行为面仅 :582 一行赋值**
  `started_at = datetime.fromtimestamp(der.start_ns // 1_000_000_000, tz=timezone.utc).replace(tzinfo=None)`，其余为注释；
- `tests/test_scene_result_report.py` +138/-0：R-01 秒末边界三参数用例 + `_count_bag_record_updates` 助手 + R-03 零 UPDATE 断言强化；
- `tests/test_scene_slice_scheduling.py` +19/-0：断言强化。

**确认无 app 行为面越出 :582 一行赋值**，与派单口径一致。

## 清理

- 隔离容器 `tester-r2-mysql-a5`、网络 `tester-r2net5` 已 `docker rm -f`/`docker network rm`；
- 宿主 33072 端口已释放（`ss -ltn` grep=空），无 tester 容器残留（`docker ps -a` grep=空）；
- 全程零业务代码改动。

## 结论

- **PASS 4/4**（AC1/AC2/AC3/AC4），R-01 秒末截断边界 + R-03 零 UPDATE 在真 MySQL 8.4.11 隔离连接（无 CLIENT_FOUND_ROWS，changed-rows 语义）下独立复测全绿；**连接语义边界**：生产默认建连带 FOUND_ROWS（codex 11:05 定论），本单证据不外推生产默认连接。
- 06 聚合放行剩余 = 强模型增量复审 R2I-20261010-06（target 随本次合入更新为 `4697be0`，**用户手动触发**）→ PASS 收口即 03/05/06 聚合 DONE → TASK-08。
- 本单交付 TEST_REPORT_PENDING，等协调者验收。