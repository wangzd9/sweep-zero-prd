---
task: TASK-06
item: r2-final-mysql-e2e
owner: 测试者
status: TEST_REPORT_PENDING（21:47 TESTER attempt-3 交付 PASS：真 MySQL 8.4.11 31/31 + 幂等二次探针 200/200 无 StaleDataError；报告 reports/TASK-06/r2-final-mysql-e2e-attempt-3.md，回执 test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-3.md）
dispatched_by: 协调者
dispatched_at: 2026-10-10 21:40
base: main 5f0124b（2号缺陷3修复 4e2158e --no-ff 合入，已推 origin）
round: 缺陷3（reconcile 幂等二次 StaleDataError）修复后，聚焦复测（新 attempt，不重跑已 PASS 场景）
receipt_path: test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-3.md
---
# TESTER 聚焦复测：06B 缺陷3 reconcile 幂等二次（main 5f0124b）

前一轮 `r2-final-mysql-e2e` attempt-2（20:04 交付，TEST_REPORT_PENDING）裁决结果：
S1 三 AC 全 PASS（迁移链 1406 高阻塞**已解除**）+ 不变式套件 39/40；
唯一残留 FAIL = `test_reconcile_backfills_after_publish_without_report`
（**缺陷3，06B app 代码面**：reconcile 幂等重放路径二次 UPDATE `updated_at`
在 MySQL 下 affected rows=0 抛 `StaleDataError`，`scene_result_report_service.py:928` commit；
DATETIME(0) 秒精度同秒 no-op 值 + 无 CLIENT_FOUND_ROWS，SQLite 恒 1 遮坑）。

协调者已回派 2号并收口：

- **修复**（2号 4e2158e，21:14 交付，base 0f6aa87，单文件
  `app/services/scene_result_report_service.py` +27/-3）：
  `_mark_children_available` 捕获 6 业务字段（availability/relative_path/
  started_at/duration_ns/message_count/total_size_bytes）赋值前原值，
  仅确有业务变化才推进 `updated_at`；幂等重放 no-op **零 UPDATE**。
- **协调者机械核验全绿**：零越界、方向与派单一致（逐行核 diff）；
  开发自测=真 MySQL 8.4.11 A/B 复现闭环（旧码 FAILED / 修复后 1 passed，
  隔离库 0 残留）+ SQLite 定向 31 passed + 全量 822 passed + ruff 绿。
- **OCR D3 收口 0 findings**：D3-r1（session `5ee653d5`，21:19 起跑）
  被 cron 化身回合结束杀死（4 组完成、无 run manifest，`--resume` 被工具
  拒绝）→ 协调者按 §4 重跑 D3-r2（session `81a9e337`，21:30 起，365s，
  terminal_state=complete，**0 findings**，coverage 1/1 selected=completed，
  base 0f6aa87..head 4e2158e 精确一致）。批次账
  `reviews/TASK-06B/attempt-1-defect3-reconcile-replay/ocr-batches.md`。
- **已合入 main `5f0124b`**（21:37 --no-ff，0 冲突，已推 origin）；
  合入后 sanity：`alembic heads` 单头 `20261009_02_ingest_frozen` ✓、
  该文件 ruff 绿 ✓、`tests/test_scene_result_report.py` SQLite 31 passed ✓。

## 本单只复测缺陷3（真实 MySQL 8.x 隔离库，逐项给 SQL 输出/断言证据，不得只报"通过"）

1. **reconcile 幂等二次真 MySQL PASS**：
   `tests/test_scene_result_report.py::test_reconcile_backfills_after_publish_without_report`
   在真实 MySQL 8.x 库下 PASS——重点断言二次 reconcile（幂等重放）
   **不再抛 StaleDataError**；可加探针记录二次 UPDATE 的 affected rows
   与行 `updated_at` 是否未被无谓推进（方向证据，非硬门禁）。
2. **定向不回归**：`tests/test_scene_result_report.py` 全套（31 用例）
   真 MySQL 或 SQLite 口径跑 PASS（本笔改动仅触及
   `_mark_children_available` 一个函数路径）。
3. **前一轮残留口径核对**：不变式套件前一轮 39/40，本单复测后若第 40 条
   （reconcile_backfills）转 PASS 即 40/40，报告注明。

## 停止条件
- 不重跑 S1/S2/S3/S4/B8c/B8a/r6（已 PASS，且本笔改动仅
  `scene_result_report_service.py` 幂等重放路径，未触及迁移/switch/
  publish/vehicle 面）。
- 不扩展范围、不修代码；若复测仍 FAIL，报告探针证据（SQL/rowcount/
  会话隔离对比），定性后由协调者回派，不在本单内代修。

## 交付
- 回执 `test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-3.md`
  + 报告 `reports/TASK-06/r2-final-mysql-e2e-attempt-3.md`，
  落盘后发 TESTER 事件（TEST_REPORT_PENDING）。
- PASS → 协调者解锁 06 聚合最后一道业务门禁；剩余=强模型增量复审
  （用户手动触发，缺陷3 并入复审包）→ 03/05/06 聚合 DONE → TASK-08。