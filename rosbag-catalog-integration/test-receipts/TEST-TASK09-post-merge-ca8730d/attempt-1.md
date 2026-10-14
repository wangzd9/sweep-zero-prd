# 回执：TEST-TASK09-post-merge-ca8730d attempt-1（合入后独立真 MySQL 验证）

- status: **TEST_REPORT_PENDING**
- 角色：测试者（TESTER，独立取证）
- 派单：`inbox/TESTER/TASK-09/post-merge-ca8730d-verify-dispatch.md`（21:4x，协调者 cron poll 回合）
- 交付时间：2026-10-11 21:49 +08:00
- 被测 base：**main `ca8730d7050c105b73e9387f4adda182d3a14e64`**（= origin/main，git fetch 双核独立复核一致；`a60bb81` 已 --no-ff 合入，merge-base --is-ancestor a60bb81 main = yes）
- 被测改动：`a60bb81` 3 文件 +187/-3（`app/scene/slope/vlm.py` / `app/scene/slope/adapter.py` / `tests/test_slope_vlm_wiring.py`），影响面=VLM 客户端构造，**抽帧/segment/时间映射/迁移 0 改动**
- 验收 decision 参考：`inbox/coordinator/TASK-09/attempt-1-acceptance-decision.md`（ACCEPT_MERGED，合入后验证挂 TESTER）

## 独立验证环境（口径同 TESTER pm08/t09_plug 先例，独立取证不代开发）

- 独立 detached worktree 检出 `ca8730d`（干净，`wt-tester-pm09`，.venv 软链）→ 验证后已 `git worktree remove --force`
- 真 **MySQL 8.4.11** STRICT 隔离容器 `tester-pm09-mysql`（镜像 6ea90827b110，独立网络 `tester-pm09net` @172.22.0.2，root 用户）→ 验证后容器+网络已毁
- 逐文件新库 create_all + FK off（`SET SESSION FOREIGN_KEY_CHECKS=0`），每项 fresh DB 用后即毁
- 运行器 `~/.hermes/cache/scratch/t09-tester-pm09/pm09_runner.py` + plug `pm09_plug.py`；生产默认 PyMySQL
- **零业务代码改动**（仅测试 scratch 运行器/plug）

## AC 结果（全部 PASS，独立复跑，非采信交付侧自测）

| # | AC | 独立复跑命令/口径 | 结果 |
|---|----|------|------|
| 1a | 真 MySQL 06B 核心不回归 | `pytest tests/test_scene_result_report.py tests/test_scene_result_storage.py` @ t_pm09_0 | **60 passed**（1 warning），RC=0 |
| 1b | slope 接线面真 MySQL | `pytest tests/test_slope_vlm_wiring.py tests/test_slope_adapter.py` @ t_pm09_1 | **44 passed**，RC=0（=交付侧 SQLite 44 口径在真 MySQL 复跑一致） |
| 2 | 迁移链 upgrade head | `alembic upgrade head` @ t_pm09_alembic（DATABASE_URL 指 MySQL） | **RC=0**，`alembic current`=`20261009_02_ingest_frozen (head)` **单头**，31 表，与交付/协调者口径一致（本次零迁移改动，快速确认达成） |
| 3 | SQLite 全量不回归 | `pytest tests/ --ignore=tests/test_devflow.py` | **813 passed / 10 skipped**，RC=0（=交付侧口径一致） |
| 4a | ruff 3 文件 | `ruff check app/scene/slope/vlm.py app/scene/slope/adapter.py tests/test_slope_vlm_wiring.py` | **All checks passed!** |
| 4b | 隔离资源 0 残留 | `SHOW DATABASES LIKE 't_pm09%'` + docker ps -a + worktree list | **DB 空 / 容器+网络+worktree 全毁 / grep rc=1**，0 残留核实 |

## 结论

- **合入快照 `ca8730d` 独立真 MySQL 8.4.11 STRICT 验证全部 PASS**，交付侧自测口径（06B 60 / slope 44 / SQLite 813）逐项独立复跑一致，迁移链单头无破坏，ruff 绿，隔离资源 0 残留。
- 未发现 app 行为回归；无失败项，无 FAIL/BLOCKED。
- 证据：`~/.hermes/cache/scratch/t09-tester-pm09/results.json`（all_pass=true）+ `logs/pm09_*.log`（5 项逐文件日志）。
- 门禁影响：TASK-09 合入后独立验证 PASS → **满足 09 收口条件**（待协调者裁决写 DONE + TASK-10 候选重算派单）；本 TESTER 不代裁决、不写 DONE、不派单。
- 生产启用 TASK-11 门禁维持未放行（非本单范围）；VLM 500 帧/假阴性事实为 TASK-11 前置输入（协调者 decision 已记）。

## 未执行项（如实申报）

- 无。全部 4 项 AC 均独立执行到 RC=0。
- 本单为**合入后快照验证**，非真实坡道样本/VLM 端到端重跑（该面已在 attempt-1 交付侧按用户授权完成并获协调者 ACCEPT_MERGED，本单不影响其结论）。

## 交付三件套

- 报告：`reports/TEST-TASK09-post-merge-ca8730d/attempt-1.md`
- 回执：本文件 `test-receipts/TEST-TASK09-post-merge-ca8730d/attempt-1.md`
- 下一步：交协调者裁决；如 PASS 收口→09 DONE→TASK-10 派单，届时按新 attempt 开工。