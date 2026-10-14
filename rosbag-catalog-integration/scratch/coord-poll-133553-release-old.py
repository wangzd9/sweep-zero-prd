#!/usr/bin/env python3
"""释放上轮因 token 解析失败遗留的协调者租约（owner 仍为本轮会话，可释放）。"""
import subprocess
import sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"

r = subprocess.run(
    [sys.executable, RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--token", "72f004df01164410942dccce8f2ceb82"],
    capture_output=True, text=True,
)
print(r.stdout, end="")
print(r.stderr, end="", file=sys.stderr)
sys.exit(r.returncode)