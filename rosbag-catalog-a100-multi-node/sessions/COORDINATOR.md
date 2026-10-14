# COORDINATOR恢复入口

状态：UNBOUND，无有效派单或运行授权；业务状态只看[TODO](../TODO.md)。

Skill：complex-task-coordinator。先读[启动](../SESSION-START.md)→[绑定](../ROLE-BINDINGS.json)→[协议](../inbox/PROTOCOL.md)→[交接](../HANDOFF.md)。共享根为`/home/wang/work/doc/prd/rosbag-catalog-a100-multi-node`。

未来核对用户实施阶段授权、最新base、其他专项在途角色/工作树、公共文件与资源后绑定；首波候选MN-01/02/03，未实际派发。负责单写共享文档、派单、证据审核、串行OCR和批准合入，不代业务开发或日常测试。依赖接受后重算候选；空槽不扩大范围。

派单写inbox/A、B、C、TESTER对应task/attempt；回执receipts/test-receipts；更新DEVELOPMENT-LOG/TIMELINE。强审查默认人工，未授权不自动调用；MN-09/10保持单独门禁。
