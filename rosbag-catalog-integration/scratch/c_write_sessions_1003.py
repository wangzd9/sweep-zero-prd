#!/usr/bin/env python3
# write round-10:03 entry into canonical sessions/C.md (prepend), with dry-run on temp TARGET first
import io, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
ENTRY = io.open(ROOT + "/scratch/c_entry_1003.md", encoding="utf-8").read().rstrip("\n")
assert ENTRY.startswith("- 最后更新：2026-10-12 10:03 +08:00"), "entry signature missing"
assert len(ENTRY) > 500, "entry too short"

def build(existing: str) -> str:
    return ENTRY + "\n" + existing

def check(content: str, old_lines: int) -> None:
    sig = "最后更新：2026-10-12 10:03 +08:00"
    assert content.count(sig) == 1, f"signature count={content.count(sig)}"
    first = content.split("\n", 1)[0]
    assert first.startswith("- " + sig), "first line is not the new entry"
    # line count must be old + 1 (both normalized to end with newline)
    n_new = content.count("\n")
    assert n_new == old_lines + 1, f"line count {n_new} != {old_lines}+1"
    # previous top entry survived as second line
    second = content.split("\n")[1]
    assert "2026-10-12 09:51 +08:00" in second, "previous 09:51 entry not preserved as line 2"

existing = io.open(ROOT + "/sessions/C.md", encoding="utf-8").read()
if not existing.endswith("\n"):
    existing += "\n"
old_lines = existing.count("\n")

new = build(existing)
# dry-run on temp TARGET
tmp = ROOT + "/scratch/c_sessions_dryrun_1003.md"
check(new, old_lines)
io.open(tmp, "w", encoding="utf-8").write(new)
back = io.open(tmp, encoding="utf-8").read()
check(back, old_lines)

# real write last
io.open(ROOT + "/sessions/C.md", "w", encoding="utf-8").write(new)
final = io.open(ROOT + "/sessions/C.md", encoding="utf-8").read()
check(final, old_lines)
print(f"OK lines {old_lines}->{final.count(chr(10))} first_sig=1 second=09:51-preserved")