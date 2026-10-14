# TASK-16C-B attempt-1 — 执行者B

父任务 TASK-16C；REQ-16/05、AC-16/05。用户2026-10-14恢复UI并要求修复历史OCR。先读 [当前入口](../../control/V04-UI-RESUME-20261014.md)、[DESIGN §7.3.3](../../../DESIGN.md#733-页面查询与步骤映射)、[OCR逐项账](../../../reviews/TASK-16C/OCR-LEGACY-20261014.md)。本单为明确开发派单；当前DISPATCHED，角色在原收尾安全点自行ACK后才RUNNING，不代写ACK。

固定开发 seed `bd0db1d2a0fc293cb4562e2079e741739bacb0de`，未接受、带已知缺陷；从它自行建专属 branch/worktree，不改共享种子/旧冻结树/主仓。父完整增量从 `63bfcf8` 起核，叶只提交seed之后自己的增量。代码版本保留已上线水雾，不改代理/算法/阈值/schema/NAS/部署，不调用真实模型。缺公共接口改动先回协调者，保护其他owner。

回执 receipts/TASK-16C-ROLE/attempt-1.md（ROLE替换本角色），含完整base/head、文件diff、命令/退出码、逐条OCR ID/修复SHA/复验或驳回依据、未测项。对应新测试文件由各自owner写；已有 tests/test_task16c_ui_minimal.py 仅A单写。开发者自测不代替独立验证/OCR；无新缺陷且原AC满足即冻结交付，不擅自合入或部署。自身session/events按原短租约写。

文件：app/web/bags.py、app/templates/bags.html、新 test_task16cb_*.py；不写共享分类服务或旧公共测试文件。

实现：严格“切片、原始数据、全部”；URL slices/originals/all保留。三类原始包括自建、英伟达、场景输入，双用途双标一行。按A共享谓词消费，不改角色掩盖NVIDIA漏项；默认当前AVAILABLE切片、全部历史/待完成/下架/未知。切tab、分页、排序、取消筛选/书签保留实际条件并正确重置页码；不相容条件明确空集。Bag详情/父子追溯/受控获取能到达，保留07B审计/修订/下架，不做07C。

自测：HTML链接参数与标签、NVIDIA空数据展示、双用途、空结果、父子/获取入口；独立浏览器交TESTER。A接口不变即可并行，不等A审查完才写页面；接口变化只暂停受影响接线。若详情其他文件存在真实必要缺口，先交协调者划定owner，禁止越界。
