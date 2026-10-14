#!/usr/bin/env python3
"""T10D2-r1 OCR 批：wt-04a-t10d2 d4719f6 (ca8730d..d4719f6)，入选 scene_publish_service.py。
持 inbox/ocr.lock 稳定 inode（fcntl flock），前台跑 ocr，stdout 直落 log。
"""
import fcntl, json, subprocess, sys, time
from pathlib import Path

ROOT = Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
WT = "/home/wang/.local/state/rosbag-scene/wt-04a-t10d2"
LOCK = ROOT / "inbox" / "ocr.lock"
LOG = ROOT / "scratch" / "coord_t10d2_ocr_r1.log"
BATCH = {
    "owner": "cron-coord-poll-20261012-005053",
    "task": "T10D2-r1",
    "commit": "d4719f6",
    "base": "ca8730d",
    "status": "RUNNING",
    "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "note": "1 file scene_publish_service.py (303L<500 单批); tests default_path 排除; max-tokens 60000",
}

fh = open(LOG, "w", encoding="utf-8")
fh.write("=== ocr preview ===\n"); fh.flush()
try:
    p = subprocess.run(["ocr", "review", "-c", "d4719f6", "--audience", "agent", "--max-tokens", "60000", "--preview"],
                       cwd=WT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)
    fh.write(p.stdout or "(empty)")
except Exception as e:
    fh.write(f"PREVIEW FAILED: {e}\n"); fh.close()
    with open(LOCK, "w") as lf:
        json.dump({**BATCH, "status": "FAILED_PREVIEW", "error": str(e), "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}, lf)
    sys.exit(2)
fh.write("\n=== ocr run ===\n"); fh.flush()

lf = open(LOCK, "r+")
acquired = False
try:
    fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
    acquired = True
except BlockingIOError:
    fh.write("OCR LOCK HELD BY OTHER RUNNER\n"); lf.close(); fh.close()
    with open(LOCK, "w") as lf2:
        json.dump({**BATCH, "status": "LOCK_HELD", "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}, lf2)
    sys.exit(3)

if acquired:
    lf.seek(0); lf.truncate()
    json.dump(BATCH, lf); lf.flush()
    t0 = time.time()
    r = subprocess.run(["ocr", "review", "-c", "d4719f6", "--audience", "agent", "--max-tokens", "60000"],
                       cwd=WT, stdout=fh, stderr=subprocess.STDOUT, text=True, timeout=400)
    fh.write(f"\nEXIT={r.returncode} elapsed={int(time.time()-t0)}s\n")
    BATCH.update({
        "status": "COMPLETE" if r.returncode == 0 else "FAILED",
        "exit_code": r.returncode,
        "elapsed_s": int(time.time() - t0),
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    })
    lf.seek(0); lf.truncate()
    json.dump(BATCH, lf); lf.flush()
finally:
    if acquired:
        fcntl.flock(lf, fcntl.LOCK_UN)
        lf.close()
    fh.close()
print("OCR_RUN_DONE", json.dumps(BATCH))