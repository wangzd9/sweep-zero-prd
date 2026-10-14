# TASK-16C-A 合入前清理项（派单，17:2x，协调者）

> **⛔ 状态更正（协调者 17:50，`ocr-r1-rework-2-dispatch-20261014.md` 为准）**：本单 ① `data_kind_case` 删除**已由 A 按 R1 返修单 `ocr-r1-rework-dispatch-20261014.md` 交付并核验（commit `4838ef8`，17:15:40，协调者 17:20 机械核验独立复跑全绿）**，勿重复执行。② view_label 改新名**继续有效**，按 `ocr-r1-rework-2-dispatch-20261014.md` 口径执行（base 续 `4838ef8`，非本单的 `ff2a005`）。本单末尾「scene_original 误报 REJECTED、本单无需再 OCR」口径**作废**：F2 经 17:30 裁决冲突统一维持 CONFIRMED（防御性），且 R1 已交付；A 最终 head（含 view_label 续 commit）冻结后按 ocr-and-merge 做一次单文件增量 OCR（`bag_search_service.py`），不以 finding 处置名义跳过。A 交付时以 R1-2 单为回执依据即可，本单不另立回执段。

- status: DISPATCH；owner=1号(A)；base=`ff2a005`（A 叶当前冻结 head）续 commit，同 branch `a/task-16c-a-query-api`
- 性质：**OCR 已发现 finding 的直接处置**（初 run + retry1 + B 叶转交共 2 处），**不烧 OCR/VLM**，协调者机械核验 diff + 复跑 `tests/test_web.py` 定向断言即可收口。
- 两处改动，均在 A 独占文件 `app/services/bag_search_service.py`：
  1. **删除 `data_kind_case()` 函数**（初 run 7a72eed8 + retry1 finding①：迁移到 `data_kind_pred` 后全仓零引用 dead code，协调者已 grep 确认无 .py/模板/前端调用者）。
  2. **`view_label` 统一为新名**（B 叶 `ocr-verdict.md` 转交 finding）：`bag_search_service.py:664` 的 `{"originals":"原始包","all":"全部/历史"}` → `{"originals":"原始数据","all":"全部"}`，与 `bags.html` tab（B 叶 e399daf）及 `test_web.py:365-366` 断言「原始数据/全部」一致，消除同屏两套叫法。
- 完成标准：一个最小 commit（只动 `bag_search_service.py`，含两处）；本地 `test_web.py` 定向断言绿；回执 `receipts/TASK-16C-A/attempt-1.md` 追加清理段（commit SHA + 两处 diff 摘要 + 测试退出码）。
- 不越界：不动其他文件、不重新跑全仓回归（集成候选已有 1163 passed 基线，两处为删除+字面量，行为面零变化），不合入（合入等协调者 + TESTER 16D 齐后统一集成 SHA）。
- 16C-A OCR 门禁：初 run + retry1 已全裁完（2 findings：data_kind_case 成立→本单①；scene_original 误报 REJECTED）；本单是 finding 处置非新发现，无需再 OCR。