#!/usr/bin/env python3
"""C 13:13 poll control: claim -> run(prepend sessions/C.md, dry-run first) -> event -> release."""
import io
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
RUNTIME = Path("/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py")
OWNER = "C-cron-poll-20261012-131353"
ENTRY = (ROOT / "scratch" / "c_entry_1313.md").read_text(encoding="utf-8")
SESSIONS = ROOT / "sessions" / "C.md"
SIGN = "2026-10-12 13:13"
PREV = "2026-10-12 13:03"

def sh(args):
    p = subprocess.run(args, capture_output=True, text=True)
    return p

# 1) claim, parse token from FULL json output
p = sh(["python3", str(RUNTIME), "claim", "--project", str(ROOT), "--role", "C", "--owner", OWNER])
if p.returncode != 0:
    sys.exit("CLAIM_FAIL rc=%d out=%s err=%s" % (p.returncode, p.stdout[-400:], p.stderr[-400:]))
tok = None
try:
    start = p.stdout.index("{")
    tok = json.loads(p.stdout[start:])
except Exception:
    tok = None
token = tok.get("token") if isinstance(tok, dict) else None
if not token:
    # fallback: lease file same-origin
    lease = json.loads((ROOT / "inbox" / "control" / "runtime" / "leases" / "C.json").read_text())
    assert lease.get("owner") == OWNER, "lease owner mismatch"
    token = lease["token"]
print("claimed token ok")

# 2) dry-run build against temp target: compute/verify BEFORE any shared file open
current = SESSIONS.read_text(encoding="utf-8")
old_lines = current.count("\n")
new_content = ENTRY if ENTRY.endswith("\n") else ENTRY + "\n"
new_content += current
tmp = ROOT / "scratch" / "c_sessions_dryrun_1313.md"
tmp.write_text(new_content, encoding="utf-8")
lines = new_content.count("\n")
first = new_content.split("\n", 1)[0]
assert first.startswith("- 最后更新：%s" % SIGN), "first line signature mismatch"
assert old_lines + 1 == lines, "line count: expected %d got %d" % (old_lines + 1, lines)
assert new_content.split("\n", 2)[1] == current.split("\n", 1)[0], "second line must be old first line"
# spot signature count: previous 13:03 entry must survive
assert PREV in new_content, "13:03 entry lost in dry run"
print("dry-run verified: lines %d -> %d" % (old_lines, lines))

# 3) run: replace shared file only after verification passed (single last write)
sh(["python3", str(RUNTIME), "run", "--project", str(ROOT), "--role", "C", "--token", token,
    "--", "cp", str(tmp), str(SESSIONS)])
written = SESSIONS.read_text(encoding="utf-8")
assert written == new_content, "post-write content mismatch"
assert written.count("\n") == lines, "post-write line count mismatch"
print("sessions written and verified")
tmp.unlink()

# 4) event
sh(["python3", str(RUNTIME), "event", "--project", str(ROOT), "--role", "C", "--token", token,
    "--event-id", "C-poll-20261012-131353-nochange", "--task", "NONE", "--attempt", "0",
    "--status", "POLL_NO_CHANGE",
    "--summary", "C 巡检 13:13:53：13:03:53 后 C 范围零新增、无 C 新派单（新增=协调者 r79 T07A-r1f-bagsvc-r3 续批 OCR 在途（协调者范围）+leases/B.json 瞬时在途已释放+各角色例行刷新）；main 453da0c=origin 双核、wt-03b 6f1a9ad 干净、ps 0、leases 无 C 在途租约、保持空闲待派单",
    "--evidence", "sessions/C.md 13:13 条目; find -newermt 13:03:53; rev-parse 双核",
    "--next", "等协调者派单；不接管非 C 租约"])
print("event written")

# 5) release
p = sh(["python3", str(RUNTIME), "release", "--project", str(ROOT), "--role", "C", "--token", token])
if p.returncode != 0:
    sys.exit("RELEASE_FAIL rc=%d out=%s err=%s" % (p.returncode, p.stdout[-400:], p.stderr[-400:]))
print("released OK")