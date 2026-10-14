#!/usr/bin/env python3
import io, json, subprocess
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
lease = json.load(io.open(ROOT + "/inbox/control/runtime/leases/C.json", encoding="utf-8"))
print("current owner:", lease.get("owner"))
out = subprocess.run(f"python3 {RUNTIME} release --project {ROOT} --role C --token {lease['token']}",
                     shell=True, capture_output=True, text=True)
print("release rc:", out.returncode, out.stdout[-200:], out.stderr[-200:])
# verify
try:
    l2 = json.load(io.open(ROOT + "/inbox/control/runtime/leases/C.json", encoding="utf-8"))
    print("after release owner:", l2.get("owner"))
except Exception as e:
    print("after release: lease gone", e)