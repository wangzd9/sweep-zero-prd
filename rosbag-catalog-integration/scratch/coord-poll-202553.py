#!/usr/bin/env python3
import json, subprocess, datetime, os

R = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-coord-poll-202553"

def sh(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()

rc, out = sh(f"python3 {RUNTIME} claim --project {R} --role COORDINATOR --owner {OWNER}")
print("claim:", rc, out[:300])
if rc != 0:
    print("CLAIM_FAILED — not writing")
    raise SystemExit(0)
m = None
for line in out.splitlines():
    if "token" in line or "TOKEN" in line or '"' in line:
        m = line.strip()
token = None
try:
    # claim may print json with token
    jstart = out.find("{")
    if jstart >= 0:
        j = json.loads(out[jstart:out.rfind("}")+1])
        token = j.get("token")
except Exception as e:
    print("token parse warn:", e)
print("token:", bool(token))

ts = "2026-10-11T20:25:53+08:00"
ckpt = f"""## 2026-10-11 20:26 巡检检查点（cron poll 14ae4556629a，真实 checked_at {ts}：20:22 后零业务变化，TASK-08 DONE 维持收口）

- **20:22 后零业务变化**：main HEAD `0a8ca8a`（= origin/main，rev-parse 双核一致，top1=08 t08c-1 秒精度合入 19:17 已在案）；20:20:53 后共享根业务目录（receipts/test-receipts/reports/inbox/decision/reviews/dispatches）**零新增业务文件**（find -newermt 核实，新增仅各角色 events/ticks 例行心跳）。
- **角色占用**：A/B/C/TESTER 全空闲（B 20:22 nochange 心跳报 TASK-08 DONE 收口、C 20:03 例行 nochange、A 20:07 均无新派单）；`ocr.lock`/`coordinator.lock` 0 字节无在途持有者；leases 仅 C 05:19 / TESTER 12:46 零字节例行租约；ps 无协调侧 ocr/pytest 业务进程（仅 wxocr 桌面）。
- **门禁**：生产启用/真实样本（TASK-09/10/11）维持未放行；TASK-08 DONE 已收口（19:46 decision，收口 2/2 = c3-1→`98f6c88` + t08c-1→`0a8ca8a`，TESTER post-merge 14/14 真 MySQL RC=0）；TASK-10 前置 09 仍 BLOCKED（待用户授权真实坡道样本/VLM），候选重算 **无新派单**。
- 本轮控制动作：claim（`{OWNER}`）→巡检核查（rev-parse 双核/find -newermt/各角色 events 复核/ps/locks/leases）→event+prepend 检查点→release。**无新派单、无合入、无 OCR、无状态变更**。
- **下一步**：维持 5 分钟巡检；等用户授权 TASK-09 真实坡道样本/VLM 后重算 TASK-10 派单；空闲不扩需求。
"""

ev = {
  "event_id": "coord-poll-20261011-202553-nochange",
  "role": "COORDINATOR",
  "task": "NONE",
  "attempt": 0,
  "status": "IDLE_POLL",
  "summary": "20:22 后零业务变化；main 0a8ca8a=origin 双核一致；A/B/C/TESTER 全空闲例行心跳（B 20:22 / C 20:03）；无新派单/合入/OCR；TASK-08 DONE 维持收口",
  "evidence": "sessions/COORDINATOR.md checkpoint 2026-10-11 20:26",
  "next": "维持 5 分钟巡检；等用户授权 TASK-09 真实坡道样本/VLM 后重算 TASK-10 派单",
  "checked_at": ts,
}

def run_step(name, payload):
    # write via runtime run if token available
    cmd = None
    if token:
        cmd = f"python3 {RUNTIME} run --project {R} --role COORDINATOR --token {token} -- "
    if name == "ckpt":
        target = f"{R}/sessions/COORDINATOR.md"
        with open(target) as f: old = f.read()
        with open(target, "w") as f: f.write(ckpt.rstrip() + "\n" + old)
        print("ckpt: written, new size", os.path.getsize(target))
    elif name == "event":
        target = f"{R}/events/COORDINATOR/coord-poll-20261011-202553-nochange.json"
        with open(target, "w") as f: json.dump(ev, f, ensure_ascii=False, indent=2)
        print("event: written", target)

run_step("event", None)
run_step("ckpt", None)

rc2, out2 = sh(f"python3 {RUNTIME} release --project {R} --role COORDINATOR --token {token}" if token
               else f"python3 {RUNTIME} release --project {R} --role COORDINATOR")
print("release:", rc2, out2[:200])