# 回执：C3-lineage 夹具 bag_uid 越宽最小修复（c3-1）

- status: REVIEW_PENDING
- owner/attempt：1号（A）/ C3-lineage c3-1（TASK-08 attempt-1 联调 §C3 回派）
- 派单：`inbox/1号/TASK-05/c3-lineage-fixture-uid-dispatch.md`；ACK：`inbox/1号/TASK-05/c3-lineage-fixture-uid-ack.md`
- base/head：base main `f9bafb0`（= origin/main，ACK 时 fetch 核实零前移）→ head `f656507`（单 commit，1 文件 +14/-4，零 app 变更，零越界）
- 分支/worktree：`scene/task-08-c3-lineage-fixture` / `/home/wang/.local/state/rosbag-scene/wt-01-c3`（在冻 `wt-01`/`wt-01-i1` 未动）
- 文件清单（1 文件）：
  - `tests/test_scene_slice_lineage.py`：
    1. `lineage` fixture 父/子 uid：`BAG_PREFIX + (hex+"PARENT"/"CHILD")[:24]` = 27 字符越 `bag_record.bag_uid` VARCHAR(26)（真 MySQL 8.4.11 strict setup 1406，2号 10 errors 全因它，SQLite 遮坑）→ `[:23]` = 26 字符，构造处各加 `assert len(uid) <= 26` 防回归（口径与 i1-1 `6823f2d` 完全一致）
    2. `test_derivation_unique_child_and_run_slice` OTHERCHILD uid：`3+10+14`=27 字符（同族越宽，进 `child_bag_uid` String(26)）→ `hex[:13]`=26
    3. `test_parent_delete_blocked_by_fk_restrict` 加 SQLite 方言守卫（`engine.dialect.name != "sqlite"` 则 skip）：该用例用 `PRAGMA foreign_keys=ON` 为 SQLite 语义（文件 docstring 既有声明"SQLite PRAGMA + MySQL 由迁移验收覆盖"）；uid 1406 修复后此预存失败首次被揭开（MySQL 下 1064 语法错），**非本单引入**，按仓库方言 guard 先例（`test_bag_cleanup_mysql.py`）最小处置，未弱化任何断言（SQLite 路径照常全量执行）
  - 同文件其余 uid/24-hex 用法逐处核对：L156 `PLAIN+[:18]`=26 合规不动；`run_id` String(64)/`name`/`relative_path`/`fast_fingerprint` 均不越宽
- 自测（命令/退出码/环境）：
  - SQLite 定向：`.venv/bin/python -m pytest tests/test_scene_slice_lineage.py -q` → **11 passed** RC=0（worktree `wt-01-c3`）
  - ruff：`.venv/bin/ruff check tests/test_scene_slice_lineage.py` → **All checks passed**
  - AC 真 MySQL 8.4.11 STRICT 隔离库：独占容器 `c31-accept-74e554dbb444`（`docker.m.daocloud.io/mysql:8.4`，独立新库 `c31_accept_f1b3…`，随机密码，sql_mode 核实含 `STRICT_TRANS_TABLES`，`DATABASE_URL`+`DEMO_DATA=1` 对齐 2号 t08 口径）→ 文件级 **10 passed, 1 skipped RC=0**（skip=SQLite 语义 FK 用例），**容器即毁 0 残留**（residual_check: CLEAN）
  - 日志：`/home/wang/.hermes/cache/scratch/a-c3-mysql-suite.out` + `a-c3-mysql-runner.log`；runner 脚本 `a-c3-mysql-run.py`（i1-1 同构改写）
- 未执行项：不重跑 2号 t08 全量 allfiles 批（9 红文件全绿复核归 08 收口条件/协调者）；C1/C2 秒精度专项=2号 `t08c-1` 单，不碰；app 面零改动故无 app 回归跑
- 越界申报：无（1 文件纯测试；app 零变更）
- 交付时间：2026-10-11 16:57 +08:00
- 报告：`reports/TASK-08/c3-lineage-c3-1.md`
- 下一步：等协调者审核合入（纯测试交付，OCR 预期 0 入选=I1-r1/R8/R9 先例口径）；合入后 08 收口条件=两单合入+9 红文件全绿复核