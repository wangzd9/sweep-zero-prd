#!/usr/bin/env python3
import os, subprocess, glob, json

ROOT = "/home/wang/work/docs/rosbag-catalog-integration".replace("/docs/", "/doc/")
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"

def sh(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=60)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

# 1. 19:30 后共享根新增（排除噪音目录）
excl = ("sessions", "events", "leases", "ticks", "scratch", "control", ".git")
new = []
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in excl and not d.startswith(".")]
    for f in fn:
        p = os.path.join(dp, f)
        try:
            st = os.stat(p)
        except OSError:
            continue
        import datetime
        t = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%m-%d %H:%M:%S")
        if st.st_mtime > 0 and datetime.datetime.fromtimestamp(st.st_mtime) >= datetime.datetime(2026,10,11,19,30,0):
            new.append(f"{t} {p}")
print("=== 19:30 后新增文件 ===")
for line in sorted(new):
    print(line)

# 2. inbox/3号 最新
print("\n=== inbox/3号 最新 ===")
for p in sorted(glob.glob(ROOT + "/inbox/3号/**/*", recursive=True)) if False else []:
    pass
rc, out, _ = sh("ls -lt --time-style='+%F %T' " + ROOT + "/inbox/3号/TASK-03B/")
print(out[:800])

# 3. inbox/coordinator 最新
print("\n=== inbox/coordinator 最新 ===")
rc, out, _ = sh("find " + ROOT + "/inbox/coordinator -type f -printf '%TY-%Tm-%Td %TH:%TM:%TS %p\\n' | sort | tail -12")
print(out)

# 4. main HEAD
print("\n=== main HEAD ===")
rc, out, _ = sh("git rev-parse --short=7 main && git rev-parse --short=7 origin/main", cwd="/home/wang/work/rosbag-catalog")
print(out)

# 5. wt-03b
WT = "/home/wang/.local/state/rosbag-scene/wt-03b"
print("\n=== wt-03b ===")
rc, out, _ = sh("git rev-parse --short=7 HEAD", cwd=WT)
print("HEAD:", out)
rc, out, _ = sh("git status --porcelain", cwd=WT)
lines = [l for l in out.splitlines() if ".venv" not in l]
print("dirty:", lines if lines else "clean")

# 6. C 在途进程
print("\n=== C 进程 ===")
rc, out, _ = sh("ps aux | grep -E 'wt-03b|role_runtime' | grep -v grep")
print(out if out else "(none)")

# 7. leases
print("\n=== leases ===")
for f in sorted(glob.glob(ROOT + "/inbox/leases/*")):
    size = os.path.getsize(f)
    if size > 0:
        print(f, size, "->", open(f).read().strip())
    else:
        print(f, "0-byte")
if not glob.glob(ROOT + "/inbox/leases/*"):
    print("(empty dir)")