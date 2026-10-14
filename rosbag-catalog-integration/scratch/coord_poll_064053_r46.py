#!/usr/bin/env python3
"""COORDINATOR poll 2026-10-12T06:40:53 P0 收口后常规空转第 46 轮：claim -> 检查点(sessions+HANDOFF) -> event -> release"""
import json, subprocess, sys, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-coord-poll-14ae4556629a-20261012-064053-p0-idle-r46"
EVENT_ID = "coord-poll-20261012-064053-p0-idle-r46"

def run(*args):
    r = subprocess.run([sys.executable, RUNTIME, *args], capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

rc, out = run("claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER)
print("claim rc=%d out=%s" % (rc, out[:500]))
if rc != 0:
    print("CLAIM_FAILED")
    sys.exit(1)

m = None
for line in out.splitlines():
    line = line.strip()
    if line.startswith("{"):
        try:
            m = json.loads(line)
        except Exception:
            pass
token = m.get("token") if m else None
if not token:
    # token 可能在 run 输出里；从 lease 文件兜底
    lease = os.path.join(ROOT, "inbox/control/runtime/leases/COORDINATOR.json")
    try:
        with open(lease) as f:
            token = json.load(f).get("token")
    except Exception:
        token = None
print("token=%s" % (token,))
if not token:
    print("TOKEN_FAILED")
    sys.exit(1)

checkpoint = """## 2026-10-12 06:40 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-12T06:40:53+08:00：P0 收口后常规空转第 46 轮，06:35:53 后零业务变化）

- main `453da0c`=origin/main 双核一致（fetch 后 rev-parse 实测 06:41）；06:35:53 后共享根业务目录（receipts/test-receipts/reports/reviews/decision/dispatches/inbox 各角色含 coordinator）**零新增业务文件**（find -newermt 核实），新增仅 B 06:37/06:40（`b-poll-20261012-063753-nochange-task10-done-p0-idle`）、C 06:40（`C-poll-20261012-063853-nochange`）例行心跳与 sessions 记账，独立复核均报 NO_CHANGE/IDLE_WAITING，非业务交付。
- **角色占用**：A/B/C/TESTER 全空闲（ticks 均在跳：A 06:36:53 / B 06:37:53 / C 06:38:53 / TESTER 06:39:53，COORDINATOR 本轮 06:40:53）；leases 仅 C/TESTER 06:41 各自本轮例行短巡检租约（无业务持有），无在途业务持有者；ps 无 ocr/pytest/t10/t11 业务进程（仅 wxocr 桌面残留）。
- **门禁**：TASK-10 已 DONE（main `453da0c`，P0 收口，停止派发）；TASK-11 生产启用**维持未放行**（待用户独立授权）；TASK-07/12/13/14/15 维持 DEFERRED 不扩；worktree 释放（`wt-04a-t10d3`/`wt-01-t10def1`）属运维收尾，待用户指示不擅动。
- 本轮控制动作：claim（`%s`）→巡检核查（fetch+rev-parse 双核/find -newermt 06:35:53/B+C 心跳 event 独立复核/ticks 五角色/leases/ps）→prepend 检查点（sessions+HANDOFF）+event→release。**无新派单、无合入、无 OCR、无状态变更**。
- **下一步：** 维持 5 分钟常规空转巡检；TASK-11 等用户独立授权不自动推进；空闲不扩需求。
""" % OWNER

# prepend to sessions/COORDINATOR.md
sp = os.path.join(ROOT, "sessions/COORDINATOR.md")
with open(sp, "r", encoding="utf-8") as f:
    old = f.read()
with open(sp, "w", encoding="utf-8") as f:
    f.write(checkpoint + old)
print("sessions/COORDINATOR.md checkpoint prepended, now %d bytes" % os.path.getsize(sp))

# prepend to HANDOFF.md
hp = os.path.join(ROOT, "HANDOFF.md")
with open(hp, "r", encoding="utf-8") as f:
    old = f.read()
with open(hp, "w", encoding="utf-8") as f:
    f.write(checkpoint + old)
print("HANDOFF.md checkpoint prepended, now %d bytes" % os.path.getsize(hp))

event = """# Event: %s

- time: 2026-10-12T06:40:53+08:00
- owner: %s
- role: COORDINATOR
- task: P0 收口后常规空转（TASK-10 DONE 维持，main 453da0c）
- status: NO_CHANGE
- summary: 06:35:53 后共享根业务目录零新增业务文件（find -newermt）；main 453da0c=origin 双核一致；A/B/C/TESTER 全空闲（ticks 均在跳），仅 B/C 例行 nochange 心跳；ps 无 ocr/pytest 业务进程；门禁不变（TASK-11 未放行、07/12/13/14/15 DEFERRED）
- next: 维持 5 分钟常规空转巡检；无新派单、无合入、无 OCR
""" % (EVENT_ID, OWNER)
ep = os.path.join(ROOT, "inbox/events/COORDINATOR", EVENT_ID + ".md")
with open(ep, "w", encoding="utf-8") as f:
    f.write(event)
print("event written: %s" % ep)

rc2, out2 = run("release", "--project", ROOT, "--role", "COORDINATOR", "--token", token)
print("release rc=%d out=%s" % (rc2, out2[:300]))
print("DONE" if rc2 == 0 else "RELEASE_FAILED")
sys.exit(0 if rc2 == 0 else 1)