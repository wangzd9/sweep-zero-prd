# A100 双节点专项角色启动

> 范围：MN-v1只覆盖自建/NVIDIA。场景v0.4角色从 [主入口](/home/wang/work/doc/prd/rosbag-catalog-integration/SESSION-START.md)恢复，场景worker在处理机、A100只服务模型请求；不要从本入口为场景启动MN节点任务或上传Bag。

状态：**DESIGN_READY，仅文档；control=UNBOUND，角色/群/cron未绑定**。
共享根：`/home/wang/work/doc/prd/rosbag-catalog-a100-multi-node`。
代码根：`/home/wang/work/rosbag-catalog`，main；实际派单base另冻结。

| 用户声明 | Skill | 恢复入口 |
|---|---|---|
| 我是规划者，修订双节点设计 | complex-task-planner | PRD→DESIGN→TODO→HANDOFF→VALIDATION |
| 我是协调者，接续双节点专项 | complex-task-coordinator | ROLE-BINDINGS→inbox/PROTOCOL→TODO→HANDOFF→sessions/COORDINATOR |
| 我是执行者1号/角色A | complex-task-executor | 基础材料→sessions/A→inbox/A实际派单 |
| 我是执行者2号/角色B | complex-task-executor | 基础材料→sessions/B→inbox/B实际派单 |
| 我是执行者3号/角色C | complex-task-executor | 基础材料→sessions/C→inbox/C实际派单 |
| 我是测试者/TESTER | complex-task-tester | 基础材料→ACCEPTANCE→sessions/TESTER→固定SHA测试派单 |
| 我是审查者，审查已完成双节点批次 | complex-task-reviewer | 用户或有效授权指定的MN-08冻结包，按原AC纠错 |

开发角色A/B/C与执行服务器A/B不同。role声明不自动迁移上级在途任务，不抢旧cron，不重派未核验的运行任务。当前没有有效派单，阅读文档不能触发开发/测试/SSH写入或生产。

MN-01/02/03是未来首波；具体依赖、文件owner和完成事件接续只看TODO。绑定后每角色按role_runtime claim/run/release保护控制写入；UNBOUND时不得调用业务运行入口，协调者先取得后续授权并核对绑定。

## 审查、开发日志与呈现

开发日志入口 [DEVELOPMENT-LOG](DEVELOPMENT-LOG.md)，验证 [VALIDATION](VALIDATION.md)，事件历史 [TIMELINE](TIMELINE.md)。OCR由协调者串行，TESTER不跑OCR；强审查默认人工。用户后续给定时长或任务范围授权后，协调者落原话/来源、绝对期限及范围，统一脚本滚动60分钟最多5次，报告授权/次数/结果/用量，未知如实标明。

未来Hermes绑定后每5分钟脚本检查、按quiet-digest-v1报告、白天关键事件即时汇报；实际唤醒依赖原生cron，不由Markdown保活。本次不创建cron或发群消息。飞书运行时另加载feishu-progress-style；IDE规划无需群呈现Skill。正式日志仍按pending→用户批准approved→实际发布released，不由规划文档批准功能日志。

## 分时段汇报（2026-10-13，替代旧空闲降频）

当前报告策略quiet-digest-v1（Asia/Shanghai）：21:00–08:00所有运行角色停止主动定时/事件群通知，但开发、5分钟脚本检查、必要模型接续、派单、测试、OCR和文档记录继续。协调者08:00汇总21:00–08:00全部角色时间段/任务、确认空闲、完成记录和当前工作，另附18:00–21:00补充；白天08:20–20:40保留20分钟全局短报。执行者A/B/C、测试者仅在11:00、15:00、18:00生成08–11/11–15/15–18时段总结（无任务也总结），取消旧20分钟及2小时空闲报告。所有总结no_agent；白天实质变化即时通报，夜间只落盘，用户主动提问可答复。时间为任务状态观察估算，等待/阻塞/记录不足不算空闲，不能倒填无证据历史。完整规则：/home/wang/.codex/skills/complex-task-coordinator/references/reporting-policy.md。未绑定专项仅同步模板，不新建cron。


## 脚本巡检与短快照（2026-10-13）

每5分钟由独立role-document-observer.timer运行role_observer.py scan，对每个角色相关文档计算SHA-256，写ticks/快照并持久保留pending。原生角色poll仍5分钟错峰；无变化不因RUNNING或20/30分钟到点再次调用模型。有变化且角色忙碌时只排队，不重启同角色；当前工作结束后由poll接续，模型在安全检查点核对新输入。处理后才ack本轮指纹，旧ack拒绝消费新通知。未完成工作需分回合接续时先落实质检查点。报告仍quiet-digest-v1且no_agent；门禁、任务状态与分支不变。未注册项目只同步规则，不因模板更新自行创建运行群或timer。
