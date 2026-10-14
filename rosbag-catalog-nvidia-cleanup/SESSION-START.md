# NVIDIA 删除专项角色启动

状态：**DESIGN_READY；角色/群/cron 未绑定，只有规划文档**。
共享根：`/home/wang/work/doc/prd/rosbag-catalog-nvidia-cleanup`。
代码根：`/home/wang/work/rosbag-catalog`，主分支 main；调查 base 见 HANDOFF，实际派单另冻结。

| 用户声明 | Skill | 本专项入口 |
|---|---|---|
| 我是规划者，修改 NVIDIA 删除设计 | complex-task-planner | PRD→DESIGN→TODO→HANDOFF |
| 我是协调者，接续 NVIDIA 删除 | complex-task-coordinator | ROLE-BINDINGS→inbox/PROTOCOL→TODO→HANDOFF→sessions/COORDINATOR |
| 我是执行者1号/A，领取 NVIDIA 删除派单 | complex-task-executor | 同上基础材料→sessions/A→inbox/A 中实际派单 |
| 我是执行者2号/B，领取 NVIDIA 删除派单 | complex-task-executor | 同上基础材料→sessions/B→inbox/B 中实际派单 |
| 我是执行者3号/C，领取 NVIDIA 删除派单 | complex-task-executor | 同上基础材料→sessions/C→inbox/C 中实际派单 |
| 我是测试者，验证 NVIDIA 删除 | complex-task-tester | 同上基础材料→ACCEPTANCE→sessions/TESTER→实际固定快照派单 |
| 我是审查者，审查 NVIDIA 删除包 | complex-task-reviewer | 用户指定 NC-07 已完成批次包，冻结既有 AC |

同一个角色在场景专项仍承担在途任务时，不能把声明理解为自动迁移或抢占；协调者核对文件/资源/空闲状态后派本专项。不要复制上级任务状态或 cron ID。

后续用户要求实施后，由协调者恢复本专项、确认绑定和实际定时配置，再派首波。执行者没有有效派单不开发；TESTER 没有固定 SHA 不整链取证。本轮不能因为读到 ACTIVE 配置字段就启动，授权以 HANDOFF 与用户请求为准。

运行阶段才配置Hermes原生5分钟脚本检查/分时段总结，白天关键事件即时报告；Skill/Markdown 不自行保活。若在飞书群执行，同时加载 `feishu-progress-style`；此 IDE 规划不发送群消息。

## 自动审查授权与开发日志

协调者支持用户自行指定任意明确时长、起止时间或本次任务完成前的自动Codex审查授权；按角色Skill references/review-authorization.md记录原话/来源和绝对期限，通过绑定的strong_review_runtime执行。滚动60分钟跨项目最多5次，失败/超时/复审计入，无有效授权保持人工流程；本页示例不是实际授权。二十分钟报告必报授权、次数、结果与实际用量/费用。协调者在重要进展时更新 [DEVELOPMENT-LOG](DEVELOPMENT-LOG.md)，正式功能日志在功能完成并验证后更新pending候选和REVIEW.md，用户明确批准后approved，实际发布成功后released并更新公开页面。授权不会绑定角色、启动尚未授权专项或开启数据删除/生产。

协调者可以在原REQ/AC、已接受契约和已授权阶段内动态拆分粗任务，并按实际空闲角色分派最多三路开发；先同步父子任务与依赖，已在途工作先确认检查点交接。空槽无法利用时报告具体串行原因，不扩需求。详见 [当前协作协议](inbox/PROTOCOL.md)。

## 分时段汇报（2026-10-13，替代旧空闲降频）

当前报告策略quiet-digest-v1（Asia/Shanghai）：21:00–08:00所有运行角色停止主动定时/事件群通知，但开发、5分钟脚本检查、必要模型接续、派单、测试、OCR和文档记录继续。协调者08:00汇总21:00–08:00全部角色时间段/任务、确认空闲、完成记录和当前工作，另附18:00–21:00补充；白天08:20–20:40保留20分钟全局短报。执行者A/B/C、测试者仅在11:00、15:00、18:00生成08–11/11–15/15–18时段总结（无任务也总结），取消旧20分钟及2小时空闲报告。所有总结no_agent；白天实质变化即时通报，夜间只落盘，用户主动提问可答复。时间为任务状态观察估算，等待/阻塞/记录不足不算空闲，不能倒填无证据历史。完整规则：/home/wang/.codex/skills/complex-task-coordinator/references/reporting-policy.md。未绑定专项仅同步模板，不新建cron。


## 脚本巡检与短快照（2026-10-13）

每5分钟由role_observer.py脚本真正检查并写ticks；无变化不唤醒模型，有派单/返修/结果/控制或进程身份变化才接续。明确RUNNING及未知状态保持模型核查；协调者无事件时每20分钟模型调度复核。模型读短快照及相关权威证据，处理本轮输入后再用本轮fingerprint执行ack，不预先吞事件、不以观察确认代替业务ACK或通过门禁。当前报告按quiet-digest-v1运行，详见报告协议；原派单、测试、OCR和强审查门禁不变。
