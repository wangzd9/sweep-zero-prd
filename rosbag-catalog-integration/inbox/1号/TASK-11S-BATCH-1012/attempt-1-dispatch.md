# TASK-11S-BATCH-1012 / A / attempt-1

状态：DISPATCHED，owner=A，2026-10-13T20:58:48+08:00。生产业务固定3c9c496；用户已明确授权本批生产数据复制及水雾全链。

先读inbox/coordinator/SPRAY-BATCH-1012-20261013/HANDOFF.md和input-manifest.json；本单替代旧角色即时动作，仅旧任务历史保留。先核在途owner，再ACK固定快照/范围/实际进程，禁止双写。

任务：原始拷贝/完整SHA校验/幂等正式元数据提交。

只写本任务operations/上传台账/ACK/回执。你是唯一上传及提交owner；先短包后长包，完整包在扫描树外同盘暂存后原子移入incoming/spray。读取共享清单，不修改源、不修改业务实现、不写主TODO。已完成首包只核摘要复用，不重新提交。长传输冻结operation跨回合执行。

原Skill门禁与只写自己ACK/session/事件/回执保持；业务修复不是本次预设任务，发现具体问题报协调者再最小派单。长机械操作用runtime_tools.py冻结spec的start/status，观察到新状态再接续，不阻塞模型会话等复制/推理。

输出inbox/1号/TASK-11S-BATCH-1012/attempt-1-ack.md与receipts/TASK-11S-BATCH-1012/a-attempt-1.md（TESTER使用test-receipts/TASK-11S-BATCH-1012/attempt-1.md）。失败如实保留证据，未完成不PASS。
