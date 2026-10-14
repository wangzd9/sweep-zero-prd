#!/usr/bin/env python3
"""r95: claim COORDINATOR control lease, print token from lease JSON."""
import json, subprocess, sys
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
SCRIPT = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-coord-poll-14ae4556629a-20261012-195553-r95-t07b-b5b10-detached-launch"
r = subprocess.run([sys.executable, SCRIPT, "--project", ROOT, "--role", "COORDINATOR",
                   "--owner", OWNER, "claim"], capture_output=True, text=True)
print("claim rc=", r.returncode)
print(r.stdout.strip()[:800])
print(r.stderr.strip()[:300])
lp = f"{ROOT}/inbox/control/runtime/leases/COORDINATOR.json"
if r.returncode == 0:
    lease = json.load(open(lp))
    print("TOKEN=", lease.get("token"))