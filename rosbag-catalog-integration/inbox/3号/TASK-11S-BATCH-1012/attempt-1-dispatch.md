# TASK-11S-BATCH-1012 / C / attempt-1

状态：DISPATCHED，owner=C，2026-10-13T20:58:48+08:00。生产业务固定3c9c496；用户已明确授权本批生产数据复制及水雾全链。

先读inbox/coordinator/SPRAY-BATCH-1012-20261013/HANDOFF.md和input-manifest.json；本单替代旧角色即时动作，仅旧任务历史保留。先核在途owner，再ACK固定快照/范围/实际进程，禁止双写。

任务：生产装配/资源/租约与进度只读观察。

核当前3c9c496源码/overlay/注册表/ready只读/发布别名/本地write到NAS copy/资源池、旧8765/8766与8767；监测批次run续租和checkpoint区分adapter长阶段，无变化不模型轮询。不要重启、重部署、改挂载、迁移、起新run或模型。原16B/12S-C已DONE。

原Skill门禁与只写自己ACK/session/事件/回执保持；业务修复不是本次预设任务，发现具体问题报协调者再最小派单。长机械操作用runtime_tools.py冻结spec的start/status，观察到新状态再接续，不阻塞模型会话等复制/推理。

输出inbox/3号/TASK-11S-BATCH-1012/attempt-1-ack.md与receipts/TASK-11S-BATCH-1012/c-attempt-1.md（TESTER使用test-receipts/TASK-11S-BATCH-1012/attempt-1.md）。失败如实保留证据，未完成不PASS。
