---
task: TASK-03B
attempt: 4
item: verify-05-03b-outbox-e2e
verifier: 测试者（TESTER）
target: main 533aa1c（03B attempt-4 86baad5 + 05 attempt-2 6ce7b7a 均已在 main）
verdict: PASS（6/6）
environment: SQLite（派单指定；事件流为业务逻辑链，非并发/DDL 验证）
evidence: ~/.hermes/cache/scratch/tester_05_03b_e2e/{pytest_run.log, regression.log, test_verify_05_03b_outbox_e2e.py}
completed: 2026-10-09 23:0x CST
---

# 03B 生产端 → 05 消费端 真实 outbox 事件流端到端联调 · 验证报告（PASS 6/6）

## 被测与范围
- 被测提交：main **533aa1c**（核对 `git log` HEAD 一致）。
- 验收来源：强模型裁决 #4（接受时冻结 hash / 无 NULL-hash 事件 / 漂移建失败 run 留痕 / 缺 hash 原子 DROPPED）的合入顺序核心——
  此前 05 测试全用 fixture 手写事件，未走 03B 真实 emit 路径；本报告补齐真实生产→真实消费证据。
- 方式：S1/S2/S6 走真实 03B 路径（profile + create_submission 冻结 → bind 真实 emit 到 purpose_schedule_event 表）
  + 真实 05 poll_and_consume_purpose_events；S3/S4/S5 按派单直接 INSERT outbox 行模拟修前形态。
- 零业务代码改动；测试脚本在 scratch/，不进仓库。

## 逐项结果
1. **正常 scene_slice 事件 — PASS**。03B 真实 bind emit 1 行 PENDING（capability_config_hash=1c5b7c63… 非 NULL）→
   05 消费：outbox=**CONSUMED**、run 创建（pipeline_type=SCENE_SLICE、status=SCENE_SLICE_QUEUE）、
   **run.scene_identity_key 非空**（scene:733b5b12…）。
2. **冻结 hash 正确性 — PASS**。事件 hash == 接受时 registry `effective_params` 计算的 config_hash（逐字节相等）。
   消费后移除 registry 中 test-capability（模拟漂移/换版）→ 同 payload 新 event_id 重放：
   **reused_runs=1 / created_runs=0**，run 状态/快照/身份键不变，全库仍仅 1 个 run——消费结果不受 registry 后续变化影响。
3. **漂移→失败运行留痕 — PASS**。未注册 ghost-scene/ghost-v1 事件 → 建 **SCENE_UNAVAILABLE** 失败 run
   （status=SCENE_FAILED、error_message 含原因、PRECHECK step=FAILED、PipelineEvent SCENE_RUN_FAILED 三重留痕），
   非静默丢弃；outbox 离开 PENDING（实现语义=CONSUMED，见下"语义说明"）。
4. **缺 hash→DROPPED 终态 — PASS**。NULL capability_config_hash 事件 → **CONTRACT_VIOLATION**、
   outbox=**DROPPED + error_reason 非空**（"CONTRACT_VIOLATION: scene 事件缺少冻结的 capability_version/capability_config_hash"）、
   未建 run、再 poll **不重捞**（PENDING-only 过滤生效）。
5. **DROPPED 不堵队 — PASS**。50 行坏事件（49 NULL-hash + 1 未知用途）排在正常行前：
   第 1 轮 LIMIT 50 窗口取前 50 坏行 → **50 DROPPED 离开 PENDING**；第 2 轮正常行**被消费**（run=SCENE_SLICE_QUEUE），
   队列清空、无残留 PENDING。修复前坏行永久占 PENDING 头部，正常行永远出不了窗口。
6. **self_built 用途 — PASS**。真实 03B 路径 emit purpose=self_built 事件（无 scene 字段）→ 05 消费
   **不建任何 run**、outbox=CONSUMED（对账痕迹）、error_reason=NULL。

## 语义说明（供协调者验收参考，非缺陷）
S3 派单预期"outbox 行离开 PENDING（CONSUMED 或终态，具体看 05 实现语义）"。05 实现语义 =
失败 run 留痕后事件标 **CONSUMED**（"已处理（含处理为失败运行）"）；**DROPPED 桶仅用于无 run 可建的永久无效**
（契约违约/源身份失效/未知用途）。与 05 代码 docstring（强模型 #5 修复）一致，满足派单核心要求（留痕 + 离开 PENDING）。

## 回归
定向回归 tests/test_scene_slice_scheduling.py + tests/test_ingest_frozen_hash.py：**41 passed**（RC=0）。

## 证据
- pytest：~/.hermes/cache/scratch/tester_05_03b_e2e/pytest_run.log（6 passed，RC=0，1.92s；含每场景关键断言行值）
- 回归：~/.hermes/cache/scratch/tester_05_03b_e2e/regression.log（41 passed）
- 脚本：~/.hermes/cache/scratch/tester_05_03b_e2e/test_verify_05_03b_outbox_e2e.py
- 一次性 SQLite 库：~/.hermes/cache/scratch/tester_05_03b_e2e/test.db（无容器/网络残留）