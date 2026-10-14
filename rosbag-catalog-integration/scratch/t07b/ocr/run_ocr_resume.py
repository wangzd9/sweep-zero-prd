#!/usr/bin/env python3
"""resume 版：断点续审单文件。用法: run_ocr_resume.py <FILE> <session-uuid>"""
import fcntl, subprocess, sys, time

FILE = sys.argv[1]
SID = sys.argv[2]
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
logpath = f"{LOGDIR}/ocr_{FILE.replace('/', '_')}_resume.log"
lock = open(LOCK, "a+")
fcntl.flock(lock, fcntl.LOCK_EX)
t0 = time.time()
with open(logpath, "w") as log:
    rc = subprocess.run(
        ["ocr", "review", "--from", BASE, "--to", HEAD, "--audience", "agent",
         "--max-tokens", "60000", "--exclude", excl, "--resume", SID],
        cwd=WT, stdout=log, stderr=subprocess.STDOUT,
    ).returncode
dt = int(time.time() - t0)
tail = [l.rstrip() for l in open(logpath) if l.strip()]
print(f"FILE={FILE} RC={rc} SECONDS={dt}")
for l in tail[-12:]:
    print(l)