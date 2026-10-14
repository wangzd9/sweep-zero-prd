#!/usr/bin/env python3
# 协调者 11:50 巡检：claim -> prepend 检查点(sessions+HANDOFF) -> event -> release
import subprocess, sys, json, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-poll-14ae4556629a-115053"
SESSION = ROOT + "/sessions/COORDINATOR.md"
HANDOFF = ROOT + "/HANDOFF.md"

CKPT = """## 2026-10-11 11:50 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T11:50:53+08:00：11:45 后零业务变化）
- **11:45 后零业务变化**：main HEAD `b7cee07c71adf8fcfec5465247170f45f9c648e9`（= origin/main，rev-parse 双核一致）；11:45:53 后业务目录新增仅 B 11:42 / C 11:48 两条例行 IDLE 心跳（`d44cabdc…`/`dedc7d2e…`，均报无新派单、强复审 result 仍缺，非业务交付）。
- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**（目录最新 11:22 仅 pack，target `b7cee07`），保持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。
- **06 聚合放行门禁（唯一剩余，不变）**：强复审 R2I-20261010-06 → PASS 收口即 03/05/06 聚合 DONE → TASK-08 联调派单。
- **角色占用**：A/B/C/TESTER 全空闲（legacy_busy 空）；无在途 ocr/pytest 业务进程（ps 复核仅 wxocr 桌面进程）；`ocr.lock`/`coordinator.lock` 0 字节无他角色在途持有者。
- 本轮控制动作：claim→巡检核查（find -newermt/rev-parse/ps/lock/event 复核）→event 落盘（`coord-poll-20261011-115053-nochange`）→prepend 检查点（sessions+HANDOFF）→release，**无新派单、无合入、无状态变更**。
"""

r = subprocess.run([sys.executable, RUNTIME, "claim", "--project", ROOT,
                   "--role", "COORDINATOR", "--owner", OWNER],
                  capture_output=True, text=True)
out = (r.stdout or r.stderr).strip()
print("claim:", out)
if r.returncode != 0:
    sys.exit(1)
token = out.splitlines()[-1].strip()
if not token or "error" in out.lower():
    sys.exit(2)

def prepend_once(path, header):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if CKPT.splitlines()[0] in content:
        print(f"{os.path.basename(path)}: checkpoint already present, skip")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(CKPT + content)
    print(f"{os.path.basename(path)}: checkpoint prepended")

prepend_once(SESSION, SESSION)
prepend_once(HANDOFF, HANDOFF)

event = {
    "event_id": "coord-poll-20261011-115053-nochange",
    "occurred_at": "2026-10-11T11:50:53+08:00",
    "recorded_at": "2026-10-11T11:51:30+08:00",
    "role": "COORDINATOR",
    "task": "TASK-08",
    "attempt": "0",
    "status": "IDLE",
    "summary": "11:45 后零业务变化：main HEAD b7cee07=origin/main 复核一致；唯一新增=B 11:42/C 11:48 例行 IDLE 心跳（非业务）；强复审 R2I-20261010-06 结果文件仍不存在，保持 READY_FOR_USER_TRIGGER 等用户手动触发；A/B/C/TESTER 全空闲、无在途 ocr/pytest",
    "evidence": "git rev-parse HEAD=origin/main=b7cee07c71adf8fcfec5465247170f45f9c648e9; events/B d44cabdc (IDLE_WAITING); events/C dedc7d2e (IDLE); reviews/strongmodel 无 R2I-20261010-06-result.md（目录最新 11:22 pack target b7cee07）; ps 仅 wxocr 桌面进程",
    "next": "下轮核强复审结果文件与事件；06 聚合放行=强复审 PASS → 03/05/06 聚合 DONE → TASK-08 联调派单",
}
r2 = subprocess.run([sys.executable, RUNTIME, "event", "--project", ROOT,
                    "--role", "COORDINATOR", "--token", token,
                    "--event-id", event["event_id"], "--task", event["task"],
                    "--attempt", event["attempt"], "--status", event["status"],
                    "--summary", event["summary"], "--evidence", event["evidence"],
                    "--next", event["next"]],
                   capture_output=True, text=True)
print("event:", (r2.stdout or r2.stderr).strip())

r3 = subprocess.run([sys.executable, RUNTIME, "release", "--project", ROOT,
                    "--role", "COORDINATOR", "--token", token],
                   capture_output=True, text=True)
print("release:", (r3.stdout or r3.stderr).strip())
sys.exit(r3.returncode)