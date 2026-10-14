#!/usr/bin/env python3
"""C 角色 19:03 巡检短控制 run：claim → 追加 sessions/C.md 检查点 → event → release。"""
import subprocess, json, sys, os

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261011-190353"

def sh(args, **kw):
    r = subprocess.run(args, capture_output=True, text=True, **kw)
    return r

# claim
r = sh([sys.executable, RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
print("claim rc=%d" % r.returncode)
print(r.stdout.strip() or r.stderr.strip())
if r.returncode != 0:
    print("CLAIM_FAILED — no write, exit")
    sys.exit(1)
token = r.stdout.strip().split()[-1]

# checkpoint text (事实全部来自本轮已核实证据)
line = ("- 最后更新：2026-10-11 19:07 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T19:03:53+08:00）、legacy_busy 空；"
        "18:59:52 后共享根**零 C 范围新增**（find -newermt 排除 sessions/events/leases/scratch/control 核实仅各角色 ticks 刷新）；"
        "`inbox/3号/` 无新文件（ls 核实最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、"
        "`inbox/coordinator/` 无面向 3号 新单（find -newermt 17:02 核实为空，最新仍 17:01:40 c3-1 decision，1号范围），**无 C 新派单**；"
        "main HEAD 未变（`98f6c88`=origin/main，wt-03b 内 rev-parse 核实）、wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 核实仅 .venv untracked）；"
        "**新观察（只读核实，非 C 范围不处置）**：2号 t08c-1 OCR 又换进程再跑——`ocr review -c bf48a45`（pid 2664993，lstart 19:03，"
        "exclude 集 6 文件与 18:55 巡检一致），18:55 的 pid 2655424 已被替换，`bf48a45` 仍 REVIEW_PENDING **未合入**"
        "（等 OCR 收口→协调者 rebase `98f6c88` 复核→合入）；leases 仅 `COORDINATOR.json` 在途（owner `cron-coord-poll-182053-t08c1-review` "
        "claim 18:22、pid null、expires 20:24 未到期，协调者 t08c-1 复核业务，非 C 范围）、C 租约无占用；"
        "ps 核实无 C 在途业务进程；C 本轮短占用 owner `C-cron-poll-20261011-190353` 控制动作结束释放（脚本 `scratch/c_poll_1903.py`）；"
        "**保持空闲待派单**。前一条 18:59 巡检见下）")

path = os.path.join(ROOT, "sessions", "C.md")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
if line in content:
    print("checkpoint already present, skip append")
else:
    content = line + "\n" + content
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("sessions/C.md checkpoint appended")

# event
r = sh([sys.executable, RUNTIME, "event", "--project", ROOT, "--role", "C", "--token", token,
        "--event-id", "C-poll-20261011-190353-nochange", "--task", "TASK-03B", "--attempt", "0",
        "--status", "IDLE", "--summary", "巡检：无 C 新派单，main 98f6c88 未变，wt-03b 6f1a9ad 干净，保持空闲",
        "--evidence", "scratch/c_poll_1903.py", "--next", "继续检查本角色派单"])
print("event rc=%d" % r.returncode)
print(r.stdout.strip() or r.stderr.strip())

# release
r = sh([sys.executable, RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token])
print("release rc=%d" % r.returncode)
print(r.stdout.strip() or r.stderr.strip())