#!/usr/bin/env python3
import os, glob, json, subprocess, time
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"

print("=== leases ===")
for f in sorted(glob.glob(ROOT + "/inbox/control/runtime/leases/*.json")):
    if os.path.getsize(f) > 0:
        d = json.load(open(f))
        exp = d.get("expires_at")
        exp_s = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(exp)) if isinstance(exp, (int, float)) else exp
        print(os.path.basename(f), "->", d.get("role"), "owner:", d.get("owner"), "expires:", exp_s, "EXPIRED" if (isinstance(exp, (int, float)) and exp < time.time()) else "")
print("(end leases)")

print("=== TODO TASK lines ===")
r = subprocess.run(f"grep -nE '^\\| ?\\*?TASK|^\\| ?T[0-9]|TASK-0[0-9]' {ROOT}/TODO.md | head -40", shell=True, capture_output=True, text=True)
print(r.stdout[:3000])

print("=== TASK-08 / 06 相关行 ===")
r = subprocess.run(f"grep -nE 'TASK-08|t08c|c3-1|03/05/06|聚合' {ROOT}/TODO.md | tail -25", shell=True, capture_output=True, text=True)
print(r.stdout[:4000])

print("=== try claim coordinator ===")
OWNER = "cron-coord-poll-175053"
r = subprocess.run(f"python3 {RUNTIME} claim --project {ROOT} --role COORDINATOR --owner {OWNER}", shell=True, capture_output=True, text=True)
print("RC:", r.returncode)
print(r.stdout[-800:])
print(r.stderr[-400:])
out = ROOT + "/scratch/coord-poll-175053-claim.json"
open(out, "w").write(r.stdout)
print("saved:", out)