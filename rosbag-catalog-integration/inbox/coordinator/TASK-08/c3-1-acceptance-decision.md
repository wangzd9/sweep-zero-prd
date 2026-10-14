# Decision：C3-lineage 夹具 uid 越宽最小修复（c3-1）验收

- status: ACCEPT_MERGED
- 裁决时间：2026-10-11 17:03 +08:00（cron poll，真实 checked_at 2026-10-11T16:55:53+08:00 preflight）
- task/attempt：C3-lineage / c3-1（TASK-08 attempt-1 联调 §C3 回派）
- 交付：1号（A），commit `f656507a25b559c864f35da32566b764177cb662`（16:56:25），base `f9bafb0`（= origin/main，ACK 时 fetch 核实零前移）
- 范围：`tests/test_scene_slice_lineage.py` 1 文件 +14/-4，零 app 变更
  1. lineage fixture 父/子 uid `[:24]`=27 字符 → `[:23]`=26 字符 + 各加 `len<=26` assert 防回归（同 i1-1 `6823f2d` 口径）
  2. `test_derivation_unique_child_and_run_slice` OTHERCHILD `3+10+14`=27 → `hex[:13]`=26（同族越宽一并收敛）
  3. `test_parent_delete_blocked_by_fk_restrict` 加 SQLite 方言守卫（`engine.dialect.name != "sqlite"` skip）：PRAGMA foreign_keys 为 SQLite 语义，文件 docstring 既有声明"SQLite PRAGMA + MySQL 由迁移验收覆盖"；uid 1406 修复后该预存失败首次被揭开（MySQL 下 1064），**非本单引入**，按仓库方言 guard 先例（`test_bag_cleanup_mysql.py`）最小处置，SQLite 路径照常全量执行、未弱化断言
- 协调者独立机械核验（wt-01-c3 复核）：
  - 单 commit，`f656507~1`=`f9bafb0`=合入前 main/origin，零越界（worktree git status 零业务改动）
  - 同文件其余 uid 用法核对：L156 `PLAIN+[:18]`=26 合规未触碰；`run_id` String(64)/`name`/`relative_path`/`fast_fingerprint` 均不越宽（与回执一致）
  - 模块级 `engine.dialect.name` 取值位置核实：文件已 import `from app.database import engine`，skip 守卫语义正确
  - SQLite 定向独立复跑：`pytest tests/test_scene_slice_lineage.py -q` → **11 passed RC=0**；ruff **All checks passed**
  - 真 MySQL 证据复核：`a-c3-mysql-suite.out` = **10 passed, 1 skipped RC=0**（skip=SQLite 语义 FK 用例）；`a-c3-mysql-runner.log`：容器 `c31-accept-74e554dbb444`（mysql:8.4.11，sql_mode 含 STRICT_TRANS_TABLES）→ removed → **residual_check: CLEAN**；docker ps -a 复核 0 残留
- 串行 OCR R1-r1（17:01，session `df3efba6-d894-453e-9223-cf81d4e87767`）：`--preview` 入选 1 文件 `tests/test_scene_slice_lineage.py`（+14/-4）被 default_path 排除，**0 app 侧入选 = 纯测试交付预期口径**（I1-r1/R8-r1/R9-r1 先例），非漏审非故障；账 `reviews/TASK-08/c3-1/ocr-batches.md`
- 合入：**--no-ff 合入 main `98f6c88`（2026-10-11 17:02，推 origin f9bafb0..98f6c88）**；合入后 sanity：alembic heads 单头 `20261009_02_ingest_frozen` ✓ / ruff 绿 ✓ / SQLite 定向 **11 passed** ✓
- TASK-08 收口进度：c3-1 已合入（收口条件 1/2）；剩 t08c-1（2号 C1/C2 秒精度专项，16:54 ACK 已开工）交付→机械核验→串行 OCR 增量→合入 → 08 收口核 9 红文件全绿复核
- 裁决人：协调者 cron（单写租约 token 持有，控制动作即时释放）