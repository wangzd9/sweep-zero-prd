#!/usr/bin/env python3
import subprocess, os, glob, json

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
SINCE = "2026-10-11 10:08:53"

def sh(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

print("=== inbox/3号 changes since", SINCE, "===")
code, out, err = sh(f"find {ROOT}/inbox/3号 -type f -newermt '{SINCE}'")
print(out or "(none)", err if code else "")

print("=== shared root changes since", SINCE, "===")
code, out, err = sh(
    f"find {ROOT} -type f -newermt '{SINCE}' "
    f"! -path '*/sessions/*' ! -path '*/events/*' ! -path '*/scratch/*' "
    f"! -path '*/inbox/control/runtime/*' ! -name '*.lock' 2>/dev/null | head -30"
)
print(out or "(none)")

print("=== main HEAD ===")
code, out, err = sh("git rev-parse --short HEAD", cwd="/home/wang/work/rosbag-catalog")
print(out)

print("=== wt-03b ===")
code, out, err = sh("git rev-parse --short HEAD", cwd="/home/wang/.local/state/rosbag-scene/wt-03b")
print("HEAD:", out)
code, out, err = sh("git status --porcelain", cwd="/home/wang/.local/state/rosbag-scene/wt-03b")
lines = [l for l in out.splitlines() if ".venv" not in l]
print("dirty(tracked):", lines if lines else "(clean, only .venv untracked)")

print("=== ps C tasks ===")
code, out, err = sh("ps aux | grep -iE 'wt-03b' | grep -v grep")
print(out if out else "(none)")

print("=== leases ===")
for f in sorted(glob.glob(ROOT + "/inbox/control/runtime/leases/*.json")):
    if os.path.getsize(f) > 0:
        try:
            d = json.load(open(f))
            print(os.path.basename(f), "->", d.get("role"), d.get("owner"), d.get("task"), d.get("expires_at") or d.get("renew_until") or "")
        except Exception as e:
            print(os.path.basename(f), "parse-err", e)
print("(end leases)")