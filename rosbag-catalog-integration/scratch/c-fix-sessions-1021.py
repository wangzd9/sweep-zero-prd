#!/usr/bin/env python3
"""Fix sessions/C.md: collapse lines 2-8 (split by lease JSON newlines) into one line."""
import os
import subprocess

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261011-101853"
sessions_path = f"{ROOT}/sessions/C.md"

# claim + get token
r = subprocess.run(
    f"python3 {RUNTIME} claim --project {ROOT} --role C --owner {OWNER}",
    shell=True, capture_output=True, text=True
)
rc, out = r.returncode, (r.stdout + r.stderr).strip()
print("CLAIM:", rc, out[:200])
# token is persisted in the lease file after claim
token = ""
lease_path = f"{ROOT}/inbox/control/runtime/leases/C.json"
if os.path.exists(lease_path):
    import json as _json
    with open(lease_path) as fh:
        ld = _json.load(fh)
    if ld.get("owner") == OWNER:
        token = ld.get("token", "")
print("TOKEN:", repr(token[:30]))

with open(sessions_path) as f:
    lines = f.readlines()

# lines[0] is marker, lines[1] is start of the broken report (index 1 in 0-based)
# Find the line that starts with "- 最后更新：2026-10-11 10:21"
# and merge until the line that ends with "前一条 10:15 巡检见下）\n"
start = None
end = None
for i, l in enumerate(lines):
    if "最后更新：2026-10-11 10:21" in l and l.startswith("- "):
        start = i
    if start is not None and "前一条 10:15 巡检见下）" in l:
        end = i
        break

if start is None or end is None:
    print(f"start={start} end={end} — aborting, could not locate broken block")
else:
    merged = "".join(lines[start:end+1]).replace("\n", "")
    # Build the clean lease summary without raw JSON
    clean = (
        f"- 最后更新：2026-10-11 10:21 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T10:18:53+08:00）、"
        f"legacy_busy 空；10:15 后共享根变更=无（find -newermt 10:15:00 排除 scratch/sessions/events/control 核实为空）；"
        f"`inbox/3号/` 最新仍 `inbox/3号/TASK-03B/attempt-4-ocr-rework.md`（ACCEPT_MERGED 已收口），**无 C 新派单**；"
        f"`inbox/coordinator/` 10:15 后无新增（最新 `inbox/coordinator/TASK-06/attempt-5-mysql-e2e-acceptance-decision.md`）；"
        f"main HEAD 仍 `4697be0`（rosbag-catalog rev-parse 核实）、wt-03b HEAD=`6f1a9ad` 干净（仅 .venv untracked）、ps 核实无 C 在途进程；"
        f"leases：C.json 本轮 C 巡检短占用（owner `{OWNER}`，renew 10:21 后 release 结束）、C.lock/TESTER.lock 均 0 字节空文件；"
        f"06 聚合唯一剩余门禁=强复审 R2I-20261010-06（target `4697be0`）等用户手动触发，PASS 后接 TASK-08 联调（届时才可能涉及 C，当前无单）；"
        f"**保持空闲待派单**。前一条 10:15 巡检见下）\n"
    )
    new_lines = lines[:start] + [clean] + lines[end+1:]
    tmp = f"{ROOT}/scratch/c-sessions-fix-1021.md"
    with open(tmp, "w") as f:
        f.writelines(new_lines)
    if token:
        r2 = subprocess.run(
            f"python3 {RUNTIME} run --project {ROOT} --role C --token {token} -- cp {tmp} {sessions_path}",
            shell=True, capture_output=True, text=True
        )
        rc2, out2 = r2.returncode, (r2.stdout + r2.stderr).strip()
        print("WRITE:", rc2, out2[:100])
        r3 = subprocess.run(
            f"python3 {RUNTIME} release --project {ROOT} --role C --token {token}",
            shell=True, capture_output=True, text=True
        )
        rc3, out3 = r3.returncode, (r3.stdout + r3.stderr).strip()
        print("RELEASE:", rc3, out3[:100])
    else:
        with open(sessions_path, "w") as f:
            f.writelines(new_lines)
        print("WRITE: direct (no token)")
    print("DONE")