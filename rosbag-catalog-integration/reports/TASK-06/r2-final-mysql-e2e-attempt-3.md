# r2-final-mysql-e2e attempt-3：06B 缺陷3 reconcile 幂等二次复测报告

- 时间：2026-10-10 21:47 CST（TESTER，cron-tester-poll-2144）
- 被测 commit：main `5f0124b4c5df1c7782d46b0bb956542537b729b1`（`git rev-parse HEAD` 复核一致；含 2号缺陷3修复 `4e2158e`，--no-ff 合入，单文件 `app/services/scene_result_report_service.py` +27/-3）
- 环境：真实 **MySQL 8.4.11** 隔离容器 `tester-r2-mysql`（本地镜像 `6ea90827b110` 不拉取，net `tester-r2net3` 172.22.0.2，宿主 33071）+ 主仓 `.venv`，口径同 attempt-2（`tester_r2_mysql` pytest plugin：creator SSL 连接 + `SET SESSION FOREIGN_KEY_CHECKS=0` 仅供夹具清理）
- 隔离库：`t_r2app3`（31 用例全套）、`t_dbg6`（探针），`SELECT VERSION()` = 8.4.11
- 派单：`inbox/TESTER/TASK-06/r2-final-mysql-e2e-defect3-retest.md`（21:40，只复测缺陷3，不重跑 S1/S2/S3/S4/B8c/B8a/r6）

## 结果汇总

| 项 | 口径 | 结果 |
|---|---|---|
| AC1 reconcile 幂等二次 | 真 MySQL `t_dbg6` 探针 + 套件内同用例 | **PASS** |
| AC2 定向不回归（31 用例全套） | 真 MySQL `t_r2app3` | **PASS（31 passed，RC=0，3.43s）** |
| AC3 前一轮 39/40 口径 | 套件 31 + 探针佐证 | **转 40/40 等价达成**（见下） |

## AC1：reconcile 幂等二次真 MySQL PASS（探针证据）

最小复现路径（`scratch/tester_r2_a3_probe.py`，全新库 `t_dbg6` + app lifespan + 真实 TestClient）：

1. 建 run → claim → stage+publish 单段 `slope`（child uid `T06Bc-d3462dec7c974`，18 字符）。
2. `POST .../reconcile-scene` **第一次**：`200 {"reconciled":true,"registered":true}`。
3. **同 body 第二次（幂等重放）：`200`，不再抛 `StaleDataError`**——attempt-2 中该二次调用在 `scene_result_report_service.py:928 db.commit()` 抛 `StaleDataError: UPDATE bag_record ... expected 1 row 0 matched`，现已消失。

`bag_record` 行级 dump（SQL `SELECT id, LEFT(bag_uid,26), availability, row_version, updated_at FROM bag_record ORDER BY id`）：

```
--- after reconcile 1 ---
    (1, 'T06Brec-a1449a404f', None, 1, datetime.datetime(2026, 10, 10, 21, 46, 50))
    (2, 'T06Bc-d3462dec7c974', 'AVAILABLE', 1, datetime.datetime(2026, 10, 10, 21, 46, 50))
--- after reconcile 2 ---
    (1, 'T06Brec-a1449a404f', None, 1, datetime.datetime(2026, 10, 10, 21, 46, 50))
    (2, 'T06Bc-d3462dec7c974', 'AVAILABLE', 1, datetime.datetime(2026, 10, 10, 21, 46, 50))
```

方向证据（非硬门禁）：二次幂等重放后子包行 `updated_at` **未被无谓推进**（21:46:50 → 21:46:50 不变）、`row_version` 不变、可用性终态 `AVAILABLE` 保持——与修复方向（仅业务字段确有变化才推 `updated_at`，no-op 零 UPDATE）一致。

## AC2：定向不回归

命令（`scratch/tester_r2_a3_run.sh`）：

```
cd /home/wang/work/rosbag-catalog
R2_MYSQL_DB=t_r2app3 .venv/bin/python -m pytest -p tester_r2_mysql -p no:cacheprovider -q --tb=short tests/test_scene_result_report.py
```

输出尾部：`31 passed, 1 warning in 3.43s`，`PYTEST_RC=0`。日志 `scratch/tester_r2_a3_suite.log`。

## AC3：前一轮残留口径

attempt-2 不变式套件 40 用例 39 PASS / 1 FAIL（FAIL=`test_reconcile_backfills_after_publish_without_report`，缺陷3）。本单按派单口径只跑 `tests/test_scene_result_report.py` 31 用例（含该 reconcile 用例，真 MySQL **PASS**）+ 独立探针复现同路径；`test_scene_r2_rework_1.py` 9 用例未被本笔改动触及（修复仅 `_mark_children_available` 幂等重放路径，且 attempt-2 中该文件全 PASS）→ 40 条口径**等价达成 40/40**，不机械复跑。

## 失败项

无。

## 清理与残留

- 容器 `tester-r2-mysql`（docker rm -f）、网络 `tester-r2net3`（network rm -f）已销毁；`docker ps -a | grep tester-r2` = 空，**0 残留**。
- 零业务代码改动（仅 scratch 探针/脚本）。

## 证据文件

- `~/.hermes/cache/scratch/tester_r2_a3_suite.log`（31 用例真 MySQL 全套）
- `~/.hermes/cache/scratch/tester_r2_a3_probe.out`（AC1 探针全文 dump）
- `~/.hermes/cache/scratch/tester_r2_a3_probe.py` / `tester_r2_a3_run.sh` / `tester_r2_a3_setup.sh`

**结论：缺陷3 修复 `4e2158e` 真 MySQL 复测 PASS（31/31 + 幂等二次探针 200/200，updated_at 无谓推进消除）；06 聚合放行业务门禁的最后一道 TESTER 复测通过，等协调者解锁。**