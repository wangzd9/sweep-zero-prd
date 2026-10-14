#!/usr/bin/env python3
"""coord poll 132053: retry event+release with known token (same owner)."""
import subprocess, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
TOKEN = "045c7a7ab59c4aa9a2671a38ac109f76"
EVENT_ID = "coord-poll-20261011-132053-nochange"

def sh(args):
    return subprocess.run(args, capture_output=True, text=True)

er = sh(["python3", RUNTIME, "event", "--project", ROOT, "--role", "COORDINATOR",
         "--token", TOKEN, "--event-id", EVENT_ID, "--task", "NONE",
         "--attempt", "0", "--status", "NOCHANGE",
         "--summary", "13:20 巡检：13:15 后零业务变化；main 65ca0be 三核一致；强复审 R2I-20261010-06 result 仍缺维持 READY_FOR_USER_TRIGGER；A/B/C/TESTER 全空闲仅例行心跳；无在途 ocr/pytest",
         "--evidence", "sessions/COORDINATOR.md 13:20 checkpoint",
         "--next", "等用户手动触发强复审 R2I-20261010-06 或新交付"])
sys.stdout.write(er.stdout + er.stderr)
print("rc_event=", er.returncode)

rr = sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN])
sys.stdout.write(rr.stdout + rr.stderr)
print("rc_release=", rr.returncode)