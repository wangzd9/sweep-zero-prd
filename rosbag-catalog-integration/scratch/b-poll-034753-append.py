import io, hashlib, sys

TARGET = "/home/wang/work/doc/prd/rosbag-catalog-integration/sessions/B.md"
SRC = "/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/b-poll-034753-append.txt"
SIG = "b-poll-20261014-034753-tester-034x-infer-active-b-noaction-idle-quiet"

with io.open(TARGET, "r", encoding="utf-8") as f:
    orig = f.read()
with io.open(SRC, "r", encoding="utf-8") as f:
    entry = f.read()

lines0 = orig.count("\n")
assert orig.endswith("\n"), "target last line not newline-terminated, ABORT"
assert entry.endswith("\n"), "entry must be newline-terminated"
assert entry.startswith("- 巡检 2026-10-14 03:52"), "entry marker mismatch"
assert SIG in entry
assert orig.count(SIG) == 0, "signature already present, ABORT"
assert "\n- 巡检 2026-10-14 03:52" not in orig, "duplicate entry, ABORT"

md5_pre = hashlib.md5(orig.encode("utf-8")).hexdigest()
new = orig + entry
with io.open(TARGET, "a", encoding="utf-8") as f:
    f.write(entry)
with io.open(TARGET, "r", encoding="utf-8") as f:
    back = f.read()
assert back == new, "post-write content mismatch, ABORT"
assert back.count(SIG) == 1
assert back.count("\n") == lines0 + 1
print("OK md5_pre=%s lines_pre=%d lines_post=%d" % (md5_pre, lines0, back.count("\n")))