#!/usr/bin/env python3
import io, json, subprocess, sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261012-062353"
ENTRY_FILE = ROOT + "/scratch/c_poll_062353_entry.txt"
SESSIONS = ROOT + "/sessions/C.md"

def sh(args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=120)
    return p

# 1. claim (lease may already exist from a prior interrupted run: same owner + matching token allowed)
p = sh(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
out = p.stdout.strip()
token = None
try:
    data = json.loads(out)
    token = data.get("token")
except Exception:
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                token = json.loads(line).get("token")
            except Exception:
                pass
if not token:
    # existing lease from earlier partial run: verify owner matches, reuse same-source token
    lease = ROOT + "/inbox/control/runtime/leases/C.json"
    with io.open(lease, "r", encoding="utf-8") as f:
        lj = json.load(f)
    assert lj.get("owner") == OWNER, "lease owner mismatch: %r" % lj.get("owner")
    token = lj.get("token")
print("claim owner", OWNER, "token len", len(token or ""))

# 2. append entry (read temp file, append; all validation BEFORE opening shared file)
entry = io.open(ENTRY_FILE, "r", encoding="utf-8").read()
assert entry.startswith("- 最后更新：2026-10-12 06:24"), "entry signature mismatch"
assert entry.rstrip("\n").endswith("巡检见下"), "entry tail mismatch"

# 3. run wrapper: sessions append (idempotent: skip if already landed from a partial run) + event + release handled after
first = io.open(SESSIONS, "r", encoding="utf-8").readline()
if first.startswith("- 最后更新：2026-10-12 06:24 +08:00"):
    print("entry already appended in partial run; skipping append")
else:
    p = sh(["python3", RUNTIME, "run", "--project", ROOT, "--role", "C", "--token", token, "--",
            "python3", ENTRY_FILE.replace("_entry.txt", "_append.py")])
    print("run rc", p.returncode)
    print(p.stdout[-500:])
    if p.returncode != 0:
        print("run stderr", p.stderr[-500:])

# 4. event (idempotent: skip if already landed)
eid = "C-poll-20261012-062353-nochange"
import os
evdir = os.path.join(ROOT, "events", "C")
ev_exists = any(eid in n for n in os.listdir(evdir)) if os.path.isdir(evdir) else False
if ev_exists:
    print("event already landed; skipping")
else:
    p = sh(["python3", RUNTIME, "event", "--project", ROOT, "--role", "C", "--token", token,
            "--event-id", eid, "--task", "TASK-03B", "--attempt", "0", "--status", "POLL_NO_CHANGE",
            "--summary", "06:23:53巡检：06:13:53 后共享根新增均为非 C 范围（HANDOFF 06:21:42=协调者 06:20:53 空转第 42 轮检查点+五角色 ticks）；inbox/3号、inbox/coordinator 无新文件，无 C 新派单；main 453da0c=origin 双核一致，wt-03b 6f1a9ad 干净，无 C 在途业务进程，leases 无在途；保持空闲待派单",
            "--evidence", "sessions/C.md", "--next", "等协调者派单"])
    print("event rc", p.returncode, (p.stdout or "")[-300:], (p.stderr or "")[-300:])

# 5. release
p = sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token])
print("release rc", p.returncode, (p.stdout or "")[-200:], (p.stderr or "")[-200:])