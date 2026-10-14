#!/usr/bin/env python3
"""r95: launch detached OCR runner (new session, survives this cron session), print child pid."""
import os, subprocess
d = "/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t07b/ocr"
child = subprocess.Popen(
    ["python3", f"{d}/r95_ocr_detached.py"],
    start_new_session=True,
    stdout=open(f"{d}/r95_detached_stdout.txt", "ab"),
    stderr=subprocess.STDOUT,
    cwd="/home/wang/work/doc/prd/rosbag-catalog-integration",
)
print("CHILD_PID=", child.pid)