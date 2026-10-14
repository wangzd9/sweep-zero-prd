#!/usr/bin/env python3
"""Round 2026-10-11 08:11 poll: claim COORDINATOR control lease."""
import json
import subprocess
import sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "cron-poll-14ae4556629a-081053"

r = subprocess.run(
    [sys.executable, RUNTIME, "claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER],
    capture_output=True, text=True,
)
out = r.stdout.strip()
print("RC", r.returncode)
print(out or r.stderr.strip())
try:
    data = json.loads(out)
    tok = data.get("token")
except Exception:
    tok = out.split()[-1] if out else None
if tok:
    with open(f"{ROOT}/scratch/coord_token_0811.txt", "w") as f:
        f.write(tok)
    print("TOKEN_SAVED")