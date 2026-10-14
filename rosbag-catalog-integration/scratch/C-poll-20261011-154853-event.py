import json, subprocess, datetime

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261011-154853"

def rt(*args):
    r = subprocess.run(["python3", RUNTIME, *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"runtime {' '.join(args)} rc={r.returncode}\n{r.stdout}\n{r.stderr}")
    return r.stdout.strip()

claim_out = rt("claim", "--project", ROOT, "--role", "C", "--owner", OWNER)
token = json.loads(claim_out)["token"]

ts = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%dT%H:%M:%S+08:00")
event = {
    "event_id": "C-poll-20261011-154853-nochange",
    "role": "C",
    "ts": ts,
    "task": "TASK-03B",
    "attempt": 4,
    "status": "IDLE",
    "summary": "5分钟巡检（preflight checked_at 2026-10-11T15:48:53+08:00）：15:45:00 后共享根新增仅 reviews/TASK-05/attempt-1/ocr-batches.md + inbox/coordinator/TASK-05/i1-1-acceptance-decision.md（协调者 1号 i1-1 验收记账）+ HANDOFF 刷新，均非 C 范围；inbox/3号/TASK-03B 无新派单（最新仍 10-10 00:58 attempt-4-ocr-rework 已 ACCEPT_MERGED）；main HEAD f9bafb0、wt-03b HEAD 6f1a9ad 无变更、无 C 在途进程、无在途租约。保持空闲待派单。",
    "evidence": "sessions/C.md",
    "next": "等协调者新派单",
}

ev_path = f"{ROOT}/events/C/C-poll-20261011-154853-nochange.json"
rt("run", "--project", ROOT, "--role", "C", "--token", token,
   "--", "python3", "-c",
   f"import json;json.dump({json.dumps(event)},open('{ev_path}','w'),ensure_ascii=False,indent=2)")

rt("release", "--project", ROOT, "--role", "C", "--token", token)
print("OK", ts, ev_path)