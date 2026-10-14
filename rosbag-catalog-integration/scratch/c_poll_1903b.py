#!/usr/bin/env python3
"""C 角色 19:03 巡检补收尾：用正确 token 补 event + release（claim 已输出 token 34728ad…）。"""
import subprocess, sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
TOKEN = "34728adbdeea4cf4b4ea25214ace7f24"

def sh(args):
    r = subprocess.run(args, capture_output=True, text=True)
    print("$", " ".join(args[:6]), "... rc=%d" % r.returncode)
    print(r.stdout.strip() or r.stderr.strip())
    return r

sh([sys.executable, RUNTIME, "event", "--project", ROOT, "--role", "C", "--token", TOKEN,
    "--event-id", "C-poll-20261011-190353-nochange", "--task", "TASK-03B", "--attempt", "0",
    "--status", "IDLE", "--summary", "巡检：无 C 新派单，main 98f6c88 未变，wt-03b 6f1a9ad 干净，保持空闲",
    "--evidence", "scratch/c_poll_1903.py", "--next", "继续检查本角色派单"])
sh([sys.executable, RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", TOKEN])