# ACK：TASK-16C attempt-1 界面最小补齐

- status: ACKED
- 派单路径：`inbox/2号/TASK-16C/attempt-1-dispatch.md`（协调者 r136，2026-10-13 08:5x 落盘，本侧 08:37:53 巡检回合发现并领取）
- task/attempt：TASK-16C / attempt-1（REQ-16、REQ-05 / AC-16、AC-05）
- owner：B（前端功能开发群，cron poll `6f7471d8747c`）
- base：main `4b9f30a`（07B 整链已合入；`3d2a075` 为纯文档 changelog 候选，不入本链）
- 分支/worktree：`b/task-16c-scene-ui-minimal` @ `/home/wang/.local/state/rosbag-scene/wt-04a-t16c`（2026-10-13 08:4x 新建，HEAD 实测 `4b9f30a`，洁净）
- 时间：2026-10-13 08:4x +08:00（claim owner `cron-b-poll-6f7471d8747c-20261013-083753-t16c`）
- 边界确认：独占 `app/web/{bags,pipelines}.py`、相关模板/静态资源、Bag 查询及共用分类模块、`GET /api/v1/bags` 集合路由/装配及对应测试；不碰 `app/config.py`/`app/scanner/`/`ingest_service.py`/`source_service.py`/`bootstrap.py`/迁移面（16A 域）/`scripts/`（16B 域）；保留 07B 审计/修订面不回退；零新表/迁移
- 自测口径：AC-16 + AC-05 新增项定向测试全绿 + 浏览器/API 口径（三类原始行、四种切片态、双用途原包、旧书签兼容、筛选保留/分页/未知类型、八步终态刷新、不相容组合空结果）+ ruff + `alembic heads` 单头（零迁移面）
- 交付口径：commit + 回执 `receipts/TASK-16C/attempt-1.md` + 报告，REVIEW_PENDING
- 停止条件：发现需扩面（新表/迁移/16A/16B 域文件/预览统计）立即停并回报协调者，不自行扩