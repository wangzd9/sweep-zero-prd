# TASK-07B attempt-1 OCR r101 findings 裁决（协调者）

- 时间：2026-10-12 21:5x +08:00（r101 poll，preflight 2026-10-12T21:30:53+08:00）
- 被测：`502bf8ec..f4bfcf2a`（base main `502bf8e`，未合入）
- 依据：`reviews/TASK-07B/attempt-1/ocr-batches.md`（r101 更新）+ 协调者独立核代码（`wt-04a-t07b`）

## CONFIRMED CORRECTION（须返修）
- **b9-1 [bug·HIGH] detail.html:52 `corrected_label` 选项域与服务校验域不一致**：模板列出 slope/flat/construction/congestion/night/rain/other 共 7 项；服务 `scene_manual_revision_service.py:44 _VALID_LABELS = {LABEL_SLOPE, LABEL_FLAT, LABEL_UNKNOWN}`（= {slope,flat,unknown}，见 :198 校验 `corrected_label not in _VALID_LABELS` → 422）。f4bfcf2 只改了 service + tests 两处对齐，**漏改模板** → 用户选 construction/congestion/night/rain/other 五个必 422，且合法 `unknown` 无选项可勾。独立核实：`app/templates/detail.html:52` 现仍为 7 项列表；`app/scene/slope/segment.py:22-24` 权威常量 = slope/flat/unknown。**违反 AC-04「人工纠错」可用性**。最小修复：detail.html:52 选项改为 {slope,flat,unknown}（或引用 service 常量）。
- **b3 [bug·MEDIUM] scene_manual_revision.py:26/:35 `request.json()` 后非 dict JSON（list/scalar）→ `body.get` AttributeError → 500**，与文档化 422 面不一致。独立核实：两接口 `body = await request.json()` 后直接 `service(..., body, ...)`，service 内 `body.get(...)`，无 isinstance 守卫。兄弟 API `ingest_submissions._parse_model` 有先例。最小修复：`isinstance(data, dict)` 守卫或 pydantic DTO，非 dict → 422。

## 非阻塞（随同一返修合并，不单独触发返修）
- **b9-2 [maintainability·LOW] detail.html:72** 审计「时间」列渲染 `r.created_at.isoformat()` 字符串（含 T/微秒/+08:00），全站其余用 `|datetime_local`（detail.html:86 等）；建议 service 侧改展示格式或保留 datetime 由模板过滤。
- **b9-3 [bug·LOW] detail.html:52** `corrected_label` select 缺 `required`，空串提交触发无效 422 往返；随 b9-1 修复一并加 `required`。
- **b8 [maintainability·LOW] bags.html:226** 状态三元 `'failed' if WITHDRAWN else 'failed'` 冗余分支 + 非 WITHDRAWN 切片行空 `title=""`；功能正确（WITHDRAWN 红标/tooltip 测试已覆盖），可选简化。

## 返修派发决策
- **暂缓**：b5（核心 service +383）/b7（css）r101 低负载期 `--resume` 最后一次 **INFLIGHT**（detached pid 607379，21:59 起）。在途 resume 的 review 范围锚定 `..f4bfcf2`；此时若移动 B 的 HEAD，会使在途 resume 失效并可能引发二次返修。**等 b5/b7 收口后，把 CONFIRMED CORRECTION（b9-1 + b3）+ 非阻塞 LOW 全部并入一次最小返修派 B**（`wt-04a-t07b` 续 attempt），返修 commit 覆盖文件 = `app/templates/detail.html` + `app/api/scene_manual_revision.py`（b8 bags.html 可选）。返修后走增量 OCR + 强审查 pack + 合入 + TESTER 独立验证 → 07B DONE → 派 07C。
- b5/b7 若最后一次 resume 仍 FAILED → 该文件挂 NEEDS_REVIEW **冻结 07B 合入门禁**（未覆盖文件不得宣称收口），不无限重试。
