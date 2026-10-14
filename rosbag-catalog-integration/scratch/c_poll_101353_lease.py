#!/usr/bin/env python3
import os, glob, json
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
for f in sorted(glob.glob(ROOT + "/inbox/control/runtime/leases/*.json")):
    if os.path.getsize(f) > 0:
        d = json.load(open(f))
        print(os.path.basename(f), "->", d.get("role"), d.get("owner"), "claimed_at:", d.get("claimed_at"), "expires:", d.get("expires_at"))
print("(end leases)")
# also verify inbox/3号 latest mtime
import subprocess
r = subprocess.run(f"find {ROOT}/inbox/3号 -type f -printf '%T+ %p\\n' | sort -r | head -5", shell=True, capture_output=True, text=True)
print(r.stdout)