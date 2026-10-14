**结论：REWORK_REQUIRED，阻塞 TASK-16B 模块合入。** 跨 TTL 续租及首 GET 故障的原反例已修复，但本轮冻结 AC 内仍有两处可复现残余。子包车辆、路径、时区及部署装配增量未发现阻塞缺陷。

- review_id：`SR-SPRAY-FINAL-R4-20261013`
- 触发：`AUTHORIZED_CODEX`
- grant_id：`6b2d83fb978644b7938424e4652024ce`
- call_id：`f1de0b11c9f44a9185c8f28054cd9c38`
- base：`6ddcbcb0200450b7cc0c9d337ac9c953f58d5560`
- target／实际 HEAD：`29af08a58819790fe6cc467603091817a5b705fb`
- 契约：本包冻结需求及 AC；独立 `contract_version`、`semantic_hash` 未提供。
- 范围：9 个增量文件、必要收尾调用链和引用验证证据；未重审已关闭问题、B 算法、UI 或生产门禁。

| 裁决对象 | 结果 |
|---|---|
| R1-02 | 跨 TTL 续租已修；明确停写后的零补写仍未满足，见 R4-02。 |
| R3-01 | 成功意图保存前首 GET 的原反例已关闭；后续通信故障仍有提前永久阻塞分支，见 R4-01。 |
| 子包索引／装配 | 本轮增量核验通过；不等于生产验收通过。 |

**R4-01｜CORRECTION｜中｜已确认：终态幂等重放的一次通信故障被永久阻塞**

- **对应 AC：** 后续 GET／step／complete 故障保持成功待收尾语义，在既定有界窗口内对账收敛。
- **预期／实际：** complete 已提交但响应丢失后，应按原身份重放确认。实际[终态重放分支](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/f1de0b11c9f44a9185c8f28054cd9c38/snapshot/scripts/scene_host_proxy.py:1025)把所有重放异常转换为 `FinalizationBlocked`，包括一次性超时；外层立即持久 `FINALIZATION_BLOCKED` 并释放 ACTIVE。
- **触发与证据：** run 为同 attempt 的 `SCENE_DONE`，首次幂等重放注入 `TimeoutError`，下一次相同请求即可成功。调用实际 `_finalization_loop` 的只读内存复现结果为：`replay_calls=1`、触发 `BLOCKED`、`active=False`；随后相同重放成功。
- **后果：** 尚未耗尽收尾窗口就停止自动对账；重启恢复跳过该台账，后续 `/run` 返回 409，短暂通信故障被升级为人工对账。
- **最小修复：** 区分确定的身份／内容冲突与通信不确定；超时、连接故障和可重试服务错误继续保留成功意图。同步核对 `lease_terminal` 停止标记，避免终态清租约后提前终止合法幂等对账。
- **解除条件：** 覆盖“提交丢响应→终态重放一次／持续故障→窗口内恢复”，确认正确清台账、零模型／业务重执行、零终态后步骤补写；确定冲突和超窗仍有限 BLOCKED。**阻塞模块合入。**

**R4-02｜CORRECTION｜高｜已确认：失败收尾首次补报绕过明确停写检查**

- **对应 AC：** 明确停写时先持久 `FINALIZATION_BLOCKED`，零步骤／status／complete 补写。
- **预期／实际：** `_finalization_loop` 有入口停写检查，但[失败收尾入口](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/f1de0b11c9f44a9185c8f28054cd9c38/snapshot/scripts/scene_host_proxy.py:954)先调用 `_report_steps`、`_confirm_terminal`，仅补报失败后才移交该循环。
- **触发与证据：** `stop_cancel` 已置位、`reason="lease_lost"`，任务 token 尚有效。此状态可由资源心跳持续失败、任务心跳仍成功产生。使用实际 `_finish_failure`、`_report_steps` 和既有状态机替身复现，仅将文件操作替换为内存存储：**10 次 step 写入、1 次 `SCENE_FAILED` 写入、未 BLOCKED、台账被清除**。
- **后果：** 明确停写后仍能补写业务状态，违反本轮零补写约束。现有 stop 测试直接调用 `_finalization_loop`，未覆盖此前入口。
- **最小修复：** 首次失败收尾在任何补报前执行停写检查；命中失效停写分支则保存事实并 BLOCKED，不进入步骤／终态补报。保留正常失败、有效身份待补报的既有行为。
- **解除条件：** 从实际 execute／失败收尾入口注入上述停写状态，证明持久 BLOCKED、零 step／status／complete、零业务重执行，并回归正常失败与跨 TTL 收敛。**阻塞模块合入。**

**验证与证据边界**

本轮实际执行了上述两个只读内存反例、6 个变更 Python 文件 AST 解析、base 祖先关系检查、`git diff --check`，以及 catalog overlay 的真实 Compose 解析和逐服务比较：旧环境字段及既有挂载保持一致，默认开关为 `0/0/空 URL`；工作树保持干净。

已读取并核验既有 **72 passed** 日志及两个测试文件 SHA256，读取子包测试 **修前 3 failed、修后 50 passed** 和[真实 reconcile 证据](/home/wang/work/.local/spray-runtime/real-e2e-6ddcbcb02004/reconcile-result.json)：两次登记均成功，车辆为 `test`，相对路径包含 `scene/slices`，时间为业务时区 `15:58:24`，current 和八步 DONE 保持一致。这些是已有执行证据，**不是本轮重跑结果**。

本轮未执行需要临时文件的完整 pytest、真实模型、MySQL 业务写入、弱 OCR 或生产部署。生产门禁继续保留；无范围外阻塞建议。

下一步由 16B owner 仅修复 R4-01／R4-02，TESTER 按上述解除条件复验。本轮确认 2 项范围内缺陷；未裁决新误报，后续遗漏及 token／费用未知。现有 reviewer Skill 已覆盖流程，无需新增 Skill。结果未写文件，由包装器保存；未修改代码、合并、部署或委派模型。