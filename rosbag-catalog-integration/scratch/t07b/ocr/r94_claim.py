#!/usr/bin/env python3
"""r94: claim COORDINATOR control lease."""
import subprocess, sys
script = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
root = "/home/wang/work/doc/prd/rosbag-catalog-integration"
claim = "cron-coord-poll-14ae4556629a-20261012-192553-r94-b5-bg-reap-check"
r = subprocess.run([sys.executable, script, "claim", "--role", "COORDINATOR",
                   "--project-root", root, "--owner", claim],
                  capture_output=True, text=True)
print("RC=", r.returncode)
print("OUT:", r.stdout.strip()[:2000])
print("ERR:", r.stderr.strip()[:500])