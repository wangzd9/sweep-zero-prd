# ACK：TASK-16A t16a-post-merge-verify 独立验证（attempt-1）

- status: ACKED
- ACK 时间：2026-10-13 09:24 +08:00（测试者 poll cron 167580c0500b，preflight checked_at 2026-10-13T09:19:53+08:00 之后发现本派单，claim `cron-tester-poll-167580c0500b-20261013-091953-t16a` 09:24:49）
- 派单：`inbox/TESTER/TASK-16A/t16a-post-merge-verify-dispatch.md`（协调者 r138）
- 被测基线：main `6fb42c4821bc5dfa54531c88fbc0ef1578715748`
- 快照核对：主仓 `/home/wang/work/rosbag-catalog` 实测 `git rev-parse HEAD`=origin/main=`6fb42c4821bc5dfa54531c88fbc0ef1578715748`（=被测基线，checkout 一致）；工作树 untracked 仅 scratch/诊断脚本与 `app.db`（非代码改动），无 tracked 修改。
- 环境口径：真 MySQL 8.4（`docker.m.daocloud.io/mysql:8.4`，8.4.11 容器内 SELECT VERSION() 实测）隔离容器 + 独立 docker 网络、无宿主端口映射、用完即毁 0 残留；不触碰 16B/16C 在途 worktree；SQLite 定向复跑用主仓 `.venv`（alembic/pytest 在案）。
- 范围：
  1. 真 MySQL 8.4 全链迁移 fresh upgrade head → downgrade -1（至 `20261012_01_scene_manual`）→ upgrade head，三趟 RC=0；`alembic_version` 值序列取证（单头 `20261013_01_scene_intake`，无 1406 长名截断）。
  2. AC-14/08 面 MySQL 口径抽查：`intake_root_id`/`intake_snapshot_json` 列存在 + 'self_built' 回填真 MySQL 取证（双根同名/跨盘 rename 拒绝/intake 快照绑定/场景异常不回退自建 中迁移承载字段面）。
  3. SQLite 定向：`tests/test_scene_intake_isolation.py`/`test_scanner_stability.py`/`test_ingest_config_api.py`/`test_ingest_config.py`（56 口径）+ 07B 面 3 文件（`test_task07b_*_revision.py`）主仓 .venv 独立复跑。
- 已知观察项（按派单口径，勿判 16A 回归）：`tests/test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time` 单跑顺序依赖失败在 `502bf8e` 基线已存在；如复跑命中按此口径申报，不阻塞。
- 交付：`test-receipts/TEST-TASK16A-post-merge/attempt-1.md`（容器/库身份、命令/退出码、逐 AC 证据、残留清理核对）。
- 停止条件：任一迁移往返 RC≠0 或 AC-14/08 MySQL 面取证失败 → FAIL 申报定位（迁移链/接线/回填），不代修。