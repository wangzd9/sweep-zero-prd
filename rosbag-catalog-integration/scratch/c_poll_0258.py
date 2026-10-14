#!/usr/bin/env python3
import json, subprocess, sys, datetime, os

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
owner = f"C-cron-poll-20261012-025853"

def run(args):
    r = subprocess.run([sys.executable, RUNTIME] + args, capture_output=True, text=True)
    return r

# 1) claim
r = run(["claim", "--project", ROOT, "--role", "C", "--owner", owner])
if r.returncode != 0:
    print("CLAIM_FAIL", r.stdout, r.stderr)
    sys.exit(1)
# claim 返回多行 JSON，整体解析取 token
lines = r.stdout.strip().splitlines()
token = None
for i in range(len(lines)):
    for candidate in lines[i:]:
        try:
            data = json.loads("".join(lines[i:]))
            if isinstance(data, dict) and "token" in data:
                token = data["token"]
            break
        except Exception:
            continue
    if token:
        break
if not token:
    print("TOKEN_PARSE_FAIL", r.stdout)
    sys.exit(1)

event_id = f"C-poll-20261012-025853-nochange"
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

# 2) event
ev = run(["event", "--project", ROOT, "--role", "C", "--token", token,
          "--event-id", event_id, "--task", "NONE", "--attempt", "0",
          "--status", "IDLE_WAITING",
          "--summary", "P0 收口后空转巡检：02:53:53 后共享根新增仅他角色巡检 events/sessions/ticks 心跳（B/COORDINATOR 02:55-02:57 nochange、ticks 五角色刷新）与上轮自身 C 事件，零业务文件；inbox/3号 最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED、inbox/coordinator 最新仍 02:08 e2e-reverify-v2 decision，均无 C 新派单；main HEAD 453da0c=origin/main 双核一致；wt-03b HEAD 6f1a9ad 干净（排除 .venv 0）；ps 无 C 在途业务进程；leases 无 size>0 在途租约",
          "--evidence", "scratch/c_poll_0258.py",
          "--next", "保持空闲待派单；如后续涉 C 由协调者另行派单"])
if ev.returncode != 0:
    print("EVENT_FAIL", ev.stdout, ev.stderr)

# 3) sessions append (只追加，禁止 > 覆盖)
line = ("- 最后更新：2026-10-12 02:58 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T02:58:53+08:00）、legacy_busy 空；02:53:53（前条 C 巡检 preflight 时点）后共享根新增核实均为**非 C 范围**：`events/B/` 2 条 + `events/C/` 1 条（前条 C 自身 nochange）+ `events/COORDINATOR/e9a64011…`（cat 核实=协调者 02:55:53 巡检 `coord-poll-20261012-025553-nochange` status IDLE_POLL：P0 收口后空转第 7 轮、main `453da0c` 双核一致、五角色全空闲、无 ocr/pytest 业务进程，协调者范围非 C）+ 各角色 sessions/ticks 巡检刷新（find -newermt 02:53:53 核实，无业务文件新增）；`inbox/3号/` 实测最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED、`inbox/coordinator/` 实测最新仍 02:08 e2e-reverify-v2 decision（ls --time-style 核实，均非 C 新单）、**无 C 新派单**；main HEAD `453da0c`=origin/main 双核一致（rosbag-catalog rev-parse 实测）、wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 排除 .venv 实测 0）、ps 实测无 C 在途业务进程（wt-03b/scene-03b/t03b/task-03b 命中为空）；leases 实测无 size>0 在途租约（find 核实为空）；C 本轮 owner `%s` claim 成功（token 整体 JSON 解析），事件 `%s` 落盘后 release；**保持空闲待派单**（P0 已收口，如后续涉 C 将另行派单）。前一条 02:53 巡检见下\n" % (owner, event_id))
r = subprocess.run(["bash", "-c", "cat >> " + ROOT + "/sessions/C.md"],
                   input=line.encode(), capture_output=True)
print("SESSIONS_APPEND_RC", r.returncode, r.stderr.decode())

# 4) release
rel = run(["release", "--project", ROOT, "--role", "C", "--token", token])
print("RELEASE_RC", rel.returncode, rel.stdout.strip(), rel.stderr.strip())
print("OK")