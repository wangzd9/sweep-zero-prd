# TESTER 派单：TASK-16A 独立验证（post-merge，2026-10-13 09:2x，协调者 r138）

- **task/attempt**：TASK-16A / t16a-post-merge-verify（独立验证 attempt-1）
- **owner**：测试者
- **被测基线**：main `6fb42c4`（=origin=github 三核一致；16A rebase 链 995e351/bed9006/24d934e/da304e2 已全部入 main）
- **范围（只取证，不改业务代码）**：
  1. **真 MySQL 8.4 全链迁移往返**（本单核心，SQLite 全绿遮 MySQL 口径的既有教训）：隔离库 fresh upgrade head（链起点→`20261013_01_scene_intake`）→ downgrade 一步至 `20261012_01_scene_manual` → 再 upgrade head，三趟 RC=0；`alembic_version` 值序列取证（单头 `20261013_01_scene_intake` 25 字符内，无 1406）。
  2. **AC-14/08 面（MySQL 口径抽查）**：双根同名/跨盘 rename 拒绝/intake 快照绑定/场景异常不回退自建 中迁移承载字段（intake_root_id/intake_snapshot_json 列存在+回填 'self_built'）真 MySQL 取证。
  3. **SQLite 定向不回归**：`tests/test_scene_intake_isolation.py`/`test_scanner_stability.py`/`test_ingest_config_api.py`/`test_ingest_config.py`（56 口径）+ 07B 面 3 文件（`test_task07b_*_revision.py`）在主仓 .venv 独立复跑。
- **已知观察项（勿判 16A 回归）**：`tests/test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time` 单跑顺序依赖失败在 07B 合入前基线 `502bf8e` 已存在（协调者独立二分核实），全模块口径通过；如复跑单跑失败按此口径申报即可，不阻塞。
- **停止条件**：任一迁移往返 RC≠0 或 AC-14/08 MySQL 面取证失败 → 直接 FAIL 申报定位（迁移链/接线/回填），不代修。
- **交付**：`test-receipts/TEST-TASK16A-post-merge/attempt-1.md`（含容器/库身份、命令/退出码、逐 AC 证据、残留清理核对）。
- **资源**：MySQL 8.4 隔离容器用完即毁，0 残留口径；不得触碰 16B/16C 在途 worktree。
