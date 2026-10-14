#!/usr/bin/env python3
import io, subprocess

D = "/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/c_poll_064853_dry.md"
S = "/home/wang/work/doc/prd/rosbag-catalog-integration/sessions/C.md"

def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True).stdout

lines = sh(f"wc -l < {D}").strip()
grep = sh(f"grep -c '063853' {D}").strip()
head = sh(f"head -1 {D}")
tail = sh(f"tail -1 {D}")

c1 = lines == "383"
c2 = head.startswith("- 最后更新：2026-10-12 06:56")
c3 = "06:39 +08:00" in tail
c4 = "C-cron-poll-20261012-063853" in tail
c5 = grep == "4"
print("lines:", repr(lines), "c1:", c1)
print("head[:40]:", repr(head[:40]), "c2:", c2)
print("tail sig: c3:", c3, "c4:", c4)
print("grep:", repr(grep), "c5:", c5)
print("all:", c1 and c2 and c3 and c4 and c5)

# also check the entry source file for hidden chars
E = "/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/c_poll_064853_entry.txt"
raw = io.open(E, encoding="utf-8").read()
print("entry starts with prefix:", raw.startswith("- 最后更新：2026-10-12 {HHMM} +08:00"))
print("entry newline count:", raw.count("\n"))
print("entry repr head:", repr(raw[:60]))
print("entry repr tail:", repr(raw[-60:]))