#!/usr/bin/env python3
import os, subprocess, json

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
REPO = "/home/wang/work/rosbag-catalog"
WT = "/home/wang/.local/state/rosbag-scene/wt-03b"

def sh(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

print("== new files since 19:20:30 (excluding sessions/events/leases/ticks/scratch/inbox-control) ==")
out = subprocess.run(
    f"find {ROOT} -newermt '2026-10-11 19:20:30' -type f ! -path '*sessions/*' ! -path '*events/*' "
    f"! -path '*leases/*' ! -path '*ticks/*' ! -path '*scratch/*' ! -path '*inbox/control/*' ! -path '*.git/*' "
    f"-printf '%T+ %p\\n' | sort",
    shell=True, capture_output=True, text=True).stdout.strip()
print(out or "(empty)")

print("== inbox/3号 latest ==")
print(sh(f"find {ROOT}/inbox/3号 -type f -printf '%T+ %p\\n' | sort | tail -5")[1])
print("== inbox/coordinator latest ==")
print(sh(f"find {ROOT}/inbox/coordinator -type f -printf '%T+ %p\\n' | sort | tail -5")[1])
print("== main HEAD ==")
print(sh(f"git -C {REPO} rev-parse --short main")[1])
print("== origin/main ==")
print(sh(f"git -C {REPO} rev-parse --short origin/main")[1])
print("== wt-03b HEAD + status ==")
print(sh(f"git -C {WT} rev-parse --short HEAD")[1])
print(sh(f"git -C {WT} status --porcelain | grep -v '^?? .venv' || true")[1])
print("== leases >0 ==")
print(sh(f"find {ROOT}/inbox/control -name '*.json' -size +0c -printf '%T+ %p\\n' 2>/dev/null || ls -la {ROOT}/inbox/control/leases/ 2>/dev/null")[1])
print("== ps C-related ==")
ps = subprocess.run(f"ps -eo pid,lstart,args | grep -E 'wt-03b|3号|pytest|ocr' | grep -v grep", shell=True, capture_output=True, text=True).stdout.strip()
print(ps or "(empty)")