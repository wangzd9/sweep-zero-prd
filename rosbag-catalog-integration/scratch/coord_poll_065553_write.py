#!/usr/bin/env python3
"""COORDINATOR poll 2026-10-12T06:55:53 P0 收口后常规空转第 48 轮：claim -> 检查点(sessions+HANDOFF) -> event -> release"""
import json, subprocess, sys, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-coord-poll-14ae4556629a-20261012-065553-p0-idle-r48"
EVENT_ID = "coord-poll-20261012-065553-p0-idle-r48"

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

checkpoint = """## 2026-10-12 06:55 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-12T06:55:53+08:00：P0 收口后常规空转第 48 轮，06:45:53 后零业务变化；C 截断恢复抽查**按最新磁盘通过（1 处格式残留，不阻塞）**）

- main `453da0c`=origin/main 双核一致（fetch rc=0 后 rev-parse 实测 06:56）；06:45:53 后共享根业务目录（receipts/test-receipts/reports/reviews/decision/dispatches/inbox 各角色含 coordinator）**零新增业务文件**（find -newermt 核实，biz_new 为空）。
- 新增事件独立复核均为例行 nochange 心跳，非业务交付：A 06:43（`a-poll-20261012-064153-nochange`，POLL_NO_CHANGE，报 main 零前移/开发槽空闲）、B 06:50（`b-poll-20261012-064753-nochange-task10-done-p0-idle`，IDLE_WAITING）、TESTER 06:41/06:46/06:51（`tester-poll-…-nochange`×3，均报双核未变/无 PENDING 派单/无残留进程维持 IDLE）。
- **C `sessions/C.md` 截断恢复抽查（06:47 轮记「不通过」口径已过期，本轮按最新磁盘复核=通过）**：06:45:53 时点实测的 24 行/31571 字节快照为**恢复落盘前瞬间**（06:40:54 并发重建覆盖后、06:46:32 并发会话恢复写入前）；当前磁盘实测 **383 行/378112 字节**（mtime 07:00:07，含 C 06:48 轮 `c_poll_064853` 干跑+cp 重建写后验证 lines 382→383 在案），**06:38 巡检条目内容完整在盘**（末行 383 尾部，`grep 063853` 3 命中，关键签名核对通过：preflight 06:38:53/main 453da0c 双核/wt-03b 6f1a9ad 干净/无 C 新派单/事件 `C-poll-20261012-063853-nochange` 落盘后 release），与幸存事件 `inbox/events/C/C-poll-20261012-063853-nochange.md` 口径一致；**1 处轻微格式残留=06:38 条目与 06:24 条目同行无换行分隔（内容零丢失，不阻塞）**，沿用 05:40 轮 B 恢复抽查同类处置口径；06:47 轮预告的「向 C 派最小返修单」以恢复未落盘为前提，前提已不成立，**不派单不返修**；C 重建方 owner 未定位仅记事件 `C-sessions-truncation-20261012-064054`，不追不阻塞业务。
- **角色占用**：A/B/C/TESTER 全空闲（ticks 均在跳：A 06:51:53 / B 06:52:53 / C 06:52:53 / TESTER 06:54:53，COORDINATOR 本轮 06:55:53）；leases 仅 C（`C-cron-poll-20261012-064853`，exp 07:01:01）/TESTER（`cron-tester-poll-20261012-065453`，exp 07:00:59）各自本轮例行短巡检租约（无业务持有），无在途业务持有者；ps 无 ocr/pytest/t10/t11 业务进程（仅 wxocr 桌面残留）。
- **门禁**：TASK-10 已 DONE（main `453da0c`，P0 收口，停止派发）；TASK-11 生产启用**维持未放行**（待用户独立授权）；TASK-07/12/13/14/15 维持 DEFERRED 不扩；worktree 释放（`wt-04a-t10d3`/`wt-01-t10def1`）属运维收尾，待用户指示不擅动。
- 本轮控制动作：claim（`%s`）→巡检核查（fetch+rev-parse 双核/find -newermt 06:45:53/A+B+TESTER 五例心跳 event 独立复核/C sessions 截断恢复按最新磁盘三核复核/ticks 五角色/leases/ps）→prepend 检查点（sessions+HANDOFF）+event→release。**无新派单、无合入、无 OCR、无业务状态变更**（C 恢复抽查改判=文档完整性核实收口）。
- **下一步：** 维持 5 分钟常规空转巡检；TASK-11 等用户独立授权不自动推进；空闲不扩需求。
""" % OWNER

sp = os.path.join(ROOT, "sessions/COORDINATOR.md")
with open(sp, "r", encoding="utf-8") as f:
    old = f.read()
with open(sp, "w", encoding="utf-8") as f:
    f.write(checkpoint + old)
print("sessions/COORDINATOR.md checkpoint prepended, now %d bytes" % os.path.getsize(sp))

hp = os.path.join(ROOT, "HANDOFF.md")
with open(hp, "r", encoding="utf-8") as f:
    old = f.read()
with open(hp, "w", encoding="utf-8") as f:
    f.write(checkpoint + old)
print("HANDOFF.md checkpoint prepended, now %d bytes" % os.path.getsize(hp))

event = """# Event: %s

- time: 2026-10-12T06:55:53+08:00
- owner: %s
- role: COORDINATOR
- task: P0 收口后常规空转（TASK-10 DONE 维持，main 453da0c）
- status: NO_CHANGE（业务）+ C 截断恢复抽查按最新磁盘通过（格式残留不阻塞，不派返修单）
- summary: 06:45:53 后共享根业务目录零新增业务文件（find -newermt）；main 453da0c=origin 双核一致（fetch rc=0+rev-parse 06:56）；A/B/C/TESTER 全空闲（ticks 06:51:53/06:52:53/06:52:53/06:54:53），新增 5 例 A/B/TESTER nochange 心跳独立复核非业务交付；**C sessions/C.md 截断恢复抽查改判=通过**：06:47 轮「不通过」基于 24 行恢复前瞬间快照（06:40:54 覆盖后、06:46:32 恢复写入前），最新磁盘 383 行/378112 字节、06:38 条目内容完整在盘（末行 383 尾部，grep 063853 计 3 命中，关键签名与幸存事件 C-poll-20261012-063853-nochange 口径一致），1 处格式残留=条目与 06:24 条目同行无换行（内容零丢失不阻塞），返修单前提（恢复未落盘）已不成立不派单；ps 无 ocr/pytest 业务进程；门禁不变（TASK-11 未放行、07/12/13/14/15 DEFERRED）
- evidence: scratch/coord_poll_065553.py 输出（dual_core_match_after_fetch=true, biz_new=[]）+ sessions/C.md wc 383/stat mtime 07:00:07 + grep 063853×3 + tail 末行 06:38 条目在案
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