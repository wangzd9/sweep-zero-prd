# TASK-16C-B attempt-1 OCR 裁决（协调者）
- 记录：2026-10-14 17:20 +08:00；run ocr-run-20261014（base bd0db1d→head e399daf，v1.13.0，24m7s）
- 1 finding 核实：[low] `bags.html` tab 已改「切片/原始数据/全部」，但同屏「已选筛选条件」chip 的 `view_label`（`bag_search_service.py:664` = `{"originals":"原始包","all":"全部/历史"}`）仍旧名 → 同屏两套叫法（`视图：原始包` vs tab `原始数据`）。
- 判定：**CONFIRMED（成立，UI 一致性低危）**。修复点在 A 叶独占文件 `bag_search_service.py`，超出 B 叶授权（B 正确识别转交）。
- 处置：并入 **A 叶合入前清理**（与初/补审的 `data_kind_case` dead-code 删除同包，A 叶文件），不单独烧 OCR——两处均为 OCR 已发现 finding 的直接处置，协调者机械核验 diff 即可（ocr-and-merge 口径：AWAITING_DECISION 时处理 findings 不重跑求干净）。
- **B 叶 OCR 门禁满足（1/1 finding 已裁、转 A 叶清理）**；B 叶本身 `e399daf` 冻结无待修。

# A 叶合入前清理项（两处，均在 bag_search_service.py，打包一个最小 commit）
1. 删除 `data_kind_case`（初 run 7a72eed8 + retry1 finding①：迁移后全仓零引用 dead code）。
2. `view_label` 统一为新名（`{"originals":"原始数据","all":"全部"}`），与 tab/test_web.py 断言一致（B 叶 finding）。
- 完成后 A 叶 head ff2a005→新 commit，更新集成候选，机械核验 diff + 复跑 test_web.py 定向断言即可，不烧 OCR/VLM。