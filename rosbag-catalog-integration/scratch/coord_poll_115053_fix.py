#!/usr/bin/env python3
# 协调者 11:50 巡检续跑：recover 旧租约(claim owner 115053) -> 重新 claim -> event -> release
import subprocess, sys, json, os, time

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OLD_OWNER = "cron-poll-14ae4556629a-115053"
NEW_OWNER = "cron-poll-14ae4556629a-115053b"

# 证据：上一脚本的失败输出（token 解析错误导致 release 未执行）
ev_dir = ROOT + "/scratch"
ev_path = ev_dir + "/coord_115053_stale_token_evidence.txt"
with open(ev_path, "w", encoding="utf-8") as f:
    f.write("coord_poll_115053.py 运行输出（2026-10-11T11:52:39+08:00 claim 成功，event/release 因 token 取到整块 JSON 失败）：\n")
    f.write('claim: {"claimed": true, "owner": "cron-poll-14ae4556629a-115053", "token": "e8dea42a12e9428eafe78093048835af", ...}\n')
    f.write("COORDINATOR.md: checkpoint prepended\n")
    f.write("HANDOFF.md: checkpoint prepended\n")
    f.write('event: {"error": "Missing, stale or expired writer token; recheck owner before continuing"}\n')
    f.write('release: {"error": "Missing, stale or expired writer token; recheck owner before continuing"}\n')
print("evidence written:", ev_path)

def run(args, label):
    r = subprocess.run([sys.executable, RUNTIME] + args, capture_output=True, text=True)
    print(label + ":", (r.stdout or r.stderr).strip()[:400])
    return r

run(["recover", "--project", ROOT, "--role", "COORDINATOR", "--owner", OLD_OWNER,
     "--confirmed-stopped", "--evidence", ev_path], "recover")
time.sleep(1)

r = run(["claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", NEW_OWNER], "claim")
if r.returncode != 0:
    sys.exit(1)
# token 是 JSON 里的字段
try:
    token = json.loads(r.stdout.strip())["token"]
except Exception:
    token = r.stdout.strip().splitlines()[-1].strip()
print("token parsed:", token[:8] + "...")

event = {
    "event_id": "coord-poll-20261011-115053-nochange",
    "occurred_at": "2026-10-11T11:50:53+08:00",
    "recorded_at": "2026-10-11T11:53:30+08:00",
    "role": "COORDINATOR",
    "task": "TASK-08",
    "attempt": "0",
    "status": "IDLE",
    "summary": "11:45 后零业务变化：main HEAD b7cee07=origin/main 复核一致；唯一新增=B 11:42/C 11:48 例行 IDLE 心跳（非业务）；强复审 R2I-20261010-06 结果文件仍不存在，保持 READY_FOR_USER_TRIGGER 等用户手动触发；A/B/C/TESTER 全空闲、无在途 ocr/pytest",
    "evidence": "git rev-parse HEAD=origin/main=b7cee07c71adf8fcfec5465247170f45f9c648e9; events/B d44cabdc (IDLE_WAITING); events/C dedc7d2e (IDLE); reviews/strongmodel 无 R2I-20261010-06-result.md（目录最新 11:22 pack target b7cee07）; ps 仅 wxocr 桌面进程",
    "next": "下轮核强复审结果文件与事件；06 聚合放行=强复审 PASS → 03/05/06 聚合 DONE → TASK-08 联调派单",
}
r2 = run(["event", "--project", ROOT, "--role", "COORDINATOR", "--token", token,
          "--event-id", event["event_id"], "--task", event["task"],
          "--attempt", event["attempt"], "--status", event["status"],
          "--summary", event["summary"], "--evidence", event["evidence"],
          "--next", event["next"]], "event")

r3 = run(["release", "--project", ROOT, "--role", "COORDINATOR", "--token", token], "release")
sys.exit(r3.returncode)