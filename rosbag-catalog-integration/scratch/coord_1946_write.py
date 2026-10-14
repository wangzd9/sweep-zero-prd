import json, os
base = '/home/wang/work/doc/prd/rosbag-catalog-integration'
# event
evt_dir = os.path.join(base, 'events', 'COORDINATOR')
os.makedirs(evt_dir, exist_ok=True)
evt = {
    "role": "COORDINATOR",
    "event_id": "coord-poll-20261011-1946-task08-done",
    "type": "task_closure",
    "checked_at": "2026-10-11T19:45:53+08:00",
    "recorded_at": "2026-10-11T19:47+08:00",
    "task": "TASK-08",
    "summary": "TESTER post-merge-0a8ca8a 复核 19:44 交付 PASS（14/14 真 MySQL RC=0）；协调者独立机械核验（rev-parse 双核/results.json/日志 spot-check/docker+worktree 0 残留）→ 收口条件 2/2 满足 → TASK-08 DONE。候选重算：TASK-10 待 TASK-09（用户授权真实坡道样本/VLM）解除后派单，本轮无新派单。生产门禁维持未放行。",
    "decision": "inbox/coordinator/TASK-08/post-merge-0a8ca8a-acceptance-decision.md",
    "main_head": "0a8ca8a",
    "status_change": "TASK-08 RUNNING→DONE",
}
p = os.path.join(evt_dir, "coord-poll-20261011-1946-task08-done.json")
with open(p, 'w') as f:
    json.dump(evt, f, ensure_ascii=False, indent=2)
print('event written', p)

# session checkpoint append
sess = os.path.join(base, 'sessions', 'COORDINATOR.md')
cp = """
## 2026-10-11 19:46 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T19:45:53+08:00：TESTER 合入后复核 19:44 PASS → TASK-08 收口 DONE）
- **TASK-08 收口 DONE**：TESTER post-merge-0a8ca8a 复核 19:44 交付 PASS（14/14 文件真 MySQL 8.4.11 STRICT RC=0：9 红文件全绿+06B 回归 35/25 不破坏+迁移链 RC=0+scene_slice_lineage 10+1skipped，隔离库 0 残留）→ 独立机械核验（rev-parse 双核 main `0a8ca8a`=origin / results.json all_pass 14 文件 rc=0+dropped / 日志 spot-check 24·41·36·10+1skipped 一致 / docker+worktree 0 残留）→ 收口 2/2（c3-1→`98f6c88` 17:02 + t08c-1→`0a8ca8a` 19:17）满足 → **08 转 DONE**（decision `inbox/coordinator/TASK-08/post-merge-0a8ca8a-acceptance-decision.md`）。
- **候选重算：本轮无新派单**：TASK-10 前置 08+09，09 仍 BLOCKED（需用户授权真实坡道样本/VLM）→ 10 维持 WAITING；A/B/C/TESTER 空闲不扩需求。生产启用/真实样本门禁（09/10/11）维持未放行。
- **角色占用**：A/B/C/TESTER 全空闲（例行心跳）；leases 无在途业务持有；`ocr.lock`/`coordinator.lock` 无他角色在途；ps 无协调侧 ocr/pytest 业务进程。
- 本轮控制动作：claim→巡检核查（rev-parse 双核/results.json+日志 spot-check/docker+worktree 残留/TODO+BASELINE 更新）→写 decision+HANDOFF+event+TODO 08 行 DONE→release。**状态变更=TASK-08 DONE**，无新派单/合入/OCR。
- **下一步**：TASK-09 待用户授权真实坡道样本/VLM 后解除 → 届时 10 派单；生产门禁维持未放行；继续每轮核 inbox 新交付/派单/ACK。
"""
with open(sess, 'a') as f:
    f.write(cp)
print('session checkpoint appended')