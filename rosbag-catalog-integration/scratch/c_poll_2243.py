#!/usr/bin/env python3
import json, subprocess, sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261011-224353"

def rt(*args):
    r = subprocess.run([sys.executable, RUNTIME, *args], capture_output=True, text=True)
    return r

r = rt("claim", "--project", ROOT, "--role", "C", "--owner", OWNER)
if r.returncode != 0:
    print("claim failed", r.stdout, r.stderr)
    sys.exit(1)
token = json.loads(r.stdout).get("token")
claimed = json.loads(r.stdout).get("claimed", True)
print("claim rc=0 claimed=", claimed, "token ok" if token else "NO TOKEN")

session_line = (
    "- 最后更新：2026-10-11 22:43 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T22:43:53+08:00）、legacy_busy 空；"
    "22:41（前条巡检写入 `sessions/C.md`）后共享根零新增（find -newermt 22:41 排除 sessions/events/ticks/leases/scratch/control 核实为空）；"
    "`inbox/3号/` 无新文件（find 核实最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、"
    "`inbox/coordinator/` 21:57 后无新增（find 核实最新仍 21:57:39 TASK-09 post-merge decision，测试者/协调者范围，非 C），**无 C 新派单**；"
    "main HEAD `ca8730d`=origin/main 双核一致（rosbag-catalog rev-parse 核实）、"
    "wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 排除 .venv 核实为空）、ps 核实无 C 在途业务进程；"
    "leases 无 size>0 在途租约（find 核实为空）；C 本轮 owner `" + OWNER + "` claim 22:44，"
    "事件 `C-poll-20261011-224353-nochange` 落盘，控制动作结束释放；**保持空闲待派单**。前一条 22:38 巡检见下\n"
)

sp = rt("run", "--project", ROOT, "--role", "C", "--token", token, "--",
        "python3", ROOT + "/scratch/c_poll_2243_session_write.py")
print("session write rc=", sp.returncode, sp.stderr.strip()[:300])

ep = rt("event", "--project", ROOT, "--role", "C", "--token", token,
        "--event-id", "C-poll-20261011-224353-nochange",
        "--task", "none", "--attempt", "-", "--status", "NO_CHANGE",
        "--summary", "22:43 巡检零变化：22:41 后共享根零新增，inbox/3号 最新仍 10-10 00:58 已收口，无 C 新派单",
        "--evidence", "sessions/C.md 22:43 行",
        "--next", "保持空闲待派单，继续 5 分钟巡检")
print("event rc=", ep.returncode, ep.stdout.strip()[:200], ep.stderr.strip()[:200])

rp = rt("release", "--project", ROOT, "--role", "C", "--token", token)
print("release rc=", rp.returncode, rp.stdout.strip()[:100], rp.stderr.strip()[:200])