#!/usr/bin/env python3
import json, subprocess, sys, datetime, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261012-020353"
EVENT_ID = "C-poll-20261012-020353-nochange"

def run(args, check=True):
    r = subprocess.run(args, capture_output=True, text=True)
    if check and r.returncode != 0:
        print("FAIL", " ".join(args))
        print(r.stdout)
        print(r.stderr)
        sys.exit(1)
    return r

# 1. claim (parse whole JSON for token)
r = run(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
print("claim rc", r.returncode)
claim = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {}
# find the JSON object in output
try:
    obj = json.loads(r.stdout[r.stdout.index("{"):])
    token = obj.get("token") or obj.get("lease", {}).get("token")
except Exception:
    obj = {}
    token = None
if not token:
    # try scanning all lines for json
    for line in r.stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                o = json.loads(line)
                token = o.get("token") or o.get("lease", {}).get("token")
                if token:
                    obj = o
                    break
            except Exception:
                pass
if not token:
    print("NO TOKEN in claim output:", r.stdout, r.stderr)
    sys.exit(1)
print("token ok:", token[:8], "...")

now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M +08:00")

sessions_line = (
    f"- 最后更新：{now}（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T02:03:53+08:00）、legacy_busy 空；"
    f"01:59:55（前条 C 巡检写入）后共享根新增核实均为**非 C 范围**："
    f"`scratch/t10/` 01:59（frame_log/model_results/publish 切片 db3/t10-e2e.db/t10-driver-v2.out/t10-run.log = "
    f"**TESTER E2E 复跑 v2 驱动在途产物，t10 收口链，非 C**）+ `events/B/` 01:59 + `sessions/B.md`/`sessions/A.md` 巡检刷新 + "
    f"`scratch/coord_t10_evidence_check.py`/`coord_t10_source_check.py` 02:02/02:04（协调者 t10 证据核对脚本，非 C）+ "
    f"`inbox/TESTER/TASK-10/e2e-reverify-v2-dispatch.md` mtime 02:03 刷新（内容前条 01:59 巡检已核=TESTER 复跑 v2 派单在途，测试者范围）+ "
    f"各角色 ticks 巡检刷新（find -newermt 01:58:53 核实，find 输出无 C 收件箱/协调者面向 3号 新单）；"
    f"`inbox/3号/TASK-03B/` 无新文件（ls 核实最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单仍已收口），"
    f"**无 C 新派单**；main HEAD `453da0c`=origin/main 双核一致（rosbag-catalog rev-parse 实测，与前条一致，2号 t10-defect3 合入后未再推进，非 C 交付）、"
    f"wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 实测为空）、"
    f"ps 实测无 C 在途业务进程（wt-03b/scene-03b/t03b/task-03b 命中为空）；"
    f"leases 仅 `TESTER.json` 在途（217 字节 02:04，TESTER E2E 复跑 v2 业务，非 C 范围）；"
    f"C 本轮 owner `{OWNER}` claim 成功（token 整体 JSON 解析），事件 `{EVENT_ID}` 落盘，控制动作结束释放；"
    f"**保持空闲待派单**（TASK-10 收口链=TESTER 复跑 v2 判定→协调者验收→TASK-10 DONE→P0 收口，如后续涉 C 将另行派单）。前一条 01:59 巡检见下）"
)

sessions_path = f"{ROOT}/sessions/C.md"
new_sessions = sessions_line + "\n" + open(sessions_path, encoding="utf-8").read()
r = run(["python3", RUNTIME, "run", "--project", ROOT, "--role", "C", "--token", token, "--",
         "python3", "-c", f"open({sessions_path!r}, 'w', encoding='utf-8').write({new_sessions!r})"])
print("sessions write rc", r.returncode)
if r.returncode != 0:
    print(r.stdout, r.stderr)

# 2. event
r = run(["python3", RUNTIME, "event", "--project", ROOT, "--role", "C", "--token", token,
         "--event-id", EVENT_ID, "--task", "TASK-03B", "--attempt", "4", "--status", "NO_CHANGE",
         "--summary", "C 空闲巡检：inbox/3号 无新派单，TESTER E2E 复跑 v2 在途（scratch/t10 驱动产物 01:59），main 453da0c 未动，wt-03b 干净",
         "--evidence", "sessions/C.md", "--next", "等 TESTER 复跑 v2 判定与协调者 TASK-10 收口；无 C 新单保持空闲待派单"])
print("event rc", r.returncode)
if r.returncode != 0:
    print(r.stdout, r.stderr)

# 3. release
r = run(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token])
print("release rc", r.returncode)
if r.returncode != 0:
    print(r.stdout, r.stderr)

# verify
leases = subprocess.run(["find", f"{ROOT}/inbox/control/runtime/leases", "-type", "f", "-size", "+0c"],
                        capture_output=True, text=True).stdout.strip()
print("remaining leases:", leases or "(none)")
print("DONE")