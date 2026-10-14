#!/usr/bin/env python3
"""C 执行者 22:38 巡检：claim -> 写 nochange 事件 -> release。"""
import json
import subprocess
import datetime

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261011-223853"

def sh(args):
    r = subprocess.run(args, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

rc, out, err = sh(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
print("claim rc:", rc)
print("claim stdout:", out.strip())
print("claim stderr:", err.strip()[:300])
token = None
try:
    token = json.loads(out).get("token") or json.loads(out).get("lease", {}).get("token")
except Exception:
    # 输出可能多行，取最后一个可解析的 JSON 块
    for line in reversed(out.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                token = json.loads(line).get("token")
                break
            except Exception:
                continue
print("token:", token)
if not token:
    print("NO_TOKEN_ABORT")
    raise SystemExit(1)

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
event_path = f"{ROOT}/inbox/events/C/C-poll-20261011-223853-nochange.md"
with open(event_path, "w", encoding="utf-8") as f:
    f.write(
        f"# C 巡检事件 C-poll-20261011-223853-nochange\n\n"
        f"- 时间：{now} +08:00（checked_at 2026-10-11T22:38:53+08:00）\n"
        f"- 结论：**无 C 新派单，保持空闲待派单**。22:34:37（前条巡检写入）后共享根零新增"
        f"（find -newermt 核实，排除巡检类目录）；`inbox/3号/` 最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED、"
        f"`inbox/coordinator/` 最新仍 21:57 TASK-09 post-merge decision（非 C）。\n"
        f"- 快照：main `ca8730d` = origin/main 双核一致（rosbag-catalog rev-parse）；wt-03b HEAD `6f1a9ad` "
        f"分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 为空）；ps 无 C 在途业务进程。\n"
        f"- 租约：leases 仅 C.lock/TESTER.lock 0 字节，无在途他角色租约；owner {OWNER} 短占用后释放。\n"
        f"- 非 C 范围在途：2号 TASK-10 attempt-1 已 ACK 开工（22:04，`wt-04a-t10`，端到端长任务），不跨群通报。\n"
    )
print("event written:", event_path)

rc, out, err = sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token, "--owner", OWNER])
print("release rc:", rc)
print("release stdout:", out.strip()[:300])
print("release stderr:", err.strip()[:300])