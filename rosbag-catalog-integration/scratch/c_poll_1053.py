#!/usr/bin/env python3
"""C 10:53 poll control: claim -> run(prepend sessions/C.md, dry-run first) -> event -> release."""
import io
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
RUNTIME = Path("/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py")
OWNER = "C-cron-poll-20261012-105353"
ENTRY = (ROOT / "scratch" / "c_entry_1053.md").read_text(encoding="utf-8")
SESSIONS = ROOT / "sessions" / "C.md"
SIGN = "2026-10-12 10:53"
NEXT = "前一条 10:33 巡检见下"

def sh(args):
    p = subprocess.run(args, capture_output=True, text=True)
    return p

# 1) claim, parse token from FULL json output
p = sh(["python3", str(RUNTIME), "claim", "--project", str(ROOT), "--role", "C", "--owner", OWNER])
if p.returncode != 0:
    sys.exit("CLAIM_FAIL rc=%d out=%s err=%s" % (p.returncode, p.stdout[-400:], p.stderr[-400:]))
tok = None
for line in p.stdout.splitlines():
    line = line.strip()
    if line.startswith("{"):
        try:
            tok = json.loads("".join(p.stdout[p.stdout.index("{"):]))
            break
        except Exception:
            pass
token = tok.get("token") if isinstance(tok, dict) else None
if not token:
    # fallback: lease file same-origin
    lease = json.loads((ROOT / "leases" / "C.json").read_text())
    assert lease.get("owner") == OWNER, "lease owner mismatch"
    token = lease["token"]
print("claimed token ok")

# 2) dry-run build against temp target: compute/verify BEFORE any shared file open
current = SESSIONS.read_text(encoding="utf-8")
old_lines = current.count("\n")
new_content = ENTRY if ENTRY.endswith("\n") else ENTRY + "\n"
new_content += current
tmp = ROOT / "scratch" / "c_sessions_dryrun_1053.md"
tmp.write_text(new_content, encoding="utf-8")
lines = new_content.count("\n")
first = new_content.split("\n", 1)[0]
assert first.startswith("- 最后更新：%s" % SIGN), "first line signature mismatch"
assert old_lines + 1 == lines, "line count: expected %d got %d" % (old_lines + 1, lines)
assert new_content.split("\n", 2)[1] == current.split("\n", 1)[0], "second line must be old first line"
# spot signature count: previous 10:33 entry must survive
assert "2026-10-12 10:33" in new_content, "10:33 entry lost in dry run"
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
    "--event-id", "C-poll-20261012-105353-nochange", "--task", "NONE", "--attempt", "0",
    "--status", "POLL_NO_CHANGE",
    "--summary", "C 巡检 10:53:53：10:35:05 后 C 范围零新增、无新派单（新增=前条 C 自身 nochange 事件×2+协调者 r74/r75 空转巡检 B 07A 在途+TESTER 心跳+各角色 sessions/TIMELINE 例行刷新）；补记 10:38 轮另一 C 会话 nochange（事件在盘、规范 sessions 条目缺失）；main 453da0c=origin 双核、wt-03b 6f1a9ad 干净、ps 0、leases 无在途、保持空闲待派单",
    "--evidence", "sessions/C.md 10:53 条目; find -newermt 10:35:00; rev-parse 双核",
    "--next", "等协调者派单；不接管非 C 租约"])
print("event written")

# 5) release
p = sh(["python3", str(RUNTIME), "release", "--project", str(ROOT), "--role", "C", "--token", token])
if p.returncode != 0:
    sys.exit("RELEASE_FAIL rc=%d out=%s err=%s" % (p.returncode, p.stdout[-400:], p.stderr[-400:]))
print("released OK")