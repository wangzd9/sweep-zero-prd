---
task: TASK-06B
attempt: 1-rework
owner: 2号
status: ACCEPT_MERGED
decision: ACCEPTED
base: 3b78736
merged_commits: 6e6bb73 + 6b21c91（--no-ff 合并提交 2e674b2，主会话 2026-10-10 09:07 执行）
updated: 2026-10-10 11:26（机械验收化身补核收口）
---
# TASK-06B attempt-1-rework 验收结论

**决策：ACCEPTED（已合入 main 2e674b2，化身 11:2x 补核并推送 origin）**

## 机械核验证据（化身 2026-10-10 11:2x，main eff0479 上）

1. **范围**：`git diff --name-only 3b78736..2e674b2` = 7 文件（app/api/__init__.py、app/api/scene_results.py、app/schemas/scene_result.py、app/services/scene_publish_service.py、scene_result_report_service.py、scene_slice_service.py、tests/test_scene_result_report.py），+1966/-1，全部 06B scope，零 .venv/环境产物。
2. **wt-01 旧初版 2dc80c7 已完全吸收**：`git diff main..2dc80c7 -- <上述 7 文件>` 仅 tests/test_scene_result_report.py 差 5+/11-（= 10-05 rework 修掉的两个用例旧版），6 个 app 文件与 main 逐字节一致 → worktree HEAD 无需再动。
3. **base 正确**：2e674b2 父链 = 3b78736 + 6b21c91（--no-ff），指向返修单指定 base。
4. **定向复跑（化身独立，main eff0479）**：`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q tests/test_scene_result_report.py tests/test_scene_result_storage.py` → **49 passed**（exit 0，3.52s）。
5. **全量**：804 passed / 10 skipped / 3 failed（2号 08:5x 实测，3 failed 全部 tests/test_devflow.py 沙箱环境性，同基线，不算回归）——化身本轮未重复全量（49 定向 + 主会话合入前全量已覆盖）。
6. **ruff**：check + format 2号 08:5x 全绿（All checks passed / 202 files already formatted）。
7. **推送**：`git push origin main` 2e674b2..eff0479 成功（gitlab-local，11:2x 执行；此前 main 领先 origin 1 个 commit）。

## 门禁与在途事项

- **OCR B8a 补跑已收口（2026-10-10 11:48，主会话 flock 代跑）**：`ocr review -c 6e6bb73 --exclude 'tests/*'`（session 819c9dab，b8a-exit=0）= **6 findings（1 high + 4 medium + 1 low）**，全文见 ~/.hermes/cache/scratch/ocr-b8a-06b-app.log，批次账与定位见 reviews/TASK-06B/attempt-1-rework/ocr-batches.md。high = 多场景 run 完成路径疑似死锁（finish_scene_run 按全场景 summarize）。
- **2026-10-10 12:14 机械化身（持 coordinator.lock）补记**：fresh 模块首审出 high，findings 定性/回派返修属深度裁决 → 已写 inbox/coordinator/TASK-06B/NEEDS_MAIN_REVIEW.md 挂主会话，**本 decision 的 ACCEPT_MERGED 维持（合入事实不变），但 06B 任务行保持 🔁 不收口**，等主会话逐条裁决后回派 2号或注记误报；B8b（tests 部分）是否补跑一并待裁决。
- **06 聚合不解锁**：R2B 首审（R2-20261010，review-bundle-20261010/）等用户手动触发，06 父任务维持 WAITING。
- 06B 合入门禁解除后，TASK-08 联调依赖（03/04/05/06）仍等 06 聚合。

## 返修对照（返修单 3 条逐条核实）

1. `_create_run` 透传 reanalysis_id —— tests 文件 main 版本在位（6b21c91 +5/-11 已含）。
2. 两个失败用例 run2 带独立 reanalysis_id —— 定向 49 passed 含 `test_late_old_version_no_rollback`/`test_failed_keeps_old_current` 复跑通过（08:49 时 2 failed 已消除）。
3. 未改 05 服务代码 —— diff 范围内无 app/services/pipeline* 等 05 文件，仅 scene_slice_service.py 3 行（06B 本 scope 接线）。