# TASK-12S-C attempt-1（前置接线）OCR 背景

## 交付
base `22ffb71`（依赖集成基线：16B-r1 `40ab818`+main `0e9a2df` 已 merge）→ head `92dcb52`，业务面**仅 27 行**：`scripts/scene_host_orchestrator.py` +18（spray 八步接线）、`scripts/scene_host_proxy.py` +9（spray 派发/恢复接线）；测试 `tests/test_scene_spray_wiring.py` +470（排除挂 TESTER）。

## 审查口径（用户 16:02 加速指令③）
- **只审 22ffb71..92dcb52 的增量 27 行业务**，base 树里已导入的 A/B/16B 代码**不重审**（各自已有审查记录：12S-A OCR 4 批零 findings 已合入、12S-B c01/c02 16 条已裁+返修、16B r9+r1 增量已收口）
- 27 行分属两文件同一调用链（派发→恢复），可合批

## 关键不变量（审查重点）
1. spray 接线不破坏 slope 默认行为（12S-A 合入面坡道零回归）
2. disabled spray 时 `incoming/spray` 不得被错误调度为坡道（REPORT 点名风险）
3. 八步编排复用既有 claim/analyze/publish/results/complete-scene 契约，不复制未审代理逻辑（16B 契约明文）
4. 幂等/单写者/恢复对账语义不因接线变化（16B-r1 六处修复面不得回退）

## 测试证据
C 回执 `receipts/TASK-12S-C/attempt-1.md`：470 行接线测试全绿（八步 DONE/发布/入库/reconcile 面）；TESTER 前置验证单并行在途（模块级，非联调）。

## 非本次范围
正式联调+真实模型全链（12S-D，等三依赖全接受）、16B-r2 返修面（C 另一单在修，r2 合入后接线受影响项复验）、算法面（12S-B 冻结+返修中）。