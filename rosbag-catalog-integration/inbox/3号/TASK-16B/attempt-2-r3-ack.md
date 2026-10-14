# ACK：TASK-16B attempt-2-r3（仅关闭 R1-02/R1-03 残余反例）

- status: ACCEPTED
- 派单：`inbox/3号/TASK-16B/attempt-2-r3-dispatch.md`（2026-10-13 18:03:29+08:00 落盘，status=DISPATCHED，owner=C）
- task/attempt：TASK-16B / attempt-2-r3（强审 `SR-16B-R2-20261013` call `005277e6e60a` REWORK_REQUIRED：R1-01/04/05 已关闭不重做，只关 R1-02/R1-03 两项原 CORRECTION 残余，不扩全量、不引入新队列/业务流程）
- owner：C
- base：`e152465`（r2 冻结 head），延续分支 `c/task-16b-scene-host-proxy` @ `wt-03b-t16b` 续 commit
- 读写范围：只动 `scripts/scene_host_proxy.py` + `tests/test_scene_host_proxy.py`；如 proxy-only 确无法满足原契约→先交具体调用/状态反例+最小接口变更给当前协调者（Codex 接管 owner=codex-user-request-correction-20261013），不模拟后端、不扩文件边界、不降断言
- 强审 result.md 全文已读（`reviews/strongmodel/runs/005277e6e60a43308431b5505f0bf6dc/result.md`）：
  - R1-02 反例=补报/对账继续失败时调用方仍无条件清 recovery，步骤永久卡 RUNNING（4 反例：DONE/FAILED × 未提交丢响应/对账 GET 失败）；边界=步骤回报返回明确确认结果、未确认持久保留可补报事实、按原 attempt 收敛、不重烧模型、遵守真实 Backend 租约（complete-scene 清任务租约，核 REGISTER/complete 调用顺序）
  - R1-03 反例=失败收尾意图未持久化，重启 recover_pending_runs 见 SCENE_RUNNING 再起 execute_run→编排器再次分析（extra_model_invocations=1）；边界=持久区分"执行中恢复"与"待失败终态确认"（原 attempt/目标终态/原因/必要步骤 checkpoint），后者重启只做对账补报收尾，Backend 短时不可用不掉回业务执行
- 12S-C：`wt-03b-t12sc`@`92dcb52` 冻结等待不变；本轮已落短接续检查点（merge `e152465` 零冲突 + 38 passed + ruff 绿，事件 `c-t12sc-finaldep-assembly-checkpoint-20261013`），r3 合入后按接线核验单重算
- 自测口径（按派单）：先新增可复现失败的定向断言（修前失败证据留最小日志）→修复到通过；只跑 proxy/orchestrator 受影响定向组+ruff，复用 r2 已通过的 39 用例及未改模块证据，不重跑全仓
- ACK 时间：2026-10-13 18:2x +08:00（cron 轮 18:16 唤醒消费 pending 指纹 de3cc9de；原 owner 无在途：`wt-03b-t16b` porcelain 干净 HEAD=`e152465`，ps 无 C 业务进程）
- 交付：续 commit 冻结 r3_head + 回执 `receipts/TASK-16B/attempt-2-r3.md`（完整 SHA、两问题 ID 设计/命令 rc/关键断言/实际边界）→ 协调者增量 OCR + 原授权两问题复审 + TESTER 独立核恢复；不等待 OCR 先交付
- 停止条件：两项反例全部关闭且解除条件自测通过；同根因两轮仍未解决→报告当前协调者，不无限重试