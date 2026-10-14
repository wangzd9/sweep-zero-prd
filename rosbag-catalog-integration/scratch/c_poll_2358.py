#!/usr/bin/env python3
"""C poll 23:58 nochange: prepend sessions/C.md line + emit event via runtime."""
import json
import subprocess
import sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261011-235853"
TOKEN = "0bf459bf1565471b8a304d985f126dec"

new_line = (
    "- 最后更新：2026-10-11 23:58 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at "
    "2026-10-11T23:58:53+08:00）、legacy_busy 空；23:53:53（前条 C 事件落盘）后共享根新增核实均为"
    "**非 C 范围**：`events/COORDINATOR/` 23:56 协调者 23:50 巡检事件（read 核实=2号 TASK-10 驱动第 5 跑——"
    "VLM endpoint 404 已解（B 改完整路径 /v1/chat/completions）、新失败=requests 模块缺失复发"
    "（harness 环境层非 app 缺陷，B 在途处置）+ `HANDOFF.md` 23:50 协调者检查点（2号/协调者范围，非 C）"
    "+ 各角色 sessions 巡检刷新；`inbox/3号/` 无新文件（find -printf 核实最新仍 10-10 00:58 "
    "attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、`inbox/coordinator/` "
    "21:57:39 后无新增（find 核实最新仍 TASK-09 post-merge decision），**无 C 新派单**；"
    "main HEAD `ca8730d`=origin/main 双核一致（rosbag-catalog rev-parse 核实，2号 TASK-10 在途未交付，非 C）、"
    "wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 核实为空）；"
    "**只读观察（非 C 范围不处置）**：23:59 快照见一条 pytest 进程（pid 3072518，相对 .venv 路径 cwd 不可定位，"
    "测试文件 test_scene_result_report/test_scene_result_storage/test_slope_vlm_wiring/test_slope_adapter "
    "=06B/TASK-09 域，属 2号/协调者业务），复查（00:00:2x）已不存在、无 C 在途业务进程；"
    "leases 无 size>0 在途租约（find 核实为空）；C 本轮 owner `C-cron-poll-20261011-235853` "
    "claim 2026-10-12T00:00:21（token 整体 JSON 解析），事件 `C-poll-20261011-235853-nochange` 落盘，"
    "控制动作结束释放；**保持空闲待派单**。前一条 23:53 巡检见下\n"
)

path = f"{ROOT}/sessions/C.md"
with open(path, "r", encoding="utf-8") as f:
    old = f.read()
if new_line.strip()[:40] in old:
    print("ALREADY_PRESENT")
    sys.exit(0)
with open(path, "w", encoding="utf-8") as f:
    f.write(new_line + old)
print("SESSIONS_PREPENDED")

summary = (
    "23:53:53后共享根零C范围新增（协调者23:50巡检事件=2号TASK-10驱动第5跑VLM 404已解/"
    "requests缺失复发harness层B在途 + HANDOFF 23:50检查点 + 各角色sessions刷新，均非C）；"
    "inbox/3号最新仍10-10 00:58 ACCEPT_MERGED、inbox/coordinator 21:57:39后无新增；"
    "main ca8730d=origin/main双核一致；wt-03b 6f1a9ad干净；23:59快照一条06B/TASK-09域pytest进程"
    "复查已不存在非C在途；leases无在途；保持空闲待派单"
)
cmd = [
    "python3", RUNTIME, "event",
    "--project", ROOT, "--role", "C", "--token", TOKEN,
    "--event-id", "C-poll-20261011-235853-nochange",
    "--task", "NONE", "--attempt", "0", "--status", "NO_CHANGE",
    "--summary", summary,
    "--evidence", "sessions/C.md",
    "--next", "继续5分钟巡检",
]
r = subprocess.run(cmd, capture_output=True, text=True)
print("EVENT rc=%d" % r.returncode)
print(r.stdout[-800:])
if r.returncode != 0:
    print(r.stderr[-800:], file=sys.stderr)
    sys.exit(1)

r2 = subprocess.run(
    ["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", TOKEN],
    capture_output=True, text=True,
)
print("RELEASE rc=%d" % r2.returncode)
print(r2.stdout[-300:])
if r2.returncode != 0:
    print(r2.stderr[-800:], file=sys.stderr)
    sys.exit(1)