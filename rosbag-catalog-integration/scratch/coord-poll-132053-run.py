#!/usr/bin/env python3
"""coord poll 132053: claim, append sessions/COORDINATOR.md checkpoint, event, release."""
import subprocess, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "coord-cron-poll-20261011-132053"
EVENT_ID = "coord-poll-20261011-132053-nochange"

def sh(args):
    return subprocess.run(args, capture_output=True, text=True)

r = sh(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER])
sys.stdout.write(r.stdout + r.stderr)
if r.returncode != 0:
    print("CLAIM_FAILED: report-only, no write.")
    sys.exit(2)
token = r.stdout.strip().splitlines()[-1].strip()

p = ROOT + "/sessions/COORDINATOR.md"
text = open(p, encoding="utf-8").read()
ck = """
## 2026-10-11 13:20 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T13:20:53+08:00：13:15 后零业务变化，例行巡检时间更新）
- **13:15 后零业务变化**：main HEAD `65ca0beb0111a2d45065206886d432bd20eb76d0`（= main = origin/main，rev-parse 三核一致）；13:15:53 后共享根新增仅 A 13:17 / B 13:1x / C 13:19 / TESTER 13:20 各角色例行 IDLE 心跳（find -newermt 核实，均报无新派单、强复审 result 仍缺，非业务交付）。
- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**（目录最新 12:31 pack，target `65ca0be`），维持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。
- **06 聚合放行门禁（唯一剩余，不变）**：强复审 PASS 收口即 03/05/06 聚合 DONE → TASK-08 联调派单。
- **角色占用**：A/B/C/TESTER 全空闲（legacy_busy 空，ticks 13:1x–13:20 例行）；无在途 ocr/pytest 业务进程（ps 复核无匹配）；`ocr.lock`(12:28)/`coordinator.lock` 0 字节无他角色在途持有者。
- 本轮控制动作：claim→巡检核查（find -newermt/rev-parse/ps/locks/事件复核）→append 检查点→event→release，**无新派单、无状态变更、无 OCR**。
"""
if "## 2026-10-11 13:20 巡检检查点" not in text:
    open(p, "w", encoding="utf-8").write(text.rstrip("\n") + "\n" + ck)

er = sh(["python3", RUNTIME, "event", "--project", ROOT, "--role", "COORDINATOR",
         "--token", token, "--event-id", EVENT_ID, "--task", "NONE",
         "--attempt", "0", "--status", "NOCHANGE",
         "--summary", "13:20 巡检：13:15 后零业务变化；main 65ca0be 三核一致；强复审 R2I-20261010-06 result 仍缺维持 READY_FOR_USER_TRIGGER；A/B/C/TESTER 全空闲仅例行心跳；无在途 ocr/pytest",
         "--evidence", "sessions/COORDINATOR.md 13:20 checkpoint",
         "--next", "等用户手动触发强复审 R2I-20261010-06 或新交付"])
sys.stdout.write(er.stdout + er.stderr)

rr = sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--token", token])
sys.stdout.write(rr.stdout + rr.stderr)
print("DONE rc_event=", er.returncode, "rc_release=", rr.returncode)