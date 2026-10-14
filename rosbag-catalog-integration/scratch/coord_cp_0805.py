#!/usr/bin/env python3
"""Round 2026-10-11 08:05 poll: prepend checkpoint + record event + release."""
import subprocess
import sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-poll-14ae4556629a-080553"
TOKEN = open(f"{ROOT}/scratch/coord_token_0805.txt").read().strip()
CHECKPOINT = """## 2026-10-11 08:05 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T08:05:53+08:00）
- **零业务变化**：main HEAD `6d30a6844844131649042686c8d2039cd33ecce5`（= origin/main，/home/wang/work/rosbag-catalog rev-parse 双核一致）；07:55:53 后业务目录（inbox/receipts/test-receipts/reviews/reports/decision/dispatches/events，除 runtime）**唯一新增为 B/C 例行 IDLE 心跳**（events/B、events/C 2026-10-11 08:0x，无派单/返修/交付，非业务）与自身记账 event。
- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**（strongmodel 目录复核 mtime 10-10 22:47 仅 pack，target `6d30a68`），保持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。
- **门禁**：06 聚合放行唯一剩余 = 强复审（TESTER attempt-4 项 22:57 已验收收口）；03/05/06 聚合 DONE 后派 TASK-08 路径不变。
- **角色占用**：A/B/C/TESTER 全空闲（legacy_busy 空，B/C 08:0x 例行心跳）；无在途 ocr/pytest 业务进程（ps 复核无匹配）；`ocr.lock`/`coordinator.lock` 0 字节无在途持有者。
- 本轮控制动作：claim→巡检核查→prepend 检查点→event→release，**无新派单、无状态变更**。
"""

sess = f"{ROOT}/sessions/COORDINATOR.md"
old = open(sess).read()
open(sess, "w").write(CHECKPOINT + old)
print("CHECKPOINT_PREPENDED", len(old))

r = subprocess.run(
    [sys.executable, RUNTIME, "event", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN,
     "--event-id", "coord-poll-20261011-080553-nochange", "--task", "IDLE", "--attempt", "0",
     "--status", "NO_CHANGE", "--summary", "08:05巡检：零业务变化，main 6d30a68=origin，强复审R2I-20261010-06仍待用户手动触发，全角色空闲",
     "--evidence", "sessions/COORDINATOR.md#2026-10-11-08:05", "--next", "继续5分钟巡检，等强复审结果文件"],
    capture_output=True, text=True,
)
print("EVENT_RC", r.returncode)
print((r.stdout or r.stderr).strip()[:300])

r = subprocess.run(
    [sys.executable, RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN],
    capture_output=True, text=True,
)
print("RELEASE_RC", r.returncode)
print((r.stdout or r.stderr).strip()[:200])