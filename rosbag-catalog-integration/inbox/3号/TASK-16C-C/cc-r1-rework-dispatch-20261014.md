# TASK-16C-C 返修单 CC-R1（协调者，2026-10-14 13:00 +08:00）

- 状态：REWORK_DISPATCHED。并入 C 的 TASK-16C-C attempt-1 同一冻结链（不新开 attempt）；base 续 `522bb3f358f042160b25b5a66d55434500ab2928`，同 branch `c/task-16cc-pipeline-detail`、同 worktree `wt-c-16cc`。
- 来源：协调者 OCR 唯一入口 run `e7a5580cdf9f4eed8b448aad1c61f53b`（base `bd0db1d…`→head `522bb3f…`，AWAITING_DECISION 收口）b01 唯一 finding；裁决 `inbox/coordinator/TASK-16C-C/ocr-attempt1-adjudication-20261014.md`。

## 返修项（唯一）

CC-R1（medium/bug，c05-04 半修）：`app/templates/pipeline_detail.html` 数据血缘兜底分支（`scene_lineage` 存在但 lineage 与 children 均为空的 `{% else %}`，当前 line 67 附近）只有 `<li class="muted">…</li>` + 悬空 `</ol>`，缺开始标签。最小修复=该分支补 `<ol class="lineage">` 开始标签，保持兜底文案与 muted 类不变；不扩面、不改其他分支。

同步修正 `tests/test_task16cc_scene_detail.py::test_no_lineage_fallback_li_in_ol`（C 独占）：兜底 `<li>` 必须同时断言位于 `<ol class="lineage">` 开始标签之后、`</ol>` 之前（当前只断言 `</ol>` 存在，掩盖了半修）。仅改本断言面，不加需求。

## 边界与自测

- 只动 C 独占两文件（模板 + C 新测试文件）；不碰 seed/旧 B 冻结树/主仓/A/B owner 文件。
- 复跑 `pytest tests/test_task16cc_scene_detail.py tests/test_task16c_ui_minimal.py -q` 并回执；seed 固有失败按原口径不计本账。
- 交付=续 commit 冻结 + 回执补返修段（新 head/文件/断言/复跑结果）；状态回 REVIEW_PENDING。

## 审查口径（协调者已定）

- 返修后**不整叶重跑 OCR**：CC-R1 修复面（模板血缘分支 3 行 + 测试断言）在返修 commit 上由协调者独立核 diff 与实际文件；若 diff 超出模板血缘分支/C 测试断言两小面，转增量 OCR（原 run 已退出、身份变化由协调者按唯一入口处理，不自动重试）。
- TESTER 独立验证（真实浏览器 JS/严格 MySQL/联合面）仍按 16D 原口径，在固定集成候选上收口；本返修不阻塞 TESTER 准备。
- 16R 盘点对 c05-04 的账随本返修闭合后更新为「修复已交付待独立核」。

## 协调者核验段（2026-10-14 13:27 +08:00）

- C 返修续 commit `ce5921d`（13:10:15 落盘）机械核验**全绿**：diff 严格在返修单两小面内——模板数据血缘兜底 `{% else %}` 分支 +1 行 `<ol class="lineage">` 开始标签（已读实际文件 line 67 确认闭合结构 `<ol><li class="muted">…</li></ol>` 有效）；测试断言升级为先核开始标签位置、再核 li 后闭合（3 条断言防半修回归）。零越界，同 branch/worktree。
- C 叶状态 REWORK_DISPATCHED → **DELIVERED_REVIEW_PENDING（返修闭环，待独立验证）**；按返修单口径**不整叶重跑 OCR**（修复面已在协调者独立核范围内）。
- 已并入协调者集成候选 `wt-coord-intcheck-16c`（三叶零冲突，候选 head `1d7f15c`），六测试文件合跑 108 passed+1 seed 固有失败（13:27 实测）。
- 剩余门禁：TESTER 16D 真实浏览器 JS/严格 MySQL 独立验证（不互斥，TESTER 13:15 已开工 ce5921d 面）→ 齐后接受。