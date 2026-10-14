<!-- prd-reorganization-20261014 -->
> **文档归属更新（2026-10-14）**：基础/界面/水雾文档已拆到同级需求包，入口见 [目录导航](README.md)。本运行根、唯一TODO、派单/ACK/回执/租约/注册/cron保持原位；当前任务按原身份继续，不重新领取、不重置状态。修订业务契约时修改对应新包，旧PRD/DESIGN/ACCEPTANCE只作章节跳转。详见 [迁移说明](../MIGRATION-20261014.md)。

<!-- spray-post-v04-plan-20261014 -->
> **后续规划（2026-10-14T13:53:01+08:00）**：[水雾生产收尾](SPRAY-POST-V04.md)已按用户要求纳入[TODO §11](TODO.md#11-v04收尾后的水雾生产收尾2026-10-14)：自动绑定/幂等E、异常输入拒绝恢复F、原12S-D资料D1与独立实测D2。全部在当前v0.4收尾后由协调者核条件派单；当前仍按TASK-16执行，不抢占、不自动启用后续阶段。仅规划DESIGN_READY，未实现/未测/未部署。

先读 [inbox/control/V04-UI-RESUME-20261014.md](inbox/control/V04-UI-RESUME-20261014.md) → TODO §8 → 本角色 TASK-16C-A/B/C 或16D/16R派单 → DESIGN §7.3.3/OCR逐项账。不要继续执行旧“UI暂停”或“B独扛16C”的指令。

> **当前执行决定（2026-10-14T11:25:19+08:00）：用户恢复 v0.4 最小界面闭环，并要求原 OCR 未修项进入任务。** 唯一入口 [V04-UI-RESUME-20261014](inbox/control/V04-UI-RESUME-20261014.md)；TASK-16C-A/B/C 三路开发、16D准备/固定快照验收、16R审查遗留并行。下面2026-10-13 UI暂停及旧“不恢复UI”仅为历史。水雾上线接受保留；大包优化仍等ros2_slice交付，其他DEFERRED不恢复。状态唯一见TODO §8。

# 五角色启动入口 v2.1


## 人工对话与工程操作接续（runtime-v2）

普通人工问答、进展查询、原因解释与方向调整保留Hermes原生模型会话，不自动转为后台待办，不等待五分钟巡检。明确执行动作才按原生消息身份登记；群与cron使用同一角色租约，取得后复读有效派单、ACK及已有证据，防重复执行。原生slash控制/审批保留；暂停job不因消息或入队自动启用。TODO仍是唯一任务状态，queue-ack与observer ack不等于业务通过或用户已收到答复。

绑定群的机械负载查询直读LAN指标，需要解释时再调用模型。环境检查与长工程操作复用[固定工具](/home/wang/.codex/skills/complex-task-coordinator/references/runtime-helpers.md)，UNKNOWN不重跑，命令成功不等于业务PASS。原任务范围、分支、自测/独立测试/OCR/适用强审查、授权及合入/生产门禁全部保留。



共享根：/home/wang/work/doc/prd/rosbag-catalog-integration

## 2026-10-13水雾优先入口（历史，UI已于10-14恢复）

用户暂停界面增量，先水雾接收→本机点云/渲染→远端模型→切片→NAS发布/MySQL入库→已有API获取，保留旧功能。先读 [TODO §9](TODO.md#9-v05-水雾优先与生产接入2026-10-13)→[水雾设计](SPRAY-INTEGRATION.md)→[数据要求](RAW-DATA-REQUIREMENTS.md)→[验收](ACCEPTANCE.md)→[今日发布门禁](SPRAY-RELEASE.md)，再按各卡加载PRD/DESIGN和实际代码，不要求弱模型通读历史巡检。

16A已DONE保留，C继续16B原门禁；A候选12S-A，B先安全暂停交接16C再候选12S-B；16B及A/B全接受才12S-C→TESTER 12S-D→核11S生产门禁。16C/16D/父16原UI聚合暂停，不纳入水雾发布；已有交付/审查/验证归档保留。没有车辆编号的1012样本仅能做隔离探针，生产所需车辆信息向数据方补齐。

规划状态DESIGN_READY只代表文档可开发；今天上线目标仍须G1～G6真实通过，本会话不执行部署/模型请求/派单。后续协作恢复核原owner、授权、检查点和资源，不自动重建角色或续审查授权。下方v0.4入口为历史交接，涉及新页面优先级以本节为准。

## 本轮 v0.4 场景链路调整入口（2026-10-12）

状态：**DESIGN_READY，仅文档完成**。先读 [PRD](PRD.md)→[DESIGN §7.3](DESIGN.md#73-v04-场景专用接收执行与界面补齐)→[TODO §8](TODO.md#8-v04-最小闭环补齐规划2026-10-12)→[ACCEPTANCE](ACCEPTANCE.md)→[HANDOFF 本轮规划节](HANDOFF.md)。TASK-16 的状态只在 TODO §8 维护，旧 TASK-01～15 和角色/群/cron 绑定保留。

用户确认仅场景识别/切片链路迁为处理机本机执行，远端只调用模型服务；NAS 目标 `/public/rosbag_scene_processing/{incoming,ready,slices}`，测试根 `/test/scene/{incoming,ready,slices}`。基础流水线详情与 Bag 三视图属于最小闭环，不能再按旧章节后置到预览/其他场景之后。

协调者恢复时先核对 07B 在途检查点/页面文件 owner，再在实际实施授权内派16A/16B/16C；三项接受后TESTER验证16D。原07B不由规划文档取消/重派，07C预览不阻塞本轮。TASK-11生产启用和MN-v1独立；本入口不会启动代理、开发者、模型请求、cron或部署。

用户在对应群只需声明角色；先加载Skill并恢复现有任务，不重新创建角色或重派旧任务。群绑定冲突先澄清。

| 声明 | Skill | 运行角色 |
|---|---|---|
| 我是规划者／进行复杂任务开发设计 | complex-task-planner | 按需设计 |
| 我是协调者 | complex-task-coordinator | COORDINATOR |
| 我是执行者1号／A | complex-task-executor | A |
| 我是执行者2号／B | complex-task-executor | B |
| 我是执行者3号／C | complex-task-executor | C |
| 我是测试者 | complex-task-tester | TESTER |
| 我是审查者，审查这个包 | complex-task-reviewer | 默认人工；有效用户授权内可由协调者限额调用Codex |

运行恢复阅读：ROLE-BINDINGS.json → inbox/PROTOCOL.md → TODO → HANDOFF最新检查点 → 自身sessions → 派单/ACK/回执/decision。只有计划和当前任务相关材料默认加载，不加载五角色全文。

默认每5分钟脚本检查，报告按quiet-digest-v2，白天关键事件即时通报；cron已显式注入Skill。READY必须给角色/项目/当前任务/实际定时状态。定时不配置定时，Skill本身不保活。

旧owner仍存活时preflight会报告legacy_busy，禁止接管；报告角色仍可只读汇报。旧job e0263b8ac010 保持暂停，只保留在途运行自然完成，新协调者复用14ae4556629a。

群内显示同时加载 **feishu-progress-style**，适用于普通回复、READY、即时事件及周期报告；协调者整体进度用整体目标与进度、执行者进度、测试者进度、OCR情况与后续、强审查情况、风险与阻塞、下一步七个加粗分区，区内用单层短bullet；普通单题直接答题，默认工程取证明细按需展开。调度/门禁由角色Skill与当前协议负责，显示Skill不承担第六个角色。

## 自动审查授权与开发日志

协调者支持用户自行指定任意明确时长、起止时间或本次任务完成前的自动Codex审查授权；按角色Skill references/review-authorization.md记录原话/来源和绝对期限，通过绑定的strong_review_runtime执行。滚动60分钟跨项目最多5次，失败/超时/复审计入，无有效授权保持人工流程；本页示例不是实际授权。协调者报告保留强审查分区，说明当前需要与否、执行/返回状态、结论与后续；授权期限或额度影响接续时写明具体条件。完整授权、次数、call/token/费用仍从原账本核对并保留详情，正文不倾倒工程字段。协调者在重要进展时更新 [DEVELOPMENT-LOG](DEVELOPMENT-LOG.md)，正式功能日志在功能完成并验证后更新pending候选和REVIEW.md，用户明确批准后approved，实际发布成功后released并更新公开页面。授权不会绑定角色、启动尚未授权专项或开启数据删除/生产。

协调者可以在原REQ/AC、已接受契约和已授权阶段内动态拆分粗任务，并按实际空闲角色分派最多三路开发；先同步父子任务与依赖，已在途工作先确认检查点交接。空槽无法利用时报告具体串行原因，不扩需求。详见 [当前协作协议](inbox/PROTOCOL.md)。


<!-- a100-multi-node-entry-mn-v1 -->
## A100 双节点纳管独立专项入口

2026-10-12：[开发文档入口](A100-MULTI-NODE.md) / [角色启动](a100-multi-node/SESSION-START.md)。MN-v1仅文档DESIGN_READY；任务状态只在专项TODO维护，五角色未绑定，未开始业务开发、远端写入或生产启用。此入口不改变本文件既有任务状态、编号、派单、授权或角色绑定。

## 分时段汇报（2026-10-13，替代旧空闲降频）

当前报告策略quiet-digest-v2（Asia/Shanghai）：21:00–08:00所有运行角色停止主动定时/事件群通知，但开发、5分钟脚本检查、必要模型接续、派单、测试、OCR和文档记录继续。协调者08:00汇总21:00–08:00全部角色时间段/任务、确认空闲、完成记录和当前工作，另附18:00–21:00补充；白天08:20–20:40保留20分钟全局短报。执行者A/B/C、测试者仅在11:00、15:00、18:00生成08–11/11–15/15–18时段总结（无任务也总结），取消旧20分钟及2小时空闲报告。所有总结no_agent，不新增模型汇报定时请求；白天有意义变化先落唯一事件再即时通知一次，夜间只落盘，用户主动问答保留原生模型入口。时段报告按角色分别列角色阶段、LLM客户端响应时间、任务排队、真实空闲；阶段占用不等于模型计算。客户端API耗时不得称纯服务端排队，业务队列须有入队/开始处理证据；等待、阻塞、未知不算空闲。未知必须说明具体缺失原因与补采动作，不把缺数据当0，不倒填历史。完整规则：/home/wang/.codex/skills/complex-task-coordinator/references/reporting-policy.md。未绑定专项仅同步模板，不新建cron。


## 脚本巡检与短快照（2026-10-13）

每5分钟由独立role-document-observer.timer运行role_observer.py scan，对每个角色相关文档计算SHA-256，写ticks/快照并持久保留pending。原生角色poll仍5分钟错峰；无变化不因RUNNING或20/30分钟到点再次调用模型。有任务或实质变化先落持久pending，角色空闲才由poll唤醒模型；忙碌时只排队，不重启同角色，当前工作结束后接续。各角色通过文档交互，模型在安全检查点核对新输入。处理后才ack本轮指纹，旧ack拒绝消费新通知。未完成工作需分回合接续时先落实质检查点。报告仍quiet-digest-v2且no_agent；门禁、任务状态与分支不变。未注册项目只同步规则，不因模板更新自行创建运行群或timer。

## 人工会话、后台执行与进度答复（2026-10-14）

自然语言问进展、解释或讨论方向保留Hermes原生群模型会话，不自动入业务队列，不等待五分钟巡检；夜间用户主动问话可答复。绑定协调群的新会话通过原生auto_skill加载协调者与显示Skill；旧会话在人工回合提示先读取最新版Skill，不强制清空历史。只有显式/progress为可选脚本简报。模型与脚本统一读取当次`runtime_tools.py progress-facts --project ROOT`，当前事实存于`inbox/control/runtime/progress/facts.json`，不是第二份任务状态。每字段保留来源及有依据的发生/观测/记录时间；缺失或冲突说明具体来源差异、影响与核对动作，不用刷新时间冒充进展。协调者整体进度先给加粗结论，再按整体目标与进度、执行者进度、测试者进度、OCR情况与后续、强审查情况、风险与阻塞、下一步七个加粗分区组织，区内用单层短bullet，工程取证明细按需给详情链接。

明确要执行的业务动作才用runtime_tools.py request保留原文、原生消息身份与引用/附件。群与cron共用COORDINATOR租约，取得后重读TODO/派单/ACK/decision、实际任务/attempt及已有处理证据；已处理不重做。空闲时群可直接接续；已有owner忙时保存待办并解释，不抢占、不恢复暂停。问答不刷业务事件或制造派单。原测试/OCR/强审/合入/生产授权全部保留；HANDLED不等于业务完成或回复送达。详见[流程指南§0](/home/wang/work/doc/SKILL-DEVELOPMENT-WORKFLOW.md#0-先看这里我该怎么使用飞书协调者)。

## 精确时间与固定记账（2026-10-14更新）

所有面向用户的实际时间统一为`YYYY-MM-DD HH:MM +08:00`，精确到分钟即可；禁止`10:2x`、`10:1x`、十点多等占位或模糊钟点。标题用实际系统生成时间；动作发生时间取可信记录，明确区分发生、观测、补录。只有分钟的可靠记录可直接显示；发生时刻没有记录就写“发生时间未记录”，可另列精确观测时间，不拿文件mtime、消息发送、cron结束或租约时间代替，不编造秒。内部结构化时间保留原始精度与时区。

日常角色记账用`runtime_tools.py role-record`，正常观察独立写runtime/observations，不反复追加session/event制造唤醒；真实业务变化保持事件和自身session。固定只读长任务采样供各角色共享，正常心跳/CPU/mtime只更新事实；状态/attempt/身份、异常、未知与恢复更新稳定notice。独立测试取证复用原runner的`evidence-record`/`evidence-check`，机械匹配不替代关键断言、独立验收或审批。详情以当前Skill参考文件为准，不另造任务状态源。
