---
task: TASK-06B
attempt: 1
owner: 2号
status: ACCEPTED
dispatched_by: 协调者
updated: 2026-10-09 15:2x
base: main 8bd5618（=origin/main，含 06A 终版 e92ef17 / 05 四 commit / 03B a8fac99）
worktree: /home/wang/.local/state/rosbag-scene/wt-04a（分支自 8bd5618 新开 scene/task-06b；.venv 软链主仓）
---
# TASK-06B attempt-1 派单：正式回报 API、原子发布、幂等登记、换版/对账

## 范围（TODO §3 TASK-06B 卡）
- 阅读：05（scene_slice_service/orchestrator 场景租约面）、04B（slope writer/CDR/manifest）、
  06A（scene_result_service/scene_result_query 终版 e92ef17）；DESIGN §6/7/9。
- 修改：真实回报/complete-scene API、staging 校验/原子发布、子 Bag 登记、换版/对账及重试；
  执行面结果路由（/results 归本任务，05 已声明不实现）。
- 允许文件：新增 scene 结果回报路由/服务 + 对应测试；复用 06A 仓储/查询（不另建切片索引）、
  05 的 SCENE_RUNNING/CANCELLING/SCENE_EXEC_HOST 租约通道（只消费不修改 05 枚举）。
  需改共享入口（app/api/__init__.py 路由注册、app/schemas/__init__.py、config）时：
  按 DESIGN §11.3 属协调者串行合入范围——commit 里带上你的入口改动，回执申报，协调者合入时接线。

## 契约输入（06A 终版已确认，直接引用）
1. **完整性门禁**：expected_segment_count == registered_segment_count **等值比较**
   （同基数 = manifest 全部区间数含 flat）；可发布子集用 `list_segments(publish_only=True)`
   与 manifest `expected_slice_keys` 核对，不混入段数基数。
2. **换版**：`switch_current` 3 次有界重试后 409（重放语义），路由层 409 映射兼容；
   新版失败保旧 current 不动。
3. **staging_offset**：writer storage_offset_ns 由编排层从 manifest 推导，不可推导则阻塞发布
   （TODO 交接约束，失败语义写回执）。
4. PENDING/未 complete 的版本不展示可用（current=False 默认不可见）。

## 验收标准（任务卡 AC）
- 真实租约/源代次验证（05 lease 通道 + 03B bound_source_generation）；重复单子包幂等
  （06A IntegrityError 兜底语义重放 200）；发布后登记故障补偿；晚到旧版不倒退；
  新版失败保旧/无命中切空；PENDING 不展示可用。
- 边界：文件非空/可打开/时间证据 + 数据库登记均完成才可用；不复制父/子文件；
  输出不入 Scanner；预览非阻断。

## 交付要求
- attempt-1 回执（receipts/TASK-06B/attempt-1.md，PROTOCOL 模板）：owner/status/base/
  output_commit/验证证据；commit 只含本任务文件（零 .venv 产物）。
- 全量 + 定向 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q` 真实退出码；
  ruff check+format 全绿；devflow 沙箱 3 例 worktree 环境性失败不算回归（对照 main 单跑即可）。
- OCR 由协调者代跑（flock inbox/ocr.lock），**不要自跑**（06A 期间出现过双 ocr 挤单挂死）。
- 多轮唤醒：频繁 commit 检查点，中断可 resume；同因返修上限 2 轮。