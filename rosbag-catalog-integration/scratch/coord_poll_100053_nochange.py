#!/usr/bin/env python3
"""coord poll 10:00:53 nochange checkpoint: claim -> event + sessions append -> release."""
import json, os, subprocess, sys, time

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-coord-poll-14ae4556629a-20261012-100053"
CHECKED = "2026-10-12T10:00:53+08:00"

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

r = sh(f"python3 {RUNTIME} claim --project {ROOT} --role COORDINATOR --owner {OWNER}")
if r.returncode != 0:
    print("CLAIM_FAIL", r.stdout, r.stderr); sys.exit(0)
token = json.loads(r.stdout.strip().splitlines()[-1])["token"] if r.stdout.strip() else r.stdout
try:
    ev = os.path.join(ROOT, "inbox/events/COORDINATOR/coord-poll-20261012-100053-nochange.md")
    with open(ev, "w") as f:
        f.write(
            "event_id: coord-poll-20261012-100053-nochange\n"
            f"checked_at: {CHECKED}\n"
            "role: COORDINATOR\n"
            "status: NO_CHANGE\n"
            "summary: P0 收口后常规空转；main 453da0c=origin 双核零前移；B TASK-07A attempt-1 开发在途（wt-04a-t07a 三文件 10:00-10:02 活跃写入，未 commit，正常在途）；A/C/TESTER 空闲 tick 在跳；无 OCR 在途；无新派单/合入/状态变更。\n"
            "next: 维持 5 分钟巡检；等 B 07A 交付后机械核验+串行 OCR。\n"
        )
    sess = os.path.join(ROOT, "inbox/sessions/COORDINATOR.md")
    entry = (
        f"## 2026-10-12 10:00 巡检检查点（cron poll 14ae4556629a，真实 checked_at {CHECKED}）\n\n"
        "- main `453da0c`=origin/main 双核一致（fetch 后 rev-parse 实测 10:0x），零前移；09:5x 后共享根业务目录零新增（新增仅 C 09:58 / TESTER 09:54 例行 nochange 心跳与 ticks）。\n"
        "- **B TASK-07A attempt-1 开发在途**：`wt-04a-t07a` 分支 `scene/task-07a-visibility-lineage` 实测 3 文件未 commit（`app/api/sources.py` 10:01:07 / `app/services/scene_result_query.py` 10:00:56 / `app/templates/pipelines.html` 10:02:12，活跃写入中），B tick 09:48:53 在跳、ACK 09:50 在案——**属正常在途，不催单不接管**。\n"
        "- **角色占用**：B=TASK-07A（在途）；A/C/TESTER 空闲（ticks A 10:01:53 / C 09:58:53 / TESTER 09:59:53 均在跳）；leases 无在途业务持有（C/TESTER 0 字节陈旧锁）；ps 无 ocr/pytest 业务进程（仅 wxocr 桌面残留）。\n"
        "- **门禁**：TASK-10 DONE/P0 收口维持；TASK-11 生产启用维持 PRODUCTION BLOCKED 待用户独立授权；07B/07C 待 07A 收口后派。\n"
        "本轮控制动作：claim → 巡检核查（fetch+rev-parse 双核/ticks 五角色/leases/ps/wt-04a-t07a git status+文件 mtime 实测）→ event + 本检查点 → release。**无新派单、无合入、无 OCR、无任务状态变更**。\n"
        "- **下一步：** 维持 5 分钟巡检；等 B 07A 交付 `receipts/TASK-07A/attempt-1.md` 后机械核验 → 串行 OCR → 合入 → TESTER 验证。\n"
    )
    run = sh(f"python3 {RUNTIME} run --project {ROOT} --role COORDINATOR --token {json.dumps(token)} -- "
             f"python3 {os.path.join(ROOT, 'scratch/coord_poll_100053_write.py')}")
    print("RUN", run.returncode, run.stdout[-400:], run.stderr[-400:])
finally:
    r2 = sh(f"python3 {RUNTIME} release --project {ROOT} --role COORDINATOR --token {json.dumps(token)}")
    print("RELEASE", r2.returncode, r2.stdout[-200:], r2.stderr[-200:])