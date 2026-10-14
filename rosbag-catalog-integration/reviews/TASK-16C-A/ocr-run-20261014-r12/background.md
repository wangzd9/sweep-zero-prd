# TASK-16C-A R1-2 增量 OCR 背景（协调者冻结）

- 任务：TASK-16C-A（查询/API 叶，父 TASK-16C）attempt-1 OCR 增量复审；REQ-16/05、AC-16/05。
- 授权来源：用户 2026-10-14 恢复 v0.4 最小界面闭环（inbox/control/V04-UI-RESUME-20261014.md）。
- base/head：`bd0db1d2a0fc293cb4562e2079e741739bacb0de`（未接受开发 seed）→ `1489bc6`（A 叶最终冻结 head：R1 `4838ef8` 删 data_kind_case 死函数 + scene_original 补 ~_scene_slice_pred；R1-2 `1489bc6` 仅 line 664 view_label 字面量「原始包/全部/历史」→「原始数据/全部」对齐 B 叶 tab）。
- 本批只审：`app/services/bag_search_service.py` 单文件（ocr.lock 串行，tests 排除归 TESTER 16D 面）。
- 既有覆盖声明：`scene_result_query.py` 已由补审 run `0aba25ee`（16:24 收口，rc=0，0 findings，指纹在 manifest）覆盖，本批不重复；该文件 seed..1489bc6 与 seed..ff2a005 内容未变（R1/R1-2 均未触碰），协调者 diff --stat 独立核在案。
- 前序 findings 处置状态（不重复裁决，供审查对照）：A-OCR-1 data_kind_case 已删（4838ef8）；A-OCR-2 scene_original 已补 ~_scene_slice_pred（4838ef8）；view_label 已改新名（1489bc6）。审查重点=这三处修复自身是否引入新问题（import 残留/谓词语义漂移/字面量一致性），以及同文件未被前两轮覆盖到的新增行面。
- 关键不变量：DESIGN §7.3.3 分类单源（SQL 谓词与 Python 标签同一优先级）；双用途原包两筛选都命中、UID 一条；data_kind 枚举与集合 GET 路径不变。
- 测试证据（协调者独立复跑 17:5x）：74 passed + 1 failed（seed 固有 bounded-query，stash 同口径）；ruff 全绿。
- 待核实风险：严格 MySQL 与真实浏览器面归 TESTER 16D，本 OCR 不替代。