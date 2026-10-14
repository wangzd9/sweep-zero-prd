---
task: TASK-06
item: r2-final-mysql-e2e
owner: 测试者
status: TEST_REPORT_PENDING
dispatched_by: 协调者
updated: 2026-10-10 20:14（TESTER 交付，指针见文末）
base: main 0f6aa87（已推 origin gitlab-local 19:0x）
round: S1 返修 + 夹具返修后，聚焦复测（新 attempt，不重跑已 PASS 的 5 场景）
---
# TESTER 聚焦复测：S1 迁移改短 + 夹具 uid（main 0f6aa87）

前一轮 `r2-final-mysql-e2e`（18:17 交付，test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-1.md）
**6 PASS / 1 FAIL**：S2/S3/S4/B8c/B8a/r6 全 PASS；**唯一 FAIL=S1 R2-01 迁移链 1406**。
协调者已回派两笔最小返修并合入：

- **S1 修复**（1号 ceeac16，已合入 main 0f6aa87，OCR S1-r1 0 findings）：
  `alembic_version.version_num VARCHAR(32)` 容不下 33 字符 head revision
  `20261009_02_ingest_frozen_columns` → 改短为 **25 字符** `20261009_02_ingest_frozen`
  （down_revision 不动、零兼容风险：全仓无旧 ID 功能引用、无任何 MySQL 库应用过该 revision）。
- **夹具修复**（2号 6ee858b，已合入 main c2dbe91，纯测试 +4/-1）：
  `tests/test_scene_result_report.py::_parent` bag_uid hex12→hex10 收敛 ≤26 字符 + assert 防护
  （前一轮缺陷2：tag>10 生成 27 字符 uid 越 `bag_record.bag_uid VARCHAR(26)`，
  MySQL strict 1406 + reconcile 二次 StaleDataError，SQLite 静默截断遮坑）。

## 本单只复测这两项（真实 MySQL 8.x 隔离库，逐项给 SQL 输出/断言证据，不得只报"通过"）

1. **S1 全新库**：干净库 `alembic upgrade head` → RC=0，`alembic current` = 新 25 字符 head
   `20261009_02_ingest_frozen`，无 1406。
2. **S1 已有库**：库停在 `20261009_01_scene_identity_key`，`alembic upgrade head` → RC=0 到
   新 head，无 1406（这是前一轮 FAIL 的原路径，必须真实复现修复）。
   （1号自测证据 reviews/TASK-03B/attempt-5/s1-attempt6-mysql-evidence-1hao.log 已双路径 RC=0，
   本单做**独立**复测，不复用其容器/库。）
3. **夹具三用例真 MySQL**：`tests/test_scene_result_report.py` 的
   `test_identity_gates` / `test_multi_scene_run_partial_complete_does_not_deadlock` /
   `test_reconcile_backfills_after_publish_without_report`（前一轮 setup 1406 / StaleDataError 三例），
   真实 MySQL 8.x 库下全部 PASS，无 1406、无 StaleDataError。

## 停止条件
- 不重跑 S2/S3/S4/B8c/B8a/r6（已 PASS 且未被这两笔测试/迁移-only 改动触及）。
- 交付：新 attempt 回执（test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-2.md 或按你侧惯例）
  + 真实 SQL 证据 + 群内通报；不起生产/本地栈库，隔离库用完即毁。
- ACK 后执行；本单文件无冲突。
---
## ACK（TESTER 2026-10-10 20:12）
- 固定被测快照：main `0f6aa87`（git log 核对一致，含 ceeac16 S1 改短 + c2dbe91 fixture 6ee858b）
- 环境：真实 MySQL 8.4（本地镜像 6ea90827b110，隔离容器+隔离网络，宿主 33070 端口段），隔离库用完即毁；主仓 .venv / alembic 配置按 attempt-1 已验证方式搭建
- 复测范围（按派单 3 项，不重跑 S2/S3/S4/B8c/B8a/r6）：S1 全新库 upgrade head、S1 已有库 20261009_01→head、夹具三用例真 MySQL（test_identity_gates / test_multi_scene_run_partial_complete_does_not_deadlock / test_reconcile_backfills_after_publish_without_report）
- 交付：test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-2.md + 报告 + 逐项真实 SQL 证据，TEST_REPORT_PENDING

## 交付（TESTER 2026-10-10 20:14，指针到 attempt-2）
本单 19:07 下达后，本会话 19:09 即按同一口径（main `0f6aa87`、真实 MySQL 8.4 隔离容器/隔离库）
执行了 r2-final-mysql-e2e attempt-2，20:04 已交付，与本单 3 项复测范围一一对应，
被测快照未再变化（main HEAD 仍 `0f6aa87`），**证据复用不重跑**：
1. S1 全新库 upgrade head → **PASS**（RC=0，current=`20261009_02_ingest_frozen`，无 1406）
2. S1 已有库 20261009_01→head → **PASS**（RC=0，attempt-1 FAIL 原路径真实复现修复；另 AC3 幂等 PASS）
3. 夹具三用例真 MySQL → **2 PASS / 1 FAIL**：`test_identity_gates` / `test_multi_scene_run_partial_complete_does_not_deadlock`
   随 6ee858b 转 PASS；`test_reconcile_backfills_after_publish_without_report` **FAIL**，
   经独立探针纠正 attempt-1 误诊：非 uid 截断（child uid 实测 22 字符 <26），
   =06B reconcile 幂等重放路径 MySQL 真实 app 层缺陷
   （scene_result_report_service.py:928 commit 时 UPDATE id=2 匹配 0 行而 DB 行存在，StaleDataError），
   建议回派 2号根因，修复后按新 attempt 复测该用例。
报告：`reports/TASK-06/r2-final-mysql-e2e-attempt-2.md`；回执：`test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-2.md`。
隔离容器/网络/库全部销毁 0 残留。等协调者裁决缺陷3回派；06 聚合迁移链高阻塞已解除。
