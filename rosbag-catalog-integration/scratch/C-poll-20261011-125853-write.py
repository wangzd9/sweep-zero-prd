import re

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261011-125853"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"

import json, subprocess

r = subprocess.run(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER], capture_output=True, text=True)
out = r.stdout + r.stderr
m = re.search(r'"token"\s*:\s*"([^"]+)"', out)
if not m:
    print("CLAIM_FAILED", out[:500])
    raise SystemExit(1)
token = m.group(1)
print("claimed", token[:8])

p = ROOT + "/sessions/C.md"
s = open(p).read()
line = (
    "- 最后更新：2026-10-11 12:58 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T12:58:53+08:00）、"
    "legacy_busy 空；12:53:53 后共享根新增仅 `TODO.md` 12:55:55（协调者 r9 裁决记账刷新，内容与 12:55 已核实的 "
    "codex 第六轮 APPROVED 零 comment 一致，非 C 范围）与 `reviews/codex-r9-rework8-20261010-verdict.md` 12:54"
    "（前条已核实）；`inbox/3号/` 无新文件（find -printf 核实最新仍 10-10 00:58 attempt-4-ocr-rework 已 ACCEPT_MERGED，"
    "TASK-03B 名下全部派单已收口）、`inbox/coordinator/` 无 C 新增，**无 C 新派单**；main HEAD 仍 `65ca0be`"
    "（rosbag-catalog rev-parse 核实）、wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 排除 .venv 核实为空）、"
    "ps 核实无 C 在途进程；leases 无 size>0 在途租约，C 本轮短占用 owner `C-cron-poll-20261011-125853` 控制动作结束释放；"
    "唯一剩余门禁=强复审 R2I-20261010-06（target `65ca0be`，READY_FOR_USER_TRIGGER，result 文件不存在）等用户手动触发，"
    "非 C 范围；**保持空闲待派单**。前一条 12:55 巡检见下）\n"
)
s = s.replace("<!-- five-role-v2 -->\n", "<!-- five-role-v2 -->\n" + line, 1)
open(p, "w").write(s)
print("checkpoint appended")

r = subprocess.run([
    "python3", RUNTIME, "event", "--project", ROOT, "--role", "C", "--token", token,
    "--event-id", "C-poll-20261011-125853-nochange",
    "--task", "-", "--attempt", "-", "--status", "IDLE_WAITING",
    "--summary", "12:58巡检：无C新派单，TODO变更=协调者r9记账（已核实一致），main 65ca0be不变，wt-03b干净，强复审R2I-20261010-06仍等用户手动触发，保持空闲",
    "--evidence", "sessions/C.md", "--next", "继续5分钟巡检",
], capture_output=True, text=True)
print("event rc", r.returncode, (r.stdout + r.stderr).strip()[:200])

r = subprocess.run(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token], capture_output=True, text=True)
print("release rc", r.returncode, (r.stdout + r.stderr).strip()[:200])