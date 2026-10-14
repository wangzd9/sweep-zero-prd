# TASK-16C-C attempt-1 — 执行者C

父任务 TASK-16C；REQ-16/05、AC-16/05。用户2026-10-14恢复UI并要求修复历史OCR。先读 [当前入口](../../control/V04-UI-RESUME-20261014.md)、[DESIGN §7.3.3](../../../DESIGN.md#733-页面查询与步骤映射)、[OCR逐项账](../../../reviews/TASK-16C/OCR-LEGACY-20261014.md)。本单为明确开发派单；当前DISPATCHED，角色在原收尾安全点自行ACK后才RUNNING，不代写ACK。

固定开发 seed `bd0db1d2a0fc293cb4562e2079e741739bacb0de`，未接受、带已知缺陷；从它自行建专属 branch/worktree，不改共享种子/旧冻结树/主仓。父完整增量从 `63bfcf8` 起核，叶只提交seed之后自己的增量。代码版本保留已上线水雾，不改代理/算法/阈值/schema/NAS/部署，不调用真实模型。缺公共接口改动先回协调者，保护其他owner。

回执 receipts/TASK-16C-ROLE/attempt-1.md（ROLE替换本角色），含完整base/head、文件diff、命令/退出码、逐条OCR ID/修复SHA/复验或驳回依据、未测项。对应新测试文件由各自owner写；已有 tests/test_task16c_ui_minimal.py 仅A单写。开发者自测不代替独立验证/OCR；无新缺陷且原AC满足即冻结交付，不擅自合入或部署。自身session/events按原短租约写。

文件：app/web/pipelines.py、app/templates/pipeline_detail.html、新 test_task16cc_*.py。

实现：按pipeline_type优先判断场景；八步中文映射及实际latest attempt/StepRun，不伪DONE、不回写历史。SUCCESS/NO_MATCH/NOT_APPLICABLE/FAILED/PARTIAL_FAILED/CANCELLED按实际结果分开；无StepRun未开始，全部真实终态停刷新。场景无Phase0/1/3、A100执行路径/自建强制重试；保留旧自建和NVIDIA页面。父子链接/错误/attempt可查。环境模型身份仅显示snapshot/refs的真实证据，没有记录写未登记。

逐条处置C1、C2、C3、C4（旧驳回保持）、C8、C9、16C-c05-03/04/05。C3及c05-03共修，INPUT_INVALID不是场景终态。C8 guard必须覆盖CANCELLED无retry DOM；NVIDIA来源场景run不得误露NVIDIA旧契约。自测类型×终态矩阵、缺步骤/无命中、真假身份来源、旧页面，浏览器脚本异常由TESTER独立取证。
