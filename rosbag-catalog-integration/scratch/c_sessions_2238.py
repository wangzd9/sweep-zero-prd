#!/usr/bin/env python3
"""C 巡检：claim → 更新 sessions/C.md → release。"""
import json, subprocess, datetime

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261011-223853s"

def sh(args):
    r = subprocess.run(args, capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

rc, out, err = sh(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
token = json.loads(out)["token"]
print("claimed, token:", token[:8])

# 读取现有 sessions/C.md
path = f"{ROOT}/sessions/C.md"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_entry = (
    "- 最后更新：2026-10-11 22:38 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T22:38:53+08:00）、legacy_busy 空；"
    "22:34:37（前条巡检写入 `inbox/sessions/C.md`）后共享根零新增（find -newermt 核实，排除巡检类目录）；"
    "`inbox/3号/` 无新文件（find 核实最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、"
    "`inbox/coordinator/` 无面向 3号 新单（find 核实最新仍 21:57 TASK-09 post-merge decision，非 C），**无 C 新派单**；"
    "main HEAD `ca8730d`=origin/main 双核一致（rosbag-catalog rev-parse 核实）、"
    "wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 核实为空）、"
    "ps 核实无 C 在途业务进程；"
    "leases 仅 C.lock/TESTER.lock 0 字节无在途租约；"
    "C 本轮 owner `C-cron-poll-20261011-223853` claim 22:41，事件 `C-poll-20261011-223853-nochange` 落盘，控制动作结束释放；"
    "**保持空闲待派单**。前一条 22:30 巡检见下\n"
)

# 插入到第一行（marker 注释之后）
if lines and lines[0].startswith("<!--"):
    lines.insert(1, new_entry)
else:
    lines.insert(0, new_entry)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)
print("sessions/C.md updated")

rc, out, err = sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token])
print("released, rc:", rc)