import json, subprocess, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261012-033353"
EVENT_ID = "C-poll-20261012-033353-nochange"

r = subprocess.run(
    [sys.executable, RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER],
    capture_output=True, text=True,
)
if r.returncode != 0:
    print("CLAIM_FAIL rc=%d\nstdout: %s\nstderr: %s" % (r.returncode, r.stdout, r.stderr))
    sys.exit(1)
token = json.loads(r.stdout)["token"]
print("claim ok owner=%s" % OWNER)

sessions_line = (
    "- 最后更新：2026-10-12 03:34 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T03:33:53+08:00）、legacy_busy 空；"
    "03:08:53（前条 C 巡检 preflight 时点）后共享根新增核实均为**非 C 范围**：`TIMELINE.md`/`HANDOFF.md` 协调者记账刷新（tail 核实=03:30:53 空转第 13 轮：main `453da0c` 双核、五角色全空闲、零业务事件）+ 各角色 sessions 巡检刷新 + scratch 本轮前序巡检自身产物；"
    "`inbox/3号/` 实测最新仍 10-10 00:58 attempt-4-ocr-rework、`inbox/coordinator/` 实测最新仍 02:08:34 e2e-reverify-v2-acceptance-decision（find -newermt 02:50 核实均无 C 新单）、**无 C 新派单**；"
    "main HEAD `453da0c`=origin/main 双核一致（rosbag-catalog rev-parse 实测，TASK-10 已 DONE 收口，非 C）、"
    "wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 实测 0）、"
    "ps 实测无 C 在途业务进程（wt-03b/scene-03b 命中 0）；"
    "leases 仅 `B.json` 在途（03:33:43 claim，owner cron-b-poll-…-033253，2号巡检，未到期不接管，非 C）；"
    "C 本轮 owner `C-cron-poll-20261012-033353` claim 成功（token 整体 JSON 解析），事件 `%s` 落盘后 release；"
    "**保持空闲待派单**（P0 已收口、TASK-11 生产门禁待用户授权，如后续涉 C 将另行派单）。前一条 03:08 巡检见下）" % EVENT_ID
)

sp = ROOT + "/sessions/C.md"
with open(sp, "r", encoding="utf-8") as f:
    old = f.read()
head = old.split("\n", 1)[0]
assert head.startswith("- 最后更新："), "sessions head unexpected, abort"
with open(sp, "w", encoding="utf-8") as f:
    f.write(sessions_line + "\n")
    f.write(head)
    if old[len(head):]:
        f.write("\n" + old[len(head):])
print("sessions prepended ok, old head kept:", head[:50])

r = subprocess.run(
    [sys.executable, RUNTIME, "event", "--project", ROOT, "--role", "C", "--token", token,
     "--event-id", EVENT_ID, "--task", "NONE", "--attempt", "0",
     "--status", "IDLE_NO_CHANGE", "--summary", "P0 收口后空转：03:08 后 C 范围零新增、无新派单，main 453da0c 双核、wt-03b 干净、无在途进程",
     "--evidence", "sessions/C.md", "--next", "继续 5 分钟巡检"],
    capture_output=True, text=True,
)
print("event rc=%d %s" % (r.returncode, (r.stdout + r.stderr).strip()[:200]))

r = subprocess.run(
    [sys.executable, RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token],
    capture_output=True, text=True,
)
print("release rc=%d %s" % (r.returncode, (r.stdout + r.stderr).strip()[:200]))