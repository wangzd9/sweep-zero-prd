> **2026-10-14当前恢复覆盖**：用户明确恢复UI及OCR遗留，先读 [inbox/control/V04-UI-RESUME-20261014.md](/home/wang/work/doc/prd/rosbag-catalog-integration/inbox/control/V04-UI-RESUME-20261014.md)。本文件旧“UI不恢复/暂停”为历史，不再阻止新16C-A/B/C与16D准备；原收尾在途安全点接续，不抢占，TODO §8为唯一状态。当前main调查63bfcf8、生产3c9c496；seed bd0db1d未接受。

<!-- POST-SPRAY-CLOSEOUT-20261014 -->
> **当前接续（2026-10-14T10:49:02+08:00）**：水雾受控首包已上线，用户要求原五角色继续既定收尾。唯一当前恢复入口 `inbox/control/POST-SPRAY-CLOSEOUT-20261014.md`；下文2026-10-13临时接替/初次批次上传声明均为历史，原协调poll继续，禁止重做旧上线任务或已完成拷贝/绑定。UI与平台大包优化保持暂停。

> **当前恢复决定（2026-10-13T20:58:48+08:00）**：用户明确恢复飞书原协调者及A/B/C/TESTER和按需审核。临时Codex接替结束；本批唯一任务TASK-11S-BATCH-1012，先读inbox/coordinator/SPRAY-BATCH-1012-20261013/HANDOFF.md。旧“协调poll暂停/等待16B/S9b”等为历史，不再执行；UI仍暂停。

> **历史接管声明（已结束，不再执行）：Codex临时接替协调者直到水雾上线，旧协调者poll当时暂停。** 先读inbox/control/COORDINATOR-TAKEOVER-20261013.md；现有开发/测试和独立审查服务继续。


## 人工对话与工程操作接续（runtime-v2）

普通人工问答、进展查询、原因解释与方向调整保留Hermes原生模型会话，不自动转为后台待办，不等待五分钟巡检。明确执行动作才按原生消息身份登记；群与cron使用同一角色租约，取得后复读有效派单、ACK及已有证据，防重复执行。原生slash控制/审批保留；暂停job不因消息或入队自动启用。TODO仍是唯一任务状态，queue-ack与observer ack不等于业务通过或用户已收到答复。

绑定群的机械负载查询直读LAN指标，需要解释时再调用模型。环境检查与长工程操作复用[固定工具](/home/wang/.codex/skills/complex-task-coordinator/references/runtime-helpers.md)，UNKNOWN不重跑，命令成功不等于业务PASS。原任务范围、分支、自测/独立测试/OCR/适用强审查、授权及合入/生产门禁全部保留。



# 五角色文档协作协议 v2.1

> 当前用户纠正入口（2026-10-13T17:45:32+08:00）：`inbox/control/SPRAY-CORRECTION-20261013.md`。覆盖旧派单中的错误现状/重复实验/发布后补证据；原REQ/AC、单写、审查及生产授权门禁保持。

启用时间：2026-10-10T14:19:08+08:00。共享根：/home/wang/work/doc/prd/rosbag-catalog-integration。角色与定时绑定见 ../ROLE-BINDINGS.json；主分支 main，仓库 /home/wang/work/rosbag-catalog。P0 本地实现授权沿用用户已有授权，生产/真实样本等单独门禁保持。旧业务任务与回执不重置。

项目现有路径：开发派单 inbox/1号、2号、3号；测试派单 inbox/TESTER；开发交付 receipts/ 与既有 inbox/coordinator/ 回执；测试交付 test-receipts/；决策兼容 decision/ 与 inbox/coordinator/。旧派单已有 status=ACCEPTED 的不重新领取。OCR 可用调用能力由协调者核实 ocr --help；整命令持有稳定 inbox/ocr.lock，不删除锁文件。

## 单一来源与角色

- TODO：唯一业务任务状态与依赖源。DESIGN：契约。HANDOFF：最新恢复检查点。TIMELINE：事件历史，不替代状态。
- ROLE-BINDINGS.json：项目根、角色/群/Skill、cron、控制模式和迁移信息，不复制任务状态。
- 协调者单写共享主文档、派单、decision、OCR批次、强审查包和全局时间线；群聊与定时具有同一批准/调度权限。
- A/B/C 只写自己的代码范围、sessions、ACK、receipts、events；测试者只写指定测试材料、sessions/TESTER、test-receipts、验证报告与自身 events。
- 每个执行者自己新建任务专属分支/worktree；测试者独立取证；协调者审核门禁后合入，不代业务开发和日常测试。

## 领取、交付和接续

派单必须包含 task/attempt、固定 base、角色、范围、AC、停止条件和路径。先独立 ACK 后执行；已有派单允许只改 status ACK 的保留兼容，正文不改。扫描全部 inbox 中有效派单，不依赖自由文件名是否符合某个 glob。

任务状态沿用已有 TODO；常用交付状态 REVIEW_PENDING / TEST_REPORT_PENDING 只是等待审核，非通过。最新有效 attempt 由协调者明确，不能用新的无效文件覆盖已接受身份。接受后记录真实 merge 和合入后必要验证，满足门禁才 DONE。

依赖接受、阻塞解除、冻结交付释放槽后重新计算候选。本期已授权、依赖齐全、输入完整、文件/资源无冲突且 owner 确认可接才派。最多三路开发，不等整波；无可派任务不扩需求。强审查等待只冻结受审门禁。

## 运行时拆分与并发补位

协调者在5分钟巡检、任务接受、阻塞解除或开发槽空闲时，先检查已有可派发的具体任务；任务过粗则在原REQ/AC、已接受契约和已授权阶段内主动拆分剩余工作，不需为正常细化反复申请批准。按实际可接人数及产物独立性分配，最多三名开发执行者，不机械按人数切块。共享文件、迁移顺序、GPU/环境及硬依赖保持串行，或明确公共接线owner及接受条件。

先在短协调写锁内重读状态，更新TODO父子关系、稳定子ID、任务卡、依赖/接续、HANDOFF和拆分事件，再派单。子卡包含原REQ/AC、固定base/契约、owner、文件/资源边界、产物、验证/证据和停止条件；总任务汇总各功能并完成集成验收，不重复派完整实现，子产物接受且必要集成验证完成才DONE。已ACK、在途或等待审查的任务先核实执行者/分支/进程与检查点，确认交接及旧派单替代边界后调整，不直接换owner重派。

一个子任务接受后立即重算接续，不等整波；二十分钟报告只读，说明角色占用，有空槽却不能并行时给出具体原因及解除动作。拆分不增加逐子任务强审，按原风险合批；不激活DEFERRED/WAITING_AUTH、不增加需求或提高AC。范围/关键契约/架构变化升级规划者或用户。操作细节见 /home/wang/.codex/skills/complex-task-coordinator/references/task-decomposition.md。

## 单写与恢复

绑定中的 runtime_script 提供 claim/renew/release、短控制 run、preflight、event 和 timeline。使用真实 Hermes 会话身份作 owner；能够定位独立会话 worker 时记录其 PID，不使用即将结束的 shell PID或共享 gateway PID。未知 owner 存活时不能自动抢占。

每个角色写入或执行关键控制动作前 claim；拿不到租约只核查和报告。用带 token 的 run 包裹短文档/派单/ACK/合入操作，确保与群会话互斥；run 内执行前重读相关版本，旧 token 不可复用。每轮控制动作结束立即 release；长测试/OCR/开发先写实际进程与固定快照检查点，释放控制租约，后续巡检只核查，不重复启动。

租约到期不证明 owner 已退出；PID/start identity 已失效时才可在到期后接管。无法定位 owner 时报告需要核对，禁止删除稳定锁 inode。协调者沿用 inbox/coordinator.lock，OCR 独立沿用 inbox/ocr.lock；文件存在不等于锁被持有。

同一owner的匹配token在未被接管时可以renew或release过期租约，之后才继续控制动作。未知owner中断后，先核实原会话与进程已停止并保存证据；用recover --owner 原owner --confirmed-stopped --evidence 证据绝对路径清理过期租约，再claim。recover拒绝仍存活PID和未到期租约，禁止自动用“超时”代替停止证明。

claim成功只代表取得文档写权限，不是重新启动业务或测试许可；同task/attempt/被测commit仍有存活或未核验进程时，只检查并续写状态，不再次ACK、测试或启动OCR。

运行示例（按绑定中的真实绝对脚本路径替换 RUNTIME 与 ROOT，TOKEN 为 claim 返回值，不在群公开）：

```text
python3 RUNTIME claim --project ROOT --role A --owner 本轮会话ID
python3 RUNTIME run --project ROOT --role A --token TOKEN -- 允许的短文档写入命令
python3 RUNTIME event --project ROOT --role A --token TOKEN --event-id 稳定事件ID --task TASK-xx --attempt 1 --status REVIEW_PENDING --summary 交付行为 --evidence 回执路径或commit --next 等协调者审核
python3 RUNTIME release --project ROOT --role A --token TOKEN
```

preflight 在每个巡检回合更新真实检查时间并报告 ACTIVE/PAUSED、旧 owner/租约情况。不要把重启/压缩理解成重新派已 ACK 的任务。异常中断保留日志、PID和资源身份，逾期告警，不自动 kill、reset 或重派。

## 5分钟巡检、分时段总结和事件

五个运行角色各有 poll/report 两个 Hermes 原生 cron，均显式绑定对应 Skill，origin 与 deliver 指向同一角色群。巡检不用Hermes monitor跳过检查本身：每5分钟由脚本真正核查，无变化不调用模型；独立检查、变化入队与原生角色接续按下方最新规则。

当前报告策略quiet-digest-v2（Asia/Shanghai）：21:00–08:00所有运行角色停止主动定时/事件群通知，但开发、5分钟脚本检查、必要模型接续、派单、测试、OCR和文档记录继续。协调者08:00汇总21:00–08:00全部角色时间段/任务、确认空闲、完成记录和当前工作，另附18:00–21:00补充；白天08:20–20:40保留20分钟全局短报。执行者A/B/C、测试者仅在11:00、15:00、18:00生成08–11/11–15/15–18时段总结（无任务也总结），取消旧20分钟及2小时空闲报告。所有总结no_agent，不新增模型汇报定时请求；白天有意义变化先落唯一事件再即时通知一次，夜间只落盘，用户主动问答保留原生模型入口。时段报告按角色分别列角色阶段、LLM客户端响应时间、任务排队、真实空闲；阶段占用不等于模型计算。客户端API耗时不得称纯服务端排队，业务队列须有入队/开始处理证据；等待、阻塞、未知不算空闲。未知必须说明具体缺失原因与补采动作，不把缺数据当0，不倒填历史。完整规则：/home/wang/.codex/skills/complex-task-coordinator/references/reporting-policy.md。未绑定专项仅同步模板，不新建cron。

派单、ACK、开工、返修、实质进展、阻塞/解除、交付、测试/OCR结论、批准、合入、接续及暂停/恢复先落有权写的文档与 events/<ROLE>/；白天有意义变化按event_id通知一次，夜间只落盘，纯等待静默。cron final 自动投递，禁止再 send_message 双发；角色事件唯一 event_id，协调者去重汇总 TIMELINE。

事件落盘由既有五分钟检查接续；仅在确认不会启用暂停job的原生入口可提前唤醒。当前trigger_job会启用job，禁止以它绕过暂停。已运行目标只排pending，不重启。定时回合不创建或更改定时任务；巡检回合只有用户有效授权且明确需要时才通过统一限额脚本调用Codex，二十分钟报告仍只读不起跑。

统一显示由 `feishu-progress-style`（/home/wang/.codex/skills/feishu-progress-style/SKILL.md）维护，普通群回复、READY、事件和周期报告均加载。协调者整体进度使用整体目标与进度、执行者进度、测试者进度、OCR情况与后续、强审查情况、风险与阻塞、下一步七个加粗分区，各区下拆单层短bullet。普通单题直接答题；默认不展示diff数量、完整commit、grant/token字典等取证明细，需要时给详情链接，不用“叶/聚合/冻结head/机械全绿”等内部话。所有角色的即时事件也用具体功能名，原始记录只作证据，不直接复制成群报。当前 A=查询/API，B=Bag 三视图（切片、原始数据、全部），C=流水线详情；其他任务按有效派单确定功能名。模型执行绑定的`runtime_tools.py progress-facts --project ROOT --json`并读取返回正文；只拿到文件索引不算已读。长操作结束、最终汇报前再读一次相关最新事实。各角色session按ROLE-BINDINGS中的session_file相对项目根解析，不按镜像mtime选权威。TASK事实和门禁仍以原权威文档为准，样式不改变职责。

普通poll只有正常心跳、持续在途、纯等待、自写观察或重复进展时final仅[SILENT]；白天有意义的新完成/交付/失败/阻塞变化/返修/实质问题及需用户决策事项，先落稳定event_id与证据，允许一条即时通报。固定时段总结与人工问答正常输出。周期报告不是重复事件，不伪造时间线业务进展。实际排队延迟如实记录，5 分钟是调度周期而非模型运行时限。

## 审查和合入

本机OCR执行规范已固化到协调者Skill 1.5.0的 `/home/wang/.codex/skills/complex-task-coordinator/references/ocr-runtime.md`。唯一入口 `ocr_runtime.py prepare → start → status`，prepare零模型冻结完整范围/规则，start独立systemd service全链global/project双锁，参数版本化且不改共享配置。禁止直接ocr review、terminal后台、nohup/setsid、临时runner/等待链或恢复18002。失败立即停后批；原run退出且根因处理/授权仍有效时才显式reuse-run补审，复用身份一致的成功批且最多一次；同run/同身份重复调用拒绝。全批覆盖有效仅AWAITING_DECISION，核findings、跨契约/独立测试及必要强门禁后再裁决合入。旧在途只观察收口，不杀后重跑；本规则不新增强审/生产或付费调用授权。


弱模型 OCR 流程保留，由协调者串行触发；覆盖清单、大文件完整职责拆批、上下游契约、固定快照及在途运行全部记录。超时、空输出、缺工具不是通过；先确认旧批停止才重启。开发者与测试者都不跑 OCR。

强审查额外，默认人工触发；用户可授权协调者在自行指定的时长、起止时间或当前任务范围内自动调用Codex审查者。范围、原话/消息来源和绝对时间落盘到统一授权账本，无授权/过期/撤销仍等待人工；更换授权不重置额度。所有项目共用strong_review.py，滚动60分钟最多5次且在途串行，失败/超时/复审计入，禁止裸Codex/API绕过。协调者报告保留强审查分区，说明当前需要与否、执行/返回状态、结论与后续；授权期限或额度影响接续时写明具体条件。完整授权、次数、call/token/费用仍从原账本核对并保留详情，正文不倾倒工程字段。默认在功能批次完成开发和常规测试后审，不增加实现前审查或按任务/commit机械触发；冻结原AC，具体风险、问题与门禁明确才REVIEW_NOW，旧PASS不覆盖新行为。

强审查只纠正原功能：CORRECTION须证明违反既定需求/AC，回派原任务最小修复；VERIFICATION_GAP只补证明原AC所需证据；OUT_OF_SCOPE（新功能、未来规模、偏好重构或额外质量标准）默认不派单、不进当前TODO、不阻塞。跨模块阅读须与当前错误有因果关系；真实样本和生产等独立阶段的原门禁不提前变成无关模块条件。复审只看问题ID、修复diff和必要上下文；问题关闭且原AC满足即收口，不以“还可完善”继续加单。同根因两轮未解决按原规则升级，不无限返修。历史已确认问题不因本次范围收紧自动撤销，现有待办按上述分类继续核对。

合入前核对代码、开发自测、必要独立验证、OCR及适用强门禁。禁止自动“先合后审”例外。同根因两轮返修失败升级；不得删测试、弱化断言或成功标准。已批准工程闭环与生产启用分别记录。

## 授权与结束

当前授权写在项目 HANDOFF；Skill 不新增推送、生产部署、NAS/处理机写入或付费调用授权。已有用户明确授权继续执行，不逐项重复询问。

PAUSED/CANCELLED/COMPLETE 时停止新业务领取，保存检查点与恢复入口；协调者安排暂停本专项周期任务，并发送最后报告。定时任务不是无限模型调用，逻辑角色通过文档和持久调度恢复。

协调者按交付、验证、审查、合入、阻塞变化和里程碑更新绑定的development_log；无变化巡检不刷日志，记录真实commit/结果/证据与遗留事项。正式功能日志按仓库既有流程：功能完成且有适用验证证据后，在交付收口时自动生成/合并pending候选并更新changelog/REVIEW.md；用户明确批准指定功能后才approved；实际系统更新成功后才released并更新CHANGELOG.md和Web /changelog。一个完整功能可汇总多个子任务，协调者不自行批准或发布。

## 分时段汇报（2026-10-13，替代旧空闲降频）

报告频率与静默边界统一遵循上文quiet-digest-v2；旧20分钟个人报告/2小时空闲报告已停用，不从历史恢复。

Hermes现有report_job_id沿用，旧idle_report_job_id停用；协调者独立morning_report_job_id，所有报告no_agent；绑定保存计划不复制业务任务状态。

## 脚本巡检与短快照（2026-10-13）

每5分钟由独立role-document-observer.timer运行role_observer.py scan，对每个角色相关文档计算SHA-256，写ticks/快照并持久保留pending。原生角色poll仍5分钟错峰；无变化不因RUNNING或20/30分钟到点再次调用模型。有任务或实质变化先落持久pending，角色空闲才由poll唤醒模型；忙碌时只排队，不重启同角色，当前工作结束后接续。各角色通过文档交互，模型在安全检查点核对新输入。处理后才ack本轮指纹，旧ack拒绝消费新通知。未完成工作需分回合接续时先落实质检查点。报告仍quiet-digest-v2且no_agent；门禁、任务状态与分支不变。未注册项目只同步规则，不因模板更新自行创建运行群或timer。

## 人工会话、后台执行与进度答复（2026-10-14）

自然语言问进展、解释或讨论方向保留Hermes原生群模型会话，不自动入业务队列，不等待五分钟巡检；夜间用户主动问话可答复。绑定协调群的新会话通过原生auto_skill加载协调者与显示Skill；旧会话在人工回合提示先读取最新版Skill，不强制清空历史。只有显式/progress为可选脚本简报。模型与脚本统一读取当次`runtime_tools.py progress-facts --project ROOT`，当前事实存于`inbox/control/runtime/progress/facts.json`，不是第二份任务状态。每字段保留来源及有依据的发生/观测/记录时间；缺失或冲突说明具体来源差异、影响与核对动作，不用刷新时间冒充进展。协调者整体进度先给加粗结论，再按整体目标与进度、执行者进度、测试者进度、OCR情况与后续、强审查情况、风险与阻塞、下一步七个加粗分区组织，区内用单层短bullet，工程取证明细按需给详情链接。

明确要执行的业务动作才用runtime_tools.py request保留原文、原生消息身份与引用/附件。群与cron共用COORDINATOR租约，取得后重读TODO/派单/ACK/decision、实际任务/attempt及已有处理证据；已处理不重做。空闲时群可直接接续；已有owner忙时保存待办并解释，不抢占、不恢复暂停。问答不刷业务事件或制造派单。原测试/OCR/强审/合入/生产授权全部保留；HANDLED不等于业务完成或回复送达。详见[流程指南§0](/home/wang/work/doc/SKILL-DEVELOPMENT-WORKFLOW.md#0-先看这里我该怎么使用飞书协调者)。

## 精确时间与固定记账（2026-10-14更新）

所有面向用户的实际时间统一为`YYYY-MM-DD HH:MM +08:00`，精确到分钟即可；禁止`10:2x`、`10:1x`、十点多等占位或模糊钟点。标题用实际系统生成时间；动作发生时间取可信记录，明确区分发生、观测、补录。只有分钟的可靠记录可直接显示；发生时刻没有记录就写“发生时间未记录”，可另列精确观测时间，不拿文件mtime、消息发送、cron结束或租约时间代替，不编造秒。内部结构化时间保留原始精度与时区。

日常角色记账用`runtime_tools.py role-record`，正常观察独立写runtime/observations，不反复追加session/event制造唤醒；真实业务变化保持事件和自身session。固定只读长任务采样供各角色共享，正常心跳/CPU/mtime只更新事实；状态/attempt/身份、异常、未知与恢复更新稳定notice。独立测试取证复用原runner的`evidence-record`/`evidence-check`，机械匹配不替代关键断言、独立验收或审批。详情以当前Skill参考文件为准，不另造任务状态源。
