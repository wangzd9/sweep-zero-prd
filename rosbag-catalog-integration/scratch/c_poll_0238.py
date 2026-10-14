#!/usr/bin/env python3
import json, subprocess, sys, datetime

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261012-023853"
EVENT_ID = "C-poll-20261012-023853-nochange"

def run(args):
    r = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
    return r.returncode, r.stdout, r.stderr

# 1. claim (skip if lease already held by this same owner from crashed prior run)
import pathlib
lease_file = pathlib.Path(ROOT)/"inbox/control/runtime/leases/C.json"
existing = None
if lease_file.exists():
    try:
        existing = json.loads(lease_file.read_text())
    except Exception:
        existing = None
if existing and existing.get("owner") == OWNER:
    token = existing.get("token")
    print("TOKEN_REUSED_SAME_OWNER:", bool(token))
else:
    rc, out, err = run(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
    if rc != 0:
        print("CLAIM_FAILED", out, err)
        sys.exit(1)
    ld = json.loads(lease_file.read_text())
    assert ld.get("owner") == OWNER, f"owner mismatch: {ld.get('owner')} vs {OWNER}"
    token = ld.get("token")
    print("TOKEN_PARSED:", bool(token))

# 2. append sessions line (append only, never overwrite)
now = "2026-10-12 02:38 +08:00"
line = (f"- 最后更新：{now}（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T02:38:53+08:00）、legacy_busy 空；"
        f"02:34（前条 C 巡检写入）后共享根 C 范围零新增：`inbox/3号/`、`inbox/coordinator/` 与根两级业务文件 find -newermt 核实均为空，**无 C 新派单**（TASK-03B 名下全部派单已收口）；"
        f"main HEAD `453da0c`=origin/main 双核一致（wt-03b rev-parse 实测，非 C 交付）、wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 实测 0）、ps 实测无 C 在途业务进程（wt-03b/scene-03b/t03b/task-03b 命中 0）；"
        f"leases 实测无 size>0 在途租约（find 核实为空，A/B 前条已释放维持）；P0 已收口（协调者 02:08 裁决）C 保持空闲待派单（TASK-11 待用户独立授权，生产门禁未放行）；"
        f"前一条 02:34 巡检见下）\n")
tmpf = ROOT + "/scratch/c_poll_0238_line.txt"
with open(tmpf, "w") as f:
    f.write(line)
rc, out, err = run(["python3", RUNTIME, "run", "--project", ROOT, "--role", "C", "--token", str(token), "--",
                    "cat", tmpf, ">>", ROOT + "/sessions/C.md"])
print("SESSIONS_APPEND rc=", rc, out.strip()[:200], err.strip()[:200])

# 3. event
summary = "P0收口后空转巡检第6轮：02:34后C范围零新增；inbox/3号与inbox/coordinator无C新派单；main 453da0c=origin双核一致、wt-03b 6f1a9ad干净、无C在途进程、leases无在途租约；保持空闲待派单"
rc, out, err = run(["python3", RUNTIME, "event", "--project", ROOT, "--role", "C", "--token", str(token),
                    "--event-id", EVENT_ID, "--task", "NONE", "--attempt", "0", "--status", "POLL_NO_CHANGE",
                    "--summary", summary,
                    "--evidence", "sessions/C.md 顶部巡检行；find -newermt 02:34 inbox/3号、inbox/coordinator、根两级均为空；wt-03b rev-parse 453da0c/6f1a9ad；ps 0 命中",
                    "--next", "保持空闲待派单；如后续涉C将另行派单"])
print("EVENT rc=", rc, out.strip()[:200], err.strip()[:200])

# 4. release
rc, out, err = run(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", str(token)])
print("RELEASE rc=", rc, out.strip()[:200], err.strip()[:200])