#!/usr/bin/env python3
import json, subprocess, sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261011-234853"

def run(*args):
    p = subprocess.run([sys.executable, RUNTIME, *args], capture_output=True, text=True, timeout=120)
    return p

out = run("claim", "--project", ROOT, "--role", "C", "--owner", OWNER)
print("claim rc", out.returncode)
data = json.loads(out.stdout[out.stdout.index("{"):])
token = data["token"]
print("claim ok, token len", len(token))

ev = run("event", "--project", ROOT, "--role", "C", "--token", token,
         "--event-id", "C-poll-20261011-234853-nochange",
         "--task", "NONE", "--attempt", "0", "--status", "NO_CHANGE",
         "--summary", "23:38:53后共享根零C范围新增（仅ticks/sessions/协调者23:46事件t10-vlm-404-probing属2号范围）；inbox/3号最新仍10-10 00:58 ACCEPT_MERGED；main ca8730d=origin/main；wt-03b 6f1a9ad干净；无C在途进程；保持空闲待派单",
         "--evidence", "sessions/C.md", "--next", "继续5分钟巡检")
print("event rc", ev.returncode)
if ev.returncode != 0:
    print(ev.stdout, ev.stderr)

rel = run("release", "--project", ROOT, "--role", "C", "--token", token)
print("release rc", rel.returncode)
if rel.returncode != 0:
    print(rel.stdout, rel.stderr)