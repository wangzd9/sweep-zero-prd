import json, subprocess, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RT = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-coord-poll-20261012-013553"

def sh(args):
    r = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
    out = r.stdout.strip()
    if r.returncode != 0:
        raise SystemExit(f"CMD FAILED rc={r.returncode}: {' '.join(args[:4])}\n{r.stdout}\n{r.stderr}")
    return out

token = json.loads(sh(["python3", RT, "claim", "--project", ".", "--role", "COORDINATOR", "--owner", OWNER]))["token"]
try:
    line = ("| 巡检 2026-10-12 01:35 (cron poll, checked_at 2026-10-12T01:35:53+08:00 preflight): "
            "no new business change vs 01:25 checkpoint. B t10-defect3 still coding in-flight "
            "(wt-04a-t10d3: 2 app files changed +31/-10 uncommitted, last mtime 01:24:13, "
            "silence ~13min = single observation round, below 3-round stall-alert threshold); "
            "main a77aa45 == origin/main double-check; no new receipts/dispatch/merge; "
            "leases B+TESTER in-flight by other roles (not expired, no takeover); "
            "ocr.lock holds the closed 00:56 batch record (no active holder). "
            "TASK-10 stays RUNNING. closure chain: B delivers -> mech verify -> serial OCR -> merge -> TESTER rerun v2. "
            "No new dispatch, no merge, no OCR started this round.\n")
    ctrl = ("| control actions: claim " + OWNER + " -> read-only checks "
            "(rev-parse double-check, wt-04a-t10d3 git diff --stat + stat mtime, ps, locks, find newermt 01:25) "
            "-> poll line appended -> event -> release.\n")
    sp = sh(["python3", RT, "run", "--project", ".", "--role", "COORDINATOR", "--token", token,
             "--", "bash", "-c",
             f"cd {ROOT} && printf '%s%s' {json.dumps(line)} {json.dumps(ctrl)} "
             f"| cat - sessions/COORDINATOR.md > /tmp/coord_013553.md && cp /tmp/coord_013553.md sessions/COORDINATOR.md && echo APPENDED"])
    ev = sh(["python3", RT, "event", "--project", ".", "--role", "COORDINATOR", "--token", token,
             "--event-id", "coord-poll-20261012-013553-nochange-t10defect3-running",
             "--task", "TASK-10", "--attempt", "t10-defect3-publish-bounds/1",
             "--status", "RUNNING",
             "--summary", "01:25 checkpoint since: zero business change; B t10-defect3 coding in-flight (wt-04a-t10d3 2 files +31/-10 uncommitted, last mtime 01:24); main a77aa45 unchanged",
             "--evidence", "inbox/sessions/COORDINATOR.md 01:35 poll line + wt-04a-t10d3 git diff --stat/stat mtime measured",
             "--next", "await B delivery receipt -> mech verify -> serial OCR -> merge -> TESTER rerun v2; silence 3 straight rounds triggers stall alert"])
    rel = sh(["python3", RT, "release", "--project", ".", "--role", "COORDINATOR", "--token", token])
    print("APPENDED:", sp)
    print("EVENT:", ev[:200])
    print("RELEASE:", rel[:120])
finally:
    pass