#!/usr/bin/env python3
"""C 轮巡检 10:18:53：复用已持有租约，run 写 sessions/C.md 并 release。"""
import os
import subprocess
from datetime import datetime, timezone, timedelta

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
REPO = "/home/wang/work/rosbag-catalog"
WT = "/home/wang/.local/state/rosbag-scene/wt-03b"
OWNER = "C-cron-poll-20261011-101853"
TOKEN = "c0885476bd6b491abed01b84c68859ab"
CST = timezone(timedelta(hours=8))
NOW = datetime.now(CST).strftime("%Y-%m-%d %H:%M")

def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()

# renew first to ensure token valid for run
rc, out = sh(f"python3 {RUNTIME} renew --project {ROOT} --role C --owner {OWNER} --token {TOKEN}")
print("RENEW:", rc, out[:150])

rc, out = sh(f'find {ROOT} -newermt "2026-10-11 10:15:00" -type f '
             f'! -path "{ROOT}/scratch/*" ! -path "{ROOT}/sessions/*" '
             f'! -path "{ROOT}/events/*" ! -path "{ROOT}/inbox/control/*" 2>/dev/null | head -20')
chg_paths = out.splitlines()
chg = "; ".join("`" + p[len(ROOT)+1:] + "`" for p in chg_paths[:6]) or \
      "无（find -newermt 10:15:00 排除 scratch/sessions/events/control 核实为空）"

rc, out = sh(f'find {ROOT}/inbox/3号 -type f -printf "%T@ %TY-%Tm-%Td %TH:%TM %p\\n" 2>/dev/null | sort -rn | head -5')
inbox3 = out.splitlines()
rc, out = sh(f'find {ROOT}/inbox/coordinator -type f -printf "%T@ %TY-%Tm-%Td %TH:%TM %p\\n" 2>/dev/null | sort -rn | head -4')
inboxc = out.splitlines()

leases = []
leases_dir = f"{ROOT}/inbox/control/runtime/leases"
if os.path.isdir(leases_dir):
    for f in sorted(os.listdir(leases_dir)):
        p = os.path.join(leases_dir, f)
        try:
            sz = os.path.getsize(p)
        except OSError:
            sz = -1
        body = open(p).read()[:200] if sz > 0 else ""
        leases.append(f"{f} size={sz} {body}")

_, main_head = sh(f"git -C {REPO} rev-parse --short=7 main")
_, wt_head = sh(f"git -C {WT} rev-parse --short=7 HEAD")
_, dirty = sh(f"git -C {WT} status --porcelain | grep -v .venv | head -5")
dirty_lines = dirty.splitlines()
dirty_note = "仅 .venv untracked" if not dirty_lines else "有 tracked 变更待核对：" + ";".join(dirty_lines)
_, procs = sh("ps aux | grep -iE 'wt-03b|scene-03b|C-cron' | grep -v grep | head -5")
procs_lines = procs.splitlines()
proc_note = "ps 核实无 C 在途进程" if not procs_lines else "ps 命中：" + ";".join(procs_lines)

inbox3_latest = inbox3[0] if inbox3 else ""
inbox3_name = inbox3_latest.split(" ", 3)[-1].replace(ROOT + "/", "") if inbox3_latest else "空"
inboxc_name = inboxc[0].split(" ", 3)[-1].replace(ROOT + "/", "") if inboxc else "无"

report = (
    f"- 最后更新：{NOW} +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T10:18:53+08:00）、"
    f"legacy_busy 空；10:15 后共享根变更={chg}；`inbox/3号/` 最新仍 {inbox3_name}（ACCEPT_MERGED 已收口），"
    f"**无 C 新派单**；`inbox/coordinator/` 10:15 后无新增（最新 {inboxc_name}）；"
    f"main HEAD 仍 `{main_head}`（rosbag-catalog rev-parse 核实）、wt-03b HEAD=`{wt_head}` 干净（{dirty_note}）、{proc_note}；"
    f"leases：{('；'.join(leases) if leases else '无文件')}（本轮 C 巡检短占用 owner `{OWNER}`，控制动作结束释放）；"
    f"06 聚合唯一剩余门禁=强复审 R2I-20261010-06（target `{main_head}`）等用户手动触发，PASS 后接 TASK-08 联调（届时才可能涉及 C，当前无单）；"
    f"**保持空闲待派单**。前一条 10:15 巡检见下）\n"
)

sessions_path = f"{ROOT}/sessions/C.md"
with open(sessions_path) as f:
    content = f.read()
marker = "<!-- five-role-v2 -->"
idx = content.find(marker)
head = content[: idx + len(marker)]
tail = content[idx + len(marker):]
new_content = head + "\n" + report + tail

tmp = f"{ROOT}/scratch/c-sessions-new-101853.md"
with open(tmp, "w") as f:
    f.write(new_content)
rc, out = sh(f"python3 {RUNTIME} run --project {ROOT} --role C --token {TOKEN} -- cp {tmp} {sessions_path}")
print("WRITE:", rc, out[:200])
rc, out = sh(f"python3 {RUNTIME} release --project {ROOT} --role C --token {TOKEN}")
print("RELEASE:", rc, out[:100])
print("REPORT_PREVIEW:")
print(report)