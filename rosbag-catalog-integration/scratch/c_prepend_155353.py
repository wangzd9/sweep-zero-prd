import io, sys, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
target = sys.argv[1]  # temp TARGET for dry-run, or real sessions/C.md
entry = io.open(os.path.join(ROOT, "scratch/c_entry_155353.md"), encoding="utf-8").read()
assert entry.endswith("\n"), "entry temp file must end with newline (line-merge guard)"

# --- all checks BEFORE any shared-file open ---
assert entry.startswith("- 最后更新：2026-10-12 15:53 +08:00"), "entry signature mismatch"
cur = io.open(target, encoding="utf-8").read()
cur_lines = cur.split("\n")
assert cur_lines[0].startswith("- 最后更新：2026-10-12 15:24 +08:00"), "line1 must be 15:24 entry, got: " + cur_lines[0][:60]
assert "c-poll-20261012-151853" in cur_lines[0], "15:24 entry signature missing"
assert cur_lines[-1] == "", "must end with newline"
assert len(cur_lines) == 441, "line count must be 441 (440 + trailing empty), got %d" % len(cur_lines)

new = entry + cur
io.open(target, "w", encoding="utf-8").write(new)

# --- post-write verification ---
n = io.open(target, encoding="utf-8").read().split("\n")
assert n[0].startswith("- 最后更新：2026-10-12 15:53 +08:00"), "after: line1 signature"
assert n[1].startswith("- 最后更新：2026-10-12 15:24 +08:00"), "after: line2 signature"
assert len(n) == 442, "after: line count (1 entry + 440 + trailing empty) %d" % len(n)
print("WRITE_OK lines=%d" % len(n))