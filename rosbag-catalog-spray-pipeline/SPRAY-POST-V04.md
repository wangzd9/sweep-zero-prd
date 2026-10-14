# 水雾生产收尾：v0.4完成后的接续计划

规划时间：2026-10-14T13:53:01+08:00（Asia/Shanghai）；DESIGN_READY，仅文档可开发。用户要求三项列入后续任务，**等当前v0.4收尾后再由协调者派单**。唯一动态状态在 [TODO §11](../rosbag-catalog-integration/TODO.md#11-v04收尾后的水雾生产收尾2026-10-14)。当前执行仍是 [v0.4入口](../rosbag-catalog-integration/inbox/control/V04-UI-RESUME-20261014.md)，本计划不是立即开发派单，不唤醒/重分配现有角色，不续审查或发布授权。

## 事实、目标和阶段门

10-14的修复证据表明，三份提交曾PENDING_INPUT、源已ready；正式API重登记复用既有终态run，created_runs=0/reused_runs=3，未重烧模型。这是个案恢复，尚不能当提交/登记时序的永久修复。父子共享快指纹仍会误拒合法原包；16_33_10空包Scanner拒绝有效，但submission未结束。证据见 [分析](../../analysis/spray-batch-progress-20261014/REPORT.md)、[恢复回执](../rosbag-catalog-integration/inbox/coordinator/SPRAY-BATCH-1012-20261013/codex-repair-receipt-20261014.md)、[批次记录](../rosbag-catalog-integration/inbox/coordinator/SPRAY-BATCH-1012-20261013/BATCH-STATUS.md)。此处引用历史证据，不是新生产探测；旧“Codex正在修全部问题”不能作为在途开发事实。

阶段门V04_CLOSEOUT：协调者按当前原AC记录TASK-16聚合DONE（16C/16D接受、16R按已裁必要门禁处置），核文件owner/原进程安全点释放。不能为本计划延迟或改变v0.4完成定义；也不把12S-D全面质量PASS设为E/F前置而形成循环。只有到阶段门且协调者核依赖/输入/资源、补实际base/owner/attempt后，后续卡才可转READY并派发。

后续最小链路：合法提交与源登记任意先后→自动准确绑定→单份用途事件/运行→已有结果复用；无效输入→可查询的INPUT_REJECTED→补齐后显式恢复/重校验→同一合法绑定链。工程修复后用真实车辆、真阴性、跨DB3及固定批次验质量与血缘，全部必要证据接受后才可扩大生产范围。

## 1. TASK-12S-E 接收/登记/绑定自动闭环（优先收尾）

- 父TASK-12S；REQ-20/AC-20，细化REQ-01/02/06/08/14/18；硬依赖V04_CLOSEOUT、已接受12S-A/16A。建议开发槽A，实际owner/attempt/base待协调者派单；当前DEFERRED_AFTER_V04。
- 输入：最新已接受main、现有source登记/ingest/outbox/scene consumer契约、三份恢复证据和c5d98d0测试候选。候选只作参考，未合入/未接受不得直接当基线，先核是否已被后续实现覆盖。
- 范围：app/services/ingest_service.py、source_service.py、必要scene_schedule_consumer.py与对应ingest/source/schedule测试；仅确需请求接线时触及app/api/ingest_submissions.py。不碰场景算法/代理/UI/ros2_slice，不复制旧恢复脚本为正式旁路。
- 登记前提交、先登记后提交、二者并发以及登记后崩溃重启都必须收敛。复用既有登记绑定与outbox业务服务；后提交必须从冻结root/profile/version及相对ready映射定位已登记源，不能只按basename/快指纹匹配。采用现有后台恢复/有界对账补事务空隙，不新建通用调度平台；时限沿现有扫描/消费配置取证，不能无限等待或依赖模型执行槽释放。资料不齐仍待补，不制造成功绑定。
- 幂等身份：source_id+source_generation+冻结场景/能力/参数身份一致才复用已有run；相同重放不分配新分析版本、不新增attempt/outbox消费副作用或模型调用。新代次、配置冲突、不同车辆必须按既有冲突规则区分；不得为“幂等”吞掉显式合法新分析。保留原hash/profile/UID/已绑定元数据不变。
- 快指纹仅候选索引。验证准确原包路径、root、已有ORIGINAL/source与代次后，允许合法原包携快指纹重登记，即使子包同指纹；绝不能把子包当原包、覆盖父路径、归并UID或移除派生围栏。歧义/越界/无法证明准确源时409并返回可追溯原因，不靠省略fingerprint才能恢复。
- 自测/TESTER：MySQL隔离库固定SHA验证两种先后、交错并发、commit/响应丢失、重启/重复扫描/重复提交/重复恢复；同时构造同指纹父子、同名跨根/跨车辆、歧义源、错误代次与不同配置。对重复路径核source/run/attempt/分析版本/outbox及模型调用计数不增加；不能仅断言HTTP200。无真实模型的机械用例可记录调用计数/桩，真实已接受结果复用单独取证，不再烧历史生产三包。旧自建/NVIDIA/坡道与派生保护必要回归。
- 完成：固定提交、自测+独立验证、适用OCR findings裁决和合入证据齐，AC-20通过；产物receipts/TASK-12S-E/attempt-N.md及test-receipts/TEST-TASK12S-E/attempt-N.md。接受事件解除F公共文件前置，并给D2最终集成候选提供基线。

## 2. TASK-12S-F 无效输入结束与补齐恢复（优先收尾）

- 父TASK-12S；REQ-21/AC-21，细化REQ-08/14/18及AC-17/18；硬依赖V04_CLOSEOUT、12S-E接受。建议槽B；E/F会共写ingest服务/API，首版顺序执行，不能以worktree隔离假称无冲突。当前DEFERRED_AFTER_V04。
- 范围：app/scanner/runner.py、metadata.py、state_store.py、backend.py及必要clients.py；app/services/ingest_service.py、app/api/ingest_submissions.py；若持久证据需增量schema，由F独占models/单头迁移/DTO与对应测试。先将最小DDL/API差异交协调者核兼容，保留旧行默认语义；禁止用本地Scanner日志/状态文件代替服务端权威拒绝状态，不改intake/effective冻结hash充当审计。
- 接收状态新增INPUT_REJECTED：只针对尚未绑定的已确认无效输入，结束本次自动接收尝试；保留原提交ID、幂等键、path claim、资料、拒绝原因/受控路径/文件摘要及观测时间，可查询且重启后保留。不生成source/run/模型请求；不是SCENE_FAILED、NO_MATCH或NOT_APPLICABLE，不自动落自建。
- 判定顺序先更新上传稳定证据，再分类校验。文件持续变化/尚未达到现有scan_stability_rounds且无可信完成声明=PENDING_INPUT，等待上传；达到完整性确认后仍空/坏metadata、缺失/空DB3等=INPUT_REJECTED。无显式完成信号时，至少要求达到既有稳定窗口且同一无效快照经两个不同扫描轮次确认，避免一次校验异常即终止；变化即重新计稳定。网络/存储不可达归基础设施故障，不能判包损坏。服务返回稳定机器错误码、必要缺失文件及恢复提示；.done等既有完成信号不免除内容校验，本轮不新增每包必传完成标记要求。
- 首期采用逻辑隔离：原包留在incoming受控位置、不修改、不删除、不移出可恢复根；相同拒绝快照重复扫描跳过业务处理、不刷重复拒绝/任务。扫描可低成本察觉文件变化但不自动重新派发；保留拒绝历史，失败不是永远PENDING_INPUT。确认拒绝前没有submission的输入也须有根+路径+观测身份的持久拒绝记录，后续合法提交能关联该证据，不能静默丢失。
- 新增目标接口POST /api/v1/ingest-submissions/{id}/resume-input（尚未实现）：既有权限+Idempotency-Key，body含row_version。只允许INPUT_REJECTED且尚未绑定恢复；旧version/已绑定/非法状态409。同一幂等重放不能重复恢复代次或绕过当前状态；HTTP200/202只表示受理，不代表已合法。保留拒绝历史，恢复为PENDING_INPUT并清本次稳定/拒绝抑制标记，重新完整校验；仍坏则再次INPUT_REJECTED，合法后走E绑定。只补文件不换车/用途：同一提交ID/业务幂等键；资料更改按原未绑定PATCH及row_version规则，已绑定内容不可原地修改/重置。不得修改原请求幂等hash来掩盖配置变化。
- Scanner上报拒绝需有现有可信服务身份及root/profile/path/当前输入快照绑定；客户端自报不能冻结别人的路径。若需内部报告端点，F在同一任务冻结其DTO/鉴权/幂等，不新增公开任意路径读写能力。审计至少记录submission或未提交输入身份、校验轮次/错误码、证据摘要/时间、状态前后、恢复操作者/请求幂等身份；有界错误详情不写凭据。
- 自测/TESTER：空包、坏metadata、缺/空DB3、持续上传、上传暂停后补齐、无submission先发现、断网、重复扫描/重启、并发resume/过期row_version/重复幂等键、无效再拒/有效转绑定/已绑定拒恢复；检查零递归/自建/模型、原文件SHA、path claim不被新提交抢占、恢复后恰好一条合法运行。真MySQL状态/迁移往返及API契约必测，当前空包历史仅作为回归证据，未经当次许可不操作生产原件。
- 完成：AC-21及E幂等回归通过，开发+独立回执、OCR裁决/必要合入验证齐。产物receipts/TASK-12S-F/attempt-N.md及test-receipts/TEST-TASK12S-F/attempt-N.md；接受后触发D2全链质量候选重算，不因API成功宣生产已修。

## 3. TASK-12S-D 真实质量与血缘补验（扩量前必验，保留原PARTIAL）

本项沿用原12S-D，不另起一套全面验收。拆D1资料/真值准备与D2独立实测；原受控test阳性PASS保留，缺雷达topic的NOT_APPLICABLE只算输入适用性用例，不能算正常阴性。REQ-22/AC-22细化REQ-09/17/18/19。

### TASK-12S-D1 资料与固定验收清单

- 硬依赖V04_CLOSEOUT；建议槽C整理资料/验收fixture与清单，上游提供真实采集资料、算法owner确认有效输入和真值，TESTER复核可测试性；不改识别逻辑、不承担独立质量批准。当前DEFERRED_AFTER_V04；缺资料只阻塞相关真实用例，不阻塞E/F。
- 输出一份逐包清单：包名/稳定数据引用、全文件摘要/DB3顺序、真实已登记vehicle_code映射及来源、采集时区、已批准sensor profile、topic及消息有效性、业务人工真值区间/正常区间（storage ns及标注来源）、预期用例、数据许可和资源预算。人工标注在包外，不能把采集意图或本次模型输出当真值。
- 至少有一个输入有效的已知水雾阳性、一个输入有效的真实正常阴性、一个目标区间跨两个DB3边界的真实多DB3包；质量样本须符合冻结算法15秒窗口/抽样和有效帧约束，4秒短包探针不能替代完整窗口质量证据；可由同一阳性包兼顾跨DB3，不强迫多造样本。至少一辆真实车辆的父/子继承完整实证；test不是实车替代。现有1012可复用已证材料，但不能凭文件数/包名认定跨边界命中或阴性。
- 冻结有限批次清单、数量/总字节/并发预算/现有许可；包含阳性/阴性/不适用/无效输入，覆盖E/F修复。业务质量接受阈值及适用范围须业务/算法owner书面确认，尚无数值时记录待确认，不编造准确率或把“有子包”定为质量通过。运维/模型许可不足明确BLOCKED_MATERIAL或BLOCKED_RESOURCE。
- 产物receipts/TASK-12S-D1/attempt-N.md与包外样本清单；可部分交付已齐用例，全部关键资料和阈值齐才解除D2对应真实验收阻塞。不得发消息向上游索取、修改生产车辆或拷贝生产包作为本规划动作。

### TASK-12S-D2 固定候选独立全链验收

- owner TESTER；硬依赖V04_CLOSEOUT、E/F已接受固定集成SHA、D1相应用例资料/质量阈值/许可齐备，原12S-A/B/C和正式环境沿用；当前DEFERRED_AFTER_V04。缺一项不得写READY或全PASS；独立机械验证可随E/F冻结先做，不等真值材料齐。
- 正式Scanner→提交/登记/绑定/outbox→Orchestrator/本机代理→模型→切片/NAS→入库/获取/血缘。冻结代码、迁移、配置、参考图/模型/解码渲染版本和数据清单；先隔离环境验证，生产抽验另按发布/数据许可，不直写数据库、绕过正式链或擅自重跑现有在途大包。
- 真阴性必须有支持雷达topic且可正常解码/识别，预期NO_MATCH且无伪切片；模型异常/未知不是正常。阳性对照人工区间核误报/漏报、起止/前后扩展边界及原规则，按冻结业务阈值裁决；输出指标的定义/分母/未知样本，不用NOT_APPLICABLE填充真阴性准确率。
- 跨DB3核storage整数ns和源消息顺序、边界两侧消息不漏不重不偏移，切片可打开/计数与声明范围一致；不能只测“有2个DB3”或借合成测试替代真实跨边界。每片父source代次/场景/版本、真实车辆、标签来源、原包与子包API/物理获取一致，原文件完整SHA不变；两次reconcile幂等。
- 固定批次逐项验收全链结果并区分SUCCESS/NO_MATCH/NOT_APPLICABLE/INPUT_REJECTED/FAILED；不删除失败条目提高通过率。重复同批提交/扫描/恢复不新烧模型、不新增无效run/attempt/子包；有意新的合法分析单独标识。记录批次耗时/调用数/重试/字节/空间及资源上限，报告适用规模，不新设吞吐SLO或顺带做性能优化。旧自建/NVIDIA/坡道及v0.4界面必要回归。
- 回执test-receipts/TEST-TASK12S-D/attempt-N.md逐项PASS/FAIL/NOT_RUN/缺资料，关联D1清单、固定SHA和真实产物；mock单列。发现产品缺陷回原模块owner最小修复，若算法需调参先提交差异给ros2_slice负责人，不自行接手大包优化。
- 完成：E/F工程门禁与D2质量/血缘/批次证据、业务阈值接受及生产发布门禁齐后，协调者才可将原12S-D/12S聚合收口并提出扩量候选。缺真阴性/实车/真实跨边界或质量阈值，维持PARTIAL及扩量阻塞；不撤销已接受受控首包，不自动授权全面生产推广。

## 接续、资源、交接

依赖：V04_CLOSEOUT→E→F；V04_CLOSEOUT→D1；E+F+D1齐→D2→原12S-D及12S聚合收口→另核扩量发布准入。D1资料缺口不会阻塞E/F，F不等真实模型质量才能修输入。

首波建议A做E、C做D1，B等E公共文件释放再做F；TESTER是独立槽。E接受即重算F；D1任一资料补齐重算对应真实测试；F接受且材料齐重算D2。共享ingest/API、迁移头、生产NAS写者、MySQL隔离库与VLM许可分别单owner，开发槽不等于资源并发；不为满三槽新增任务。

协调者在v0.4结束后补派单实际base/owner/attempt和分支创建要求，执行者自行建树；主仓用户脏文件/已有接受证据保留。开发自测→TESTER固定快照→协调者唯一ocr_runtime串行裁决→适用强审/接受合入→必要合入后验证。强审默认人工，旧grant不恢复；本计划不运行OCR、模型、迁移、生产操作或新cron。发布仍需当次有效授权和SPRAY-RELEASE适用门禁。

共享主文档/任务状态由协调者短租约单写；本规划已借同一租约落盘，后续交协调者维护，不代写执行者ACK。开发日志DEVELOPMENT-LOG.md，全局事件TIMELINE.md。遇关键身份/状态契约变化、未知写者、需要改已绑定源或越过目录保护即停相关项，提交最小修订；不借“自动化”清理/改写历史数据。
