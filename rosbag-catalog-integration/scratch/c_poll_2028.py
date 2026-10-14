import subprocess, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261011-202853"
TOKEN = "5725f4cd45624157b6db30be50c778e5"

line = ("- 最后更新：2026-10-11 20:29 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T20:28:53+08:00）、legacy_busy 空；"
        "20:24:42（前条巡检写入）后共享根业务文件零新增（find -newermt 排除 sessions/events/ticks/leases/scratch/control 核实，仅 inbox/sessions/A、B 巡检刷新）；"
        "`inbox/3号/` 无新文件（ls 核实最新仍 10-10 00:58 TASK-03B/attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、"
        "`inbox/coordinator/` 无面向 3号 新单（find 核实最新仍 19:47 TASK-08 post-merge decision，测试者/协调者范围），**无 C 新派单**；"
        "main HEAD `0a8ca8a`=origin/main 双核一致（rosbag-catalog rev-parse 分核核实，TASK-08 DONE 收口后未再推进，非 C 交付）、"
        "wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 排除 .venv 核实为空）、ps 核实无 C 在途业务进程；"
        "leases size>0 无在途租约（find 核实为空）；C 本轮短占用 owner `C-cron-poll-20261011-202853` claim 20:29:38，控制动作结束释放，"
        "事件 `C-poll-20261011-202853-nochange` 落盘；**保持空闲待派单**。前一条 20:24 巡检见下\n")

# insert after line 1 (top of file, before first existing entry)
path = ROOT + "/sessions/C.md"
with open(path, encoding="utf-8") as f:
    content = f.read()
marker = "# 执行者 C sessions"
if marker in content:
    content = content.replace(marker, marker + "\n" + line, 1)
else:
    content = line + content
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("sessions written")