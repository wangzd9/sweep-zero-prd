#!/usr/bin/env python3
import io, json, os, subprocess, time
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
lease = json.load(io.open(ROOT + "/inbox/control/runtime/leases/C.json", encoding="utf-8"))
assert lease["owner"] == "C-cron-poll-20261012-064853", lease
TOKEN = lease["token"]
DRY = ROOT + "/scratch/c_poll_064853_dry.md"
S = ROOT + "/sessions/C.md"
print("before:", subprocess.run(f"stat -c '%Y %s' {S}", shell=True, capture_output=True, text=True).stdout)
p = subprocess.run(["python3", RUNTIME, "run", "--project", ROOT, "--role", "C", "--token", TOKEN,
                    "--", "cp", DRY, S], capture_output=True, text=True, timeout=120)
print("rc:", p.returncode)
print("stdout:", repr(p.stdout[-500:]))
print("stderr:", repr(p.stderr[-500:]))
print("after:", subprocess.run(f"stat -c '%Y %s' {S}", shell=True, capture_output=True, text=True).stdout)