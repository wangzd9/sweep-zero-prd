#!/usr/bin/env python3
import json, subprocess, datetime, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261011-222853"
EID = "C-poll-20261011-222853-nochange"

now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
ts = now.strftime("%Y-%m-%d %H:%M")
iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

r = sh(f"python3 {RUNTIME} claim --project {ROOT} --role C --owner {OWNER}")
print("CLAIM rc", r.returncode, r.stdout[:600], r.stderr[:400])
s = r.stdout.strip()
i = s.find("{")
tok = json.loads(s[i:]) if i >= 0 else None
token = tok.get("token") if isinstance(tok, dict) else tok
assert token, f"no token: {r.stdout}"
print("TOKEN ok len", len(str(token)))

# event
ev_dir = os.path.join(ROOT, "inbox/events/C")
os.makedirs(ev_dir, exist_ok=True)
ev = f"""# {EID}

- 时间：{iso}
- 角色：C
- 任务：NONE
- 状态：NO_CHANGE
- 摘要：v2 cron 5分钟巡检：preflight ACTIVE（checked_at 2026-10-11T22:28:53+08:00）、legacy_busy 空；22:18:53 后共享根唯一新增为 `events/TESTER/` 22:26 TESTER nochange 巡检事件（read 核实：TESTER 空闲待派单，2号 TASK-10 attempt-1 长任务在途，非 C 范围）；`inbox/3号/`、`inbox/coordinator/` 无新文件（find 核实），**无 C 新派单**；main HEAD `ca8730d`=origin/main 双核一致（rosbag-catalog rev-parse 核实，TASK-10 2号在途未交付，非 C 交付）、wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 核实为空）、ps 核实无 C 在途业务进程；leases 无 size>0 在途租约（find 核实为空）
- 下一步：保持空闲待派单，继续 5 分钟巡检核查 `inbox/3号` 与 `inbox/coordinator` 新派单
"""
with open(os.path.join(ev_dir, EID + ".md"), "w") as f:
    f.write(ev)
print("event written")

# sessions prepend
sp = os.path.join(ROOT, "sessions/C.md")
line = (f"- 最后更新：{ts} +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T22:28:53+08:00）、legacy_busy 空；"
        f"22:18:53 后共享根唯一新增=`events/TESTER/` 22:26 TESTER nochange 巡检事件（read 核实=TESTER 空闲待派单、2号 TASK-10 在途，**非 C 范围**）；"
        f"`inbox/3号/` 无新文件（find 核实最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、"
        f"`inbox/coordinator/` 无面向 3号 新单（find 核实），**无 C 新派单**；main HEAD `ca8730d`=origin/main 双核一致"
        f"（rosbag-catalog rev-parse 核实，TASK-10 2号在途未交付，非 C 交付）、wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净"
        f"（status --porcelain 排除 .venv 核实为空）、ps 核实无 C 在途业务进程；leases 无 size>0 在途租约（find 核实为空）；"
        f"C 本轮 owner `{OWNER}` claim，事件 `{EID}` 落盘，控制动作结束释放；**保持空闲待派单**。前一条 22:18 巡检见下\n")
with open(sp) as f:
    old = f.read()
with open(sp, "w") as f:
    f.write(line + old)
print("sessions updated")

r2 = sh(f"python3 {RUNTIME} release --project {ROOT} --role C --token {json.dumps(str(token))}")
print("RELEASE rc", r2.returncode, r2.stdout[:300], r2.stderr[:300])