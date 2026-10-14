import subprocess

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261011-164353"

def run(args, **kw):
    r = subprocess.run(["python3", RUNTIME] + args, capture_output=True, text=True, **kw)
    return r

r0 = run(["claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
print("CLAIM_RC", r0.returncode, r0.stdout[-300:], r0.stderr[-300:])
import json
token = json.loads(r0.stdout)["token"]

r1 = run(["event", "--project", ROOT, "--role", "C", "--token", token,
          "--event-id", "C-poll-20261011-164353-nochange",
          "--task", "TASK-08", "--attempt", "1", "--status", "IDLE",
          "--summary", "16:36:30后共享根无C范围新增；inbox/3号与inbox/coordinator无新单；main f9bafb0、wt-03b 6f1a9ad干净；无C在途进程；leases无size>0在途",
          "--evidence", "find -newermt 16:36:30 共享根核实为空；rosbag-catalog rev-parse 核实",
          "--next", "等协调者对TASK-08 C1/C2/C3-lineage回派裁决；保持空闲待派单"])
print("EVENT_RC", r1.returncode, r1.stdout[-300:], r1.stderr[-300:])

sessions_path = ROOT + "/sessions/C.md"
line = ("- 最后更新：2026-10-11 16:44 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T16:43:53+08:00）、legacy_busy 空；"
        "16:36:30 后共享根无新增文件（find -newermt 排除 sessions/events/inbox-control/ticks/scratch/.git 核实为空）；"
        "`inbox/3号/` 无新文件（find -printf 核实仍仅 TASK-03B 已收口目录，最新 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED）、"
        "`inbox/coordinator/` 无面向 3号 新单（find -printf 核实最新仍 15:48 TASK-05 i1-1 decision，1号范围），**无 C 新派单**；"
        "main HEAD 仍 `f9bafb0`（rosbag-catalog rev-parse 核实 main=HEAD 一致）、wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 排除 .venv 核实为空）、"
        "ps 核实无 C 在途进程；leases 无 size>0 在途租约（find -size +0c 核实为空）；"
        "C 本轮短占用 owner `C-cron-poll-20261011-164353`，控制动作结束释放，事件 `C-poll-20261011-164353-nochange` 已落盘；"
        "TASK-08 attempt-1 已交付 REVIEW_PENDING（2号范围）待协调者裁决 C1/C2/C3-lineage 回派，**当前无 C 单**；**保持空闲待派单**。前一条 16:40 巡检见下）\n")
with open(sessions_path, encoding="utf-8") as f:
    content = f.read()
content = line + content
with open(sessions_path, "w", encoding="utf-8") as f:
    f.write(content)
print("SESSIONS_WRITTEN", len(content))

r2 = run(["release", "--project", ROOT, "--role", "C", "--token", token])
print("RELEASE_RC", r2.returncode, r2.stdout[-200:], r2.stderr[-200:])