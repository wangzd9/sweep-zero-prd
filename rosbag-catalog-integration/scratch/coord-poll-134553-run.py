#!/usr/bin/env python3
"""协调者 5 分钟巡检控制 run：prepend 检查点 -> event -> release（token 复用本轮已 claim）。"""
import json
import os
import subprocess
import sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
SESSION = os.path.join(ROOT, "sessions", "COORDINATOR.md")
TOKEN = "2de87d2b76e04894ad03e52a26ec67a7"
EVENT_ID = "coord-poll-20261011-134553-nochange"


def sh(args):
    return subprocess.run(args, capture_output=True, text=True)


def main():
    # 1) 只读复核（run 内重读）：main/origin 一致、强复审结果仍缺
    head = sh(["git", "-C", "/home/wang/work/rosbag-catalog", "rev-parse", "main"]).stdout.strip()
    om = sh(["git", "-C", "/home/wang/work/rosbag-catalog", "rev-parse", "origin/main"]).stdout.strip()
    assert head == om == "65ca0beb0111a2d45065206886d432bd20eb76d0", (head, om)
    sm = os.path.join(ROOT, "reviews", "strongmodel", "R2I-20261010-06-result.md")
    assert not os.path.exists(sm)

    # 2) prepend 检查点到 sessions/COORDINATOR.md
    with open(SESSION, encoding="utf-8") as f:
        old = f.read()
    if "2026-10-11 13:45 巡检检查点" in old:
        print("CHECKPOINT_ALREADY_WRITTEN — 跳过写入，仍落 event 核对", file=sys.stderr)
        cp_done = False
    else:
        cp = (
            "## 2026-10-11 13:45 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T13:45:53+08:00：13:31 后零业务变化）\n"
            "- **13:31 后零业务变化**：main HEAD `65ca0beb0111a2d45065206886d432bd20eb76d0`（= main = origin/main，rev-parse 三核一致）；13:31 后共享根新增仅 B 13:33/13:41 两条例行心跳（`b-poll-20261011-133253-nochange` IDLE_WAITING、`b-poll-20261011-133753-nochange` NO_CHANGE，均报 main `65ca0be` 一致、强复审 result 仍缺、无新派单无返修）与上轮自身 scratch/记账事件，无业务交付。\n"
            "- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**（目录最新 12:31 pack，target `65ca0be`），维持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。\n"
            "- **06 聚合放行门禁（唯一剩余，不变）**：强复审 R2I-20261010-06 → PASS 收口即 03/05/06 聚合 DONE → TASK-08 联调派单。\n"
            "- **角色占用**：A/B/C/TESTER 全空闲（ticks 13:37–13:44 例行，legacy_busy 空）；无在途 ocr/pytest 业务进程（ps 复核仅本地栈 alembic/uvicorn 服务与桌面进程）；`ocr.lock`(12:28)/`coordinator.lock` 0 字节，leases 无他角色在途持有者。\n"
            "- 本轮控制动作：claim→巡检核查（find -newermt/rev-parse/ps/locks/leases/ticks/事件复核）→prepend 检查点→event→release，**无新派单、无状态变更、无 OCR**。\n"
            "\n"
        )
        with open(SESSION, "w", encoding="utf-8") as f:
            f.write(cp + old)
        cp_done = True
    print("checkpoint_written=" + str(cp_done))

    # 3) event（run 内用 token）
    r2 = sh([
        sys.executable, RUNTIME, "event",
        "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN,
        "--event-id", EVENT_ID,
        "--task", "TASK-06", "--attempt", "0",
        "--status", "NO_CHANGE",
        "--summary", "13:31 后零业务变化：main 65ca0be=origin 三核一致；强复审 R2I-20261010-06 result 仍缺 READY_FOR_USER_TRIGGER；A/B/C/TESTER 全空闲无在途 ocr/pytest 进程；B 两条例行心跳非业务；无新派单/OCR",
        "--evidence", "sessions/COORDINATOR.md#2026-10-11 13:45",
        "--next", "等用户手动触发强复审 R2I-20261010-06；PASS 后 03/05/06 聚合 DONE → TASK-08 联调派单",
    ])
    sys.stdout.write(r2.stdout)
    if r2.returncode != 0:
        sys.stdout.write(r2.stderr)
        print("EVENT_FAILED", file=sys.stderr)
        sys.exit(2)

    # 4) release
    r3 = sh([sys.executable, RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN])
    sys.stdout.write(r3.stdout)
    if r3.returncode != 0:
        print("RELEASE_FAILED", r3.stderr, file=sys.stderr)
        sys.exit(3)
    print("OK head=" + head)


if __name__ == "__main__":
    main()