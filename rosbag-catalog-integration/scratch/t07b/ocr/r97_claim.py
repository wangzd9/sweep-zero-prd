#!/usr/bin/env python3
import json, subprocess, sys
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "cron-coord-poll-14ae4556629a-20261012-202053-r97"
out = subprocess.run([sys.executable, RUNTIME, "claim", "--project", ROOT,
                      "--role", "COORDINATOR", "--owner", OWNER],
                     capture_output=True, text=True, timeout=60)
print("RC=", out.returncode)
print(out.stdout[-1500:])
print(out.stderr[-800:])
try:
    j = json.loads(out.stdout[out.stdout.index("{"):])
    if "token" in j:
        print("TOKEN_LEN=", len(j["token"]))
except Exception as e:
    print("parse-note:", e)
    lease = open(f"{ROOT}/inbox/control/runtime/leases/COORDINATOR.json").read()
    print("LEASE=", lease[-600:])