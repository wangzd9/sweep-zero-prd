# ACK：TASK-07A attempt-2-r1 最小返修

- status: ACKED
- task/attempt：TASK-07A attempt-2-r1（返修 finding #1 view-tabs 丢筛选 + #2 col-scene 列宽）
- owner：B（前端功能开发群，cron poll 6f7471d8747c，本轮 owner `cron-b-poll-6f7471d8747c-20261012-131753`）
- 派单路径：`inbox/2号/TASK-07A/attempt-2-r1-dispatch.md`（2026-10-12 13:15 +08:00，协调者 r79 收口轮）
- base：`f94d006`（attempt-1 冻结 commit，分支 `scene/task-07a-visibility-lineage` 延续，worktree `wt-04a-t07a`）
- 范围：`app/templates/bags.html`（tab 链接）+ `app/static/bag-search.css`（col-scene 宽度）+ `tests/test_task07a_visibility.py` 补 1-2 条定向断言；不新增范围，bag_role 下拉不加（协调者已裁决接受现状）
- ACK 时间：2026-10-12 13:19 +08:00
- 计划：改码→定向+过滤组回归+ruff→自包含 uvicorn 页面实测两条→单 commit（base f94d006）→回执 `receipts/TASK-07A/attempt-2-r1.md` + 报告 `reports/TASK-07A/attempt-2-r1.md`（REVIEW_PENDING 冻结）