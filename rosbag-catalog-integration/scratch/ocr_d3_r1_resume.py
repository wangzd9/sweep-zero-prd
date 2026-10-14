#!/usr/bin/env python3
import fcntl, subprocess, os, sys, time

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
WT = "/home/wang/.local/state/rosbag-scene/wt-04a"
LOCK = os.path.join(ROOT, "inbox/ocr.lock")
LOG = os.path.join(ROOT, "reviews/TASK-06B/attempt-1-defect3-reconcile-replay/ocr-d3-r1-resume.log")
SESSION = "5ee653d5-c724-4103-b686-546fd928177a"
COMMIT = "4e2158e"

os.makedirs(os.path.dirname(LOG), exist_ok=True)
lf = open(LOCK, "a")
try:
    fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    print("LOCK_HELD: another ocr run holds ocr.lock; aborting resume")
    lf.close()
    sys.exit(3)

try:
    cmd = ["ocr", "review", "-c", COMMIT, "--resume", SESSION,
           "--max-tokens", "100000", "--timeout", "30",
           "--audience", "agent", "--format", "json"]
    t0 = time.time()
    with open(LOG, "w") as out:
        p = subprocess.run(cmd, cwd=WT, stdout=out, stderr=subprocess.STDOUT, text=True)
    rc = p.returncode
    print("RESUME_DONE rc=%d dur=%ds log=%s" % (rc, int(time.time() - t0), LOG))
finally:
    fcntl.flock(lf, fcntl.LOCK_UN)
    lf.close()