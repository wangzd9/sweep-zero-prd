#!/usr/bin/env python3
"""Coordinator poll 08:55: claim -> write checkpoint -> event -> release."""
import json
import subprocess
import sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "cron-poll-14ae4556629a-085553"


def sh(args, check=True):
    r = subprocess.run(args, capture_output=True, text=True)
    if check and r.returncode != 0:
        print("FAIL:", " ".join(args), "\nSTDOUT:", r.stdout, "\nSTDERR:", r.stderr)
        sys.exit(1)
    return r


claim = sh([sys.executable, RUNTIME, "claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER])
try:
    claim_json = json.loads(claim.stdout)
except Exception:
    print("claim output unexpected:", claim.stdout, claim.stderr)
    sys.exit(1)
if not claim_json.get("claimed") or not claim_json.get("token"):
    print("claim failed:", claim_json)
    sys.exit(1)
token = claim_json["token"]
print("claim ok")

checkpoint = (
    "## 2026-10-11 08:55 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T08:55:53+08:00）\n"
    "- **零业务变化**：main HEAD `6d30a6844844131649042686c8d2039cd33ecce5`（= origin/main，/home/wang/work/rosbag-catalog rev-parse 双核一致）；08:50:53 后业务目录唯一新增为 TESTER.lock 例行租约刷新（无派单/返修/交付，非业务）。\n"
    "- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**（ls 复核 strongmodel 目录最新 mtime 10-10 22:47 仅 pack，target `6d30a68`），保持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。\n"
    "- **门禁**：06 聚合放行唯一剩余 = 强复审（TESTER attempt-4 项 10-10 22:57 已验收收口）；03/05/06 聚合 DONE 后派 TASK-08 路径不变。\n"
    "- **角色占用**：A/B/C/TESTER 全空闲（legacy_busy 空）；无在途 ocr/pytest 业务进程（ps 复核仅 wxocr 桌面进程）；`ocr.lock`/`coordinator.lock` 0 字节无在途持有者。\n"
    "- 本轮控制动作：claim→巡检核查→prepend 检查点→event→release，**无新派单、无状态变更**。\n"
)

path = f"{ROOT}/sessions/COORDINATOR.md"
with open(path, encoding="utf-8") as f:
    content = f.read()
sh(["true"])
# prepend checkpoint
with open(path, "w", encoding="utf-8") as f:
    f.write(checkpoint + content)
print("checkpoint prepended")

event = {
    "event_id": "coord-poll-20261011-085553-nochange",
    "role": "COORDINATOR",
    "task": "TASK-06",
    "attempt": 0,
    "status": "NO_CHANGE",
    "occurred_at": "2026-10-11T08:55:53+08:00",
    "recorded_at": "2026-10-11T08:55:53+08:00",
    "summary": "巡检：main 6d30a68 不变，强复审 R2I-20261010-06 仍无 result.md（READY_FOR_USER_TRIGGER），全角色空闲，无新派单/状态变更。",
    "evidence": "sessions/COORDINATOR.md",
    "next": "下轮巡检核强复审结果文件与 events",
}
evpath = f"{ROOT}/events/COORDINATOR/coord-poll-20261011-0855-nochange.json"
with open(evpath, "w", encoding="utf-8") as f:
    json.dump(event, f, ensure_ascii=False, indent=2)
print("event written:", evpath)

rel = sh([sys.executable, RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--token", token])
print("release ok")