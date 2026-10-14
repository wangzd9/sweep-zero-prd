<!-- POST-SPRAY-CLOSEOUT-20261014 -->
> **上线后接续（2026-10-14T10:49:02+08:00）**：先读 `inbox/control/POST-SPRAY-CLOSEOUT-20261014.md` 与本角色 post-release 增补。原包已拷贝/提交，三份登记绑定已于10:23恢复并复用终态run；下文“立即让A开始上传”、proxy空闲及等待绑定为初次恢复历史。本轮不重复上传/提交/retry/模型，只完成原批次验收和既有收尾。

# 飞书角色恢复及1012生产水雾整批测试（当前唯一入口）

2026-10-13T20:58:48+08:00 用户明确恢复原飞书协调者、A/B/C、TESTER和按需审查流程。Codex临时接替已结束，由原Hermes协调者job14ae4556629a重新负责唯一调度；恢复完成前Codex仅持短交接租约，完成文档后释放，再恢复任务，禁止双写。

## 已确认生产基线

main63bfcf8（纯文档领先）、生产/本地业务3c9c496，迁移20261013_01_scene_intake。常驻rosbag-scene-host.service/rosbag-scene-proxy回环8767可用，旧8765/8766及场景proxy当前active_runs空。首包原run scene-c4a88c0746e9422ca35136035fe7 attempt2真实SCENE_DONE，子包16Bc-51ac3e1fa53dbdd6b2/1752消息，20:32:37独立PASS、源SHA不变、cache_reused=true、新模型请求0。旧R3/R4/B/部署等待是历史，不能重派旧16B/S9b/11S-PREP或重做完整副本迁移。

新任务TASK-11S-BATCH-1012，输入input-manifest.json：8包约24GB，1已有完成首包、1空metadata+空DB3异常包，其余6包需真实处理。test是用户指定受控车辆；没有人工标签真值，不冒称准确率。

## 立即执行与角色边界

- 协调者立即ACK本交接，核最新TODO/当前派单与在途身份，接受下列四份任务卡；协调全批、核证据/失败分类、维护唯一状态表，必要时按问题最小返修，不自行承担日常测试。**不再问用户是否继续、是否允许上传或生产运行**，本次原文已明确授权。
- A：inbox/1号/TASK-11S-BATCH-1012/attempt-1-dispatch.md，负责本批原始拷贝校验、正式metadata提交和逐包接收身份；不得与其他角色重复上传/提交。
- B：inbox/2号/TASK-11S-BATCH-1012/attempt-1-dispatch.md，独立读输入适用性和后续算法失败证据，不改已冻结算法/阈值、不开第二条模型线。
- C：inbox/3号/TASK-11S-BATCH-1012/attempt-1-dispatch.md，独立生产装配/资源/租约/进度观察，按run检查，不重复启动任务或改系统配置。
- TESTER：inbox/TESTER/TASK-11S-BATCH-1012/attempt-1-dispatch.md，独立观察正式生产链路及产物，按当前attempt验八步、血缘、获取、幂等、源SHA/旧功能；不提交包、retry或重调模型。

## 接收契约（必须落到实际操作）

1. 逻辑根为用户指定incoming，当前scene-spray profile消费其**spray子目录**：/public/rosbag_scene_processing/incoming/spray/<bag>；处理机实际CIFS挂载是/mnt/nas_backup/rosbag_scene_processing/incoming/spray/<bag>。不得投旧/public/vla_dataset_builder_backup/raw_rosbags，不改旧入口。
2. 本机/home/wang/下载/1012只读。A先计算每包完整文件清单/SHA/字节；通过既有SSH alias及专用key上传，长拷贝用固定operation输入和独立systemd运行，留PID/状态/日志，**不得等待模型回合承载24GB传输**。
3. 先复制至NAS同文件系统扫描树外 /mnt/nas_backup/rosbag_scene_processing/.upload-staging/spray-production-1012-20261013/<bag>，逐文件SHA一致后rename到incoming/spray/<bag>。不让Scanner看到半截拷贝，不写原包.done/sidecar、不覆盖已有incoming/ready/final。
4. 已有首包须核本机SHA与ready及正式提交完全一致，复用既有PASS及身份。其他包若已存在也先对账源/metadata/提交/run；有不同内容立即拒覆盖。同一包一份正式submit，idempotency_key由固定batch/包名/完整摘要稳定派生并持久保存，禁止每回合换key。
5. 新包完整落位前后使用正式POST /api/v1/ingest-submissions，profile_id=scene-spray、relative_path=<bag_name>（相对spray/而不是重复加spray）、source_metadata按清单固定test/Asia/Shanghai/batch/sensor_profile。用途scene_slice和场景spray由profile默认配置固定，不改参数。test已经登记，先GET核对，不重复造车。
6. Scanner稳定窗口→ready→Backend登记/绑定→场景consumer→Orchestrator→唯一正式proxy→本地解码渲染→远端VLM→分段→本地写完关闭SQLite→校验复制NAS同盘staging→原子发布→Backend入库。**拷贝并不替代必要逐包metadata提交**。场景执行按现有SCENE_EXEC_HOST资源串行，不手工并发烧模型。
7. 只读/正常业务API优先；目前已有服务与overlay正常，不重新部署/重建镜像/迁移数据库/重启gateway。若证据确需变更先由协调者明确最小纠错范围，保留授权内必要恢复，不把大包耗时当失败。

## 验收及异常

每包记录：源完整摘要、字节/DB3/topic、submission/source/run/attempt、进度时间、实际终态/scene outcome、步骤、模型请求/缓存、产物uid/消息/路径/车/时间、原始SHA及旧健康。SUCCESS要求非空AVAILABLE/current子包和两次正式reconcile幂等；NO_MATCH和NOT_APPLICABLE应无伪切片。空包应输入校验拒绝/隔离并可追溯，不回退自建；不得补造metadata或把输入失败写成功。

有两个约17.5分钟、多DB3的大包和一个9分钟多DB3包，处理可持续到夜间/次日。观察预算可以延长，后台任务继续；不为超时重烧、kill、缩短数据、降过滤阈值或伪造结论。跨DB3需真实源时间与边界证据，原单DB3首包PASS不能替代。发现真实业务缺陷保留现场，协调者指定owner最小修复；不因一包失败盲目重试整批，不复制旧checkpoint冒充新attempt。

既有审核机制恢复：后续代码类变更按唯一ocr_runtime.py串行，已有接受3c9c496不因恢复机制重新阻塞本批运行；上次OCR不等待只属于上次收尾，不永久继承。强审仅按具体风险/固定AC/有效授权经strong_review.py，旧grant已撤销，**恢复机制不等于擅自续旧授权或立即重复强审**。本批纯拷贝/提交/验收无需新代码强审。

## 周期和结束

保留原5分钟错峰poll、独立observer timer、协调者白天20分钟/08:00夜间总结、A/B/C/TESTER11/15/18总结及21–08静默。夜间照常执行任务/派单/取证，只不主动群报；用户主动问询照常答复。恢复现有job，不新建重复巡检或无变化模型循环，不恢复已废弃idle-report。新UI继续暂停。

协调者收到后写ACK和批次操作计划，立即让A先上传短包及空包验证入口，其他包同样完整排队；TESTER在首包/批次进度变更时增量验收。运行中由Hermes持续接续，不等本次Codex交互常驻。全部输入处理/拒绝均可解释且独立验收齐后收口；未完成条目保持RUNNING/BLOCKED，不预标DONE。
