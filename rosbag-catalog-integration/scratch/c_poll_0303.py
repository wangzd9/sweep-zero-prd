#!/usr/bin/env python3
"""C 巡检 03:03: claim -> event(nochange) -> sessions append -> release. Token via full JSON parse."""
import json, subprocess, sys, datetime

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261012-030353"

def sh(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, **kw)

# 1. claim (multi-line JSON output: parse whole output as JSON, never tail/grep)
r = sh(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
print("claim rc:", r.returncode)
out = r.stdout.strip()
try:
    data = json.loads(out)
except json.JSONDecodeError:
    # try to locate the JSON object within output
    start = out.find("{")
    data = json.loads(out[start:]) if start >= 0 else None
    if data is None:
        print("claim parse FAILED:", out, r.stderr)
        sys.exit(1)
token = data.get("token") or data.get("lease_token")
if not token:
    print("no token in claim output:", out, r.stderr)
    sys.exit(1)
print("claim ok, token acquired (not printed)")

# 2. event nochange
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
ev = sh(["python3", RUNTIME, "event", "--project", ROOT, "--role", "C", "--token", token,
         "--event-id", "C-poll-20261012-030353-nochange",
         "--occurred-at", ts,
         "--task", "NONE", "--attempt", "0", "--status", "IDLE_WAITING",
         "--summary", "P0 收口后空转巡检：02:58:53 轮事件落盘后共享根零业务新增；inbox/3号 最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED、inbox/coordinator 最新仍 02:08 e2e-reverify-v2 decision，均无 C 新派单；main HEAD 453da0c=origin/main 双核一致；wt-03b HEAD 6f1a9ad 干净（排除 .venv 0）；ps 无 C 在途业务进程；leases 无 size>0 在途租约",
         "--evidence", "scratch/c_poll_0303.py",
         "--next", "保持空闲待派单；如后续涉 C 由协调者另行派单"])
print("event rc:", ev.returncode, ev.stderr[:200] if ev.returncode else "")

# 3. sessions append (run wrapper, APPEND only via heredoc >>, never >)
line = ("- 最后更新：2026-10-12 03:03 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T03:03:53+08:00）、legacy_busy 空；02:58:53 轮事件落盘（events/C/b3037039…，head 核实=nochange IDLE_WAITING）后共享根**零业务新增**（find -newermt 02:53:53 排除 sessions/events/ticks/leases/scratch/nvidia-cleanup 核实为空；02:53:53 前事实由上轮 02:53 巡检全量核实）；`inbox/3号/` 最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED、`inbox/coordinator/` 最新仍 02:08 e2e-reverify-v2 decision（find 核实 02:53:53 后均无新文件），**无 C 新派单**；main HEAD `453da0c`=origin/main 双核一致（rosbag-catalog rev-parse 实测）、wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 实测为空）、ps 实测无 C 在途业务进程（wt-03b/scene-03b/t03b/task-03b 命中为空）、leases 无 size>0 在途租约（find 实测为空）；C 本轮 owner `{owner}` claim 成功（token 整体 JSON 解析），事件 `C-poll-20261012-030353-nochange` 落盘后 release；**保持空闲待派单**（P0 已收口，如后续涉 C 将另行派单）。前一条 02:53 巡检见下）".replace("{owner}", OWNER))
append_cmd = f"cat >> {ROOT}/sessions/C.md <<'EOF'\n{line}\nEOF"
run = sh(["python3", RUNTIME, "run", "--project", ROOT, "--role", "C", "--token", token, "--", "/bin/bash", "-c", append_cmd])
print("sessions append rc:", run.returncode, run.stderr[:300] if run.returncode else "")
tail = sh(["bash", "-c", f"head -1 {ROOT}/sessions/C.md"])
print("sessions head-1 starts:", tail.stdout[:80])

# 4. release
rel = sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token])
print("release rc:", rel.returncode, rel.stderr[:200] if rel.returncode else "")