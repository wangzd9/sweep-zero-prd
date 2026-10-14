# TEST 报告：TASK-08 合入后 9 红文件全绿复核（post-merge-0a8ca8a）

- status: PASS（14/14 文件真 MySQL 文件级全绿 RC=0，隔离库 0 残留）
- 测试者：TESTER（独立取证，不复用 2号 attempt 容器/库/日志）
- 报告时间：2026-10-11 19:44 +08:00
- 被测快照：main `0a8ca8a`（独立 `git fetch` 后 `main`=`origin/main` 双核一致；--no-ff merge parents `98f6c88`+`bf48a45`，合入 19:17）
- 检出：TESTER 专属 detached worktree `/home/wang/.local/state/rosbag-scene/wt-tester-pm08` @ `0a8ca8a`（.venv 软链主仓 Python 3.10.12 / pytest 8.4.1 / SQLAlchemy 2.0.41，`import app.models` 验证通过），**不占开发槽，测毕已 `git worktree remove`**

## 环境口径（对齐 t08/t08c：真 MySQL 8.4.11 STRICT 隔离库，独立新库 + FK off + create_all，用完即毁）

- 容器 `tester-pm08-mysql`（本地已有镜像 `mysql:8.4` ID `6ea90827b110`，实测 `SELECT VERSION()`=8.4.11；`@@sql_mode` 含 `STRICT_TRANS_TABLES`；`@@character_set_server`=utf8mb4）
- 独立网络 `tester-pm08-net`，容器 IP `172.22.0.2:3306`
- 测试用户 `tester_pm08`（新建，随容器销毁）
- 逐文件隔离库 `t_pm08_0..13`：每文件前 `DROP DATABASE IF EXISTS` + 新建（utf8mb4/0900_ai_ci），pytest 插件 `pm08_plug.py` 连接后 `SET SESSION FOREIGN_KEY_CHECKS=0` + `Base.metadata.create_all`（生产默认 PyMySQL 驱动，非 mock、非 SQLite），文件级跑毕即 drop
- 连接串 `mysql+pymysql://tester_pm08@172.22.0.2:3306/t_pm08_N`；`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` + `-o addopts=` 排除第三方插件干扰
- 运行器：`~/.hermes/cache/scratch/t08-tester-pm08/pm08_runner.py`（后台单进程，总耗时 79.6s，日志 `logs/pm08_*.log` + `results.json`）

## 逐文件结果（14/14 PASS，全部 RC=0）

| # | 文件 | 结果 | 口径核对 |
|---|------|------|---------|
| 0 | `tests/test_bag_cleanup_api.py` | **24 passed** RC=0 | = 2号自测口径 24 |
| 1 | `tests/test_bag_cleanup_concurrency.py` | **11 passed** RC=0 | = 2号自测口径 11 |
| 2 | `tests/test_bag_cleanup_worker.py` | **19 passed** RC=0 | = 2号自测口径 19 |
| 3 | `tests/test_clone_published_dataset_records.py` | **2 passed** RC=0 | = 2号自测口径 2 |
| 4 | `tests/test_source_register_purpose.py` | **8 passed** RC=0 | = 2号自测口径 8 |
| 5 | `tests/test_pipeline_api.py` | **25 passed** RC=0 | = 2号自测口径 25 |
| 6 | `tests/test_lineage_lifecycle.py` | **3 passed** RC=0 | = 2号自测口径 3 |
| 7 | `tests/test_web.py` | **41 passed** RC=0 | = 2号自测口径 41 |
| 8 | `tests/test_scene_slice_scheduling.py` | **36 passed** RC=0 | c3-1/i1-1 覆盖项，合入后仍绿（36 与协调者 c3-1 验收口径一致） |
| 9 | `tests/test_scene_result_report.py` | **35 passed** RC=0 | 06B 回归 35 不破坏 ✓ |
| 10 | `tests/test_scene_result_storage.py` | **25 passed** RC=0 | 06B 回归 25 不破坏 ✓ |
| 11 | `tests/test_migration_lineage_rollback.py` | **2 passed** RC=0 | 迁移链（零迁移改动，链未被破坏）✓ |
| 12 | `tests/test_china_standard_time_migration.py` | **2 passed** RC=0 | 迁移链 ✓ |
| 13 | `tests/test_scene_slice_lineage.py` | **10 passed, 1 skipped** RC=0 | c3-1 交付口径：真 MySQL 10 passed + 1 skipped（skip=SQLite 方言守卫，c3-1 回执既有口径，非本单引入） |

- 9 红文件（0–8）：全部 RC=0 全绿 → **合入产物 main `0a8ca8a` 无回归，独立取证成立**
- 06B 回归（9–10）35/25 不破坏、迁移链（11–12）RC=0、scene_slice_lineage（13）10+1 skipped，与派单 AC 全部命中
- 逐文件日志（命令/退出码/summary 行）：`~/.hermes/cache/scratch/t08-tester-pm08/logs/pm08_00..13_*.log`；机器可读汇总 `results.json`（`all_pass: true`，每文件 `rc=0` + `dropped=true`）
- 运行命令（每文件同型）：`cd wt-tester-pm08 && .venv/bin/python3 -m pytest tests/<file> -p pm08_plug -p no:cacheprovider -o addopts= -q --tb=short`（env `PM08_DB=t_pm08_N`）

## 隔离与清理证据（0 残留）

- 13 个逐文件库 `t_pm08_0..13`：runner 内每文件跑毕即 `DROP DATABASE IF EXISTS`（results.json 逐条 `dropped=true`）
- 收尾核实：`information_schema.schemata` 仅剩 `t_pm08`（容器初始化空库，从未写入业务数据）→ 随后 `docker rm -f tester-pm08-mysql` + `docker network rm tester-pm08-net`，库随容器销毁
- `docker ps -a` 核实 tester-pm08 容器 0 残留；worktree `wt-tester-pm08` 已 `git worktree remove`（主仓 worktree 列表无 tester 条目）
- 零业务代码改动（仅读检出跑测试；scratch 运行器/插件在 TESTER 测试范围）

## 结论与边界

- **PASS**：合入产物 main `0a8ca8a` 真 MySQL 8.4.11 STRICT 隔离库 14 文件文件级全绿 RC=0 + 06B/迁移口径不破坏 + 隔离库/容器/网络/worktree 0 残留
- 本单为合入后验证，非 OCR/强审查/生产门禁；生产启用与真实样本门禁维持协调者既有口径
- 与 2号自测的差异说明：本次为 TESTER 独立容器/独立库/独立检出（不复用 2号 `wt-04a-t08c` 与 t08ciso_* 口径），passed 数逐文件一致即交叉印证