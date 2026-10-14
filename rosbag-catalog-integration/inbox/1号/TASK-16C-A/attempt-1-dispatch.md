# TASK-16C-A attempt-1 — 执行者A

父任务 TASK-16C；REQ-16/05、AC-16/05。用户2026-10-14恢复UI并要求修复历史OCR。先读 [当前入口](../../control/V04-UI-RESUME-20261014.md)、[DESIGN §7.3.3](../../../DESIGN.md#733-页面查询与步骤映射)、[OCR逐项账](../../../reviews/TASK-16C/OCR-LEGACY-20261014.md)。本单为明确开发派单；当前DISPATCHED，角色在原收尾安全点自行ACK后才RUNNING，不代写ACK。

固定开发 seed `bd0db1d2a0fc293cb4562e2079e741739bacb0de`，未接受、带已知缺陷；从它自行建专属 branch/worktree，不改共享种子/旧冻结树/主仓。父完整增量从 `63bfcf8` 起核，叶只提交seed之后自己的增量。代码版本保留已上线水雾，不改代理/算法/阈值/schema/NAS/部署，不调用真实模型。缺公共接口改动先回协调者，保护其他owner。

回执 receipts/TASK-16C-ROLE/attempt-1.md（ROLE替换本角色），含完整base/head、文件diff、命令/退出码、逐条OCR ID/修复SHA/复验或驳回依据、未测项。对应新测试文件由各自owner写；已有 tests/test_task16c_ui_minimal.py 仅A单写。开发者自测不代替独立验证/OCR；无新缺陷且原AC满足即冻结交付，不擅自合入或部署。自身session/events按原短租约写。

文件：app/services/bag_search_service.py、app/services/scene_result_query.py、app/api/sources.py、tests/test_task16c_ui_minimal.py 查询面断言、新 test_task16ca_*.py。

实现：共享多成员分类谓词与展示标签，Web/API同源；双用途两个data_kind均命中且去重。三视图包含合法无血缘历史切片、NVIDIA真实形态、未分类；data_kind/dataset_type等交集保留。核修C5、C6、C7、16C-c03-02/03/04；日期输入422、全天截止与时区一致，cursor兼容旧合法值且绑定实际过滤条件。集合GET有界并可访问，保留原detail/lineage API路由。先给B消费接口说明：保持seed函数名/返回形状/标签字段，确需变化先协调。

自测：查询fixture真值、双用途两个过滤/UID唯一、历史/下架/待完成与默认current、NVIDIA空时间/topic、未知、非法/边界日期/混合时区、有界分页换筛选cursor/旧cursor。MySQL关键行为使用隔离库或明确交TESTER验证，SQLite绿不能宣MySQL通过。停止于这些既定行为通过，不顺做写链路/索引迁移。
