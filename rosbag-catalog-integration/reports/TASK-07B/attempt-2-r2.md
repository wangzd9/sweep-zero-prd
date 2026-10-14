# 报告：TASK-07B attempt-2-r2 最小返修

- 交付：`68b5188`（base `f4bfcf2`，分支 `scene/task-07b-manual-revision-withdraw` @ `wt-04a-t07b`）
- 范围：OCR r102 收口 10/10 后 CONFIRMED CORRECTION 5 处必改 + LOW 5 处随同，`git diff --stat`=6 文件 +330/−21（零越界）

## A. 改动行为

1. **标签域对齐（R2-1/R2-6）**：详情页 corrected_label 下拉从 7 个臆造标签（slope/flat/construction/congestion/night/rain/other）收敛到服务校验域 `{slope,flat,unknown}`（引 `segment.py` 权威常量域），并加 `required`——此前 5 个非模型域选项必 422、合法 `unknown` 却无入口。
2. **body 守卫（R2-2）**：`PATCH scene-labels` / `POST withdraw` 两接口的 `await request.json()` 后加 `isinstance(data, dict)` 守卫，非 dict（list/scalar）与非法 JSON → 422，消除 `body.get` AttributeError 500，对齐文档化 422 面与 `ingest_submissions._parse_model` 先例。
3. **守卫 UPDATE（R2-3）**：revise/withdraw 的 row_version 乐观锁从「读比对 + ORM `bag.row_version += 1`（commit flush）」改为单条 `UPDATE … WHERE id=… AND row_version=:expected`（`synchronize_session="fetch"`，输方 rowcount==0→rollback+409），对齐 `ingest_service.update_submission` F2 既有模式；审计/幂等写入全部在守卫之后，409 前不落任何脏数据。消除真并发同版本先后写的 lost-update / StaleDataError 500。
4. **双行防御（R2-4）**：MANUAL evidence 查询加 `.order_by(id).limit(1)`，防表无唯一约束下双 MANUAL 行 `scalar()` 抛 `MultipleResultsFound` 500。
5. **下架徽章布局（R2-5/R2-8）**：`.bag-scene-withdrawn` 删 `display:inline-block`（对 flex item 无效/blockified）与 `margin-left:6px`（相对兄弟 pill 错位 6px），加 `align-self:flex-start`（对齐 `.bag-scene-badge`/`.bag-scene-history`）——此前徽章撑满 120px 单元格且左移错位；`color` 走 `var(--red)`。
6. **审计时间口径（R2-9）**：`manual_revision_history`/`scene_manual_revisions_context` 返回 dict 的 `created_at` 从 `isoformat()`（`T` 分隔）改全站 `datetime_local` 口径 `%Y-%m-%d %H:%M:%S`（新增 `_format_local`，naive DB 时间按 display_timezone 本地化）。
7. **列表冗余三元（R2-10）**：`bags.html` 状态列 `'failed' if WITHDRAWN else 'failed'` 简化为统一 `else 'failed'`，title 改条件输出，消除非 WITHDRAWN 切片行的空 `title=""`。
8. **文件尾换行（R2-7）**：service 补 POSIX 尾换行。

## B. 验证证据

- 定向 `test_task07b_r2_revision.py` 5 用例 + 既有 `test_task07b_manual_revision.py` 3 用例全绿。
- 全量 `pytest tests`：**857 passed / 4 failed / 10 skipped**；4 failed 在 base `f4bfcf2` stash 复跑复现（3 devflow 外部沙箱 + 1 web 性能计时），**环境性非本侧回归**。
- ruff：3 个改动 Python 文件 `All checks passed`。
- 页面实测 `scratch/r2_page_smoke.py`（自包含 uvicorn 127.0.0.1:18771 + 临时 SQLite，口径同 07A）：**10/10 PASS**（徽章 CSS 规则断言 + all 视图 DOM + corrected_label 选项域/required + 审计时间口径）。

## C. 风险/留证

- R2-3 守卫并发输方 409（非 500）与 R2-4 双行路径在 SQLite 单连接 TestClient 下验证了正确性/无副作用，**真并发双会话真 MySQL 口径留 TESTER**（与 F2 既有先例同型，`synchronize_session="fetch"` 0 行不抛异常，风险低）。
- 未跑 OCR/强审查、未合入、未推 origin（留协调者合入面）。
- 隔离资源 0 残留。