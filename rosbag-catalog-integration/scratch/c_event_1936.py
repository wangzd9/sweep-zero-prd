#!/usr/bin/env python3
import subprocess, re, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUN = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261011-193353"
EVENT_ID = "C-poll-20261011-193353-nochange"

def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    print("CMD:", cmd[:110])
    print(r.stdout.strip()[:400])
    if r.returncode != 0:
        print("STDERR:", r.stderr.strip()[:400])
    return r

r = sh(f"python3 {RUN} --project {ROOT} --role C --owner {OWNER} claim")
if r.returncode != 0:
    sys.exit(1)
m = re.search(r'"token": "([a-f0-9]+)"', r.stdout)
TOKEN = m.group(1) if m else None
print("TOKEN:", TOKEN)
if not TOKEN:
    sys.exit(2)

er = sh(
    f"python3 {RUN} --project {ROOT} --role C --token {TOKEN} "
    f"--event-id {EVENT_ID} --task TASK-03B --attempt 4 --status IDLE "
    f"--summary '巡检无C新派单：main 0a8ca8a 双核一致、wt-03b 6f1a9ad 干净、TESTER 9红文件复核在途非C范围' "
    f"--evidence 'sessions/C.md' --next '继续5分钟巡检等待派单' event"
)
print("event rc:", er.returncode)

rr = sh(f"python3 {RUN} --project {ROOT} --role C --token {TOKEN} release")
print("release rc:", rr.returncode)