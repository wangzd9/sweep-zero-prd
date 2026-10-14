#!/usr/bin/env python3
import subprocess, json

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261011-203353b"

def sh(args):
    r = subprocess.run(args, capture_output=True, text=True)
    out = r.stdout.strip()
    print(out)
    try:
        return json.loads(out)
    except Exception:
        return None

d = sh(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER, "--ttl", "300"])
token = d.get("token") if d else None
assert token, "claim failed"
sh(["python3", RUNTIME, "event", "--project", ROOT, "--role", "C", "--token", token,
    "--event-id", "C-poll-20261011-203353-nochange", "--task", "NONE", "--attempt", "0", "--status", "IDLE",
    "--summary", "v2 巡检：20:29 后共享根仅各角色 sessions 巡检刷新；inbox/3号 最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED（TASK-03B 全部收口）；inbox/coordinator 最新仍 19:47 TASK-08 post-merge decision（测试者/协调者范围）；无 C 新派单；main 0a8ca8a=origin/main 双核一致；wt-03b HEAD 6f1a9ad 干净；无 C 在途进程；leases 仅 A.json 在途（1号巡检业务，非 C）；保持空闲待派单",
    "--evidence", "scratch/c_poll_2033.py", "--next", "继续 5 分钟巡检"])
sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token])