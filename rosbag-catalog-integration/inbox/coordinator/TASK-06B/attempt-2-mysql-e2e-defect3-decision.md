# Decision：TESTER r2-final-mysql-e2e attempt-2 裁决（缺陷3 回派 2号 + attempt-1 误诊更正）

- status: DECIDED
- 裁决：协调者（cron poll 14ae4556629a）
- 时间：2026-10-10 20:1x +08:00
- 输入：`test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-2.md`（20:04 交付）+
  `reports/TASK-06/r2-final-mysql-e2e-attempt-2.md` + 协调者独立核实（main HEAD 0f6aa87、
  echo 日志 1808-1910 行、探针结论、测试用例源码 tests/test_scene_result_report.py:864-909）

## 裁决 1：采纳 TESTER attempt-1 误诊更正（事实修正）

TESTER 自行更正并给探针证据：`test_reconcile_backfills_after_publish_without_report` 的
MySQL FAIL **不是** uid 截断（child uid 实测 22 字符、parent 18 字符，均小于 VARCHAR(26)，
assert 通过；fixture 6ee858b 合入后仍 FAIL）。协调者核实同意，attempt-1 报告中
「reconcile 二次 StaleDataError = 夹具口径问题、非应用缺陷」的表述**作废**，
以 attempt-2 §纠正为准。由此，2号 attempt-1-r2-rework-4 / attempt-1-r2-final-fixture-fix
两单的实际处置：`6ee858b`（夹具 uid 收敛）已合入 main c2dbe91 且**有效**（identity_gates /
multi_scene 两用例确已转 PASS），两单账目随本裁决一并收口（缺陷2 成立、修复正确；
其指认的第三条用例归因错误部分由本裁决更正）。

## 裁决 2：缺陷3 定性 = CORRECTION（既定 AC 违反，06B app 代码面）

- 现象：reconcile 幂等二次在 MySQL 8.4.11 下 `scene_result_report_service.py:928 db.commit()`
  抛 StaleDataError（`UPDATE bag_record SET updated_at=... WHERE id=2` expected 1 row, 0 matched）；
  探针证实该行存在且新连接同语句 affected rows=1 → 非行缺失/非 id 错配/非截断。
- 对应 AC：测试用例断言「再次 reconcile 不重复登记」返回 200（既定幂等契约，REQ-06 幂等登记）；
  违反面 = R2-04/06 一致性。属 CORRECTION，非 OUT_OF_SCOPE。
- 根因线索（供 2号核实，定性权在 2号）：重放时业务字段已收敛，flush 仅剩单列 updated_at 的
  UPDATE；MySQL 默认 rowcount 语义对「值无实际变化的 UPDATE」返回 0（CLIENT_FOUND_ROWS 未设），
  SQLAlchemy 按计数 0 抛 StaleDataError；SQLite 恒返回 1 → 本地全绿遮坑（与 R2-02 同类教训）。
- 处置：**回派 2号 `attempt-1-defect3-reconcile-replay`**（派单 `inbox/2号/TASK-06B/attempt-1-defect3-reconcile-replay.md`，
  base main 0f6aa87，最小单 commit，修复方向=幂等重放不得依赖 UPDATE 行计数语义；禁止改测试绕过）。

## 裁决 3：门禁更新

- 06 聚合「迁移链 MySQL」高阻塞：**解除**（S1 三 AC 全 PASS）。
- 03 聚合（03B）MySQL 路径验收缺口：**随 attempt-2 收口**（R2-01/02 真实 MySQL 全 PASS）。
- 06 聚合放行业务门禁：**仍不通过**（缺陷3 收口前）。解锁路径：
  2号缺陷3 交付 → 协调者验收+串行 OCR → 合入 → TESTER 新 attempt 复测（本用例真 MySQL PASS）
  → 强模型增量复审（用户手动触发；R2-01/02/03 MySQL 结果在案，缺陷3 建议纳入）
  → 03/05/06 聚合 DONE → TASK-08。
- 06B 行维持非 DONE（本单收口+复测 PASS 前）。
- 强审查判断：本次缺陷3 由独立测试者在约定功能批次测试中发现，属常规 CORRECTION 回派；
  不单独触发 REVIEW_NOW，按既有计划并入下一次强模型增量复审包。

## 责任人

- 缺陷3 根因+修复：2号（06B app owner）
- 复测：TESTER（2号交付合入后新 attempt，协调者届时派单）
- 本 decision 不改变 06A/04/02 等已 DONE 行。