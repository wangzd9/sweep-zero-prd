#!/usr/bin/env python3
"""coord poll 2026-10-11 08:40: claim -> append checkpoint + event -> release (nochange)."""
import json, subprocess, sys, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "coord-cron-poll-20261011-084053"
CHECKED_AT = "2026-10-11T08:40:53+08:00"

def sh(*args):
    r = subprocess.run([sys.executable, RUNTIME, *args], capture_output=True, text=True)
    if r.stdout: print("OUT:", r.stdout.strip()[:500])
    if r.returncode != 0:
        print("ERR:", r.stderr.strip()[:1000]); r.raise_for_exitcode()
    return r.stdout

# 1) claim
out = sh("claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER)
token = out.strip().splitlines()[-1].strip().strip("'\"")
if not token or token.startswith("{"):
    try: token = json.loads(out.strip()).get("token", token)
    except Exception: pass
print("token-len:", len(str(token)))

checkpoint = (
    "## 2026-10-11 08:40 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T08:40:53+08:00）\n"
    "- **零业务变化**：main HEAD `6d30a6844844131649042686c8d2039cd33ecce5`（= origin/main 双核一致）；07:50:53 后业务目录无新增（find -newermt 核实，仅各角色例行心跳事件与 sessions 心跳行）。\n"
    "- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**（strongmodel 目录最新 10-10 22:47 pack，target `6d30a68`），保持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。\n"
    "- **门禁**：06 聚合放行唯一剩余 = 强复审（TESTER attempt-4 22:57 已验收收口）；03/05/06 聚合 DONE 后派 TASK-08 路径不变。\n"
    "- **角色占用**：A/B/C/TESTER 全空闲（legacy_busy 空，各角色 08:3x 心跳均报无新派单）；无在途 ocr/pytest 业务进程（ps 复核仅 wxocr 桌面进程）；`ocr.lock`/`coordinator.lock` 无在途持有者。\n"
    "- 本轮控制动作：claim→巡检核查→append 检查点+event→release，**无新派单、无状态变更**。\n"
)
with open(os.path.join(ROOT, "sessions/COORDINATOR.md"), "a", encoding="utf-8") as f:
    f.write(checkpoint)
print("checkpoint appended")

# 2) event (nochange)
sh("event", "--project", ROOT, "--role", "COORDINATOR", "--token", token,
   "--event-id", "coord-poll-20261011-084053-nochange",
   "--status", "IDLE_WAITING",
   "--summary", "零业务变化巡检：main 6d30a68 不变、强复审 R2I-20261010-06 result 仍不存在（READY_FOR_USER_TRIGGER）、A/B/C/TESTER 全空闲、无在途 ocr/pytest 进程",
   "--next", "继续 5 分钟巡检；等用户手动触发强复审")

# 3) release
sh("release", "--project", ROOT, "--role", "COORDINATOR", "--token", token)
print("released OK")