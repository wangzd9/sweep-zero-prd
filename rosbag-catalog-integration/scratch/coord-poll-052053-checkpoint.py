#!/usr/bin/env python3
# 协调者 05:20 巡检：claim -> prepend 检查点 -> release
import subprocess, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-poll-14ae4556629a-052053"
SESSION = ROOT + "/sessions/COORDINATOR.md"

CKPT = """## 2026-10-11 05:20 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T05:20:53+08:00）
- **零业务变化**：main HEAD `6d30a6844844131649042686c8d2039cd33ecce5`（= origin/main，rev-parse 双核一致，top2=`6d30a68`+`5c854ea`）；05:15:53 后业务目录（inbox/receipts/test-receipts/reviews/reports/decision/events/dispatches，除 runtime ticks）**唯一新增为 B 05:18 例行 IDLE_WAITING 心跳** `b-poll-20261011-051753-nochange`（task=NONE，非业务）与 C 05:19 零字节例行租约刷新。
- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**（目录最新 mtime 10-10 22:47 仅 pack，target `6d30a68`），保持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。
- **门禁**：06 聚合放行唯一剩余 = 强复审（TESTER attempt-4 项 22:57 已验收收口）；03/05/06 聚合 DONE 后派 TASK-08 路径不变。
- **角色占用**：A/B/C/TESTER 全空闲（legacy_busy 空，ticks 05:16–05:20 例行心跳）；无在途 ocr/pytest 业务进程（ps 复核仅 wxocr 桌面进程）；`ocr.lock`/`coordinator.lock` 0 字节无在途持有者，leases 仅 C 05:19 / TESTER 02:15 零字节例行租约。
- 本轮控制动作：claim→巡检核查→prepend 检查点→release，**无新派单、无状态变更**。
"""

r = subprocess.run([sys.executable, RUNTIME, "claim", "--project", ROOT,
                    "--role", "COORDINATOR", "--owner", OWNER],
                   capture_output=True, text=True)
print("claim:", r.stdout.strip() or r.stderr.strip())
if r.returncode != 0:
    sys.exit(1)

token = r.stdout.strip().splitlines()[-1].strip()
if not token or "error" in r.stdout.lower():
    sys.exit(2)

with open(SESSION, "r", encoding="utf-8") as f:
    content = f.read()

# 幂等：避免重复 prepend（本文件已存在 05:20 检查点则跳过）
if CKPT.splitlines()[0] in content:
    print("checkpoint already present, skip prepend")
else:
    with open(SESSION, "w", encoding="utf-8") as f:
        f.write(CKPT + content)
    print("checkpoint prepended")

r2 = subprocess.run([sys.executable, RUNTIME, "release", "--project", ROOT,
                     "--role", "COORDINATOR", "--token", token],
                    capture_output=True, text=True)
print("release:", r2.stdout.strip() or r2.stderr.strip())
sys.exit(r2.returncode)