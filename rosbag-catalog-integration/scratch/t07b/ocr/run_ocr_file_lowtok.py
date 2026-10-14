#!/usr/bin/env python3
"""串行单文件 OCR（低 token 版）：b5 连续 reap 后按恢复入口降级 --max-tokens 30000。用法: run_ocr_file_lowtok.py <FILE>"""
import fcntl, subprocess, sys, time

FILE = sys.argv[1]
WT = "/home/wang/.local/state/rosbag-scene/wt-04a-t07b"
BASE = "502bf8ec79690cf01e130cb0591121eb10e96af5"
HEAD = "f4bfcf2aad48877c3a3add55a02eed44c055a115"
LOCK = "/home/wang/work/doc/prd/rosbag-catalog-integration/inbox/ocr.lock"
LOGDIR = "/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t07b/ocr"
ALL = [
    "alembic/versions/20261012_01_scene_manual.py",
    "app/api/__init__.py",
    "app/api/scene_manual_revision.py",
    "app/models.py",
    "app/services/scene_manual_revision_service.py",
    "app/static/bag-detail.css",
    "app/static/bag-search.css",
    "app/templates/bags.html",
    "app/templates/detail.html",
    "app/web/bags.py",
    "tests/*",
]
excl = ",".join(f for f in ALL if f != FILE)
logpath = f"{LOGDIR}/ocr_{FILE.replace('/', '_')}_lowtok.log"
lock = open(LOCK, "a+")
fcntl.flock(lock, fcntl.LOCK_EX)
t0 = time.time()
with open(logpath, "w") as log:
    rc = subprocess.run(
        ["ocr", "review", "--from", BASE, "--to", HEAD, "--audience", "agent",
         "--max-tokens", "30000", "--exclude", excl],
        cwd=WT, stdout=log, stderr=subprocess.STDOUT,
    ).returncode
dt = int(time.time() - t0)
tail = [l.rstrip() for l in open(logpath) if l.strip()]
print(f"FILE={FILE} RC={rc} SECONDS={dt}")
for l in tail[-14:]:
    print(l)