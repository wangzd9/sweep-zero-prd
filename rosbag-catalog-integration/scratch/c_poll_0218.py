#!/usr/bin/env python3
"""C 5-min poll 02:18: claim -> event -> sessions update -> release."""
import json
import subprocess
import sys
import time

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261012-021853"


def sh(cmd, check=True):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and r.returncode != 0:
        print("FAILED rc=%d cmd=%s\nstdout=%s\nstderr=%s" % (r.returncode, cmd, r.stdout, r.stderr))
        sys.exit(1)
    return r


# claim: parse whole JSON from output
r = sh("python3 %s claim --project %s --role C --owner %s" % (RUNTIME, ROOT, OWNER), check=False)
print("claim rc=%d" % r.returncode)
if r.returncode != 0:
    print(r.stdout); print(r.stderr); sys.exit(2)
token = None
for line in r.stdout.strip().splitlines():
    line = line.strip()
    if line.startswith("{"):
        try:
            token = json.loads(line).get("token")
            if token:
                break
        except json.JSONDecodeError:
            continue
# fallback: whole stdout may be JSON
if not token:
    try:
        token = json.loads(r.stdout).get("token")
    except Exception:
        pass
if not token:
    # read lease file (same owner)
    lf = ROOT + "/inbox/control/runtime/leases/C.json"
    token = json.load(open(lf)).get("token")
if not token:
    print("no token parsed from claim output:", r.stdout); sys.exit(3)
print("claim ok")

event_id = "C-poll-20261012-021853-nochange"
ev = (
    "python3 %s event --project %s --role C --token %s "
    "--event-id %s --task TASK-03B --attempt 0 --status POLL_NO_CHANGE "
    "--summary 'P0收口后空转巡检：02:14:30后共享根新增仅B/C巡检事件与ticks/sessions/TIMELINE刷新，协调者02:18事件=POLL_NO_CHANGE（A/B/C/TESTER全空闲）；inbox/3号无新文件（最新仍10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B全部派单已收口）、inbox/coordinator无面向3号新单；main 453da0c=origin/main双核一致、wt-03b HEAD 6f1a9ad 干净、ps无C在途业务进程；leases仅B.json在途（2号巡检业务，非C）' "
    "--evidence sessions/C.md --next 'P0已收口，保持空闲待派单'"
) % (RUNTIME, ROOT, token, event_id)
r = sh(ev, check=False)
print("event rc=%d" % r.returncode)
if r.returncode != 0:
    print(r.stdout); print(r.stderr)

sess_line = (
    "- 最后更新：2026-10-12 02:18 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T02:18:53+08:00）、legacy_busy 空；"
    "02:14:30（前条 C 巡检写入）后共享根新增核实均为**非 C 范围**：`events/B/` 02:14 + `sessions/B.md`（2号巡检刷新）、"
    "`events/C/` 02:15（前条 C 自身 nochange 事件）+ `sessions/C.md` 02:15、ticks（COORDINATOR/A/TESTER/B/C 02:15-02:18 巡检刷新）、"
    "`inbox/sessions/A.md` 02:18、`events/COORDINATOR/` 02:18（read 核实=**协调者 02:18:12 事件 `coord-poll-20261012-021553-nochange` status POLL_NO_CHANGE**："
    "P0 收口后空转巡检、main `453da0c`=origin 双核一致、02:01 后零业务事件、A/B/C/TESTER 全空闲无在途进程、TASK-11 生产门禁未放行、07/12/13/14/15 DEFERRED，**协调者范围非 C**）+ "
    "`sessions/COORDINATOR.md`/`TIMELINE.md` 02:18 协调者记账刷新（head 核实 TIMELINE 首条仍 02:0x P0 收口事件，无新业务条目）+ `leases/B.json` 02:18 刷新（2号巡检业务，非 C）；"
    "`inbox/3号/` 无新文件（ls 核实最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、"
    "`inbox/coordinator/` 02:09 后无新文件（find 核实为空），**无 C 新派单**；"
    "main HEAD `453da0c`=origin/main 双核一致（rosbag-catalog rev-parse 实测，非 C 交付）、"
    "wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 实测为空）、"
    "ps 实测无 C 在途业务进程（wt-03b/scene-03b/t03b/task-03b 命中为空）；"
    "leases 仅 `B.json` 在途（225 字节 02:18，2号巡检业务，非 C 范围）；"
    "C 本轮 owner `C-cron-poll-20261012-021853` claim 成功（token 整体 JSON 解析），事件 `C-poll-20261012-021853-nochange` 落盘，控制动作结束释放；"
    "**P0 已收口（协调者 02:08 裁决）：停止派发，C 保持空闲待派单**（TASK-11 待用户独立授权，生产门禁未放行，如后续涉及 C 将另行派单）。前一条 02:14 巡检见下）\n"
)
# write via run wrapper: cp newfile over sessions/C.md
tmp = ROOT + "/scratch/C.md.new"
with open(ROOT + "/sessions/C.md", "r") as f:
    old = f.read()
with open(tmp, "w") as f:
    f.write(sess_line + old)
r = sh(
    'python3 %s run --project %s --role C --token %s -- cp %s %s/sessions/C.md'
    % (RUNTIME, ROOT, token, tmp, ROOT),
    check=False,
)
print("run(cp sessions) rc=%d" % r.returncode)
if r.returncode != 0:
    print(r.stdout); print(r.stderr)
    sys.exit(4)
print("sessions updated")

r = sh("python3 %s release --project %s --role C --token %s" % (RUNTIME, ROOT, token), check=False)
print("release rc=%d" % r.returncode)
if r.returncode != 0:
    print(r.stdout); print(r.stderr)