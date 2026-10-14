---
task: TASK-06B
item: attempt-1-defect3-reconcile-replay
owner: 2号
status: ACCEPTED
dispatched_by: 协调者
updated: 2026-10-10 20:13
base: main 0f6aa87（已推 origin）
round: R2 终测缺陷3（06B reconcile 幂等重放路径 MySQL StaleDataError，中，app 代码面）
---
# 2号返修：缺陷3 reconcile 幂等二次在 MySQL 下 StaleDataError

TESTER r2-final-mysql-e2e attempt-2（20:04 交付，test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-2.md）
**纠正 attempt-1 误诊并定性 app 缺陷**：`test_reconcile_backfills_after_publish_without_report`
幂等二次 reconcile 在真实 MySQL 8.4.11 下 FAIL（SQLite 全绿遮坑，与 R2-02 同类）。

## 被测快照与失败事实（TESTER 取证）

- 快照 main 0f6aa87（git status CLEAN 核对一致）。
- reconcile-1 返回 200（补登记+子包推进 AVAILABLE，多字段 UPDATE bag_record id=2 生效，echo 1801 行）。
- **reconcile-2（幂等二次）在 scene_result_report_service.py:928 db.commit() 抛**
  StaleDataError: UPDATE bag_record SET updated_at=... WHERE id=2 expected 1 row, 0 matched。
- 探针证实：异常后新连接 SELECT 行存在（AVAILABLE，row_version=1）、同连接直接 UPDATE 同语句
  affected rows=1 → 不是行缺失、不是 id 错配、不是 uid 截断（child uid 实测 22 字符，小于 26，assert 通过）。
- echo 证据：`~/.hermes/cache/scratch/tester_r2_a2_t5_echo.log` 1808-1910 行
  （reconcile-2 事务内仅全 SELECT 缓存读 + 单列 UPDATE，无其他写）。

## 根因线索（供你核实，定性权在你）

reconcile-2 重放时所有业务字段已收敛（availability/relative_path/索引均已齐），
flush 只剩**单列 updated_at 的 UPDATE**（:928 commit 前）；
MySQL 默认（无 CLIENT_FOUND_ROWS）下 `affected rows` 对「值无实际变化的 UPDATE」返回 0，
SQLAlchemy 按 UPDATE 谓词行计数 0 抛 StaleDataError；SQLite 恒返回 1 → 本地全绿遮坑。
**注意**：`updated_at` 若为 Python 侧赋值且含微秒，两次调用值通常不同——若你的核实发现该假设
不成立（如列精度截断到秒导致同秒内两次写同值、或 updated_at 另有 onupdate 口径），以你的实测为准；
修复方向不变：**幂等重放路径不得依赖 UPDATE 行计数语义**（reconcile-2 应收敛成功返回 200）。

## 修复范围（最小，单 commit）

- 文件范围：`app/services/scene_result_report_service.py` 及其直接依赖（如需）。
  禁止改测试断言语义、禁止删用例、禁止改测试绕过。
- 方向参考（按你核实结果取一，须说明选择依据）：
  1. reconcile 重放检测到子包行已收敛（availability/relative_path/BagFile/BagTopic 索引均已齐）时走 no-op 路径，不触发 updated_at 变更写；
  2. 显式 UPDATE + where(id)，rowcount 按「命中即可」处理，不依赖值变化计数（MySQL/SQLite 语义一致化）；
  3. 引擎连接参数 CLIENT_FOUND_ROWS（**若走此项，必须先核实全仓所有 UPDATE 路径对 rowcount 的依赖面并列入回执**，影响面最大，慎用）。
- 同文件幂等重放相关路径（complete 重放等）做同类风险自查，仅在本次缺陷3 因果范围内修，不自扩需求。

## 验收（AC）

- AC1：`test_reconcile_backfills_after_publish_without_report` 真实 MySQL 8.4 幂等二次 PASS
  （200 + registered=true + current 不切），由 TESTER 新 attempt 独立复测；你侧给最小复现
  （可复用 TESTER 插件思路自建临时库，材料放 scratch）。
- AC2：SQLite 定向（tests/test_scene_result_report.py 全文件）+ 全量不回归 + ruff 绿。
- AC3：单 commit 零越界（git diff 仅 app 代码面 + 必要新增回归用例，不得改既有测试断言）。
- 交付：commit + 回执 receipts/TASK-06B/ + 群内通报；OCR 不自跑（协调者串行）。

## 门禁影响

- 本单收口前：06 聚合放行业务门禁**不通过**（不变式套件 39/40 残留此 FAIL）。
- 完成后路径：你交付 → 协调者验收+OCR → 合入 → TESTER 新 attempt 复测（本用例真 MySQL）
  → 强模型增量复审（用户手动触发，缺陷3 属 R2-04/06 一致性面，建议纳入）→ 03/05/06 聚合 DONE → TASK-08。
- 关联：attempt-1-r2-rework-4 与 attempt-1-r2-final-fixture-fix 两单已被 6ee858b 一并收口，
  本单（缺陷3）为 06B 侧最后一个返修。