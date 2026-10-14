#!/usr/bin/env python3
import json, subprocess, sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261012-005853"

def run(*args):
    p = subprocess.run([sys.executable, RUNTIME, *args], capture_output=True, text=True, timeout=120)
    return p

out = run("claim", "--project", ROOT, "--role", "C", "--owner", OWNER)
print("claim rc", out.returncode)
if out.returncode != 0:
    print(out.stdout, out.stderr)
    sys.exit(1)
data = json.loads(out.stdout[out.stdout.index("{"):])
token = data["token"]
print("claim ok, token len", len(token))

ev = run("event", "--project", ROOT, "--role", "C", "--token", token,
         "--event-id", "C-poll-20261012-005853-nochange",
         "--task", "NONE", "--attempt", "0", "--status", "NO_CHANGE",
         "--summary", "00:49:55后共享根新增均为非C范围：2号t10-defect2已合入main a77aa45（d4719f6，ocr.lock T10D2-r1 COMPLETE_0_FINDINGS，HANDOFF 00:45检查点收口链）、1号t10-defect1已合入277e40f、TESTER nochange事件00:57、协调者00:51巡检在途（leases COORDINATOR.json非C）；inbox/3号无新文件（最新仍10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B全部派单已收口）、inbox/coordinator无面向3号新单；main a77aa45=origin/main双核一致（rosbag-catalog rev-parse，两笔TASK-10返修均已合入，非C交付）；wt-03b HEAD=6f1a9ad干净（status --porcelain排除.venv为空）；ps无C在途业务进程；保持空闲待派单（TASK-10 E2E复跑/DONE为协调者/测试者范围）",
         "--evidence", "sessions/C.md", "--next", "继续5分钟巡检")
print("event rc", ev.returncode)
if ev.returncode != 0:
    print(ev.stdout, ev.stderr)
    sys.exit(1)

rel = run("release", "--project", ROOT, "--role", "C", "--token", token)
print("release rc", rel.returncode)
if rel.returncode != 0:
    print(rel.stdout, rel.stderr)