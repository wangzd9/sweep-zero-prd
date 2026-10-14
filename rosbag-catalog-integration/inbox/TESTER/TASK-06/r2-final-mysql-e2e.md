---
task: TASK-06
item: r2-final-mysql-e2e
owner: 测试者
status: TEST_REPORT_PENDING
dispatched_by: 协调者
updated: 2026-10-10 20:04（测试者 attempt-2 交付：被测 main 0f6aa87，S1 三AC全PASS(迁移1406高阻塞解除)+不变式套件39/40；残留1 FAIL=test_reconcile_backfills幂等二次，探针证实非uid截断→定性06B reconcile幂等重放MySQL真实app缺陷，建议回派2号；完整报告 reports/TASK-06/r2-final-mysql-e2e-attempt-2.md，回执 test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-2.md）
base: main 74ba3bf（已推 origin，823 passed 本地基线）
round: R2 返修终测（六笔同批合入后唯一放行业务门禁）
---
# TESTER 终测：R2 全链 MySQL 端到端（main 74ba3bf）

R2 强模型 10 HIGH + 1 MEDIUM + B8a/B8c OCR findings 已全部修复并合入 main 74ba3bf（17:13）。
SQLite 全绿不能替代 MySQL 口径验证（R2-02 双引号 bug 就是 SQLite 遮坑），**本单是 06 聚合解锁前
唯一放行业务门禁**。请用真实 MySQL 8.x 隔离库执行：

## 必测场景（每项给真实 SQL 输出/断言证据，不得只报"通过"）

1. **R2-01 已有库增量迁移**：建含旧 20261008_01 状态（ingest_config 表存在、列已建、
   alembic_version=20261008_01）的库，跑 `alembic upgrade head` → 断言无 1101、
   4 个 TEXT 列（default_purposes_json/default_scenes_json/default_scene_parameters_json/
   selection_json）DEFAULT 为 None、version=20261009_02。
2. **R2-02 outbox 方言**：MySQL 默认 sql_mode 下造 PENDING 事件 → poll 投影返回真实列值
   （非字面量 "event_id"）→ consume 后 DB 终态 CONSUMED；**_mark rowcount 接线**：
   删除事件行后 replay → 断言 stats["errors"] 计数 + warning 日志（0 行不静默）。
3. **R2-03 switch_current 并发**：同 parent+scene 两版本交错 complete（旧分配 id 先 complete、
   新分配 id 后 complete，及反序）→ 断言无 1093、current 指针指向分配 id 大的版本、
   旧版本晚到返回 409 不倒退。
4. **R2-05 契约端到端**：自动路径（事件消费建 run）与显式路径（API 建 run）各 1 例 →
   断言 run 创建事务即分配 SceneAnalysisVersion（创建后 run 未 complete 时 av 行已存在）、
   换版比较用分配 id 序号（构造"晚创建先完成"交错 → 不倒退 409）。
5. **B8c 车辆路径逃逸断言**：父包有/无 Vehicle 记录 × manifest 自报 vehicle_key=".."/"a/b"/正常 四例 →
   断言发布路径始终在 publish_root 内、自报值不生效（用父包 Vehicle.vehicle_code 或 unassigned）、
   非法 code 4xx 拒绝。
6. **B8a 多场景死锁回归**：建 2 场景 run → 先 complete 场景 A（B 未回报）→ 断言 run 不定终态
   （等 B）、B 再 complete 后切 current 成功（原 SCENE_FAILED 误判路径已修）。
7. **r6 medium 回归**：M-1 child.updated_at naive 口径（与 bag_record 列同格式、无 tz 漂移）；
   M-2 父包无 fast_fingerprint + manifest 带指纹 → 409 SOURCE_FINGERPRINT_MISMATCH。

## 交付
reports/TASK-06/r2-final-mysql-e2e.md：逐场景 SQL/输出摘录 + PASS/FAIL 表；FAIL 项给最小复现。
全部 PASS → 协调者解锁 06 聚合 + 触发强模型增量复审（R2-01/02/03 必附本单 MySQL 结果）。
本单不改业务代码；隔离库用完即毁。