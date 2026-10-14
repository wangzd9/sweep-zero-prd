# 回执：TASK-07B attempt-2-r2 最小返修（REVIEW_PENDING）

- 任务：TASK-07B R2 返修（REQ-04 / AC-04；原 attempt-1 `f4bfcf2` 之上最小修正）
- owner：B（`cron-b-poll-6f7471d8747c-20261012-232253`）
- 派单：`inbox/2号/TASK-07B/attempt-2-r2-dispatch.md`（r102 收口裁决后一次性）
- 裁决依据：`inbox/coordinator/TASK-07B/ocr-r102-closure-ruling.md`
- base：`f4bfcf2`（在其上续 commit；原 base `502bf8e` 不变）
- 交付 HEAD：**`68b5188`**（`68b51887d0ff94275f2dd9f61b1f76fa0907fd9d`），分支 `scene/task-07b-manual-revision-withdraw` @ `wt-04a-t07b`
- 时间：2026-10-12 23:xx +08:00（交付冻结）
- 状态：**REVIEW_PENDING（交付冻结，未合入、未推 origin、未跑 OCR/强审查）**

## 一、R2-1~R2-10 逐项处理

| ID | 严重 | 文件:位置 | 处理 | 证据 |
|----|------|-----------|------|------|
| R2-1 | HIGH(b9-1) | `app/templates/detail.html:52` | corrected_label 选项域 7→3 项对齐 `{slope,flat,unknown}`（权威常量域，与 `_VALID_LABELS` 字面一致） | `test_r2_1`：5 非模型域标签仍 422 + unknown 200 + 页面下拉选项域断言 |
| R2-2 | MEDIUM(b3) | `app/api/scene_manual_revision.py` 两接口 | 新增 `_parse_json_object`：非法 JSON / list / scalar / 空 body → 422（非 `body.get` AttributeError 500），对齐 `ingest_submissions._parse_model` 先例 | `test_r2_2`：两接口 list/scalar/非法 JSON 全 422 + 版本未推进 |
| R2-3 | MEDIUM(b5-1) | `app/services/scene_manual_revision_service.py` revise+withdraw | 乐观锁改**单条守卫 UPDATE** `_guarded_bump_row_version`（`UPDATE … WHERE id=… AND row_version=:expected`，`synchronize_session="fetch"`，输方 rowcount==0→rollback+409），对齐 `ingest_service.update_submission` F2 模式；审计/幂等均在守卫之后、409 不落 | `test_r2_3`：外部推进版本后带旧 rv→409 且 0 审计/0 幂等/版本不推进 |
| R2-4 | MEDIUM(b5-2) | 同文件 :215-221 | MANUAL evidence 查询加 `.order_by(BagSceneLabelEvidence.id).limit(1)`，防双 MANUAL 行 `MultipleResultsFound` 500 | `test_r2_4`：同 (bag,scene,MANUAL) 双行夹具→200 且更新 id 最小行、id 最大行不动 |
| R2-5 | MEDIUM(b7-1) | `app/static/bag-search.css:1376-1385` | `.bag-scene-withdrawn` 删 `display:inline-block`+`margin-left:6px`，加 `align-self:flex-start`（对齐兄弟 `.bag-scene-badge`/`.bag-scene-history`） | 页面实测：CSS 规则断言 + all 视图不撑满/左对齐 |
| R2-6 | LOW(b9-3) | `detail.html:52` | corrected_label select 加 `required` | `test_r2_1` + 页面实测 required 断言 |
| R2-7 | LOW(b5-3) | service 文件尾 | 补换行（POSIX） | `git diff` `\ No newline` 消除 |
| R2-8 | LOW(b7-2) | `bag-search.css:1384` | `color:#d64545` → `var(--red)`（app.css:10 已定义） | 页面实测 CSS `var(--red)` 断言 |
| R2-9 | LOW(b9-2) | service `manual_revision_history`+`scene_manual_revisions_context` | 审计时间 `isoformat()` → 全站 `datetime_local` 口径（新增 `_format_local`：naive DB 时间按 display_timezone 本地化 `%Y-%m-%d %H:%M:%S`），两返回 dict 处统一 | `test_r2_9` + 页面实测审计列 `YYYY-MM-DD HH:MM:SS` |
| R2-10 | LOW(b8) | `app/templates/bags.html:226` | 状态三元冗余分支 `'failed' if WITHDRAWN else 'failed'` 简化为 `… else 'failed'`；title 改条件输出消除非 WITHDRAWN 切片行空 `title=""` | `test_r2_9` + 页面实测 `title=""` 不在 rows |

## 二、自测证据

- **新增定向** `tests/test_task07b_r2_revision.py`（5 用例，复用 attempt-1 夹具 `_mk_bag/_mk_scene_slice/_purge`，自造自清 SQLite）：全绿。
- **既有定向** `tests/test_task07b_manual_revision.py`（3 用例）：全绿（无回归）。
- **全量**（SQLite，`pytest tests`）：**857 passed / 4 failed / 10 skipped**——本侧 R2 交付 +5 新用例（`test_task07b_r2_revision.py`）；**4 failed 均在 base `f4bfcf2` stash 复跑复现**=`test_devflow.py`×3（外部沙箱/无交互路径）+`test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time`×1（性能计时），**环境性非本侧回归**（stash 掉本侧改动、0 app 面改动即复现，口径同 attempt-1 交付申报）。
- **ruff**：改动的 3 个 Python 文件（api/service/测试）`All checks passed`（--fix 消除 I001 导入排序）。
- **页面实测**（自包含 uvicorn `127.0.0.1:18771` + 临时 SQLite，`scratch/r2_page_smoke.py`，口径同 07A）：**10/10 PASS**——withdraw 200 WITHDRAWN / all 视图含已下架 / 非 WITHDRAWN 无空 `title=""` / CSS `align-self:flex-start`+删 `display:inline-block`+删 `margin-left`+`color:var(--red)` / corrected_label 选项域 `{slope,flat,unknown}` / select required / 审计时间 `YYYY-MM-DD HH:MM:SS` 口径。隔离资源 0 残留（临时 SQLite + 自造行全清）。

## 三、未执行项（如实）

- 未跑真 MySQL 8.4：R2-3 守卫 UPDATE 与 R2-4 order_by/limit 在 SQLite 单连接 TestClient 口径下验证了正确性与 409 无副作用；**真并发双会话同版本先后写的守卫输方 409（非 500）无法在 SQLite 单连接复现**，留 TESTER 真 MySQL 口径（`synchronize_session="fetch"` + `UPDATE … WHERE row_version=:expected` 与 F2 既有先例同型，风险低）。
- 未跑 OCR/强审查（归协调者合入面）；未合入、未推 origin。
- R2-9 口径选择=**service 侧返回 dict 处格式化**（派单二选一的 service 侧方案），模板未加 filter，零新依赖。

## 四、越界申报

无越界：改动面=5 个派单允许文件（detail.html / scene_manual_revision.py / scene_manual_revision_service.py / bag-search.css / bags.html）+ 1 新增测试文件；零新表/迁移/依赖；未动 03~06B 状态机/幂等/发布；未实现 07C/16C。`git diff f4bfcf2..68b5188 --stat`=6 文件 +330/−21。

## 五、后续链（供协调者）

R2 交付 → 机械核验 → 增量 OCR（仅 R2 diff 文件）→ 强审查 pack（授权期至 2026-10-13 11:33:12）→ 合入 main → TESTER 独立验证（API 四要素+R2 新语义：非 dict 422/守卫并发 409/选项域/徽章布局/审计时间口径+既有 0 红）→ 07B DONE → 派 07C/16C。