# TASK-16B attempt-2-r3：仅关闭R1-02/R1-03残余反例

status: DISPATCHED；owner=C；2026-10-13T18:03:29+08:00。当前协调者为用户指定的Codex，见inbox/control/COORDINATOR-TAKEOVER-20261013.md。

## 固定输入及边界

base=e152465，原wt-03b-t16b续commit。强审结果`reviews/strongmodel/runs/005277e6e60a43308431b5505f0bf6dc/result.md`必须读全文，原R1-01/04/05已关闭不重做。只有两个原CORRECTION未关闭，不扩全量，不引入新队列/业务流程。12S-C92dcb52仍冻结等待。先ACK本单、核原owner停止/租约后动码，不遍历全历史。

只动scripts/scene_host_proxy.py及tests/test_scene_host_proxy.py；如现有Backend租约/状态机确使proxy-only无法满足原契约，先交具体调用/状态反例和最小所需接口变更给当前协调者，不能模拟后端支持、扩大文件边界或降低断言。

## 两项必须关闭的可执行反例

1. R1-02：checkpoint DONE/FAILED，原终态写入未提交，补报再次未提交或对账GET失败。当前_report_steps只print后返回，_finish_success无条件删recovery，失败收尾也不核步骤。必须让步骤回报有明确确认结果，并在清恢复依据前保留可补报的事实；恢复只能补报原attempt，不能重新跑解码/模型/发布。必须看真实Backend租约规则：complete-scene清任务租约，不能先终态再幻想旧token可补步骤。特别核REGISTER/complete调用顺序；有需要边界调整先报确切位置，不能仅加一层try/except。
2. R1-03：模型已失败，SCENE_FAILED上报未提交，恢复文件虽保留却仍是EXECUTING/RESOLVING；重启recover_pending_runs启动execute_run→编排器再次分析。必须先持久化失败收尾意图（原attempt/目标终态/原因/必要步骤checkpoint）再尝试回报；恢复识别此意图只做对账补报收尾，任何Backend短时不可用均不得掉回业务执行。保留已提交丢响应/其他终态不覆盖行为。

最小设计要求：区分业务执行恢复和待收尾恢复；确认状态传播到清理调用方；网络失败不无限重试、不标成功，不丢恢复入口，不重烧模型。对已有成功REGISTER造成Backend终态的情形要按真实接口能力处理，不能用宽松stub盖住409。现有_backend.step调用的lease/attempt语义要纳入验证。

## 一次自测后冻结

先新增并运行能复现上述失败的定向断言（修前失败证据可留最小日志），再修复到通过：DONE/FAILED × 已提交丢响应/原写未提交/补报继续失败/GET失败；故障解除后按原attempt步骤收敛、恢复台账清理；失败上报未提交→重启→只补原失败，模型执行计数新增0。断言调用完整收尾/恢复，不止_report_steps局部。加入真实Backend约束或准确等价fixture，不能让stub允许终态后无租约写步骤。

复用r2已通过39用例及未改模块证据，只跑proxy/orchestrator受影响定向组与ruff，不重跑全仓。遇到断言失败立即收敛原因，不反复读日志。不等待OCR先交付：续commit冻结r3_head，回执receipts/TASK-16B/attempt-2-r3.md含完整SHA、两个问题ID设计/命令rc/关键断言/实际边界。协调者→增量OCR及原授权两问题复审，TESTER独立核恢复。

本单不授权合入或生产写入。若同根因两轮后的proxy-only边界确实不足，交当前强模型协调者裁决，不再以增加重试/吞错反复试过关。
