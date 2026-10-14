#!/usr/bin/env python3
import io
ENTRY = "/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/c_poll_062353_entry.txt"
SESSIONS = "/home/wang/work/doc/prd/rosbag-catalog-integration/sessions/C.md"
e = io.open(ENTRY, "r", encoding="utf-8").read()
f = io.open(SESSIONS, "a", encoding="utf-8")
f.write(e)
f.close()
print("appended", len(e))