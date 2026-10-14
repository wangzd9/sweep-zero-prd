import subprocess, json, os, time

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
WT = "/home/wang/.local/state/rosbag-scene/wt-03b"
SINCE = "2026-10-12 03:38:53"

def sh(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=60)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

out = {}

# 1. new files in shared root since last poll (excluding routine dirs)
rc, s = sh(f"find {ROOT} -type f -newermt '{SINCE}' -not -path '*/.git/*' | "
           f"grep -v -E '(/sessions/|/events/|/ticks/|/leases/|/scratch/|/control/)' | head -40")
out["new_files"] = s.strip() or "(none)"

# 2. inbox 3号 / coordinator latest
rc1, s1 = sh(f"ls -lat {ROOT}/inbox/3号/ {ROOT}/inbox/3号/*/ 2>/dev/null | head -20")
out["inbox3"] = s1.strip()
rc2, s2 = sh(f"find {ROOT}/inbox/coordinator -type f -printf '%T+ %p\n' 2>/dev/null | sort | tail -5")
out["inbox_coord"] = s2.strip() or "(none)"

# 3. main head (both repos: worktree + origin)
rc, s = sh("git -C " + WT + " rev-parse main origin/main HEAD 2>&1")
out["heads"] = s.strip()
rc, s = sh("git -C " + WT + " status --porcelain | grep -v '.venv' | head -10")
out["wt_status"] = s.strip() or "(clean)"
rc, s = sh("git -C " + WT + " branch --show-current")
out["wt_branch"] = s.strip()

# 4. ps: any C-related business process
rc, s = sh("ps -eo pid,etimes,args | grep -E '(wt-03b|scene-03b|t03b|task-03b|3号)' | grep -v grep | head -10")
out["ps_c"] = s.strip() or "(none)"

# 5. leases
rc, s = sh(f"find {ROOT}/inbox/control/runtime/leases -type f -size +0c -printf '%s %T+ %p\n' 2>/dev/null")
out["leases"] = s.strip() or "(none)"

# 6. any C lease currently held?
rc, s = sh(f"cat {ROOT}/inbox/control/runtime/leases/C.json 2>/dev/null")
out["c_lease"] = s.strip() or "(none)"

# 7. C dispatch check: any file in inbox/3号 modified after 10-10 00:59
rc, s = sh(f"find {ROOT}/inbox/3号 -type f -newermt '2026-10-10 00:59' 2>/dev/null")
out["c_new_dispatch"] = s.strip() or "(none — no C dispatch since 10-10 00:58)"

print(json.dumps(out, ensure_ascii=False, indent=1))