#!/usr/bin/env python3
import json, subprocess, sys, pathlib

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261012-023853"

def run(args):
    r = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
    return r.returncode, r.stdout, r.stderr

# claim (fresh, event already landed under prior token which was released)
rc, out, err = run(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
if rc != 0:
    print("CLAIM_FAILED", out, err)
    sys.exit(1)
lease_file = pathlib.Path(ROOT)/"inbox/control/runtime/leases/C.json"
ld = json.loads(lease_file.read_text())
token = ld.get("token")
assert ld.get("owner") == OWNER
print("TOKEN_PARSED:", bool(token))

# build the sessions line (top-of-file is newest; but run is shell-less exec, so use bash -c to append)
now = "2026-10-12 02:38 +08:00"
line = (f"- 最后更新：{now}（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T02:38:53+08:00）、legacy_busy 空；"
        f"02:34（前条 C 巡检写入）后共享根 C 范围零新增：`inbox/3号/`、`inbox/coordinator/` 与根两级业务文件 find -newermt 核实均为空，**无 C 新派单**（TASK-03B 名下全部派单已收口）；"
        f"main HEAD `453da0c`=origin/main 双核一致（wt-03b rev-parse 实测，非 C 交付）、wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 实测 0）、ps 实测无 C 在途业务进程（wt-03b/scene-03b/t03b/task-03b 命中 0）；"
        f"leases 实测 A/B 无在途租约（前条已释放维持，本轮 claim/release 仅 C 自身短占用）；P0 已收口（协调者 02:08 裁决）C 保持空闲待派单（TASK-11 待用户独立授权，生产门禁未放行）；"
        f"前一条 02:34 巡检见上）\n")

tmpf = ROOT + "/scratch/c_poll_0238_line.txt"
with open(tmpf, "w") as f:
    f.write(line)

# shell-less exec: wrap in bash -c so >> is parsed by the shell
rc, out, err = run(["python3", RUNTIME, "run", "--project", ROOT, "--role", "C", "--token", str(token), "--",
                    "bash", "-c", "cat " + tmpf + " >> " + ROOT + "/sessions/C.md"])
print("SESSIONS_APPEND rc=", rc, out.strip()[:200], err.strip()[:200])

# verify append landed
head = pathlib.Path(ROOT+"/sessions/C.md").read_text().splitlines()[:2]
print("HEAD_LINES:", head)

rc, out, err = run(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", str(token)])
print("RELEASE rc=", rc, out.strip()[:200], err.strip()[:200])