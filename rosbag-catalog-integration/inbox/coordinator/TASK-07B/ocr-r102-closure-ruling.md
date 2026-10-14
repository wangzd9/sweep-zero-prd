# TASK-07B attempt-1 OCR r102 收口裁决 v2（协调者）

- 时间：2026-10-12 23:0x +08:00（r102 poll，preflight 2026-10-12T22:35:53+08:00，claim 23:05:46）
- 被测：`502bf8ec..f4bfcf2a`（base main `502bf8e`，未合入）
- 依据：`reviews/TASK-07B/attempt-1/ocr-batches.md`（r102 更新，10/10 全收口）+ 协调者独立核代码（`wt-04a-t07b` HEAD `f4bfcf2`）
- 续：`ocr-r101-findings-ruling.md`（b9-1 HIGH / b3 MEDIUM CONFIRMED 维持）

## 收口事实
- **OCR 10/10 全收口**：b5 resume 最后一次 RC=0 1800s（session `7d703528`，3 findings，round2 报 review_round_failed 但 core review complete=有效口径同 b9）；b7 resume 最后一次 RC=0 839s（session `997d0ddd`，3 findings）；22:43:38 `== done ==` 落盘，detached pid 607379 已退出、ocr.lock 无持有者（ps+fuser 核）。无 NEEDS_REVIEW 文件，**07B 合入门禁 OCR 面不再因覆盖缺口冻结**，改按 5 处 CONFIRMED CORRECTION 走 R2 最小返修。

## 新增 CONFIRMED CORRECTION（r102 独立核代码属实）
- **b5-1 [bug·MEDIUM] service revise:204-206 / withdraw:289-293 乐观锁非守卫写入**：`if bag.row_version != expected: raise 409` 后 ORM `bag.row_version += 1`（commit flush），真并发两个同 row_version 写方可先后都通过检查 → 一方修订静默丢失（lost-update）或 StaleDataError 500，与派单/文档化「row_version 冲突 409」语义不一致。仓库既有先例：`ingest_service.update_submission` F2 注释（单条 `UPDATE … WHERE row_version=:expected` 守卫，输方 rowcount==0→409）。最小修复：availability/row_version 变更改单条守卫 UPDATE（同 F2 模式），输方 409。
- **b5-2 [bug·MEDIUM] service:215-221 `db.scalar(select(BagSceneLabelEvidence)…label_source='MANUAL')` 无 `.order_by().limit(1)`**：该表无 (bag_uid, scene_id, label_source) 唯一约束（独立核 models.py:597-619 + 迁移 20261012_01）；历史数据或 b5-1 竞态窗口产生双 MANUAL 行时 `scalar()` 抛 MultipleResultsFound → 500。最小修复：`.order_by(BagSceneLabelEvidence.id).limit(1)`。
- **b7-1 [maintainability·MEDIUM] bag-search.css:1376-1385 `.bag-scene-withdrawn` 布局错位**：`.bag-scene-cell`（:1328）=column flex gap 4px，兄弟 `.bag-scene-badge`（:1336）/`.bag-scene-history`（:1345）均 `align-self: flex-start`，新徽章缺之 → 撑满单元格宽度（min 120px）且 `margin-left: 6px` 相对其他 pill 错位 6px；`display: inline-block` 对 flex item 无效（blockified）。最小修复：删 `display`/`margin-left`，加 `align-self: flex-start`（同规则块内 2 处 LOW 一并：:1384 `color: var(--red)` 一致性可选）。

## LOW 非阻塞（随 R2 同 commit 合并，不单独触发返修）
- b5-3 [style·LOW] service 文件尾缺换行。
- b7-2/b7-3 [style·LOW] css :1384 颜色 var(--red) 一致性与 :1378 margin 语义（与 b7-1 同规则块）。
- b9-2 [maintainability·LOW] detail.html:72 审计时间列 `isoformat()` 字符串非全站 `datetime_local` 口径（service 侧 `manual_revision_history`/`scene_manual_revisions_context` 返回 dict 处格式化或模板过滤，二选一，不新增依赖）。
- b8 [maintainability·LOW] bags.html:226 状态三元冗余分支 + 非 WITHDRAWN 切片行空 `title=""`（可选简化）。

## 返修派发决策
- **R2 最小返修已派 B**（`inbox/2号/TASK-07B/attempt-2-r2-dispatch.md`）：CONFIRMED 5 处全修 + LOW 6 处随同 commit（同一文件块内顺手项）；覆盖文件 = `app/templates/detail.html`、`app/api/scene_manual_revision.py`、`app/services/scene_manual_revision_service.py`、`app/static/bag-search.css`（必改 4）+ `app/templates/bags.html`（b8 可选）；base 保持 `f4bfcf2` 之上续 commit（原 base `502bf8e` 不变，本地 main `c2018dd` 纯文档零 app 面零冲突）。R2 交付后：机械核验 → 增量 OCR（仅 R2 diff 文件）→ 强审查 pack（授权 0/5 期限 2026-10-13 11:33:12）→ 合入 → TESTER 独立验证（含 R2 新增语义：非 dict 422、守卫 UPDATE 并发 409 口径、corrected_label 域、下架徽章布局页面实测）→ 07B DONE → 派 07C/16C。
