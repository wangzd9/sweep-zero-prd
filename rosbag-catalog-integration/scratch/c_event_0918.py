import json, subprocess, sys
RT = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261012-091853-event"
step = sys.argv[1]
if step == "claim":
    r = subprocess.run(["python3", RT, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER], capture_output=True, text=True)
    out = r.stdout
    idx = out.index("{")
    d = json.loads(out[idx:])
    print("TOKEN=" + d["token"])
elif step == "release":
    r = subprocess.run(["python3", RT, "release", "--project", ROOT, "--role", "C", "--token", sys.argv[2]], capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
elif step == "event":
    r = subprocess.run(["python3", RT, "event", "--project", ROOT, "--role", "C", "--token", sys.argv[2],
        "--event-id", "C-poll-20261012-091853-nochange", "--task", "N/A", "--attempt", "N/A",
        "--status", "NO_CHANGE",
        "--summary", "09:13:53后C范围零新增；无C新派单；main 453da0c=origin双核一致；wt-03b干净；无C在途进程；保持空闲待派单（P0收口、TASK-11生产门禁PRODUCTION BLOCKED待用户独立授权）",
        "--evidence", "sessions/C.md 09:18条目",
        "--next", "继续5分钟巡检，等协调者派单"], capture_output=True, text=True, timeout=50)
    print(r.stdout.strip() or r.stderr.strip())
    print("rc=%d" % r.returncode)