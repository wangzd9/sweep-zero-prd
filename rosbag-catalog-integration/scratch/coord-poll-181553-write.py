#!/usr/bin/env python3
"""coord poll 20261011-181553: TODO 注记 + sessions 检查点 + event（t08c-1 commit 落地 bf48a45，回执未到）"""
import json, os, sys, datetime

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
NOW = "2026-10-11 18:15"
CHECKED_AT = "2026-10-11T18:15:53+08:00"

# 1) TODO TASK-08 行末尾注记
todo_path = os.path.join(ROOT, "TODO.md")
with open(todo_path, encoding="utf-8") as f:
    todo = f.read()
suffix = "等 commit+真 MySQL A/B 交付；main `98f6c88`=origin 不变】"
add = (
    "等 commit+真 MySQL A/B 交付；main `98f6c88`=origin 不变】"
    "→【18:15 巡检：2号 t08c-1 **`bf48a45` commit 落地**（18:12:27，`f9bafb0..bf48a45` 7 文件 +91/-18："
    "bag_cleanup_service/catalog_ingest/source_service/artifact_service/bootstrap 5 app 文件"
    "+clone 脚本+test_bag_cleanup_concurrency，commit message 口径覆盖 C1 读回秒精度/排序并列/demo 去小数秒"
    "+C2 变化才推进 updated_at/整秒幂等/整数除秒，worktree 干净）但 **无交付回执**"
    "（`receipts/TASK-08/` 仍仅 attempt-1+c3-1 两份）→ commit≠交付，等回执+真 MySQL A/B 证据后机械核验"
    "（C1/C2 全修复点+文件集逐点核）→串行 OCR 增量→合入→9 红文件全绿复核；main `98f6c88`=origin 不变】"
)
assert todo.count(suffix) == 1, f"suffix count={todo.count(suffix)}"
todo = todo.replace(suffix, add)
with open(todo_path, "w", encoding="utf-8") as f:
    f.write(todo)

# 2) sessions/COORDINATOR.md 顶部 prepend 检查点
sess_path = os.path.join(ROOT, "sessions", "COORDINATOR.md")
with open(sess_path, encoding="utf-8") as f:
    sess = f.read()
checkpoint = f"""## 2026-10-11 18:15 巡检检查点（cron poll 14ae4556629a，真实 checked_at {CHECKED_AT}：2号 t08c-1 commit 落地 bf48a45，交付回执未到）

- **实质变化=2号 t08c-1 commit 落地**：`wt-04a-t08c`（branch `scene/task-08-c1c2-second-precision`）18:12:27 commit `bf48a45`，diff `f9bafb0..bf48a45`=**7 文件 +91/-18**（`bag_cleanup_service.py`/`catalog_ingest.py`/`source_service.py`/`artifact_service.py`/`bootstrap.py` 5 app 文件 + `scripts/clone_published_dataset_records.py` + `tests/test_bag_cleanup_concurrency.py`）；commit message 口径=C1 4 文件读回秒精度/deleted_at 整秒/`mark_source_input_error` 加 `id.desc()` 次级排序/seed_demo 去小数秒 + C2 变化才推进 `updated_at`（run_inspection 7 分支捕获原值）/worker_heartbeat 同秒幂等/upsert_bag 10 字段变化检测+started_at 整数除秒/clone rebind 整秒对齐——上轮「`bootstrap.py`/`artifact_service.py` 超出派单枚举文件集」已在 commit message 说明归属（C1 demo 去小数秒 + `mark_artifact_deleted` 读回秒精度），**最终越界与否交付回执后逐点核**。worktree 干净（仅 `.venv` 软链）、ps 无 pytest 在途（commit 已完成，非编码间隙）。
- **回执未到，commit≠交付**：`receipts/TASK-08/` 仍仅 `attempt-1.md`(16:32) + `c3-lineage-c3-1.md`(16:56) 两份，**无 t08c-1 交付回执**（缺真 MySQL 8.4.11 A/B 逐修复点证据、报告、隔离库 0 残留声明）→ 本轮不启动机械核验/OCR。
- **main HEAD `98f6c88`（= origin/main）不变**；B lease 活跃（owner b-poll-20261011-165253-t08c1，18:17:14 续期，tick 18:08:53 report 在跳）；A 18:11 / C 18:13 / TESTER 18:14 tick 正常空闲；`ocr.lock` 0 字节无在途，ps 无协调侧 ocr/pytest 业务进程。
- 本轮控制动作：claim（`cron-poll-20261011-181553`，首轮 token 未输出经 lease 文件核对）→巡检核查（wt-04a-t08c git log/show --stat/diff --stat f9bafb0..bf48a45+status/find -newermt receipts）→TODO 注记+prepend 检查点+event→release。**有状态变更（t08c-1 commit 落地），无新派单、无合入、无 OCR**。
- **下一步**：下轮核 2号 t08c-1 交付回执（`receipts/TASK-08/` 新文件+真 MySQL A/B 证据路径）；交付即机械核验（C1/C2 全修复点覆盖+文件集逐点+越界裁决）→串行 OCR 增量（app 行为面，起跑前 §3.6 尺寸预检）→合入 main→9 红文件全绿复核→TASK-08 DONE→TASK-10 候选重算。

"""
assert sess.startswith("## 2026-10-11 17:45 巡检检查点"), "sessions head changed, abort"
sess = checkpoint + sess
with open(sess_path, "w", encoding="utf-8") as f:
    f.write(sess)

# 3) event
ev = {
    "event_id": "coord-poll-20261011-181553-t08c1-commit-landed",
    "occurred_at": CHECKED_AT,
    "recorded_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "role": "COORDINATOR",
    "task": "TASK-08",
    "attempt": "t08c-1",
    "status": "RUNNING",
    "summary": "2号 t08c-1 commit bf48a45 落地（18:12:27，7文件+91/-18 覆盖 C1 秒精度家族+C2 no-op UPDATE 家族，worktree 干净）但无交付回执（receipts/TASK-08 仍仅 attempt-1+c3-1），commit≠交付，本轮不启动机械核验/OCR；main 98f6c88=origin 不变；A/C/TESTER 空闲",
    "evidence": "wt-04a-t08c git show --stat bf48a45 + git diff --stat f9bafb0..bf48a45 + receipts/TASK-08 ls",
    "next": "等2号 t08c-1 交付回执+真MySQL A/B证据→机械核验（C1/C2逐点+文件集+越界裁决）→串行OCR增量→合入→9红文件全绿复核→TASK-08 DONE",
}
ev_path = os.path.join(ROOT, "events", "COORDINATOR",
                       "2026-10-11-181553-t08c1-commit-landed.json")
with open(ev_path, "w", encoding="utf-8") as f:
    json.dump(ev, f, ensure_ascii=False, indent=2)
    f.write("\n")
os.chmod(ev_path, 0o600)

print("OK: TODO note + checkpoint prepended + event", ev_path)