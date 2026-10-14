# 验收决策：t10-defect3-publish-bounds（TASK-10 / r1）

- 决策：ACCEPT_MERGED
- 时间：2026-10-12 01:52 +08:00（协调者 cron poll `14ae4556629a`）
- commit：`0943885`（base `a77aa45`，merge-base --is-ancestor 双核一致）→ **--no-ff 合入 main `453da0c`（推 origin a77aa45..453da0c 成功）**
- 交付回执：`receipts/TASK-10/t10-defect3-publish-bounds.md`（REVIEW_PENDING，2026-10-12 01:46）

## 机械核验（独立复跑，非采信回执）
- diff 范围：3 文件 +166/-11 = `scene_publish_service.py` +10 / `scene_result_report_service.py` +36/-10 / `tests/test_scene_result_report.py` +131，**零越界**（`source_service.py`/`app/scene/slope/writer.py`/04B/05 域 0 改动，git diff --stat 实测）
- 行为口径逐条 vs 派单 §二：
  - §二.1 ✅ `SlicePublishSpec.actual_start_ns/actual_end_ns`（默认 None 向后兼容）+ `_write_slice_manifest` 落位（字符串口径/None 落 null）
  - §二.2 ✅ `_verify_published_files` 区间身份复核改读记录存储域边界（`observed vs actual`，变量重命名后语义不变）；**缺字段 fail-closed 409 明示"不得放行"，无 header 回退路径**
  - §二.4 ✅ writer 文件 0 改动、既有断言未删（既有 complete/reconcile 用例同步补 actual 边界，writer 同源，语义不弱化）
- 独立复跑（worktree `wt-04a-t10d3`）：定向 `TestT10Defect3PublishBounds` **2 passed** / 文件级 39 passed / **scene 面回归 204 passed, 652 deselected** / ruff **All checks passed**——与回执 §三一致
- 派单 AC 3 第 3 断言"旧记录 409 fail-closed"在 `test_old_record_missing_actual_bounds_fails_closed` 覆盖

## OCR
- T10D3-r1 串行收口 **0 findings**（session `da393f51`，2 files reviewed，elapsed 2m53s）；账 `reviews/TASK-10/t10-defect3-publish-bounds/ocr-batches.md`；`--exclude 'tests/**'` 先例口径

## 合入后 sanity（主仓独立复跑）
- alembic 单头 `20261009_02_ingest_frozen (head)`；ruff 2 文件绿；SQLite 定向 2 passed

## 强审查
- NOT_REQUIRED：单 commit、行为面=发布记录字段落位 + 复核基准切换（既有 AC 内 409→200 修复），先例口径（同 t10-defect1 15 行面）；若 E2E 复跑 v2 出现 CORRECTION 级问题再按分类处置

## 交付申报处置（重要）
- 回执 §四申报：E2E 驱动 `scratch/t10_e2e_reverify.py:336-339` 构造 `SlicePublishSpec` 未带 actual 边界 → **协调者已按申报修复驱动**（`actual_start_ns=res.actual_start_ns, actual_end_ns=res.actual_end_ns`，`SliceWriteResult` 字段存在已核 writer.py:45-46）；复跑 v2 前无需再改

## 后续
- TESTER 复跑 v2 被测快照 **`a77aa45` → `453da0c`**（#3 修复只在新快照），通知 `inbox/TESTER/TASK-10/e2e-reverify-v2-notice-after-defect3.md`；PASS → **TASK-10 DONE → P0 收口**（停止派发，不自动转 TASK-11）