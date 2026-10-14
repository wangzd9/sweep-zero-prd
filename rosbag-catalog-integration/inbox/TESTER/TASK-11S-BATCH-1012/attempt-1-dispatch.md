# TASK-11S-BATCH-1012 / TESTER / attempt-1

状态：DISPATCHED，owner=TESTER，2026-10-13T20:58:48+08:00。生产业务固定3c9c496；用户已明确授权本批生产数据复制及水雾全链。

先读inbox/coordinator/SPRAY-BATCH-1012-20261013/HANDOFF.md和input-manifest.json；本单替代旧角色即时动作，仅旧任务历史保留。先核在途owner，再ACK固定快照/范围/实际进程，禁止双写。

任务：生产正式全链逐包独立验收。

A是唯一提交者，本角色不提交/复制/retry/调模型。读正式API/物理文件/源完整SHA，按当前attempt筛八步，SUCCESS核子包消息/车辆test/获取/时间/AVAILABLE/current，两次正式reconcile；NO_MATCH/NOT_APPLICABLE/空包拒绝分别验，不强求切片。多DB3真实边界独立取证；本批无人工标签不宣称准确率。

原Skill门禁与只写自己ACK/session/事件/回执保持；业务修复不是本次预设任务，发现具体问题报协调者再最小派单。长机械操作用runtime_tools.py冻结spec的start/status，观察到新状态再接续，不阻塞模型会话等复制/推理。

输出inbox/TESTER/TASK-11S-BATCH-1012/attempt-1-ack.md与receipts/TASK-11S-BATCH-1012/tester-attempt-1.md（TESTER使用test-receipts/TASK-11S-BATCH-1012/attempt-1.md）。失败如实保留证据，未完成不PASS。
