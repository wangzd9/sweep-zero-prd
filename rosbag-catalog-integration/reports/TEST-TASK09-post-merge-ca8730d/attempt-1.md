# 报告：TEST-TASK09-post-merge-ca8730d attempt-1（合入后独立真 MySQL 验证）

- 角色：测试者（TESTER）
- 被测 base：main `ca8730d7050c105b73e9387f4adda182d3a14e64`（= origin/main，fetch 双核一致，`a60bb81` 已 --no-ff 合入）
- 环境：独立 worktree `wt-tester-pm09` @ ca8730d（detached，干净）+ 真 MySQL 8.4.11 STRICT 隔离容器 `tester-pm09-mysql`（镜像 6ea90827b110，net tester-pm09net @172.22.0.2）
- 运行器：`~/.hermes/cache/scratch/t09-tester-pm09/pm09_runner.py`（逐项 fresh DB create_all + FK off 用后即毁）
- 零业务代码改动

## 结果（全部 PASS）

| AC | 口径 | 结果 |
|----|------|------|
| 1a 真 MySQL 06B 核心 | test_scene_result_report + test_scene_result_storage | 60 passed（1 warning）RC=0 |
| 1b slope 接线面真 MySQL | test_slope_vlm_wiring + test_slope_adapter | 44 passed RC=0 |
| 2 迁移链 | alembic upgrade head（MySQL） | RC=0，current=`20261009_02_ingest_frozen (head)` 单头，31 表 |
| 3 SQLite 全量 | pytest tests/ --ignore test_devflow | 813 passed / 10 skipped RC=0 |
| 4a ruff | 3 文件 | All checks passed! |
| 4b 0 残留 | DB/docker/worktree | 全清 0 残留 |

- 总耗时 75.5s；`results.json` all_pass=true。
- 与交付侧自测（06B 60 / slope 44 / SQLite 813）逐项一致，无回归。

## 结论

合入快照 `ca8730d` 独立真 MySQL 8.4.11 STRICT 验证 **PASS**，满足 TASK-09 收口条件（待协调者裁决写 DONE + TASK-10 候选重算）。生产启用 TASK-11 门禁维持未放行（非本单）。

## 资源清理

容器 tester-pm09-mysql / 网络 tester-pm09net / worktree wt-tester-pm09 全部销毁；`SHOW DATABASES LIKE 't_pm09%'` 空；docker ps -a / git worktree list grep rc=1（0 残留核实）。