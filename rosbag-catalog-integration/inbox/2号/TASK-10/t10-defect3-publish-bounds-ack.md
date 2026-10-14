# ACK：t10-defect3-publish-bounds（独立 ACK，不改派单正文）

- task/attempt: TASK-10 / t10-defect3-publish-bounds / r1
- owner: cron-b-poll-6f7471d8747c-20261012-011753（执行者 B，前端功能开发群）
- 派单路径: `inbox/2号/TASK-10/t10-defect3-publish-bounds.md`（status 行已改 ACKED）
- base: `a77aa45`（fetch 双核一致 = origin/main，含 #1 `277e40f` + #2 `d4719f6`）
- 分支/worktree: `scene/task-10-defect3-publish-bounds` @ `wt-04a-t10d3`（新建，.venv 软链主仓）
- 时间: 2026-10-12 01:20 +08:00
- 范围确认: 允许改 `app/services/scene_publish_service.py`、`app/services/scene_result_report_service.py`、`tests/` 定向；禁止碰 `source_service.py`/`app/scene/slope/writer.py`/04B/05 域；不弱化 writer 校验、不删既有断言、`derive_storage_offset` fail-closed 保持。
- AC: 定向测试全绿（offset≠0 发布→`/results`→`/complete-scene` 200 + 旧记录无 actual 边界 409 fail-closed）+ ruff 绿；回执 `receipts/TASK-10/t10-defect3-publish-bounds.md`。
