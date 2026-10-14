# 原生恢复实测补充（Codex交接观察，非第二协调者）

2026-10-13 21:09 +08:00。原绑定5个poll及6个report均已enabled；原schedule/model/provider/skills/script/deliver/origin保持，废弃idle-report保持disabled。gateway和独立observer.timer均active。配置和真实执行记录见native-jobs-verification.json。

Codex短协调租约已于21:02释放，未再领取；当前原协调者已独立claim并写ACK.md和BATCH-STATUS.md。以下是增量事实，请原协调者在下个安全检查点更新自己的状态，不重派任务：

- TESTER已于21:05:01完成正式ACK，文件inbox/TESTER/TASK-11S-BATCH-1012/attempt-1-ack.md；它已核生产栈、源清单，等待A新包入场。BATCH-STATUS中的TESTER待ACK需按此证据更新。
- A原生execution=e6d1bfddebe9425385d46e2c051752ac，pid2491657，21:04:53开始；C=a5bfe425a90e4fcf93ebef9ab2778b3a，pid2491658；B=4d66ba14825d4b8fbe65a0e86f022ac3，pid2489288。这些是原角色在途，不因ACK暂缺再开同角色业务会话。
- 正确角色租约目录为inbox/control/runtime/leases/。21:09实测存在COORDINATOR.json、B.json、C.json；0字节.lock不等于在途。ACK.md的“无各角色JSON租约”仅保留为当时观察，不能用于后续判断角色空闲。
- 协调者direct execution=bcac35783b05497b9daf81f65889c637，pid2490490仍在途；21:05另一调度器Fire claim lost是互斥拒绝重复执行，不能把它当本角色已经退出或接管失败。
- 处理机21:08已出现.upload-staging目录，但尚未看到本批包完成上传/正式submit证据，因此不得把目录创建写成全链启动成功。

本次用户明确恢复的唯一任务保持TASK-11S-BATCH-1012。大包长传输/推理交给独立后台operation和既有生产服务，正常推进到夜间，不等Codex保持在线；没有新代码就不启动重复OCR或强审。
