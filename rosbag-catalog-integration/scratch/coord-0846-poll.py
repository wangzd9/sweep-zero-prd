#!/usr/bin/env python3
"""coord 08:46 poll: claim -> prepend checkpoint -> event -> release (scripted per protocol)."""
import subprocess, sys, json

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-poll-coord-20261011-084553"

def sh(args):
    p = subprocess.run(args, capture_output=True, text=True)
    out = (p.stdout or "")
    err = (p.stderr or "")
    if p.returncode != 0:
        print("FAIL", "".join(args), "RC=", p.returncode)
        print("OUT:", out[:1500])
        print("ERR:", err[:1500])
        sys.exit(1)
    return out

# 1) claim -> JSON
out = sh(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "COORDINATOR",
          "--owner", OWNER, "--ttl", "120"])
data = json.loads(out)
if not data.get("claimed"):
    print("CLAIM BUSY:", out)
    sys.exit(2)
token = data["token"]
print("claimed, token len", len(token))

# 2) prepend checkpoint
ckpt = """## 2026-10-11 08:46 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T08:45:53+08:00）
- **零业务变化**：main HEAD `6d30a6844844131649042686c8d2039cd33ecce5`（= origin/main，/home/wang/work/rosbag-catalog rev-parse 双核一致，top2=`6d30a68`+`5c854ea`）；08:40:53 后业务目录唯一新增为 B 08:45 例行事件（events/B 哈希文件，task=NONE 非业务交付）。
- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**（strongmodel 目录最新 mtime 10-10 22:47 仅 pack，target `6d30a68`），保持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。
- **门禁**：06 聚合放行唯一剩余 = 强复审（TESTER attempt-4 项 10-10 22:57 已验收收口）；03/05/06 聚合 DONE 后派 TASK-08 路径不变。
- **角色占用**：A/B/C/TESTER 全空闲（legacy_busy 空，B 08:45 例行事件）；无在途 ocr/pytest 业务进程（ps 复核仅 wxocr 桌面进程）；`ocr.lock`/`coordinator.lock` 0 字节无在途持有者。
- 本轮控制动作：claim→巡检核查→prepend 检查点→event→release，**无新派单、无状态变更**。
"""
path = ROOT + "/sessions/COORDINATOR.md"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
with open(path, "w", encoding="utf-8") as f:
    f.write(ckpt + "\n" + content)
print("checkpoint prepended")

# 3) event
sh(["python3", RUNTIME, "event", "--project", ROOT, "--role", "COORDINATOR",
    "--token", token,
    "--event-id", "coord-poll-20261011-084553-nochange",
    "--task", "none", "--attempt", "0",
    "--status", "NO_CHANGE",
    "--summary", "08:46 巡检：零业务变化，main 6d30a68 不变；强复审 R2I-20261010-06 仍 READY_FOR_USER_TRIGGER 等用户手动触发；全角色空闲无在途",
    "--evidence", "sessions/COORDINATOR.md#2026-10-11-08-46",
    "--next", "等强复审结果文件或用户触发；无变化不刷群"])

# 4) release
sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--token", token])
print("DONE")