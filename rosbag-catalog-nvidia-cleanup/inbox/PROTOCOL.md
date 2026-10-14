# NVIDIA 删除专项协作协议 NC-v1

唯一共享根：`/home/wang/work/doc/prd/rosbag-catalog-nvidia-cleanup`。
当前只规划，未绑定/未配置 cron/未派发开发。启动授权见 [HANDOFF](../HANDOFF.md)。

## 1. 权威来源与角色

TODO 唯一任务状态源，DESIGN 唯一冻结契约，HANDOFF 恢复检查点；ROLE-BINDINGS 只保存角色/群/cron/workspace/迁移信息，不复制业务状态。

协调者单写主文档、派单、decision、OCR记录、review包、统一时间线并批准合入；A/B/C 只写自己代码范围、session、ACK/receipt/event；TESTER 只写测试材料/回执/session/event，不改实现、不跑 OCR、不合入。规划者本次建立文档后交给协调者接续。

开发者从派单固定 base 自行建分支/worktree；共享根始终为上述绝对路径，不能使用各 worktree 的通信副本。保护用户主工作区未跟踪内容。

## 2. 领取与接续

有效派单含 task/attempt、owner、固定 SHA、worktree/分支责任、允许文件、契约、AC、输入、授权、停止条件、回报路径。先 ACK，再开发；没有派单不依赖任务卡自行领取。实际派单位置 `inbox/{ROLE}/NC-xx/attempt-N.md`，ACK 和回执独立写。

交付 REVIEW_PENDING/TEST_REPORT_PENDING 不等于通过；协调者核对文件范围、自测、独立证据、适用 OCR/强审查后才接受/合入/标 DONE。成功事件触发候选重算，硬依赖全接受、输入齐全、文件/资源无冲突且角色空闲才派；不自动启动 WAITING_AUTH/DEFERRED。

## 运行时拆分与并发补位

协调者在5分钟巡检、任务接受、阻塞解除或开发槽空闲时，先检查已有可派叶任务；任务过粗则在原REQ/AC、已接受契约和已授权阶段内主动拆分剩余工作，不需为正常细化反复申请批准。按实际可接人数及产物独立性分配，最多三名开发执行者，不机械按人数切块。共享文件、迁移顺序、GPU/环境及硬依赖保持串行，或明确公共接线owner及接受条件。

先在短协调写锁内重读状态，更新TODO父子关系、稳定子ID、任务卡、依赖/接续、HANDOFF和拆分事件，再派单。子卡包含原REQ/AC、固定base/契约、owner、文件/资源边界、产物、验证/证据和停止条件；父任务只聚合，不重复派完整实现，子产物接受且必要集成验证完成才DONE。已ACK、在途或等待审查的任务先核实执行者/分支/进程与检查点，确认交接及旧派单替代边界后调整，不直接换owner重派。

一个子任务接受后立即重算接续，不等整波；二十分钟报告只读，说明角色占用，有空槽却不能并行时给出具体原因及解除动作。拆分不增加逐子任务强审，按原风险合批；不激活DEFERRED/WAITING_AUTH、不增加需求或提高AC。范围/关键契约/架构变化升级规划者或用户。操作细节见 /home/wang/.codex/skills/complex-task-coordinator/references/task-decomposition.md。

## 3. 单写、资源与运行恢复

运行时复用实际 `role_runtime.py` 的 claim/renew/run/release；短共享文档写入用本专项角色租约，旧owner不明或仍存活不抢占，token不在群公开。并发开发/长测试先记录固定 SHA/实际 PID与恢复入口，再释放短控制租约，巡检不重复启动已有业务进程。上级角色租约不能当作本专项授权，反之亦然。

迁移链/集成环境/A100 fixture/OCR 各自串行，并与场景专项共同协调真实资源；OCR 使用全项目既有锁，不因目录分开多开 OCR。迁移/远端变更等待输入与相应授权，未知根/owner/进程停止事实不猜测。

绑定完成后才配置 Hermes 原生 5 分钟 poll、按quiet-digest-v1分时报告，origin/deliver 指向角色群并注入正确 Skill；默认本轮不设置 cron。关键事件落 `events/{ROLE}/` 并由运行渠道通报；不自行发邮件或群消息。暂停/结束由协调者记录检查点并停止新领取，不无限保活。

## 4. 审查与结束

协调者串行 OCR，超时/取消/空输出不算通过；非文档文件≤12/批，大文件按完整职责拆分。强审查为NC-07已开发且常规测试完成的功能批次，仅核对原REQ/AC；默认人工，用户可给协调者自定义时长/起止时间/当前任务授权，通过strong_review.py自动调用Codex。滚动60分钟跨项目最多5次，在途串行，失败/超时/复审计入；无授权、过期或撤销不新起跑。CORRECTION/VERIFICATION_GAP 最小返修或补证；OUT_OF_SCOPE 不自动派单、不抬高门禁。旧 PASS 不覆盖新代码，同根因两轮未解决升级。

本轮结束在 DESIGN_READY；后续本地开发、真实 A100 测试、生产发布分别按 TODO 阶段收口。文档、依赖满足、角色租约或定时配置都不是删除或生产操作授权。

二十分钟报告仍只读，必报强审授权期限/范围、脚本status的近60分钟次数/5、本授权累计、在途/最近结果和token/费用；未知如实标明。审查授权不启动专项或开放删除/生产权限。

协调者按交付、验证、审查、合入、阻塞变化和里程碑更新绑定的development_log；无变化巡检不刷日志，记录真实commit/结果/证据与遗留事项。正式功能日志按仓库既有流程：功能完成且有适用验证证据后，在交付收口时自动生成/合并pending候选并更新changelog/REVIEW.md；用户明确批准指定功能后才approved；实际系统更新成功后才released并更新CHANGELOG.md和Web /changelog。一个完整功能可汇总多个子任务，协调者不自行批准或发布。

## 分时段汇报（2026-10-13，替代旧空闲降频）

当前报告策略quiet-digest-v1（Asia/Shanghai）：21:00–08:00所有运行角色停止主动定时/事件群通知，但开发、5分钟脚本检查、必要模型接续、派单、测试、OCR和文档记录继续。协调者08:00汇总21:00–08:00全部角色时间段/任务、确认空闲、完成记录和当前工作，另附18:00–21:00补充；白天08:20–20:40保留20分钟全局短报。执行者A/B/C、测试者仅在11:00、15:00、18:00生成08–11/11–15/15–18时段总结（无任务也总结），取消旧20分钟及2小时空闲报告。所有总结no_agent；白天实质变化即时通报，夜间只落盘，用户主动提问可答复。时间为任务状态观察估算，等待/阻塞/记录不足不算空闲，不能倒填无证据历史。完整规则：/home/wang/.codex/skills/complex-task-coordinator/references/reporting-policy.md。未绑定专项仅同步模板，不新建cron。

Hermes现有report_job_id沿用，旧idle_report_job_id停用；协调者独立morning_report_job_id，所有报告no_agent；绑定保存计划不复制业务任务状态。

## 脚本巡检与短快照（2026-10-13）

每5分钟由独立role-document-observer.timer运行role_observer.py scan，对每个角色相关文档计算SHA-256，写ticks/快照并持久保留pending。原生角色poll仍5分钟错峰；无变化不因RUNNING或20/30分钟到点再次调用模型。有变化且角色忙碌时只排队，不重启同角色；当前工作结束后由poll接续，模型在安全检查点核对新输入。处理后才ack本轮指纹，旧ack拒绝消费新通知。未完成工作需分回合接续时先落实质检查点。报告仍quiet-digest-v1且no_agent；门禁、任务状态与分支不变。未注册项目只同步规则，不因模板更新自行创建运行群或timer。
