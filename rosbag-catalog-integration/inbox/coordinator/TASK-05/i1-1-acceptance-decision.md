# 验收决定：TASK-05 / i1-1（I-1 夹具 uid 越宽最小修复）——ACCEPT_MERGED

- 决定人：协调者（cron poll `14ae4556629a`，checked_at 2026-10-11T15:40:53+08:00）
- 决定时间：2026-10-11 15:45 +08:00
- 交付：`6823f2ddeb6f905153edea8f767ed29c34cfe4a3`（1号，分支 `scene/task-05-i1-fixture-uid`，wt-01-i1，回执 `receipts/TASK-05/i1-1.md` REVIEW_PENDING）
- 来源：强复审 R2I-20261010-06 VERIFICATION_GAP I-1（LOW，05 侧夹具 bag_uid 28 字符越 `VARCHAR(26)`，真 MySQL setup 1406 零覆盖，既有缺口非本增量引入）

## 独立机械核验（协调者本轮全实测）

1. 单 commit、base `6823f2d~1`=`62a85bf`=合入前 main=origin/main（rev-parse 双核一致）；`62a85bf..6823f2d` = 1 commit。
2. 范围零越界：diff 仅 `tests/test_scene_slice_scheduling.py` 1 文件 +5/-1；app/ 零变更、零迁移；`git show` 逐行核对=仅 `_make_ready_bag` uid 生成点 `hex[:16]`→`hex[:9]` + 3 行注释 + `assert len(uid) <= 26`（同 `6ee858b` 缩短口径）；该文件其余 11 处 `uuid4().hex` 未被触碰。
3. 开发自测证据独立复核：`/home/wang/.hermes/cache/scratch/a-i1-mysql-suite.out`（真 MySQL 8.4.11 STRICT 文件级 **36 passed RC=0**）+ `a-i1-mysql-runner.log`（容器 `i11-accept-1b1c973ecb08` 即毁、residual_check=CLEAN）；SQLite 定向 36 passed + ruff 绿（回执声明与 commit 消息一致）。
4. worktree `wt-01-i1` HEAD=`6823f2d` 干净（status --porcelain 排除 .venv 为空）。

## OCR 口径

串行 OCR I1-r1 实测收口（session `f71727b8`，OCR_EXIT=0，持 `ocr.lock` 稳定 inode）：diff 全在 `tests/*`（default_path 排除）→ **0 入选 0 findings**，与 R8-r1（session `b012b488`）/R9-r1（14:08，coverage 0/0）先例一致，纯测试交付预期口径；独立验证=协调者 diff 逐行核 + 定向/ruff/SQLite 复跑 + 1号真 MySQL 原始日志复核（AC 1/2 均满足，I-1 停止条件=文件级真 MySQL 全绿）。

## 合入

- **--no-ff 合入 main `f9bafb0b44e70e275ba0dd91ca3f0e078e002004`（15:45，推 origin 62a85bf..f9bafb0）**，merge message 记录验收口径。
- 合入后 sanity（主仓独立复跑）：ruff `tests/test_scene_slice_scheduling.py` All checks passed / SQLite 定向 **36 passed RC=0** / alembic heads 单头 `20261009_02_ingest_frozen` / main=origin 双核一致。

## 后续

- I-1 VERIFICATION_GAP 关闭（既有夹具缺口收敛，后续联调口径恢复全绿）。
- 回归确认口径按 1号回执：由 TASK-08 联调验证项（含 I-1 回归验证）动态核对——2号 attempt-1 ACK 时 base 仍 `62a85bf`，按 ACK 口径"若 I-1 已合入则以合入 commit 为准 rebase 复核 alembic 单头并跑文件级真 MySQL"，本合入 commit=`f9bafb0`；不另派 TESTER。
- 强复审 R2I-20261010-06 已 PASS 收口（target `62a85bf`），本 i1-1 为 PASS 后派单的最小修复合入，不触发强复审重跑。