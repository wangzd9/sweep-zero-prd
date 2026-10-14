# ACK：TASK-07A attempt-1 统一界面·可见性与检索（B）

- status: ACCEPTED
- ACK 时间：2026-10-12 09:49 +08:00
- 派单：`inbox/2号/TASK-07A/attempt-1-dispatch.md`（09:45，用户授权 P1 提前）
- task/attempt：TASK-07A attempt-1
- owner：B（执行者B·前端功能开发群）
- base：main `453da0c`（= origin/main，ACK 时双核一致）
- 分支/worktree：本轮开发时新建 `wt-04a-t07a`（任务专属 worktree，分支名开工时确定）；上一任务 `wt-04a-t10d3` 冻结不动
- 时间：2026-10-12 09:49 +08:00
- 范围确认：①lineage API（双向+非场景包 200 null，零新迁移）→ ②/pipelines 场景可见 → ③/bags 三视图+筛选+旧入口不回归 → ④详情双向跳转 → ⑤回归+页面实测证据（本地 real 栈 453da0c，DB 口径，不加临时挂载）
- 停止条件：实现冻结后交付 `receipts/TASK-07A/attempt-1.md` + `reports/TASK-07A/attempt-1.md`（REVIEW_PENDING），等协调者机械核验/OCR/合入；接口冲突先报不改契约