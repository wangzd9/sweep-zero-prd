# TASK-12S-E attempt-2 增量复验 ACK（TESTER，2026-10-15 10:27 +08:00）

- **状态**：ACKED。owner=TESTER；task/attempt=TASK-12S-E / attempt-2；派单 `inbox/TESTER/TASK-12S-E/attempt-2-reverify-dispatch.md`（协调者 10:1x）。
- **被测固定快照**：base `b39a3ec` → head `1e9c7de`（wt-01-t12se，分支 a/task-12s-e-auto-bind）。**只测该冻结 head，不追移动分支。**
- **前提确认**：attempt-1 独立验证 PASS（00:43 回执，覆盖 b39a3ec 五面）仍有效；本单只补 attempt-2 增量面，不重跑 attempt-1 全量。OCR attempt-2 增量 run `a9bf637e` 三批 0 findings 收口（裁决在案）——复验不替代也不被 OCR 替代。
- **实际 checkout 核对**：worktree `/home/wang/.local/state/rosbag-scene/wt-01-t12se` HEAD=`1e9c7deff16b532ad7430c5b3639f2e55bb62ec3`（与派单 head 一致），`tests/test_task12se_auto_bind.py` 在位（41949 B）。
- **增量复验面（真 MySQL 8.4.11 隔离库，用完即毁归零留证）**：E-R7 真实口径夹具（:813-860 新增用例）/ E-R1~R3 字段断言 / E-R8 两路（豁免/非豁免 409）/ E-R4 防御面（ROOT_MISMATCH）/ 回归抽查（目标文件 + `tests/test_pipeline_api.py` E-R6 统计 key，outbox 空不意外缩小）。
- **硬边界**：VLM=0；不写生产库/NAS/A100；不碰 1012 大包取消链与 12S-F 开发树；隔离 MySQL 用完即毁。E-R8 豁免路若真实 MySQL 下无法只读夹具构造完整前置（需真实切片产物）→ 按「断点+所需材料」登记，不 mock 冒充 PASS。
- **交付**：`test-receipts/TASK-12S-E/attempt-2-reverify.md`（5 面逐条结论 + 命令/退出码 + 隔离资源归零证据）。ACK 落 10:27（30min 时限内）；预期 1-2h。