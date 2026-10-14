# 派单：TASK-08 attempt-1（模块联调、故障与兼容）

- task/attempt：TASK-08 / attempt-1
- 角色：2号（B）
- 固定 base：main `62a85bfb6b3791ebfa706cce0125bb217635126f`（注意：1号 I-1 小单 `i1-fixture-uid-dispatch.md` 并行在途、将先合入——若 ACK 前已合入，以 I-1 合入 commit 为新 base rebase 并复核 alembic 单头）
- 范围（TODO §3 TASK-08 卡）：
  - 接收事件→调度→结果回报全链路联调（local stack + 真 MySQL 8.4 隔离库，容器用完即毁 0 残留）
  - 重启/并发/发布断点、清理竞争和旧流程回归
  - 小规模 SQL、索引、分页/查询次数、耗时/空间检查
  - **I-1 回归验证项**：I-1 合入 commit 可运行时，真 MySQL 隔离库跑 `tests/test_scene_slice_scheduling.py` 文件级确认全绿并附日志（I-1 未合入则报告中注明，等协调者后续安排）
- AC（REQ-01～08、10、13 / AC-01～08、10、13 的 P0 部分）：
  - 三用途、配置冻结、子包不递归、旧自建/NVIDIA 不回归；完整模块不保留测试旁路，原文件不变
- 边界：
  - 不等待页面/其他场景，不卡十万/百万压测；mock 只证明契约
  - **不改业务代码**：发现失败在回执+报告记录影响任务与最小复现，由协调者回派最小修复，不跨模块自行改码
- 交付：联调报告 `reports/TASK-08/attempt-1.md` + 回执 `receipts/TASK-08/attempt-1.md`（REVIEW_PENDING），附环境口径、每场景命令/退出码/关键日志路径、I-1 回归项证据
- 路径：新建任务分支 `scene/task-08-integration` + 独立 worktree（如 `wt-04a-t08`），不动在冻 worktree
