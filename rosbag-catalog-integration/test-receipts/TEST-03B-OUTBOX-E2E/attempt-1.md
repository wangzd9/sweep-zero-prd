---
task: TASK-03B
item: verify-05-03b-outbox-e2e
owner: 测试者
status: TEST_REPORT_PENDING
attempt: 1
dispatch: inbox/TESTER/TASK-03B/verify-05-03b-outbox-e2e.md（2026-10-09 22:41 协调者派单，HIGH）
target: main 533aa1c（核对 HEAD 一致；03B attempt-4 86baad5 + 05 attempt-2 6ce7b7a 均已在 main）
ack_time: 2026-10-09 22:5x CST
finished: 2026-10-09 23:0x CST
environment: SQLite（派单指定）；rosbag-catalog 主仓 .venv Python 3.10；conftest 临时库；SCENE_INGEST_ENABLED=1
evidence_dir: ~/.hermes/cache/scratch/tester_05_03b_e2e/
test_script: ~/.hermes/cache/scratch/tester_05_03b_e2e/test_verify_05_03b_outbox_e2e.py（scratch，不进仓库）
report_path: reviews/TASK-03B/attempt-4/verify-05-03b-outbox-e2e.md
verdict: PASS（6/6 场景）
---

# TEST-03B-OUTBOX-E2E attempt-1 交付（03B 生产端 → 05 消费端 真实 outbox 事件流联调）

## 执行方式
派单 6 场景逐项执行。场景 1/2/6 走**真实 03B 生产路径**（IngestProfile +
create_submission 接受冻结 hash → bind_ingest_for_registration 真实 emit 到
purpose_schedule_event 表）→ 真实 05 poll_and_consume_purpose_events 消费；
场景 3/4/5 按派单指示直接 INSERT outbox 行（模拟 03B 修前形态/坏事件）。
registry = 真实 config/scene_capabilities.yaml（test-capability/test-v1 enabled）。
脚本在 scratch/，业务代码零改动（只读 + 测试脚本）。

## 结果：6 passed（pytest RC=0，1.92s）
| 场景 | 断言要点 | 结果 |
|---|---|---|
| S1 正常 scene_slice e2e | 03B emit 1 行 PENDING（hash=1c5b7c63…=接受时 registry 计算值）；05 消费后 outbox=**CONSUMED**、run=pipeline_type SCENE_SLICE、status=SCENE_SLICE_QUEUE、**scene_identity_key 非空**（scene:733b5b12…） | PASS |
| S2 冻结 hash 正确性 | 事件 hash == 接受时 registry effective_params config_hash；消费后**移除 registry 中 test-capability 模拟漂移**，同 payload 新 event_id 重放 → **reused=1/created=0**，run 状态/快照/身份键不变，全库仍 1 个 run（消费按事件内语义 + 持久身份键，不随 registry 变化重算重建） | PASS |
| S3 漂移→失败留痕 | INSERT 未注册 ghost-scene/ghost-v1 → 建 **SCENE_UNAVAILABLE** 失败 run（status=SCENE_FAILED、error_message 含原因、**PRECHECK step=FAILED**、PipelineEvent SCENE_RUN_FAILED 留痕），非静默丢弃；outbox 离开 PENDING=CONSUMED | PASS |
| S4 缺 hash→DROPPED | INSERT capability_config_hash=NULL → **CONTRACT_VIOLATION**、outbox=**DROPPED + error_reason 非空**、未建 run、再 poll **不重捞**（PENDING-only 过滤生效） | PASS |
| S5 DROPPED 不堵队 | 49 行 NULL-hash + 1 行未知用途 + 1 行正常事件（真实 03B 生产）：第 1 轮 LIMIT 50 窗口取前 50 坏行 → **50 DROPPED 离开 PENDING**；第 2 轮正常行**被消费**（run=SCENE_SLICE_QUEUE），队列清空无残留 PENDING。修复前坏行永久占 PENDING 头部，正常行永远出不了窗口 | PASS |
| S6 self_built | 真实 03B 路径 emit purpose=self_built 事件（无 scene 字段）→ 05 消费**不建任何 run**、outbox=CONSUMED（对账痕迹） | PASS |

## 回归
定向回归 tests/test_scene_slice_scheduling.py + tests/test_ingest_frozen_hash.py：**41 passed**（RC=0）。

## S3 实现语义说明（供协调者验收参考，非缺陷）
派单预期"建 SCENE_UNAVAILABLE 失败 run 留痕（非丢弃）；outbox 行离开 PENDING（CONSUMED 或终态，具体看 05 实现语义）"。
05 实际语义 = 失败 run 留痕 + outbox 标 **CONSUMED**（消费端视"已处理（含处理为失败运行）"为终态，非 DROPPED 桶）；
DROPPED 桶只用于"永久无效且无 run 可建"（契约违约/源身份失效/未知用途）。该语义与 05 代码 docstring（强模型 #5 修复）一致，
"留痕"由失败 run + PRECHECK step + PipelineEvent 三重保证，满足派单核心要求。

## 证据
- pytest 输出：~/.hermes/cache/scratch/tester_05_03b_e2e/pytest_run.log（6 passed，含每场景关键断言行值 print）
- 回归输出：~/.hermes/cache/scratch/tester_05_03b_e2e/regression.log（41 passed）
- 测试脚本：~/.hermes/cache/scratch/tester_05_03b_e2e/test_verify_05_03b_outbox_e2e.py
- 测试库：~/.hermes/cache/scratch/tester_05_03b_e2e/test.db（SQLite，一次性，无容器残留）
- 报告：reviews/TASK-03B/attempt-4/verify-05-03b-outbox-e2e.md