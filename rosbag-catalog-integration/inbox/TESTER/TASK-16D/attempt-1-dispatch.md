# TASK-16D：界面闭环独立验证恢复

派单 2026-10-14T11:25:19+08:00；REQ/AC-16、05及旧功能必要回归。先读 [当前入口](../../control/V04-UI-RESUME-20261014.md)、[验收](../../../ACCEPTANCE.md)、[15项OCR账](../../../reviews/TASK-16C/OCR-LEGACY-20261014.md)。旧批次验收在安全点提交检查点后自行ACK新单，不能中断未知测试。

现在可做：固定seed `bd0db1d2a0fc293cb4562e2079e741739bacb0de` 建独立测试树，准备三类原始/双用途/合法无血缘历史切片/当前AVAILABLE/历史/待完成/下架/未知fixture；严格MySQL隔离库和真实浏览器环境。复现C5/C7/C8及cursor/分类风险，seed有已知缺陷不得宣验收PASS。准备阶段无正式联合验收结论。

每个A/B/C叶冻结即可固定其完整SHA验证对应面，不等三线全部审查。最终协调者提供含seed和已接受叶的完整集成SHA及测试配置摘要后，再在干净独立树联合验收。不得测试移动分支或把单模块PASS扩成集成PASS。

联合矩阵：两查询入口分类/组合/分页/日期与旧书签相同；浏览器三tab/双标签/取消条件/分页/空值；场景类型×八步×真实终态/刷新与CANCELLED无JS异常；NVIDIA来源场景和原NVIDIA流程；原自建/坡道/07B审计入口不回归。使用已接受受控test首包真实UID/产物引用验证原包↔子包、场景run、受控获取和权限边界，可走只读生产API取证；不新提交、不拷包、不retry、不烧模型、不直接写库。若需本地数据用脱敏最小fixture，实际真产物证据与fixture明确区分。

真实浏览器DOM/Console/Network证据必需；缺浏览器标BLOCKED_BROWSER，HTTP200不是替代。MySQL日期/分类/cursor关键行为真环境测，SQLite不能外推。原大包在途和12S-D资料缺口只影响原批次，不阻塞本UI准备。旧TESTER PASS仅历史，新返修必须对应新SHA复验。

产物 test-receipts/TEST-TASK16D/attempt-1.md：固定SHA/环境、AC逐项证据、命令/退出码/浏览器证据路径、源UID和获取校验、失败/未测，缺陷回原owner。独立测试不改业务实现、不运行OCR、不批准合入。
