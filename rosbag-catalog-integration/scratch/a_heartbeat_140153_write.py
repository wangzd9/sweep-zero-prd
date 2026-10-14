import io, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
CANON = ROOT + "/sessions/A.md"
MIRROR = ROOT + "/inbox/sessions/A.md"
TMP = ROOT + "/scratch/a_heartbeat_140153.md"
SIG = "- \u5fc3\u8df3\uff1a2026-10-12 14:03 CST"  # 心跳：2026-10-12 14:03 CST

# 1. read entry, sanity-check before touching any shared file
entry = io.open(TMP, "r", encoding="utf-8").read()
assert entry.startswith(SIG), "entry signature mismatch"
assert "caf385b" in entry and "140153" in entry
lines = [l for l in entry.splitlines()]
assert lines and lines[0].startswith(SIG)

# 2. read both files; if canonical already has 14:03 entry, skip (idempotent)
def read(p):
    return io.open(p, "r", encoding="utf-8").read()

canon = read(CANON)
before = len(canon.splitlines())
assert SIG not in canon, "14:03 entry already present in canonical, abort (idempotent)"
assert before > 50, "canonical line count implausibly small, abort"

# 3. ensure trailing newline then append
if not canon.endswith("\n"):
    canon += "\n"
canon_new = canon + entry.rstrip("\n") + "\n"

# 4. dry-run verification on a temp target first
dry = ROOT + "/scratch/a_sessions_dry_140153.md"
io.open(dry, "w", encoding="utf-8").write(canon_new)
check = io.open(dry, "r", encoding="utf-8").read()
cnew = len(check.splitlines())
assert cnew == before + len(lines), (cnew, before, len(lines))
assert check.count(SIG) == 1
assert check.startswith(canon[:200]), "prefix changed, abort"
import os
os.remove(dry)

# 5. write real canonical only after dry-run passes
io.open(CANON, "w", encoding="utf-8").write(canon_new)

# 6. mirror: known-divergent since 12:13 incident (reported, awaiting
#    coordinator spot-check) -- canonical is the single source; do NOT
#    append into the diverged mirror this round.
print("mirror left untouched (divergent, incident in case)")

# 7. verify on disk
final = io.open(CANON, "r", encoding="utf-8").read()
assert final.count(SIG) == 1 and len(final.splitlines()) == cnew
tail3 = final.splitlines()[-3:]
print("canonical ok:", len(final.splitlines()), "lines")
for t in tail3:
    print("TAIL:", t[:100])