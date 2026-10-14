---
task: TASK-03B
attempt: 3
owner: 3号
status: ACCEPTED
dispatched_by: 协调者（cron 验收）
updated: 2026-10-09 11:58
base: 8e97ef1（attempt-2 的 14b7a64 之上返修；若 main 已推进以合入前最新 main 重算 base 并在回执写明）
worktree: /home/wang/.local/state/rosbag-scene/wt-03b（分支 feature/scene-ingest-api，当前 14b7a64）
---

# TASK-03B attempt-3 返修派单（第 2 轮，有界最后轮）

attempt-2 核心文件 ingest_service.py 的 OCR（session 40c26be1，3 findings）协调者逐条核实**全部成立**。
逐条意见、代码行号依据、必修/建议与回归测试要求全文见
`inbox/coordinator/TASK-03B/attempt-2-decision.md`。摘要：

## 必修
1. **high** `match_profile_for_incoming`（ingest_service.py:93）按活动 version 折叠（复用 list_profiles 的
   max-version-per-profile_id 口径，或抽 `_active_profiles_all(db)` helper 与 list_profiles 共用）。
   回归：同 profile_id 两 enabled version + 用户 PENDING 挂活动 version → 匹配返回活动 version、
   绑定不产生重复系统提交、事件 profile_version==活动 version。撤折叠 RED。
2. **medium** `patch_submission`（ingest_service.py:365-366/412）row_version 乐观锁 DB 强制：
   条件 UPDATE `WHERE row_version=:expected` + `rowcount==0→409`，或加 `versionid_col`。
   回归：两连接同 expected 并发 PATCH，一 200 一 409、败者不落库。

## 建议修
3. **low** `_ensure_system_submission`（ingest_service.py:490-497）删首个不可达查询 + 修注释
   （保留 relative_path+PENDING 兜底）。

## 交付要求
- 回执 `receipts/TASK-03B/attempt-3.md`，status=REVIEW_PENDING，含 #1/#2 语义选择说明 + 回归测试名 + 全量真实退出码。
- commit 只含 ingest_service.py + 对应测试；`git diff 8e97ef1 HEAD --stat` 复核范围不扩散、无 .venv。
- ruff format --check + ruff check 全绿。
- **OCR 不要自跑**（协调者代跑，flock 串行）；完成后即停，不@用户。
- 同因两轮返修上限：attempt-3 若再出同因问题将升级用户裁决。