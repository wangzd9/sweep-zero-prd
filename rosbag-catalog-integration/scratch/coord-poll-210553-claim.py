#!/usr/bin/env python3
import json, subprocess, sys
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-coord-poll-14ae4556629a-210553"
r = subprocess.run([sys.executable, RUNTIME, "claim", "--project", ROOT,
                   "--role", "COORDINATOR", "--owner", OWNER],
                  capture_output=True, text=True)
out = (r.stdout or "").strip() or r.stderr.strip()
print("claim:", out)
sys.exit(r.returncode)