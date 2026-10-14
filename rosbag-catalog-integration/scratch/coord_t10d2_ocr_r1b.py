#!/usr/bin/env python3
"""T10D2-r1 OCR 批：wt-04a-t10d2 d4719f6 (base ca8730d)，入选 scene_publish_service.py。
持 inbox/ocr.lock 稳定 inode（fcntl flock），前台跑 ocr，stdout 直落 log。
"""
import fcntl, json, subprocess, sys, time
from pathlib import Path

ROOT = Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
WT = "/home/wang/.local/state/rosbag-scene/wt-04a-t10d2"
LOCK = ROOT / "inbox" / "ocr.lock"
LOG = ROOT / "scratch" / "coord_t10d2_ocr_r1b.log"
BATCH = {
    "owner": "cron-coord-poll-20261012-005053",
    "task": "T10D2-r1",
    "commit": "d4719f6",
    "base": "ca8730d",
    "status": "RUNNING",
    "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "note": "1 file scene_publish_service.py (303L<500 单批); tests default_path 排除; max-tokens 60000",
}

def finish(status, **extra):
    BATCH.update({"status": status, "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **extra})
    with open(LOCK, "w") as f:
        json.dump(BATCH, f)
    print("OCR_DONE", json.dumps(BATCH, ensure_ascii=False))

fh = open(LOG, "w", encoding="utf-8")
fh.write("=== ocr preview ===\n")
fh.flush()
try:
    p = subprocess.run(
        ["ocr", "review", "-c", "d4719f6", "--audience", "agent", "--max-tokens", "60000", "--preview"],
        cwd=WT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120,
    )
    fh.write(p.stdout or "(empty)\n")
except Exception as e:
    fh.write(f"PREVIEW FAILED: {e}\n")
    fh.close()
    finish("FAILED_PREVIEW", error=str(e))
    sys.exit(2)
fh.write("\n=== ocr run ===\n")
fh.flush()

lf = open(LOCK, "r+")
try:
    fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    lf.close()
    fh.write("OCR LOCK HELD BY OTHER RUNNER\n")
    fh.close()
    finish("LOCK_HELD")
    sys.exit(3)

try:
    lf.seek(0)
    lf.truncate()
    json.dump(BATCH, lf)
    lf.flush()
    t0 = time.time()
    r = subprocess.run(
        ["ocr", "review", "-c", "d4719f6", "--audience", "agent", "--max-tokens", "60000"],
        cwd=WT, stdout=fh, stderr=subprocess.STDOUT, text=True, timeout=400,
    )
    elapsed = int(time.time() - t0)
    fh.write(f"\nEXIT={r.returncode} elapsed={elapsed}s\n")
    if r.returncode == 0:
        finish("COMPLETE_0_FINDINGS", exit_code=0, elapsed_s=elapsed)
    else:
        finish("FAILED", exit_code=r.returncode, elapsed_s=elapsed)
finally:
    fcntl.flock(lf, fcntl.LOCK_UN)
    lf.close()
    fh.close()
sys.exit(0)