# 五角色 Skill 迁移记录

版本：1.0.0；核验时间：2026-10-10T14:40:41+08:00。

五个 Skill 唯一维护源：`/home/wang/.codex/skills/complex-task-{planner,coordinator,executor,tester,reviewer}`。Hermes external_dirs 已指向五个真实目录；SOUL 保留原身份并增加角色声明路由。旧综合 Skill 与旧项目 Skill 已移出扫描目录，历史材料保存在备份。

## 使用

在已绑定角色群说“我是协调者”“我是执行者1号/2号/3号”或“我是测试者”；按需强模型说“我是规划者”或“我是审查者，审查这个包”。只加载本角色 Skill。群与角色冲突、项目无法唯一确定时澄清，不从全局记忆猜测。详见 [启动入口](SESSION-START.md)、[当前协议](inbox/PROTOCOL.md)、[角色绑定](ROLE-BINDINGS.json)。

## 实际定时绑定

| 角色 | Skill | 5分钟poll | 20分钟report |
|---|---|---|---|
| COORDINATOR | complex-task-coordinator | 14ae4556629a | 99bb6c6cacc6 |
| A | complex-task-executor | d5cb80cf2fc5 | 169849556cc2 |
| B | complex-task-executor | 6f7471d8747c | 7c1cf5029635 |
| C | complex-task-executor | f01517c16f2f | b99cc17222c3 |
| TESTER | complex-task-tester | 167580c0500b | b41450f1df3c |

十个任务已启用，按角色错峰；全部显式注入单个角色 Skill、清除 monitor，origin 与 deliver 对应同一角色群。`e0263b8ac010` 旧heartbeat保持暂停，不恢复。原服务常驻状态未改变，也没有重启或强杀。旧执行 42799555e11f4041b9c773aa531fe7bf 于14:32:05自然完成，14:37:49核对接管，绑定迁移状态ACTIVE。

模型沿用 Hermes 当前本地 Qwen 配置，未配置定时强模型任务，未自行调用付费强审查。原生产与业务门禁不改变。业务任务表迁移时33条记录逐条保留，分支、ACK、回执、历史审查材料未重置；后续变化由恢复的原开发流程产生。

## 验证结果与实际边界

- 五份Skill格式校验通过；Hermes实际skill_view发现与cron注入通过；本地引用无断链。
- 隔离验证通过：同角色并发claim唯一、错误/过期token保护、原owner过期renew/release、需核验的中断恢复、PID复用及缺start身份保护、未知旧owner阻断、暂停保护、跨群解析/歧义拒绝、事件去重和冲突拒绝、仅协调者去重汇总时间线。
- 五角色report均有实际completed+delivered账本记录；五角色poll均进入实际运行并生成preflight巡检记录，无变化巡检也未被monitor跳过。
- 首轮报告观察到历史“等待主会话”说法、模糊时间和冗长报告，已据证据缩小默认阅读集、强调最新decision/协议、状态冲突不得宣称DONE、完整真实日期及6–10行中文结果规则。A/TESTER增量报告确认不再使用模糊日期；最新正文长度与长期遵守情况继续由协调者核对，不声称全部模型行为已被形式化保证。
- 发现一次重复协调者触发失去fire claim、未启动执行；既有运行持续。保留执行账本证据，不把该次失败写成业务执行成功。五分钟是计划检查周期，长调用与模型排队造成的实际延迟必须报告。
- 本次验收只覆盖Skill/文件协议/定时启动与投递，不替代Bag业务真实闭环、重启故障演练、真实时间映射或生产验收。新会话/压缩恢复的规则已写入，未为验证而重启在途服务。

证据目录：`/home/wang/.codex/skill-migrations/five-roles-20261010-140917/verification`（隔离脚本与结果、实际report/poll执行行、群报告归档、Skill哈希）。

## 备份与回退

备份：`/home/wang/.codex/skill-migrations/five-roles-20261010-140917`，权限0700，包含旧Skill、原SOUL/config/jobs及迁移前文档快照；配置备份可能含凭据，不复制到群。

回退顺序：先按ROLE-BINDINGS的十个ID暂停新任务；核对在途owner与OCR，等待检查点，禁止kill/reset。恢复归档Skill和原external_dirs/SOUL角色路由段，核对原job定义再恢复需要的旧job；不直接覆盖运行账本或整份jobs文件。项目协议从备份作差异恢复，保留回退后仍需成立的安全门禁。**不拿旧TODO/HANDOFF/sessions快照覆盖新业务进展，不重派已ACK任务**。本迁移脚本是实施取证，不当作幂等回退工具反复执行。
