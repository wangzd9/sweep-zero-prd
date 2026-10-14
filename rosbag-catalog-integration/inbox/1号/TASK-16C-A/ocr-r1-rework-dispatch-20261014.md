# TASK-16C-A OCR 最小返修单（协调者，2026-10-14 16:42 +08:00）

- 状态：REWORK_DISPATCHED。并入 TASK-16C-A attempt-1 同一冻结链（不新开 attempt）；同 worktree `wt-01-t16ca`、同 branch `a/task-16c-a-query-api`，base 续 `ff2a0055c75655f2f91f273a80af99633c9fbebf`。
- 来源：A 叶 OCR 合并裁决 `inbox/coordinator/TASK-16C-A/ocr-merge-ruling-20261014.md`（初 run `7a72eed8` + 唯一入口补审 `0aba25ee` 16:24 收口全覆盖）。两条 CONFIRMED（均 low），只改一个文件。

## 变更（仅 `app/services/bag_search_service.py`）

1. **A-OCR-1**：删除 `data_kind_case()` 函数整体（line 98 起的 SQL CASE 定义）。全仓 py/html 零调用点已独立核实（协调者 grep 在案）。删除后若 `case`、`else_` 等 import 在本文件不再被使用，一并从 import 移除；若他处仍用则保留，以 ruff 结果为准。
2. **A-OCR-2**：`data_kind_pred` 的 `scene_original` 分支（line 84-85）补 `~_scene_slice_pred()`，镜像兄弟谓词：
   `return and_(BagRecord.bag_role == "ORIGINAL", ~_scene_slice_pred(), _scene_basis_pred())`
   同步更新该函数 docstring 分类规则第 3 条口径（子包优先，与 data_kind_context 一致），避免第二套口径描述漂移。

## 边界与自测

- 不改任何其他文件（含 tests、api/sources.py、scene_result_query.py、web/）。若发现第 1 条 import 清理牵连他文件，停手报协调者，不自行扩面。
- 复跑：`pytest tests/test_task16ca_query_api.py tests/test_task16c_ui_minimal.py tests/test_web.py tests/test_task16cb_bag_views.py -q`（seed 固有失败 `test_bag_search_page_has_bounded_query_count_and_response_time` 不计本账）+ `ruff check app/services/bag_search_service.py`。
- 双用途夹具仍须两筛选都命中、UID 一条（A-OCR-2 不改变双用途行为，只堵 ORIGINAL+derivation 子包这一当前不可达组合）。
- 交付 = 续 commit 冻结 + 回执补本返修段（新 head、diff、复跑）；状态回 REVIEW_PENDING。
- 后续：协调者机械核验 → 增量 OCR 仅 `bag_search_service.py` 单文件（seed..新 head 口径由协调者定）→ TESTER 16D 增量面（含筛 scene_original 不返回 derivation 子包的一条组合断言，TESTER 自加，A 不写）。