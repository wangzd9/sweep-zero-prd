---
task: TASK-03B
item: verify-05-03b-outbox-integration
owner: 测试者
status: ACCEPTED
priority: HIGH（强模型裁决的合入顺序核心：05 rebase 到最终 03B 做真实 outbox 联调）
dispatched_by: 协调者
updated: 2026-10-09 22:41
target: main 533aa1c（03B attempt-4 86baad5 + 05 attempt-2 6ce7b7a 均已在 main）
---
# 验证派单：03B 生产端 → 05 消费端 真实 outbox 事件流端到端联调

## 背景
强模型审查 #4（跨任务契约 bug）裁决=接受时冻结 hash：03B 提交接受时计算并持久化
`frozen_capability_hashes_json`，bind 只读不重算，**任何 scene 事件必须带有效冻结 hash，
绝不允许 NULL-hash 事件**；05 消费端对漂移（registry.get None）走 SCENE_UNAVAILABLE
**建失败运行留痕**（非丢弃），对缺 hash 走 CONTRACT_VIOLATION 丢弃但**必须原子落 outbox
DROPPED 终态**。两端修复都已合入 main 533aa1c，现在需要真实生产者→真实消费者的
事件流联调证据（此前 05 测试用 fixture 手写事件，没走过 03B 真实 emit 路径）。

## 测试环境
SQLite 即可（事件流是业务逻辑链，非并发/DDL 验证）：复用 tests/test_scene_slice_scheduling.py
的 fixture 模式（Base.metadata.create_all + seed_demo_data）。用 TestClient 或直接调 service 层。

## 联调场景（每个都走真实 03B 生产 → 真实 05 消费，中间是 outbox 表真实行）
1. **正常 scene_slice 事件**：profile 配 scene_slice 用途 + 能力可用（slope-v1 或 test-capability-v1，
   看 bootstrap seed 注册了哪个）→ 03B 真实登记/绑定路径 emit 事件 → 05 `poll_and_consume`
   → **断言**：run 被创建（pipeline_type=SCENE_SLICE）、outbox 行=CONSUMED、
   run.scene_identity_key 非空（持久身份键已回填/创建）。
2. **冻结 hash 正确性**：事件里的 capability_config_hash **必须等于接受时 registry 计算的 hash**；
   消费后再改 registry（模拟漂移/换版）→ 重放同事件 → 仍按原冻结 hash 语义处理
   （05 用事件内 hash，不用当前 registry 重算——断言消费结果不受 registry 后续变化影响）。
3. **漂移→失败运行留痕**：构造事件引用未注册的 scene_code/capability_version
   （直接 INSERT outbox 行模拟 03B 历史事件，这是 03B 修前才会发的形态）→ 05 消费
   → **断言**：建 SCENE_UNAVAILABLE 失败 run（留痕可查）而非静默丢弃；outbox 行离开 PENDING
   （CONSUMED 或终态，具体看 05 实现语义）。
4. **缺 hash→DROPPED 终态**：INSERT 一行 scene_slice 事件但 capability_config_hash=NULL
   → 05 消费 → **断言**：CONTRACT_VIOLATION、outbox 行=**DROPPED + error_reason 非空**、
   再次 poll 不会重捞该行（PENDING-only 过滤）。
5. **DROPPED 不堵队**：先塞 50 行 DROPPED/坏事件 + 1 行正常事件 → poll_and_consume
   → **断言**：正常事件被消费（修复前 50 行坏事件永久占 PENDING 头部会堵死）。
6. **self_built 用途**：03B 真实路径 → 事件 purpose=self_built → 05 消费 →
   **断言**：不建 scene run、outbox=CONSUMED（对账痕迹）。

## 交付
- 过程 ACK + 证据：test-receipts/TEST-03B-OUTBOX-E2E/attempt-1.md（被测快照 533aa1c、环境、
  每场景真实退出码/断言结果、状态 TEST_REPORT_PENDING）
- **最终报告**：reviews/TASK-03B/attempt-4/verify-05-03b-outbox-e2e.md（6 场景逐项 PASS/FAIL +
  关键断言值 + 失败最小复现）
- 群内按新通报格式（结论先行 + 分点 + 关键事实加粗）
- 禁止改任何业务代码；FAIL 只报告不修。测试脚本可落 scratch/，不进仓库。