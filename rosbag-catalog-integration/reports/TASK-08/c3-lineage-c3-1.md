# 报告：C3-lineage 夹具 bag_uid 越宽最小修复（c3-1）

## 环境口径
- worktree：`/home/wang/.local/state/rosbag-scene/wt-01-c3`，分支 `scene/task-08-c3-lineage-fixture`，base main `f9bafb0`（= origin/main）→ head `f656507`
- 真 MySQL 验收：独占容器 `docker.m.daocloud.io/mysql:8.4`（实跑 8.4.11，sql_mode 含 `STRICT_TRANS_TABLES`），独立新库 `c31_accept_f1b33bcd7179466ea2e9ccec02251f4f`，随机 root 密码，`DATABASE_URL`+`DEMO_DATA=1`（对齐 2号 t08 口径：独立新库+create_all+用完即毁）
- 本地 venv：主仓 `/home/wang/work/rosbag-catalog/.venv`（worktree 软链）

## 命令与退出码
| 项 | 命令 | 结果 |
|---|---|---|
| SQLite 定向 | `.venv/bin/python -m pytest tests/test_scene_slice_lineage.py -q` | **11 passed** RC=0 |
| ruff | `.venv/bin/ruff check tests/test_scene_slice_lineage.py` | **All checks passed** |
| 真 MySQL 文件级 | `.venv/bin/python a-c3-mysql-run.py`（内含 pytest 同文件） | **pytest_rc=0**（10 passed + 1 skipped），容器 `c31-accept-74e554dbb444` 即毁 |
| 隔离库残留 | `docker ps -a --filter name=c31-accept-74e554dbb444` | **0 残留（CLEAN）** |

## 日志路径
- 真 MySQL 文件级：`/home/wang/.hermes/cache/scratch/a-c3-mysql-suite.out`
- runner：`/home/wang/.hermes/cache/scratch/a-c3-mysql-runner.log`（首轮 74e554db 前一次 `12f44e9f` 为 uid 修复后、FK 守卫前，1 failed 已被该轮证据记录）
- 复现锚点（2号 scratch）：`~/.hermes/cache/scratch/t08-e2e/fkoff/isol2_7_test_scene_slice_lineage.py.log`（10 errors 1406）

## 修复点与口径
1. `lineage` fixture 父/子 uid 27→26 字符（`[:24]`→`[:23]`）+ 构造处 `assert len(uid) <= 26`（同 i1-1 `6823f2d` 口径）
2. OTHERCHILD uid 27→26（`hex[:14]`→`hex[:13]`，同族越宽一并收敛）
3. `test_parent_delete_blocked_by_fk_restrict` SQLite 方言守卫（预存 SQLite-only 用例，1406 修复后被揭开；MySQL RESTRICT 由迁移验收覆盖=文件 docstring 既有声明；未弱化断言）

## 结论
派单 AC 全满足：真 MySQL 8.4.11 STRICT 隔离库文件级全绿（RC=0）、SQLite 定向不回归（11 passed）、ruff 绿、隔离库 0 残留。零 app 变更、零越界。等协调者审核合入。