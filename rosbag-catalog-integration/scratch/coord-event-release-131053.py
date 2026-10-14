import json, subprocess

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"

d = json.load(open(ROOT + "/inbox/control/runtime/leases/COORDINATOR.json"))
print("owner:", d.get("owner"), "token_tail:", d["token"][-8:])

r = subprocess.run([
    "python3", RUNTIME, "event", "--project", ROOT, "--role", "COORDINATOR",
    "--token", d["token"], "--event-id", "coord-poll-20261011-131053-nochange",
    "--task", "NONE", "--attempt", "0", "--status", "NOCHANGE",
    "--summary", "13:00后零业务变化；main 65ca0be 三核一致；强复审R2I-20261010-06 result仍缺维持READY_FOR_USER_TRIGGER；B 13:02/13:07例行心跳；无在途进程/锁",
    "--evidence", "sessions/COORDINATOR.md",
    "--next", "等强复审用户手动触发或新交付",
], capture_output=True, text=True)
print("event RC:", r.returncode, r.stdout[:200], r.stderr[:300])

r2 = subprocess.run([
    "python3", RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR",
    "--token", d["token"],
], capture_output=True, text=True)
print("release RC:", r2.returncode, r2.stdout[:200], r2.stderr[:300])