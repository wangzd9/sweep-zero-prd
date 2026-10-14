#!/usr/bin/env python3
import os, subprocess, datetime

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
REPO = "/home/wang/work/rosbag-catalog"
WT = "/home/wang/.local/state/rosbag-scene/wt-03b"

def sh(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()

# 1. 共享根自 20:29 后的变更（排除巡检类路径）
exclude = ("./inbox/control/", "./scratch/", "./inbox/sessions/", "./events/", "./inbox/control/runtime/")
rc, out = sh('find . -newermt "2026-10-11 20:29:00" -type f', ROOT)
hits = [f for f in out.splitlines() if f.strip() and not any(f.startswith(e) for e in exclude)]
print("CHANGED_SINCE_2029:", hits if hits else "NONE")

# 2. inbox/3号 与 inbox/coordinator 最新文件
for d in ("inbox/3号", "inbox/coordinator"):
    p = os.path.join(ROOT, d)
    entries = []
    for dp, dn, fn in os.walk(p):
        for f in fn:
            fp = os.path.join(dp, f)
            entries.append((os.path.getmtime(fp), fp))
    entries.sort()
    print(d, "NEWEST:", datetime.datetime.fromtimestamp(entries[-1][0]).strftime("%m-%d %H:%M:%S"), entries[-1][1] if entries else "-")

# 3. leases
lp = os.path.join(ROOT, "inbox/control/runtime/leases")
leases = []
if os.path.isdir(lp):
    for f in sorted(os.listdir(lp)):
        fp = os.path.join(lp, f)
        size = os.path.getsize(fp)
        if size > 0:
            leases.append(f"{f}({size}B): {open(fp).read()}")
print("ACTIVE_LEASES:", leases if leases else "NONE")

# 4. git 状态
print("MAIN:", sh("git rev-parse main", REPO)[1])
print("ORIGIN_MAIN:", sh("git rev-parse origin/main", REPO)[1])
print("WT_HEAD:", sh("git rev-parse HEAD", WT)[1])
rc, st = sh("git status --porcelain", WT)
dirty = [l for l in st.splitlines() if ".venv" not in l]
print("WT_DIRTY:", dirty if dirty else "CLEAN")

# 5. 在途进程
rc, ps = sh("ps aux | grep -E 'wt-03b|pytest|ocr' | grep -v grep | grep -v wxocr | grep -v 'code '")
print("PROCS:", ps if ps else "NONE")