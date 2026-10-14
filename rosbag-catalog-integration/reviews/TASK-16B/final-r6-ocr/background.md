# 水雾最终必要修复：8e538bb6c43d51e31de13340241ec43f835ac778

原用户授权直接修复收尾上线；车辆明确使用test，仅受控单包，不宣称真实采集车辆或批量质量验收。base=6ddcbcb，head=8e538bb6c43d51e31de13340241ec43f835ac778。原R3审查及弱OCR材料保留。本轮真实输入新增了29af的恢复修复、fe17e8a同盘发布与ad60e41两处分支修复，不是背景改字重复审查。旧prepared final-r4未启动、无模型消耗，由本最终候选取代。

冻结AC：本地场景八步保持原attempt单写者；先持久成功/失败意图，通信不确定只补报不重入模型。待收尾维持租约和ACTIVE，过期/缺租约/新attempt/明确停写→持久BLOCKED零步骤/业务补写；三个租约周期有界，不改变Backend租约验证或算法阈值。提交丢响应只按原complete幂等键确认，终态后不写steps；lease_terminal是终态清租约的正常信号，可继续有界幂等确认。

R4强审f1de0b11实际REWORK两项：终态complete一次超时错误永久BLOCKED；失败入口在stop已置位仍补写。最小修复ad60e41：真实HTTP确定4xx（408/429除外）才BLOCKED，其余异常有界重试；识别Backend RuntimeError.__cause__=HTTPError，lease_terminal不提前中止且延迟防忙循环；失败入口持久事实后先查stop并BLOCKED，不补steps/status/complete。独立测试固定29af修前16FAIL/1PASS→修后17PASS，相关正常失败/真实跨TTL/编排接线组合89PASS。完整证据r5-proxy-orchestrator-wiring-final.log及test-receipts/TEST-TASK16B-r5/codex-independent-20261013.md。按原强审处置规则最小修复+独立增量复验关闭，不升级全量重审。

fe17e8a：生产home与NAS不同st_dev，原work/staging到NAS原子rename必失败。只有切片待发布暂存改受控publish_root/.staging/run_id/attempt-N，解码/渲染/台账仍home；不降级复制、不改原包，run_id走已有safe_path_segment，空manifest不建暂存。真实/tmp与/dev/shm跨盘writer+publisher、run/attempt隔离、DB3非空、原包SHA不变、旧跨盘负例仍PUBLISH_BLOCKED及NO_MATCH共3PASS，编排组合15PASS。处理机home66310/NAS75、NAS文件/目录fsync及rename探针PASS。

子包索引修复6e91：继承父vehicle_id/link_status；relative_path相对NAS_STORAGE_ROOT按服务端根生成，不信任payload路径；epoch秒转Asia/Shanghai naive，不修改既有幂等零UPDATE规则。部署只补必需映射：proxy仅挂ready子树到/nas/rosbag_scene_processing/ready、SCENE_NAS_READY_ROOT=/nas；Backend/proxy同一只读外置能力注册表；catalog-scene显式叠加且默认0/0/URL空，旧NAS/NVIDIA/A100挂载和环境保持。

29af固定正式Scanner/Orchestrator/proxy/Backend/MySQL真实模型全链PASS：168.08s、12次VLM请求、1个3.302042339s/1752消息/43MB非空切片、12topics、8步DONE、SCENE_DONE、AVAILABLE/current=true、test/北京时间15:58:24/正确获取路径、正式reconcile两次200且结果相同、原包SHA和模型缓存不变。证据.local/spray-runtime/real-e2e-29af08a58819/final-api-verification.json。最终增量不改变模型/算法，故复用真实模型证据并对修改分支机械复验，不重复计费。B算法f76e2a9弱OCR全覆盖0findings已接受。真实多DB3 SDK仅单元证据，本次1DB3，不冒称真实多DB3生产PASS。

全仓6ddcbcb1077PASS/10SKIP/4既有失败，实际6c基线worktree同4失败：3项devflow将.git硬判目录、1项web SQL9>8。后续50 Backend/89 proxy/15 staging适用验证已通过；不弱化断言。tests由独立TESTER验证，env/service/Markdown人工按职责核对；排除不代表省略其契约审查。生产旧服务仍在，本次尚未合main或生产切换。只核既定AC，不扩UI、算法质量或全量重审。


最终生产装配增量8e538bb：proxy回报/public/rosbag_scene_processing/slices而Backend原只挂/nas，服务直接读payload根，生产无法核验。catalog-scene backend新增同一切片宿主根只读别名到/public/rosbag_scene_processing/slices，不改逻辑根与旧/nas挂载。独立真实Docker同源双路径inode/内容一致、双路写均EROFS；真实三层Compose所有旧挂载/非SCENE环境完全一致，默认0/0/空、开启1/1/回环8767正确。证据backend-slices-alias-docker-probe-20261013.json及backend-slices-alias-compose-probe-20261013.json。

本次base=6ddcbcb，实际5业务文件同一部署/恢复契约批。旧R3仍观察到固定截止，无杀进程/改参数；其Backend/proxy恢复变更已包含6dd已验证基线，最终收尾分支以本轮真实新head审查，绝不声称旧run PASS。final-r4/final-r5仅prepared，分别被新增真实恢复/跨FS/部署挂载修改取代，零模型消耗，冻结材料原样保留。R3若未覆盖installer/scene-proxy，将按其原提交b8437ad的完整两业务文件范围单独审查，不能把合main后的全体历史diff混进新批次，亦不省略未审文件。本轮只启动此最终快照一次，不再排相同输入。
