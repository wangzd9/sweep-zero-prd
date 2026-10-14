#!/usr/bin/env python3
"""release 上一轮 claim 成功但未 release 的孤儿租约（同 owner+token 同源释放）"""
import subprocess, sys
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
r = subprocess.run([sys.executable, RUNTIME, "release", "--project", ROOT,
                    "--role", "COORDINATOR", "--owner", "cron-coord-poll-224053",
                    "--token", "467c7c591f954f699db2341b1b29de53"],
                   capture_output=True, text=True)
print(r.stdout)
print("RC", r.returncode, r.stderr[:300], file=sys.stderr)