#!/usr/bin/env python3
import subprocess
d = "/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/t07b/ocr"
child = subprocess.Popen(
    ["python3", f"{d}/r101_resume.py"],
    start_new_session=True,
    stdout=open(f"{d}/r101_resume_stdout.txt", "ab"),
    stderr=subprocess.STDOUT,
    cwd="/home/wang/work/doc/prd/rosbag-catalog-integration",
)
print("CHILD_PID=", child.pid)