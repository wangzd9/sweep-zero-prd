# ACK：TASK-07B attempt-1 统一界面·人工纠错/下架

- status: ACKED
- ACK 时间：2026-10-12 15:01 +08:00
- 派单路径：`inbox/2号/TASK-07B/attempt-1-dispatch.md`（14:50 派单）
- task/attempt：TASK-07B / attempt-1
- owner：B（cron-b-poll-6f7471d8747c-20261012-145753）
- base：main `502bf8e`（派单指定，= 本地 main 与 github/main；**注意：origin/main 本轮 fetch 实测仍为 `caf385b`，`502bf8e` 尚未推 origin，开发分支从本地 main `502bf8e` 新建**）
- 分支/worktree：本轮开工时新建 `scene/task-07b-manual-revision-withdraw` @ `wt-04a-t07b`（.venv 软链主仓）
- 范围确认与派单一致：
  1. 数据面：审计表 `scene_manual_revision`（或评估 pipeline_event 承载，最小一致为准），迁移含 downgrade；不新增 bag_record.status 枚举、不动 03~06B 状态机/幂等/发布；
  2. API：`PATCH /api/v1/bags/{uid}/scene-labels` + `POST /api/v1/bags/{uid}/withdraw`，row_version/原因/幂等键/操作者证据四要素；只接受 SCENE_SLICE，ORIGINAL 父包 422 明确拒绝；
  3. 页面：切片详情纠错/下架入口 + 审计展示；已下架退出默认视图、all 可见标注；旧入口不回归；
  4. 测试：定向（冲突 409/幂等重放/保留模型原结果/下架检索语义/父包 422）+ 既有全量 0 红（基线 849 passed）+ ruff 绿 + 页面实测证据（自包含 uvicorn 口径同 07A）；
  5. 若必要迁移：真 MySQL 8.4 隔离库 upgrade/downgrade 往返实测。
- 停止条件：交付 commit + 回执 `receipts/TASK-07B/attempt-1.md`（REVIEW_PENDING）+ 报告 `reports/TASK-07B/attempt-1.md`；不占第二开发槽。
- 未执行项（开工前记录）：无。