import io, sys, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
entry = io.open(os.path.join(ROOT, "scratch/c_entry_1033.md"), encoding="utf-8").read().rstrip("\n")
assert entry.startswith("- 最后更新：2026-10-12 10:33 +08:00"), "entry signature mismatch"
assert entry.count("\n") == 0, "entry must be single line"

src = os.path.join(ROOT, "sessions/C.md")
old = io.open(src, encoding="utf-8").read()
old_lines = old.splitlines()
assert old_lines[0].startswith("- 最后更新：2026-10-12 10:28 +08:00"), "first line not the 10:28 entry, abort"
assert "C-poll-20261012-103353-nochange" not in old, "entry already present, abort"

new_lines = [entry] + old_lines
new_text = "\n".join(new_lines) + "\n"

# dry-run on temp target
tmp = os.path.join(ROOT, "scratch/c_sessions_dryrun_1033.md")
io.open(tmp, "w", encoding="utf-8").write(new_text)
chk = io.open(tmp, encoding="utf-8").read().splitlines()
assert len(chk) == len(old_lines) + 1, "line count mismatch"
assert chk[0].startswith("- 最后更新：2026-10-12 10:33 +08:00")
assert chk[1].startswith("- 最后更新：2026-10-12 10:28 +08:00")
assert chk[-1] == old_lines[-1], "last line changed"

# real write
io.open(src, "w", encoding="utf-8").write(new_text)
after = io.open(src, encoding="utf-8").read().splitlines()
assert len(after) == len(old_lines) + 1
assert after[0].startswith("- 最后更新：2026-10-12 10:33 +08:00")
assert after[-1] == old_lines[-1]
print("OK lines", len(old_lines), "->", len(after))