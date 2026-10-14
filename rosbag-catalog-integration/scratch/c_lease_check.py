import json, subprocess, sys, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261012-075853"

lease = os.path.join(ROOT, "inbox/control/runtime/leases/C.json")
if os.path.exists(lease):
    with open(lease) as f:
        d = json.load(f)
    print("lease:", json.dumps(d, ensure_ascii=False))
else:
    print("no lease file")