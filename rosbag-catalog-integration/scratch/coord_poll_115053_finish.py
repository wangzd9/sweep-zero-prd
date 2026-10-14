#!/usr/bin/env python3
# 协调者 11:50 巡检收尾：同一 owner 匹配 token，补 event + release
import subprocess, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
TOKEN = "e8dea42a12e9428eafe78093048835af"

def run(args, label):
    r = subprocess.run([sys.executable, RUNTIME] + args, capture_output=True, text=True)
    print(label + ":", (r.stdout or r.stderr).strip()[:300])
    return r

event = {
    "event_id": "coord-poll-20261011-115053-nochange",
    "occurred_at": "2026-10-11T11:50:53+08:00",
    "recorded_at": "2026-10-11T11:53:50+08:00",
    "role": "COORDINATOR",
    "task": "TASK-08",
    "attempt": "0",
    "status": "IDLE",
    "summary": "11:45 后零业务变化：main HEAD b7cee07=origin/main 复核一致；唯一新增=B 11:42/C 11:48 例行 IDLE 心跳（非业务）；强复审 R2I-20261010-06 结果文件仍不存在，保持 READY_FOR_USER_TRIGGER 等用户手动触发；A/B/C/TESTER 全空闲、无在途 ocr/pytest",
    "evidence": "git rev-parse HEAD=origin/main=b7cee07c71adf8fcfec5465247170f45f9c648e9; events/B d44cabdc (IDLE_WAITING); events/C dedc7d2e (IDLE); reviews/strongmodel 无 R2I-20261010-06-result.md（目录最新 11:22 pack target b7cee07）; ps 仅 wxocr 桌面进程",
    "next": "下轮核强复审结果文件与事件；06 聚合放行=强复审 PASS → 03/05/06 聚合 DONE → TASK-08 联调派单",
}
r2 = run(["event", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN,
          "--event-id", event["event_id"], "--task", event["task"],
          "--attempt", event["attempt"], "--status", event["status"],
          "--summary", event["summary"], "--evidence", event["evidence"],
          "--next", event["next"]], "event")

r3 = run(["release", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN], "release")
sys.exit(r3.returncode)