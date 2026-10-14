#!/usr/bin/env python3
"""C 巡检 14:13:53：claim → 准备 sessions 新内容 → run cp 落盘 → event → release（run 内仅简单 cp，避免嵌套 shell）"""
import json
import subprocess
import sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261011-141353"
SESSIONS = f"{ROOT}/sessions/C.md"
NEWFILE = f"{ROOT}/scratch/sessions-C-20261011-1414.md"


def rt(*args, check=True):
    cmd = ["python3", RUNTIME, *args]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if check and p.returncode != 0:
        print("RT_FAIL", p.returncode, " ".join(args))
        print("STDOUT", p.stdout[-2000:])
        print("STDERR", p.stderr[-2000:])
        sys.exit(1)
    return p.stdout.strip()


# 1) claim
out = rt("--project", ROOT, "--role", "C", "claim", "--owner", OWNER, "--ttl", "600")
print("CLAIM_OUT", out)
token = out
try:
    token = json.loads(out).get("token", token)
except Exception:
    for line in out.splitlines():
        line = line.strip()
        if line.startswith('"token"'):
            token = line.split(":", 1)[-1].strip().rstrip(",").strip('"')
        elif line.startswith("token"):
            token = line.split("=", 1)[-1].strip()
assert token and "{" not in token, f"bad token: {token!r}"

# 2) 生成新 sessions 内容（在首行前插入新检查点）
with open(SESSIONS, "r", encoding="utf-8") as f:
    old = f.read()

new_line = (
    "- 最后更新：2026-10-11 14:14 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T14:13:53+08:00）、"
    "legacy_busy 空；14:08:53 后共享根新增均核实为**非 C 范围**：`inbox/coordinator/TASK-06B/attempt-1-r2-rework-9-acceptance-decision.md`"
    "（14:09:58，2号 rework-9 `c2cee73` 验收合入 main `62a85bf` 的 decision）+ `reviews/TASK-06B/attempt-1-r2-rework-9/ocr-batches.md`"
    "（14:09:58 OCR 批次账）+ `reviews/strongmodel/R2I-20261010-06-pack.md`（14:10:49 协调者 pack_update_20261011_1415："
    "target `65ca0be`→`62a85bf`，增量 patch 换新 sha256 `76ff031d…`，codex 七轮全收口不再起第八轮，"
    "仍 READY_FOR_USER_TRIGGER 等用户手动）+ `TODO.md`/`HANDOFF.md`/`TIMELINE.md`/各角色 sessions/events 14:11-14:14 "
    "协调者与 B 巡检刷新，均非 C 业务；`inbox/3号/TASK-03B/` 无新文件（ls -la 核实最新仍 10-10 00:58 "
    "attempt-4-ocr-rework 已 ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、`inbox/coordinator/` 无面向 3号 的新单，"
    "**无 C 新派单**；main HEAD 仍 `62a85bf`（rosbag-catalog rev-parse 核实，与 14:04/14:09 巡检已核实的 rework-9 合入一致）；"
    f"wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 排除 .venv 核实为空）、ps 核实无 C 在途进程；"
    "leases 仅 B.json 在途（14:14:37，2号业务，非 C 范围），C 本轮短占用 owner `" + OWNER + "` 控制动作结束释放；"
    "06 聚合剩余门禁=强复审 R2I-20261010-06（target `62a85bf`，pack 已更新，等用户手动触发）→03/05/06 DONE→TASK-08"
    "（届时才可能涉及 C，当前无单），均非 C 范围；**保持空闲待派单**。前一条 14:09 巡检见下）\n"
)

new = new_line + old
with open(NEWFILE, "w", encoding="utf-8") as f:
    f.write(new)

# 3) run 内仅简单 cp 落盘
run_out = rt("--project", ROOT, "--role", "C", "--token", token, "run",
             "--", "cp", NEWFILE, SESSIONS)
print("RUN_OUT", run_out)

# 4) 读回校验
with open(SESSIONS, "r", encoding="utf-8") as f:
    first = f.readline()
assert "2026-10-11 14:14" in first, f"readback failed: {first[:80]}"
print("READBACK_OK")

# 5) event
ev_out = rt("--project", ROOT, "--role", "C", "--token", token, "event",
            "--event-id", "C-poll-20261011-141353-nochange",
            "--task", "N/A", "--attempt", "0", "--status", "IDLE",
            "--summary", "无 C 新派单；main 仍 62a85bf；强复审 pack target 已更新 62a85bf 等用户手动；保持空闲待派单",
            "--evidence", "sessions/C.md 2026-10-11 14:14 行",
            "--next", "继续 5 分钟巡检；等协调者派单")
print("EVENT_OUT", ev_out)

# 6) release
rel_out = rt("--project", ROOT, "--role", "C", "release", "--owner", OWNER, "--token", token)
print("RELEASE_OUT", rel_out)
print("OK")