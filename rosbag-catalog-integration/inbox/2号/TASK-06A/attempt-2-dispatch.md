---
task: TASK-06A
attempt: 2
owner: 2号
status: ACCEPTED
dispatched_by: 协调者
updated: 2026-10-09 11:45
base: main 1946718（验收后若 main 推进，以合入前最新 main 为 base 重算）
worktree: /home/wang/.local/state/rosbag-scene/wt-04a（分支 scene/task-06a，当前 c4ce66c）
---
# TASK-06A attempt-2 返修派单（协调者 OCR 验收结论）

OCR（c4ce66c，协调者代跑，session b29b4ae2）8 条，逐条对照代码核实后：
**2 high 真实 bug（必修）、1 medium 兜底缺失（必修）、3 建议项（建议修）、2 low（可选）。**
逐条意见与验证方式全文见 `receipts/TASK-06A/attempt-1.md` 尾部"attempt-2 返修指令"段。

## 必修
1. **high-1**：`scene_result_query.py` search_lineage_children 分页续查条件补 `or_(anchor, started_at.is_(None))`
   （对照同文件 search_scene_bags 正确分支）；回归测试：构造 NULL started_at 子包，锚定在
   非 NULL 行翻页，断言 NULL 子包在第二页出现。
2. **high-2**：expected_segment_count / registered_segment_count 语义对齐。推荐
   expected=manifest 全部区间数（与 registered 同基数）；若你判定应保留可发布口径，
   字段改名 publishable_segment_count 并在回执"契约选择说明"写明 06B 的完整性比较方式。
3. **medium**：幂等写路径（登记/换版/切 current）补 IntegrityError 兜底：捕获后重查，
   已是目标态→200 重放，冲突→409，其他→500（不得裸 500 违背模块错误码契约）。

## 建议修
4. switch_current 的"current 指针唯一性"：确认依赖 03B 合入后的迁移索引情况（03B 未合入时
   该不变式只有行锁）；在代码注释写明依赖，若 03B 迁移已含 (parent,scene,current) 唯一约束则补断言测试。
5. 血缘查询 N+1：list_lineage 改 JOIN 或一次 IN 批量取。
6. 冗余二次查询（get_after_insert 与 insert 前 SELECT 重复）：合并。

## 可选（low）
7. 死代码清理；8. 分页 has_more 的 +1 探测在超大量数据下的性能说明注释。

## 交付要求
- attempt-2 回执（receipts/TASK-06A/attempt-2.md，协议模板），status=REVIEW_PENDING
- 全量 + 定向 pytest 真实退出码；ruff 全绿；commit 只含本任务文件
- OCR 由协调者代跑（flock inbox/ocr.lock），不要自跑