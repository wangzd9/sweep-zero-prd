#!/usr/bin/env python3
import subprocess, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUN = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261011-193353"
EVENT_ID = "C-poll-20261011-193353-nochange"

def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    print("CMD:", cmd.split(";")[0][:120])
    print(r.stdout.strip()[:500])
    if r.returncode != 0:
        print("STDERR:", r.stderr.strip()[:500])
    return r

# claim
r = sh(f"python3 {RUN} claim --project {ROOT} --role C --owner {OWNER}")
if r.returncode != 0:
    print("CLAIM FAILED - no writes this round")
    sys.exit(1)
out = r.stdout.strip()
import re
m = re.search(r"token[\"':= ]+([A-Za-z0-9_\-]+)", out) or re.search(r"([a-f0-9]{16,})", out)
TOKEN = m.group(1) if m else None
print("TOKEN:", TOKEN)
if not TOKEN:
    print("no token parsed; aborting without release guess")
    sys.exit(2)

# sessions C.md: prepend new entry
sess = ROOT + "/sessions/C.md"
old = open(sess).read()
entry = (
    "- 最后更新：2026-10-11 19:34 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T19:33:53+08:00）、legacy_busy 空；"
    "19:30:13（前条写入）后共享根**零 C 范围业务新增**（全量 find 核实仅各角色 ticks/sessions/巡检 events 与本 scratch 脚本）；"
    "`inbox/3号/` 无新文件（最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、"
    "`inbox/coordinator/` 无面向 3号 新单（find 核实最新仍 19:19:34 t08c-1 decision=ACCEPT_MERGED+POST_MERGE_VERIFICATION_DISPATCHED，2号/测试者范围），"
    "**无 C 新派单**；main HEAD=`0a8ca8a`=origin/main 双核一致（rosbag-catalog rev-parse 核实，t08c-1 合入后未再推进，非 C 交付）、"
    "wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 排除 .venv 核实为空）、ps 核实无 C 在途业务进程（pytest/ocr/wt-03b 均空）；"
    "leases 仅 `inbox/control/runtime/leases/TESTER.json` 在途（206 字节，owner cron-tester-poll-1920 claim 19:22:28，"
    "**测试者合入后 9 红文件全绿复核长测试业务，非 C 范围**，TESTER tick 19:19:53 仍活跃），C 租约无占用；"
    "C 本轮短占用 owner `C-cron-poll-20261011-193353` claim 19:34 控制动作结束释放；**保持空闲待派单**。前一条 19:30 巡检见下）\n"
)
new = entry + old
# run 包裹写入
open(ROOT + "/scratch/c_sessions_new.md", "w").write(new)
wr = sh(f"python3 {RUN} run --project {ROOT} --role C --token {TOKEN} -- cp {ROOT}/scratch/c_sessions_new.md {sess}")
print("sessions write rc:", wr.returncode)

# event
er = sh(f"python3 {RUN} event --project {ROOT} --role C --token {TOKEN} --event-id {EVENT_ID} --task TASK-03B --attempt 4 --status IDLE --summary 巡检无C新派单，main 0a8ca8a 双核一致，wt-03b 干净，TESTER 9红文件复核在途非C范围 --evidence sessions/C.md --next 继续5分钟巡检等待派单")
print("event rc:", er.returncode)

# release
rr = sh(f"python3 {RUN} release --project {ROOT} --role C --token {TOKEN}")
print("release rc:", rr.returncode)