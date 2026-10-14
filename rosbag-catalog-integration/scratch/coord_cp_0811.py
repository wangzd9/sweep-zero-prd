#!/usr/bin/env python3
"""Round 2026-10-11 08:11 poll: prepend checkpoint + event + release COORDINATOR lease."""
import json
import subprocess
import sys
from pathlib import Path

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
OWNER = "cron-poll-14ae4556629a-081053"
tok = (ROOT / "scratch/coord_token_0811.txt").read_text().strip()

CP = """## 2026-10-11 08:10 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T08:10:53+08:00）
- **零业务变化**：main HEAD `6d30a6844844131649042686c8d2039cd33ecce5`（= origin/main，/home/wang/work/rosbag-catalog rev-parse 双核一致，top2=`6d30a68`+`5c854ea`）；08:05:53 后业务目录（inbox/receipts/test-receipts/reviews/reports/decision/events/dispatches/scratch，除 runtime/sessions）**唯一新增为 B 08:09 例行 IDLE_WAITING nochange 心跳** `b-poll-20261011-080753-nochange`（无派单/返修/交付，非业务）与自身记账 event。
- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**（strongmodel 目录复核 mtime 10-10 22:47 仅 pack，target `6d30a68`），保持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。
- **门禁**：06 聚合放行唯一剩余 = 强复审（TESTER attempt-4 项 10-10 22:57 已验收收口）；03/05/06 聚合 DONE 后派 TASK-08 路径不变。
- **角色占用**：A/B/C/TESTER 全空闲（legacy_busy 空，B 08:09 例行心跳）；无在途 ocr/pytest 业务进程（ps 复核仅既有本地栈 alembic+uvicorn 服务与 `rosbag-catalog-local-mysql-1` 容器）；`ocr.lock`/`coordinator.lock` 0 字节无在途持有者，leases 目录空。
- 本轮控制动作：claim→巡检核查→prepend 检查点→event→release，**无新派单、无状态变更**。
"""

sess = ROOT / "sessions/COORDINATOR.md"
cur = sess.read_text()
if cur.startswith(CP.splitlines()[0]):
    print("CP_ALREADY_PRESENT; skipping prepend")
else:
    sess.write_text(CP + cur)
    print("CP_PREPENDED")

# event (dedup by event_id; retry-safe)
ev = subprocess.run(
    [sys.executable, RUNTIME, "event", "--project", str(ROOT), "--role", "COORDINATOR", "--token", tok,
     "--event-id", "coord-poll-20261011-081053-nochange", "--occurred-at", "2026-10-11T08:10:53+08:00",
     "--task", "IDLE", "--attempt", "0", "--status", "NO_CHANGE",
     "--summary", "08:10巡检：零业务变化，main 6d30a68=origin，强复审R2I-20261010-06仍待用户手动触发，全角色空闲",
     "--evidence", "sessions/COORDINATOR.md#2026-10-11-08:10",
     "--next", "继续5分钟巡检，等强复审结果文件"],
    capture_output=True, text=True,
)
print("EVENT RC", ev.returncode)
print(ev.stdout.strip() or ev.stderr.strip())

# release
rl = subprocess.run(
    [sys.executable, RUNTIME, "release", "--project", str(ROOT), "--role", "COORDINATOR", "--token", tok],
    capture_output=True, text=True,
)
print("RELEASE RC", rl.returncode)
print(rl.stdout.strip() or rl.stderr.strip())