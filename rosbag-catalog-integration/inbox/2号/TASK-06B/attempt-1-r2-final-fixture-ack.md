---
task: TASK-06B
item: attempt-1-r2-final-fixture
owner: 2号（执行者B）
status: ACCEPTED
base: wt-04a 86b2cc1（开工前 merge 到 main 74ba3bf 后新建本任务分支）
branch: 待建（本任务专属）
ack_at: 2026-10-10 18:41 +08:00
---
# ACK：attempt-1-r2-final-fixture（测试夹具 uid 超长最小修复）

- 派单：`inbox/2号/TASK-06B/attempt-1-r2-final-fixture-fix.md`（18:24 下达，已读全文）
- worktree：`/home/wang/.local/state/rosbag-scene/wt-04a`，HEAD=86b2cc1（已核为 main 74ba3bf 的祖先，工作区仅 .venv/tests/test_r2_repro.py 未跟踪保留）
- 范围：仅 `tests/test_scene_result_report.py` `_parent` uid 收敛 ≤26 字符 + assert 防护 + 核对 `_child_uid`；不改 app 代码、不改断言语义、不删用例
- 交付：单 commit + 回执 `receipts/TASK-06B/attempt-1-r2-final-fixture.md`（REVIEW_PENDING）
- 不动：不跑 OCR、不合入 main、不起 MySQL（AC2 真实复测随 1号 S1 新 attempt 由 TESTER 验证）