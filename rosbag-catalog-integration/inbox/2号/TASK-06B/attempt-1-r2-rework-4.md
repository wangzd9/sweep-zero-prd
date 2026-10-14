---
task: TASK-06B
item: attempt-1-r2-rework-4
owner: 2号
status: CLOSED
dispatched_by: 协调者
updated: 2026-10-10 18:38
base: main 74ba3bf
round: R2 终测缺陷2（测试夹具 UID 超长，中低）
---
# 2号小修：缺陷2 测试夹具 UID 超 bag_uid VARCHAR(26)

TESTER MySQL 终测独立发现（缺陷2，中低，非应用缺陷）：
`tests/test_scene_result_report.py::_parent(db, tag)` 生成 uid = `T06B` + tag + `-` + 12 hex，
tag 含连字符且较长时（`gate-other`=10 → 27 字符、`multi-scene`=11 → 28 字符）越出
`bag_record.bag_uid VARCHAR(26)`。SQLite 静默截断掩盖（且截断后内存值与库值不一致 →
reconcile 幂等二次调用 StaleDataError），MySQL strict 1406 拒绝。本单 3 条套件 FAIL 全是此因：
1. `test_identity_gates`（`_parent(db,"gate-other")` → 27）
2. `test_multi_scene_run_partial_complete_does_not_deadlock`（`_parent(db,"multi-scene")` → 28）
3. `test_reconcile_backfills_after_publish_without_report`（`_child_uid()` 27 字符截断 → 二次更新 0 行）

**处置**：把 `_parent`/`_child_uid` 的 uid 生成**统一收敛 ≤26 字符**（tag 截断或改用短 tag +
变长 hex 补齐到定长），保证 MySQL strict 不越宽、内存值与库值一致。不改应用代码。
**验证**：3 条用例真实 MySQL 8.4 PASS（可复用 TESTER 插件思路或自建临时库），SQLite 不回归。
交付：commit + 回执 + 群内通报；OCR 不自跑。

（注：TESTER 报告里 `_scene_row` 并发首建 1062 低概率竞态=观察项不派单，留后续。）
> **2026-10-10 22:28 关单（协调者）**：本单已被 2号夹具修复 `6ee858b`（合入 main `c2dbe91`）覆盖交付并合入，无需再动作；codex 裁决 reviews/codex-r2final-20261010-verdict.md 确认关单口径。
