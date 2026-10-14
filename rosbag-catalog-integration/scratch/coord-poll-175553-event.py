#!/usr/bin/env python3
import subprocess, json, sys, shlex

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-coord-poll-175553-ev"

r = subprocess.run(f"python3 {RUNTIME} claim --project {ROOT} --role COORDINATOR --owner {OWNER}",
                   shell=True, capture_output=True, text=True)
d = json.loads(r.stdout)
print("claim rc:", r.returncode, d.get("claimed"))
if not d.get("claimed"):
    sys.exit(2)
TOKEN = d["token"]

args = [
    "python3", RUNTIME, "event", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN,
    "--event-id", "coord-poll-20261011-175553-t08c1-encoding-active-nochange",
    "--task", "TASK-08", "--attempt", "1", "--status", "RUNNING",
    "--summary", "17:50 后零业务交付：main 98f6c88=origin 双核一致、共享根业务目录零新增；2号 t08c-1 编码继续（test_bag_cleanup_concurrency.py 17:53:41 活跃写入，4 文件+probe 未 commit，无回执）；A/C/TESTER 空闲；无新派单/无 OCR",
    "--evidence", "sessions/COORDINATOR.md",
    "--next", "等 t08c-1 交付后机械核验+串行 OCR 增量+合入+9 红文件全绿复核",
]
r = subprocess.run(args, capture_output=True, text=True)
print("event rc:", r.returncode, r.stdout[-200:], r.stderr[-200:])

r = subprocess.run([
    "python3", RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN,
], capture_output=True, text=True)
print("release rc:", r.returncode, r.stdout[:120], r.stderr[:120])
print("DONE")