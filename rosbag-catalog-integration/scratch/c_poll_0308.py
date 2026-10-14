import json, subprocess, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261012-030853"
EVENT_ID = "C-poll-20261012-030853-nochange"

def sh(args):
    p = subprocess.run(args, capture_output=True, text=True)
    return p

# 1. claim
p = sh(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
out = p.stdout + p.stderr
if p.returncode != 0:
    print("CLAIM_FAILED:", out)
    raise SystemExit(1)
# parse full JSON for token
token = None
for line in out.splitlines():
    line = line.strip()
    if line.startswith("{"):
        try:
            token = json.loads(line).get("token")
            break
        except Exception:
            pass
if not token:
    # try whole stdout as json
    try:
        token = json.loads(out).get("token")
    except Exception:
        pass
if not token:
    print("TOKEN_PARSE_FAILED:", out)
    raise SystemExit(1)
print("claim ok, token len", len(token))

sessions_line = (
    "- 最后更新：2026-10-12 03:08 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T03:08:53+08:00）、legacy_busy 空；"
    "03:03:53（前条 C 巡检 preflight 时点）后共享根新增核实均为**非 C 范围**：`events/COORDINATOR/` 03:02（head 核实=协调者 03:00:53 轮 `coord-poll-20261012-030053-p0-idle-nochange` DONE_IDLE_POLL 空转第 8 轮）+ `inbox/events/COORDINATOR/coord-poll-20261012-030553-nochange.md` 03:07（head 核实=03:05:53 空转第 9 轮：main `453da0c`=origin/main 双核、全角色空闲、零业务变化，协调者范围）+ 各角色 sessions/ticks 巡检刷新（03:0x B/C/A/TESTER/COORDINATOR，find -newermt 核实无业务文件新增）；"
    "`inbox/3号/` 实测最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED、`inbox/coordinator/` 实测最新仍 02:08:34 e2e-reverify-v2-acceptance-decision（find -printf 核实，均非 C 新单）、**无 C 新派单**；"
    "main HEAD `453da0c`=origin/main 双核一致（rosbag-catalog rev-parse --verify 实测，TASK-10 DONE 已收口，非 C）、"
    "wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 实测 0）、"
    "ps 实测无 C 在途业务进程（wt-03b/scene-03b/t03b/task-03b 命中为空）；"
    "leases 实测无 size>0 在途租约（find 核实，仅 C.lock/TESTER.lock 0 字节）；"
    "C 本轮 owner `C-cron-poll-20261012-030853` claim 成功（token 整体 JSON 解析），事件 `C-poll-20261012-030853-nochange` 落盘后 release；"
    "**保持空闲待派单**（P0 已收口，如后续涉 C 将另行派单）。前一条 02:53 巡检见下）"
)

sp = ROOT + "/sessions/C.md"
with open(sp, "r", encoding="utf-8") as f:
    old = f.read()
assert old.startswith("- 最后更新："), "sessions head unexpected, abort write"
new = sessions_line + "\n" + old

# 2. run: prepend sessions (content passed via argv, no shell redirect)
cmd = ["python3", "-c", "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text(sys.argv[2], encoding='utf-8')", sp, new]
p2 = sh(["python3", RUNTIME, "run", "--project", ROOT, "--role", "C", "--token", token, "--"] + cmd)
if p2.returncode != 0:
    print("RUN_SESSIONS_FAILED:", p2.stdout + p2.stderr)
else:
    print("sessions prepended ok")

# 3. event
p3 = sh(["python3", RUNTIME, "event", "--project", ROOT, "--role", "C", "--token", token,
         "--event-id", EVENT_ID, "--task", "NONE", "--attempt", "0", "--status", "IDLE_WAITING",
         "--summary", "P0 收口后空转巡检：03:03:53 轮后共享根新增仅协调者空转第 8/9 轮事件与他角色 sessions/ticks 心跳，零业务文件；inbox/3号 最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED、inbox/coordinator 最新仍 02:08 e2e-reverify-v2 decision，无 C 新派单；main HEAD 453da0c=origin/main 双核一致、wt-03b 6f1a9ad 干净、无 C 在途进程、无 size>0 租约；保持空闲待派单",
         "--evidence", "scratch/c_poll_0308.py", "--next", "继续 5 分钟空转巡检，如后续涉 C 将另行派单"])
if p3.returncode != 0:
    print("EVENT_FAILED:", p3.stdout + p3.stderr)
else:
    print("event ok")

# 4. release
p4 = sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token])
print("release rc", p4.returncode, (p4.stdout + p4.stderr)[:200])