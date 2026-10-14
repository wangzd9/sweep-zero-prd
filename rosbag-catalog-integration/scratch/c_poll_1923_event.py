#!/usr/bin/env python3
import subprocess, json, sys

RT = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261011-192353"

def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=90)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

rc, out, err = sh(f"python3 {RT} claim --project {ROOT} --role C --owner {OWNER}")
print("claim rc=", rc)
tok = None
try:
    data = json.loads(out)
    tok = data.get("token")
except Exception:
    pass
if not tok:
    print("out:", out[:300], "err:", err[:300])
    sys.exit(1)

rc2, out2, err2 = sh(f"python3 {RT} event --project {ROOT} --role C --token {tok} --event-id C-poll-20261011-192353-nochange --task none --attempt 0 --status IDLE --summary 无C新派单 TESTER post-merge复核在途非C范围 保持空闲 --evidence sessions/C.md --next 继续5分钟巡检待派单")
print("event rc=", rc2, out2[:300], err2[:300])

rc3, out3, err3 = sh(f"python3 {RT} release --project {ROOT} --role C --token {tok}")
print("release rc=", rc3, out3[:100], err3[:100])