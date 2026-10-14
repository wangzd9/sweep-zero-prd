# 派单：TASK-07B attempt-2-r2 最小返修（OCR 收口 10/10 后一次性）

- status: ACKED
- 派单时间：2026-10-12 23:0x +08:00（r102 poll）
- 任务：TASK-07B R2 返修（REQ-04 / AC-04；原 attempt-1 交付 `f4bfcf2` 冻结面之上最小修正）
- owner：B（`wt-04a-t07b`，分支续 `scene/task-07b-manual-revision-withdraw`）
- base：`f4bfcf2`（原交付 HEAD，继续在其上 commit；原 base `502bf8e` 不变；本地 main `c2018dd` 纯文档 commit 零 app 面，合入时协调者处理，无需 rebase）

## 一、返修问题 ID 单（全部来自 OCR 收口 + 协调者独立核代码，裁决 `inbox/coordinator/TASK-07B/ocr-r102-closure-ruling.md`）

### 必改（CONFIRMED CORRECTION 5 处）
1. **R2-1（b9-1 HIGH）`app/templates/detail.html:52`**：`corrected_label` 下拉选项域与服务校验域对齐——现列 slope/flat/construction/congestion/night/rain/other 共 7 项，服务 `_VALID_LABELS`={slope,flat,unknown}（`segment.py:22-24` 权威常量），5 项必 422 且合法 `unknown` 无选项。修复：选项改为 {slope,flat,unknown}（直接引用或字面一致）。
2. **R2-2（b3 MEDIUM）`app/api/scene_manual_revision.py`**（PATCH scene-labels 与 POST withdraw 两接口，:26/:35 附近）：`await request.json()` 后非 dict JSON（list/scalar）→ `body.get` AttributeError → 500，与文档化 422 面不一致。修复：`isinstance(data, dict)` 守卫（兄弟 API `ingest_submissions._parse_model` 先例），非 dict → 422 明确语义。
3. **R2-3（b5-1 MEDIUM）`app/services/scene_manual_revision_service.py`** revise（:204-206/:255）与 withdraw（:289-293/:310）：乐观锁改**单条守卫 UPDATE**（`UPDATE bag_record SET availability=…, row_version=row_version+1 WHERE id=… AND row_version=:expected`，输方 rowcount==0 → 409），对齐 `ingest_service.update_submission` F2 既有模式；消除真并发 lost-update/StaleDataError 500。注意 evidence/audit 写入顺序与守卫失败路径（409 前不落审计、不落 evidence 变更）。
4. **R2-4（b5-2 MEDIUM）同文件 :215-221**：MANUAL evidence 查询加 `.order_by(BagSceneLabelEvidence.id).limit(1)`，防双 MANUAL 行 MultipleResultsFound 500（表无该唯一约束，已核）。
5. **R2-5（b7-1 MEDIUM）`app/static/bag-search.css:1376-1385`**：`.bag-scene-withdrawn` 删 `display: inline-block` 与 `margin-left: 6px`，加 `align-self: flex-start`（对齐兄弟 `.bag-scene-badge`/`.bag-scene-history` 口径）。

### 随同 commit（LOW 非阻塞，同文件块顺手项）
- R2-6：detail.html:52 `corrected_label` select 加 `required`（空串提交不再无效 422 往返）。
- R2-7：service 文件尾补换行（POSIX）。
- R2-8：bag-search.css:1384 `color: #d64545` → `var(--red)`（app.css:10 已定义）。
- R2-9（可选，不扩面）：detail.html:72 审计时间列展示口径与全站 `datetime_local` 一致（service 返回 dict 处格式化或模板过滤，二选一）。
- R2-10（可选，不扩面）：bags.html:226 状态三元冗余分支 `'failed' if WITHDRAWN else 'failed'` 简化 + 非 WITHDRAWN 切片行空 `title=""` 消除。

## 二、测试（最小增量，并入既有 `tests/test_task07b_manual_revision.py` 或新增同前缀文件）
- R2-1：corrected_label=construction 等 5 项提交仍 422（原断言）、unknown 提交成功（新增）；
- R2-2：两接口 body 为 JSON list/scalar → 422（新增，非 500）；
- R2-3：同 row_version 二次写 → 409（既有）；守卫 UPDATE 口径下并发输方 409 而非 500（如可用 SQLite 模拟同版本双会话则加，不能则声明留 TESTER 真 MySQL 口径）；
- R2-4：同 (bag_uid,scene_id,MANUAL) 双行夹具 → 修订成功且更新 id 最小行（新增）；
- 页面实测：下架徽章在 all 视图切片行不撑满宽度、与 scene 标签 pill 左对齐（截图或 DOM 断言，口径同 07A）；
- 既有定向 + 全量 0 红（基线 849 passed，3 devflow 环境性不算）、ruff 绿。

## 三、边界与禁止
- 只动上述 5 必改 + 4 可选文件块；不新增表/迁移/依赖；不动 03~06B 状态机/幂等/发布；不改生产 compose；不实现 07C/16C（B 后续 16C 在 07B 收口后另行派单）。
- 交付=commit + 回执 `receipts/TASK-07B/attempt-2-r2.md`（REVIEW_PENDING）+ 报告 `reports/TASK-07B/attempt-2-r2.md`；回执逐项列 R2-1~R2-10 处理与证据。
- 停止条件：回执落盘后冻结等审；不自行合入、不跑 OCR（OCR 归协调者）。

## 四、后续链（协调者侧，供 B 知悉）
R2 交付 → 机械核验 → 增量 OCR（仅 R2 diff）→ 强审查 pack（24h 授权在案，滚动 60min 0/5，期限 2026-10-13 11:33:12）→ 合入 main → TESTER 独立验证（API 四要素+R2 新语义+页面布局+既有 0 红）→ 07B DONE → 派 07C/16C。
