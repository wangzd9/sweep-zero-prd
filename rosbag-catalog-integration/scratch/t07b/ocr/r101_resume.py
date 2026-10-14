#!/usr/bin/env python3
"""r101: detached LAST-ATTEMPT resume for TASK-07B b5 (core service +383) and b7 (css +12/-1).
Policy (ocr-batches.md r100): low-load window (waiting 趋 0), --resume once each; if RC!=0 -> NEEDS_REVIEW
freezing 07B merge gate. No infinite retries. setsid to survive cron session end.
Load at launch (21:50 probe): running=4 waiting=1 (capacity, waiting near 0 = recorded condition met).
"""
import fcntl, os, subprocess, time

WT = "/home/wang/.local/state/rosbag-scene/wt-04a-t07b"
BASE = "502bf8ec79690cf01e130cb0591121eb10e96af5"
HEAD = "f4bfcf2aad48877c3a3add55a02eed44c055a115"
LOCK = "/home/wang/work/doc/prd/rosbag-catalog-integration/inbox/ocr.lock"
LOGDIR = "/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t07b/ocr"
PROG = f"{LOGDIR}/r101_resume_progress.txt"

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

# (label, file, resume_session)
JOBS = [
    ("b5", "app/services/scene_manual_revision_service.py", "81a66282-6ab7-4a78-a3d5-f309033d8dde"),
    ("b7", "app/static/bag-search.css", "daa45a1c-e3d8-4af1-97b2-8ce2585bed95"),
]

lock = open(LOCK, "a+")
fcntl.flock(lock, fcntl.LOCK_EX)
with open(PROG, "a", encoding="utf-8") as p:
    p.write(f"== r101 resume started {time.strftime('%F %T %z')} pid={os.getpid()} jobs={[(j[0], j[2][:8]) for j in JOBS]} base={BASE[:7]} head={HEAD[:7]} ==\n")
    p.flush()
    for label, f, session in JOBS:
        excl = ",".join(x for x in ALL if x != f)
        logpath = f"{LOGDIR}/ocr_{f.replace('/', '_')}_r101resume.log"
        t0 = time.time()
        with open(logpath, "w", encoding="utf-8") as log:
            rc = subprocess.run(
                ["ocr", "review", "--from", BASE, "--to", HEAD, "--audience", "agent",
                 "--resume", session, "--max-tokens", "30000", "--exclude", excl],
                cwd=WT, stdout=log, stderr=subprocess.STDOUT).returncode
        dt = int(time.time() - t0)
        lines = [l.rstrip() for l in open(logpath, encoding="utf-8") if l.strip()]
        verdict = "OK_RC0" if rc == 0 else f"FAILED_RC{rc}"
        p.write(f"\n### {label} FILE={f} {verdict} SECONDS={dt} session={session[:8]}\n")
        p.write("\n".join(lines[-16:]) + "\n")
        if rc != 0:
            p.write(f"[NEEDS_REVIEW] {label} 最后一次 resume 仍失败 -> 07B 合入门禁冻结（该文件未覆盖不得宣称收口）\n")
        p.flush()
    p.write(f"\n== r101 resume done {time.strftime('%F %T %z')} ==\n")