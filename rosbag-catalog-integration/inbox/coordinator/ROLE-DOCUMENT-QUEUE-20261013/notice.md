# 协作机制更新：五分钟独立文档检查与排队

2026-10-13 用户确认每五分钟脚本核对角色文档内容，有变化才唤醒；已有任务运行时排队。

已部署role-document-observer.timer，独立scan不受长原生模型job阻塞。变化持久保存在runtime/observer/<ROLE>.json的pending，原生poll仍五分钟错峰；同角色在途不重复启动，处理后才ack，新指纹未经读取处理不自动确认。

协调者1.5.1，执行者/测试者1.3.1；新cron prompt已更新，旧回合自然结束，不强杀、不接管未知owner。原先无变化RUNNING/20分钟强制模型唤醒已撤除。所有任务范围、分支、测试/OCR/强审查及生产门禁保持。

维护证据与验证边界：[部署报告](/home/wang/work/doc/analysis/role-document-queue-20261013/REPORT.md)；统一指南`/home/wang/work/doc/SKILL-DEVELOPMENT-WORKFLOW.md` v1.6。此通知是运行维护信息，不是业务派单或任务通过决定。请按职责记录必要开发日志/时间线，不为迁移重做已接受任务或新增强审查。
