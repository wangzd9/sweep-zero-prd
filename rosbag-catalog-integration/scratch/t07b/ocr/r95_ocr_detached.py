#!/usr/bin/env python3
"""r95: detached serial OCR runner for TASK-07B b5-b10 (setsid, survives cron session end)."""
import fcntl, os, subprocess, time

WT = "/home/wang/.local/state/rosbag-scene/wt-04a-t07b"
BASE = "502bf8ec79690cf01e130cb0591121eb10e96af5"
HEAD = "f4bfcf2aad48877c3a3add55a02eed44c055a115"
LOCK = "/home/wang/work/doc/prd/rosbag-catalog-integration/inbox/ocr.lock"
LOGDIR = "/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t07b/ocr"
PROG = f"{LOGDIR}/remaining_progress.txt"

FILES = [
    "app/services/scene_manual_revision_service.py",  # b5 (+383)
    "app/static/bag-detail.css",                      # b6
    "app/static/bag-search.css",                      # b7
    "app/templates/bags.html",                        # b8
    "app/templates/detail.html",                      # b9
    "app/web/bags.py",                                # b10
]
DONE_EXCLUDE = [
    "alembic/versions/20261012_01_scene_manual.py",  # b1 0 findings
    "app/api/__init__.py",                           # b2 0 findings
    "app/api/scene_manual_revision.py",              # b3 1 medium CORRECTION 待裁决
    "app/models.py",                                 # b4 0 findings
]

lock = open(LOCK, "a+")
fcntl.flock(lock, fcntl.LOCK_EX)
with open(PROG, "a", encoding="utf-8") as p:
    p.write(f"== r95 detached started {time.strftime('%F %T %z')} pid={os.getpid()} files={len(FILES)} base={BASE[:7]} head={HEAD[:7]} ==\n")
    p.flush()
    for f in FILES:
        excl = ",".join(x for x in DONE_EXCLUDE + FILES if x != f) + ",tests/*"
        logpath = f"{LOGDIR}/ocr_{f.replace('/', '_')}_r95.log"
        t0 = time.time()
        with open(logpath, "w", encoding="utf-8") as log:
            rc = subprocess.run(
                ["ocr", "review", "--from", BASE, "--to", HEAD, "--audience", "agent",
                 "--max-tokens", "30000", "--exclude", excl],
                cwd=WT, stdout=log, stderr=subprocess.STDOUT).returncode
        dt = int(time.time() - t0)
        lines = [l.rstrip() for l in open(logpath, encoding="utf-8") if l.strip()]
        p.write(f"FILE={f} RC={rc} SECONDS={dt}\n" + "\n".join(lines[-12:]) + "\n")
        p.flush()
    p.write(f"== r95 detached done {time.strftime('%F %T %z')} ==\n")