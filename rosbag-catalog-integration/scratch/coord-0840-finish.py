#!/usr/bin/env python3
"""coord poll 08:40: complete event + release using known token (lease already held by this owner)."""
import subprocess, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
TOKEN = "092e10fa4f354c50bd8d4288a5cf88da"

def sh(*args):
    r = subprocess.run([sys.executable, RUNTIME, *args], capture_output=True, text=True)
    if r.stdout: print("OUT:", r.stdout.strip()[:400])
    if r.returncode != 0:
        print("ERR:", r.stderr.strip()[:800]); sys.exit(1)
    return r.stdout

sh("event", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN,
   "--event-id", "coord-poll-20261011-084053-nochange",
   "--task", "none", "--attempt", "none",
   "--status", "IDLE_WAITING",
   "--summary", "零业务变化巡检：main 6d30a68 不变、强复审 R2I-20261010-06 result 仍不存在(READY_FOR_USER_TRIGGER)、A/B/C/TESTER 全空闲、无在途 ocr/pytest 进程",
   "--evidence", "none",
   "--next", "继续 5 分钟巡检；等用户手动触发强复审")
print("EVENT_OK")
sh("release", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN)
print("RELEASE_OK")