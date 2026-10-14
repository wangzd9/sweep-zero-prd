# TASK-11S-BATCH-1012 / B / attempt-1

状态：DISPATCHED，owner=B，2026-10-13T20:58:48+08:00。生产业务固定3c9c496；用户已明确授权本批生产数据复制及水雾全链。

先读inbox/coordinator/SPRAY-BATCH-1012-20261013/HANDOFF.md和input-manifest.json；本单替代旧角色即时动作，仅旧任务历史保留。先核在途owner，再ACK固定快照/范围/实际进程，禁止双写。

任务：独立输入适用性/算法证据检查。

本机原始数据只读，查实际packet/PointCloud2 topic和类型、多DB3/空包；不猜无水雾真值、不复制输入、不调模型。独立结果给协调者，后续若出现具体算法问题等待明确最小返修单。原12S-B已接受，禁止重修旧S9b。

原Skill门禁与只写自己ACK/session/事件/回执保持；业务修复不是本次预设任务，发现具体问题报协调者再最小派单。长机械操作用runtime_tools.py冻结spec的start/status，观察到新状态再接续，不阻塞模型会话等复制/推理。

输出inbox/2号/TASK-11S-BATCH-1012/attempt-1-ack.md与receipts/TASK-11S-BATCH-1012/b-attempt-1.md（TESTER使用test-receipts/TASK-11S-BATCH-1012/attempt-1.md）。失败如实保留证据，未完成不PASS。
