#!/usr/bin/env python3
import json, subprocess, sys
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "cron-coord-poll-14ae4556629a-20261012-223553-r102-t07b-ocr-10of10-ruling-r2-dispatch"
out = subprocess.run([sys.executable, RUNTIME, "claim", "--project", ROOT,
                      "--role", "COORDINATOR", "--owner", OWNER],
                     capture_output=True, text=True, timeout=120)
print("RC=", out.returncode)
print(out.stdout[-2000:])
print(out.stderr[-800:])
tok = None
try:
    j = json.loads(out.stdout[out.stdout.index("{"):])
    if "token" in j:
        tok = j["token"]
except Exception as e:
    print("parse-note:", e)
if not tok:
    lease = open(f"{ROOT}/inbox/control/runtime/leases/COORDINATOR.json").read()
    j = json.loads(lease)
    if j.get("owner") == OWNER:
        tok = j.get("token")
if tok:
    open(f"{ROOT}/scratch/t07b/ocr/r102_token.txt", "w").write(tok)
    print("TOKEN_SAVED len=", len(tok))
else:
    print("NO_TOKEN lease=", lease if 'lease' in dir() else open(f"{ROOT}/inbox/control/runtime/leases/COORDINATOR.json").read()[-600:])