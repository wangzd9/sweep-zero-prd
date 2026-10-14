#!/usr/bin/env python3
"""C 04:23:53 poll: claim -> append sessions + event -> release."""
import json
import subprocess
import sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261012-042353"
EVENT_ID = "C-poll-20261012-042353-nochange"
CHECKED_AT = "2026-10-12T04:23:53+08:00"


def run(args):
    p = subprocess.run(args, capture_output=True, text=True)
    return p


def parse_claim(out):
    i = out.index("{")
    return json.loads(out[i:])


r = run(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
print("claim exit", r.returncode)
if r.returncode != 0:
    print("CLAIM FAILED:", r.stdout, r.stderr)
    sys.exit(1)
token = parse_claim(r.stdout)["token"]

# 1) append sessions/C.md
line = (
    f"- 最后更新：2026-10-12 04:24 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at {CHECKED_AT}）、legacy_busy 空；"
    f"04:18:53（前条 C 巡检 preflight 时点）后 C 范围零新增：`inbox/3号/` 与 `inbox/coordinator/` find -printf 实测最新仍 "
    f"10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED 与 02:08:34 e2e-reverify-v2 decision、**无 C 新派单**；"
    f"main HEAD `453da0c`=origin/main 双核一致（rosbag-catalog rev-parse 实测，非 C）、wt-03b HEAD=`6f1a9ad` 分支 "
    f"`feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 实测 0）、ps 实测无 C 在途业务进程（0）；"
    f"leases 仅 0 字节历史收尾文件（C.lock/TESTER.lock，非忙碌 owner，不接管）、B.json 瞬时在途后已自行释放；"
    f"C 本轮 owner `{OWNER}` claim 成功（token 整体 JSON 解析），事件 `{EVENT_ID}` 落盘后 release；"
    f"**保持空闲待派单**（P0 已收口停止派发，TASK-11 生产门禁待用户独立授权，如后续涉 C 将另行派单）。前一条 04:19 巡检见上）"
)
with open(f"{ROOT}/sessions/C.md", "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("sessions appended")

# 2) event
event = {
    "event_id": EVENT_ID,
    "occurred_at": CHECKED_AT,
    "role": "C",
    "task": "none",
    "attempt": "0",
    "status": "POLL_NO_CHANGE",
    "summary": "04:18:53 后 C 范围零新增：无新派单；main 453da0c=origin/main 双核一致；wt-03b 6f1a9ad 干净；无 C 在途进程；leases 无在途租约",
    "evidence": "sessions/C.md 04:24 巡检行；find -printf inbox/3号 与 inbox/coordinator 最新仍 10-10 00:58 与 02:08:34",
    "next": "保持空闲待派单；TASK-11 生产门禁待用户独立授权",
}
r = run([
    "python3", RUNTIME, "event", "--project", ROOT, "--role", "C", "--token", token,
    "--event-id", EVENT_ID, "--task", "none", "--attempt", "0",
    "--status", "POLL_NO_CHANGE",
    "--summary", event["summary"],
    "--evidence", event["evidence"],
    "--next", event["next"],
])
print("event exit", r.returncode, r.stdout.strip()[:200], r.stderr.strip()[:200])

# 3) release
r = run(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token])
print("release exit", r.returncode, r.stdout.strip()[:200])