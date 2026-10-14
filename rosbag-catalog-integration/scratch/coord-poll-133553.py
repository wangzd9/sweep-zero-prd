#!/usr/bin/env python3
"""协调者 5 分钟巡检控制 run：claim -> append 检查点 -> event -> release."""
import hashlib
import json
import os
import subprocess
import sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
SESSION = os.path.join(ROOT, "sessions", "COORDINATOR.md")
OWNER = "cron-coordinator-poll-20261011-133553"
EVENT_ID = "coord-poll-20261011-133553-nochange"


def sh(args):
    return subprocess.run(args, capture_output=True, text=True)


def main():
    # 1) 只读复核：main HEAD / origin 一致性、强复审结果文件是否存在
    head = sh(["git", "-C", "/home/wang/work/rosbag-catalog", "rev-parse", "HEAD"]).stdout.strip()
    om = sh(["git", "-C", "/home/wang/work/rosbag-catalog", "rev-parse", "origin/main"]).stdout.strip()
    sm = os.path.join(ROOT, "reviews", "strongmodel", "R2I-20261010-06-result.md")
    sm_exists = os.path.exists(sm)
    assert head == om == "65ca0beb0111a2d45065206886d432bd20eb76d0", (head, om)
    assert not sm_exists

    # 2) claim
    r = sh([sys.executable, RUNTIME, "claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER])
    sys.stdout.write(r.stdout + r.stderr)
    if r.returncode != 0:
        print("CLAIM_FAILED — 本轮仅报告，不写入", file=sys.stderr)
        sys.exit(1)
    payload = json.loads(r.stdout)
    token = payload.get("token", "")
    if not token or not token.isascii() or len(token) < 8:
        print("TOKEN_UNRECOGNIZED — 放弃写入", file=sys.stderr)
        sys.exit(1)

    # 3) append 检查点
    checkpoint = (
        "\n## 2026-10-11 13:35 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T13:35:53+08:00）\n"
        f"- **13:20 后零业务变化**：main HEAD `{head}`（= main = origin/main，rev-parse 三核一致）；"
        "13:20:53 后共享根新增仅 B 13:22/13:27/13:32 例行 nochange/IDLE_WAITING 心跳事件与上轮协调者 scratch 脚本（find -newermt 核实，无派单/返修/交付）。\n"
        "- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**（目录最新 10-11 12:31 pack，target `65ca0be`），维持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。\n"
        "- **06 聚合放行门禁（唯一剩余，不变）**：强复审 PASS 收口即 03/05/06 聚合 DONE → TASK-08 联调派单。\n"
        "- **角色占用**：A/B/C/TESTER 全空闲（legacy_busy 空，B 13:2x–13:3x 心跳均报无新派单）；`ocr.lock`/`coordinator.lock`/各角色 lock 0 字节无在途持有者；无在途 ocr/pytest 业务进程（ps 复核仅桌面 wxocr/code 进程）。\n"
        "- 本轮控制动作：claim→巡检核查（find -newermt/rev-parse/ps/locks/事件复核）→append 检查点→event→release，**无新派单、无状态变更、无 OCR**。\n"
    )
    with open(SESSION, "a", encoding="utf-8") as f:
        f.write(checkpoint)

    # 4) event
    summary = "13:20 后零业务变化：main 65ca0be=origin 三核一致；强复审 R2I-20261010-06 result 仍缺 READY_FOR_USER_TRIGGER；A/B/C/TESTER 全空闲无在途进程；无新派单/OCR"
    r2 = sh([
        sys.executable, RUNTIME, "event",
        "--project", ROOT, "--role", "COORDINATOR", "--token", token,
        "--event-id", EVENT_ID,
        "--task", "TASK-06", "--attempt", "0",
        "--status", "NO_CHANGE",
        "--summary", summary,
        "--evidence", "sessions/COORDINATOR.md#2026-10-11 13:35",
        "--next", "等用户手动触发强复审 R2I-20261010-06；PASS 后 03/05/06 聚合 DONE → TASK-08",
    ])
    print(r2.stdout, end="")
    if r2.returncode != 0:
        print(r2.stderr, file=sys.stderr)

    # 5) release
    r3 = sh([sys.executable, RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--token", token])
    print(r3.stdout, end="")
    if r3.returncode != 0:
        print("RELEASE_FAILED", r3.stderr, file=sys.stderr)
        sys.exit(2)
    print("OK head=" + head + " sm_exists=" + str(sm_exists))


if __name__ == "__main__":
    main()