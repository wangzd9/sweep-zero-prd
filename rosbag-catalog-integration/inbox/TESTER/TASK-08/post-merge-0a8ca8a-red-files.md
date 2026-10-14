# 派单：TASK-08 合入后 9 红文件全绿复核（post-merge-0a8ca8a）

- task/attempt：TASK-08 / post-merge-0a8ca8a（合入后验证，非新开发）
- 角色：TESTER（独立真 MySQL 取证，不采信执行者自测）
- 背景：TASK-08 收口两单均已 --no-ff 合入 main——c3-1（1号 lineage 夹具 uid，`98f6c88`，17:02）+ t08c-1（2号 C1/C2 秒精度专项，`bf48a45`→main `0a8ca8a`，19:17）。attempt-1 联调（2号 `reports/TASK-08/attempt-1.md`）曾定 10 红文件（真 MySQL 55 PASS/10 FAIL）：其中 9 个由 t08c-1 修复、`test_scene_slice_scheduling` 由 c3-1/i1-1 覆盖；t08c-1 交付自测已证 8 红文件文件级全绿 + 06B 回归 35/25 + 迁移链 RC=0（回执 `receipts/TASK-08/c1c2-t08c-1.md`），但**合入产物 main `0a8ca8a` 需 TESTER 独立取证**（协调者不代跑日常验收测试）。
- 固定快照：main `0a8ca8a`（= origin/main，19:17 已推 gitlab-local；合入 sanity alembic 单头 `20261009_02_ingest_frozen` + ruff 7 文件绿已核）
- 范围（真 MySQL 8.4.11 STRICT 隔离库，对齐 t08/t08c 口径：独立新库 + FK off + create_all，用完即毁 0 残留）文件级跑下列 9 红文件，要求全部 RC=0：
  1. `tests/test_bag_cleanup_api.py`
  2. `tests/test_bag_cleanup_concurrency.py`
  3. `tests/test_bag_cleanup_worker.py`
  4. `tests/test_clone_published_dataset_records.py`
  5. `tests/test_source_register_purpose.py`
  6. `tests/test_pipeline_api.py`
  7. `tests/test_lineage_lifecycle.py`
  8. `tests/test_web.py`
  9. `tests/test_scene_slice_scheduling.py`（c3-1/i1-1 覆盖，确认合入后仍绿）
- 附加不破坏项：
  - 06B 回归 `tests/test_scene_result_report.py`（35）+ `tests/test_scene_result_storage.py`（25）真 MySQL 仍全绿
  - 迁移链 `tests/test_migration_lineage_rollback.py` + `tests/test_china_standard_time_migration.py` RC=0（零迁移改动，链未被破坏）
  - `tests/test_scene_slice_lineage.py`（c3-1 交付口径：真 MySQL 10 passed + 1 skipped）
- AC：上述 9+2+2+1 文件真 MySQL 文件级全绿 RC=0 + 隔离库/用户 0 残留 + 回执 REVIEW_PENDING 落盘
- 停止条件：全绿交付；任一项 FAIL → 定位到 app 文件:行 + 最小复现，回执说明根因方向（供协调者回派开发 owner，不自行改业务代码）
- 路径：独立 worktree 或干净检出 main `0a8ca8a`；不占开发槽；5 分钟巡检/20 分钟汇报持续
- 交付：回执 `receipts/TASK-08/post-merge-0a8ca8a-red-files.md` + 报告 `reports/TASK-08/post-merge-0a8ca8a-red-files.md`（环境口径、逐文件 passed/failed、命令/退出码、隔离库清理证据）
- 不复跑：t08c-1 已证且与本单无关的 SQLite 全量/定向（本单只看真 MySQL 合入产物）；06B 已收口场景（S1/S2/S3/S4/B8a/B8c/r6）不重跑