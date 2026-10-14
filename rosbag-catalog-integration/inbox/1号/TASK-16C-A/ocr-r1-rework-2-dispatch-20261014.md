# TASK-16C-A OCR 清理续单 R1-2（协调者，2026-10-14 17:30 +08:00）

- 状态：REWORK_DISPATCHED。并入 TASK-16C-A attempt-1 同一冻结链（不新开 attempt）；同 worktree `wt-01-t16ca`、同 branch `a/task-16c-a-query-api`，base 续 `4838ef8c3f9e11c3f7e5332882a9b2627085696a`（你 17:15 已交付的 R1 返修）。
- 来源：B 叶 OCR run `513ab61d`（17:09 收口，rc=0）唯一 finding，协调者裁决 CONFIRMED（`reviews/TASK-16C-B/ocr-run-20261014/ocr-verdict.md`）：B 叶 tab 已改名「切片/原始数据/全部」，但同屏「已选筛选条件」chip 的 `view_label` 仍渲染旧名「视图：原始包 / 视图：全部/历史」，同页两套叫法（UI 一致性低危）。修复点在 A 叶独占文件，超出 B 授权，由你处置。

## 变更（仅 `app/services/bag_search_service.py` 1 处）

- line 664：`view_label = {"originals": "原始包", "all": "全部/历史"}.get(...)` → `{"originals": "原始数据", "all": "全部"}`，与 B 叶 tab 名及 `test_web.py` 已改断言（切片/原始数据/全部）一致。`slices` 键不存在于该 dict（默认走 `.get` 回退 `state.view`），确认 slices 视图 chip 现行为后如需同口径（`"slices": "切片"`）一并补上，以页面三种视图 chip 均显示新名为准。
- 不改其他文件、不动谓词面（R1 的 A-OCR-1/A-OCR-2 已交付，不重做）。

## 边界与自测

- 复跑：`pytest tests/test_task16ca_query_api.py tests/test_task16c_ui_minimal.py tests/test_web.py -q`（seed 固有 bounded-query 失败不计本账）+ `ruff check`。
- 交付 = 续 commit 冻结 + 回执补本续单段（新 head、diff、复跑）；状态回 REVIEW_PENDING。
- 后续（协调者）：本 commit 为 A 叶最终冻结 head → 机械核验 → **单文件增量 OCR 一次**（覆盖 R1+R1-2 同文件小 diff，`scene_result_query.py` 未变不重跑）→ TESTER 增量面 → A 叶接受。不逐 commit 重复烧 OCR。