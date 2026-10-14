#!/usr/bin/env python3
import os, subprocess, glob, datetime

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"

# 1. 共享根 19:25:30 之后（排除本轮 scratch 脚本本身）的全部新增
print("=== 19:25:30 后共享根新增（全量，含 sessions/leases/events） ===")
cutoff = datetime.datetime(2026, 10, 11, 19, 25, 30).timestamp()
found = []
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if not d.startswith(".")]
    for f in fn:
        p = os.path.join(dp, f)
        st = os.stat(p)
        if st.st_mtime >= cutoff:
            found.append((st.st_mtime, p))
found.sort()
for t, p in found:
    print(datetime.datetime.fromtimestamp(t).strftime("%H:%M:%S"), p)
if not found:
    print("(none)")

# 2. leases 实际状态
print("\n=== leases 目录实际内容 ===")
for f in sorted(glob.glob(ROOT + "/inbox/leases/*")):
    print(f, os.path.getsize(f), "bytes")
if not glob.glob(ROOT + "/inbox/leases/*"):
    print("(empty)")

# 3. inbox/control 状态
print("\n=== inbox/control ===")
for dp, dn, fn in os.walk(ROOT + "/inbox/control"):
    dn[:] = [d for d in dn if not d.startswith(".")]
    for f in fn:
        p = os.path.join(dp, f)
        st = os.stat(p)
        print(datetime.datetime.fromtimestamp(st.st_mtime).strftime("%H:%M:%S"), p, st.st_size, "bytes")

# 4. 19:19 t08c-1 decision head
print("\n=== t08c-1 decision head ===")
d = ROOT + "/inbox/coordinator/TASK-08/t08c-1-acceptance-decision.md"
print(open(d).read()[:600])

# 5. TESTER 长测试是否仍活跃
print("\n=== TESTER 相关进程 ===")
r = subprocess.run("ps aux | grep -E 'pytest|mysql|8.4' | grep -v grep", shell=True, capture_output=True, text=True)
print(r.stdout[:600] if r.stdout else "(none)")

# 6. HANDOFF 最新检查点时间
print("\n=== HANDOFF mtime ===")
st = os.stat(ROOT + "/HANDOFF.md")
print(datetime.datetime.fromtimestamp(st.st_mtime).strftime("%H:%M:%S"))