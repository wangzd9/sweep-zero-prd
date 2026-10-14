# 用户当前进展问题：生产只读复核及旧等待口径纠正

2026-10-14 09:54 +08:00。用户询问scene-4acf689f9a6a473da1fa2f2efc70为什么没结束、每条流水线是否符合预期。Codex只读实测报告：/home/wang/work/doc/analysis/spray-batch-progress-20261014/REPORT.md；同目录production-snapshot.json和proxy-snapshot.json可逐项复核。

- 大包仍SCENE_RUNNING/attempt1；代理PID1的socket FD inode与TCP表已交叉匹配，确有到8002的ESTABLISHED连接；PCD5373/JPG1781，最后JPG写入01:30:53，此后模型阶段已超过8小时。代码逐帧串行、V18 thinking4096、非SPRAY再SIM；没有中间逐帧持久计数。可以确认仍在途，不能据此证明吞吐达标、报完成率/ETA，或把全批标正常。
- 页面八步QUEUED来自上报实现：dispatch一次包住EXTRACT/INFER/SEGMENT，返回后才补回Backend；本地PRECHECK已DONE而DB仍QUEUED。当前先保留在途任务，不为补监控kill/retry丢掉内存结果。
- **三份正式提交的原等待口径需要立即纠正**：a65a25a7/87dfebaa/518089ed至09:53仍PENDING_INPUT、source/generation/ready均NULL，其对应源READY和旧run已DONE。create_submission不主动绑定ready源，绑定发生在source登记；资源排队发生在绑定/outbox之后。当前Scanner journal仅有旧dated16_00_13的MOVED_PENDING_REGISTER/MOVE_CONFLICT，三个flat包没有恢复记录。**SCENE_EXEC_HOST释放不等于触发登记绑定；不要继续“等4acf终态自动推进”的无证据等待。** 请在现有D4③范围核正式绑定恢复/既有源与run身份复用或明确提交收口规则，先核幂等，避免重复上传、直接改库或重烧已经完成的模型。
- 已有run7=6DONE+1RUNNING，不等于8输入全闭环：14_42_48旧重复链SUCCESS，16_37_47/16_58_28旧重复链NOT_APPLICABLE，但三份正式提交未绑定；空包持续拒绝无run，submission仍PENDING_INPUT，不能宣称提交层已有失败终态隔离。

这是一份交给原协调者的只读纠正证据，不是Codex重新接管，不改变当前owner/派单范围，不开启新模型/审查/部署。请更新BATCH-STATUS中的上述错误等待归因并按现有角色机制推进；当前用户查询原文由本文件保存，不伪造飞书队列ACK。
