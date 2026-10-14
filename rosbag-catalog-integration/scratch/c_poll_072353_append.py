#!/usr/bin/env python3
"""prepend C poll 072353 entry to sessions/C.md (idempotent; dry-run before real write)."""
import io, os, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
S = ROOT + "/sessions/C.md"
ENTRY = io.open(ROOT + "/scratch/c_poll_072353_entry.txt", "r", encoding="utf-8").read()
SIG = "- 最后更新：2026-10-12 07:24 +08:00"
assert ENTRY.startswith(SIG), "entry signature mismatch"
entry = ENTRY.rstrip("\n") + "\n"

content = io.open(S, "r", encoding="utf-8").read()
lines = content.splitlines()
if lines and lines[0].startswith(SIG):
    print("SKIP entry already at head (idempotent)")
    sys.exit(0)

new = entry + content
nlines = len(new.splitlines())
assert new.startswith(entry), "prefix write failed"
assert "07:19 +08:00" in new.split("\n", 1)[1], "prior entry lost"
assert nlines == len(lines) + 1, "line count mismatch %d vs %d" % (nlines, len(lines) + 1)

# dry-run to scratch TARGET first
tmp_target = ROOT + "/scratch/c_poll_072353_dry.md"
io.open(tmp_target, "w", encoding="utf-8").write(new)
chk = io.open(tmp_target, "r", encoding="utf-8").read()
assert chk.startswith(entry) and len(chk.splitlines()) == nlines, "dry-run verify failed"
print("dry-run ok lines=%d" % nlines)

io.open(S, "w", encoding="utf-8").write(new)
post = io.open(S, "r", encoding="utf-8").read()
assert post.startswith(entry) and len(post.splitlines()) == nlines, "post-write verify failed"
print("WROTE lines=%d" % nlines)