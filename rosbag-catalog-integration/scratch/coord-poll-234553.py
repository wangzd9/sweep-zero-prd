#!/usr/bin/env python3
# coordinator 23:40:53 poll: read-only fact gathering
import subprocess, json, os, datetime

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
WT = "/home/wang/.local/state/rosbag-scene/wt-04a-t10"
SINCE = "2026-10-11 23:25:53"

def sh(cmd, cwd=None, timeout=60):
    try:
        r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"

out = {}
out["now"] = datetime.datetime.now().isoformat()

# main head
rc1, h1, _ = sh("git rev-parse main")
rc2, h2, _ = sh("git rev-parse origin/main")
out["main"] = h1
out["origin_main"] = h2
out["main_eq_origin"] = (h1 == h2)

# receipts TASK-10
rc, lst, _ = sh(f"ls -la {ROOT}/receipts/TASK-10/ 2>/dev/null || echo MISSING")
out["receipts_t10"] = lst

# wt-04a-t10 status + log
rc, wts, _ = sh("git status --porcelain=v1; git log --oneline -3", cwd=WT)
out["wt_status"] = wts

# find newer business files since last checkpoint
rc, new, _ = sh(f"find {ROOT} -newermt '{SINCE}' -type f -not -path '*/.git/*' -not -path '*/inbox/control/runtime/*' | head -80")
out["new_files_since"] = new

# scratch/t10 log tail
rc, tail, _ = sh("ls -la /home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t10/ 2>/dev/null")
out["scratch_t10_ls"] = tail
rc, logtail, _ = sh("tail -c 4000 /home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t10/t10-e2e.log 2>/dev/null")
out["e2e_log_tail"] = logtail
rc, logmt, _ = sh("stat -c '%y' /home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t10/t10-e2e.log 2>/dev/null")
out["e2e_log_mtime"] = logmt

# json evidence mtime
rc, jmt, _ = sh("stat -c '%y' /home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t10/t10-e2e.json 2>/dev/null")
out["e2e_json_mtime"] = jmt

# ps: B-side business processes (pytest / t10 driver / ocr)
rc, ps, _ = sh("ps -eo pid,etime,args | grep -Ei 't10|pytest|ocr ' | grep -v grep | head -20")
out["ps"] = ps

# ticks
for role in ("A", "B", "C", "TESTER"):
    p = f"{ROOT}/inbox/control/runtime/ticks/{role}.json"
    try:
        with open(p) as f:
            d = json.load(f)
        out[f"tick_{role}"] = {k: d.get(k) for k in ("last_tick", "mode", "busy") if k in d}
    except Exception as e:
        out[f"tick_{role}"] = f"ERR {e}"

# leases
rc, leases, _ = sh(f"ls -la {ROOT}/inbox/control/runtime/leases/ 2>/dev/null")
out["leases"] = leases
rc, leasecontent, _ = sh(f"for f in {ROOT}/inbox/control/runtime/leases/*.lock; do echo \"== $f\"; cat \"$f\" 2>/dev/null | head -5; done")
out["lease_detail"] = leasecontent

# B sessions file tail (checkpoints)
rc, btail, _ = sh(f"tail -c 3000 {ROOT}/sessions/B.md")
out["b_sessions_tail"] = btail
rc, bmt, _ = sh(f"stat -c '%y' {ROOT}/sessions/B.md")
out["b_sessions_mtime"] = bmt

print(json.dumps(out, ensure_ascii=False, indent=1))