#!/usr/bin/env python3
"""C 13:18 poll control: claim -> dry-run verify -> single prepend write -> event -> release."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
RUNTIME = Path("/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py")
OWNER = "C-cron-poll-20261012-131853"
ENTRY = (ROOT / "scratch" / "c_entry_131853.md").read_text(encoding="utf-8")
SESSIONS = ROOT / "sessions" / "C.md"
SIGN = "2026-10-12 13:20"
PREV = "2026-10-12 13:13"

def sh(args):
    return subprocess.run(args, capture_output=True, text=True)

# 1) claim; parse token from FULL json output (never tail/grep)
p = sh(["python3", str(RUNTIME), "claim", "--project", str(ROOT), "--role", "C", "--owner", OWNER])
if p.returncode != 0:
    sys.exit("CLAIM_FAIL rc=%d out=%s err=%s" % (p.returncode, p.stdout[-400:], p.stderr[-400:]))
try:
    start = p.stdout.index("{")
    tok = json.loads(p.stdout[start:])
except Exception:
    tok = None
token = tok.get("token") if isinstance(tok, dict) else None
if not token:
    lease = json.loads((ROOT / "inbox" / "control" / "runtime" / "leases" / "C.json").read_text(encoding="utf-8"))
    assert lease.get("owner") == OWNER, "lease owner mismatch"
    token = lease["token"]
print("claimed, token ok")

# 2) dry-run: compute/verify BEFORE any shared file write
current = SESSIONS.read_text(encoding="utf-8")
old_lines = current.count("\n")
new_content = ENTRY if ENTRY.endswith("\n") else ENTRY + "\n"
new_content += current
tmp = ROOT / "scratch" / "c_sessions_dryrun_131853.md"
tmp.write_text(new_content, encoding="utf-8")
lines = new_content.count("\n")
first = new_content.split("\n", 1)[0]
assert first.startswith("- 最后更新：%s" % SIGN), "first line signature mismatch"
assert old_lines + 1 == lines, "line count: expected %d got %d" % (old_lines + 1, lines)
assert new_content.split("\n", 2)[1] == current.split("\n", 1)[0], "second line must be old first line"
assert PREV in new_content, "previous 13:13 entry lost in dry run"
print("dry-run verified: lines %d -> %d" % (old_lines, lines))

# 3) single last write via run wrapper
p = sh(["python3", str(RUNTIME), "run", "--project", str(ROOT), "--role", "C", "--token", token,
        "--", "cp", str(tmp), str(SESSIONS)])
if p.returncode != 0:
    sys.exit("RUN_FAIL rc=%d out=%s err=%s" % (p.returncode, p.stdout[-400:], p.stderr[-400:]))
written = SESSIONS.read_text(encoding="utf-8")
assert written == new_content, "post-write content mismatch"
assert written.count("\n") == lines, "post-write line count mismatch"
print("sessions written and verified")
tmp.unlink()

# 4) event
p = sh(["python3", str(RUNTIME), "event", "--project", str(ROOT), "--role", "C", "--token", token,
        "--event-id", "c-poll-20261012-131853-nochange", "--task", "NONE", "--attempt", "0",
        "--status", "POLL_NO_CHANGE",
        "--summary", "C 巡检 13:18:53：13:13:53 后 C 范围零新增、无 C 新派单（inbox/3号 实测空）；新增=协调者 r79 T07A attempt-1 OCR 裁决 ACCEPT_REPORT_WITH_REWORK（bags.html 2 处 medium）+ 2号 attempt-2-r1 派单 13:15/ACK 13:19 已开工（2号范围）+ ocr 账/TODO 刷新；main 453da0c=origin 双核、wt-03b 6f1a9ad 干净、ps 0；leases B.json/COORDINATOR.json 在途未到期不接管；保持空闲待派单",
        "--evidence", "sessions/C.md 13:20 条目; find -newermt 13:13:53; inbox/coordinator/TASK-07A/attempt-1-ocr-ruling-20261012.md; inbox/2号/TASK-07A/attempt-2-r1-ack.md; rev-parse 双核",
        "--next", "等协调者派单；T07A attempt-2-r1 收口链在 2号/协调者范围"])
if p.returncode != 0:
    sys.exit("EVENT_FAIL rc=%d out=%s err=%s" % (p.returncode, p.stdout[-400:], p.stderr[-400:]))
print("event written")

# 5) release
p = sh(["python3", str(RUNTIME), "release", "--project", str(ROOT), "--role", "C", "--token", token])
if p.returncode != 0:
    sys.exit("RELEASE_FAIL rc=%d out=%s err=%s" % (p.returncode, p.stdout[-400:], p.stderr[-400:]))
print("released OK")