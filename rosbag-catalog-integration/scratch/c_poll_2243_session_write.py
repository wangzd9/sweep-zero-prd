#!/usr/bin/env python3
import sys

path = "/home/wang/work/doc/prd/rosbag-catalog-integration/sessions/C.md"
line = (
    "- 最后更新：2026-10-11 22:43 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T22:43:53+08:00）、legacy_busy 空；"
    "22:41（前条巡检写入 `sessions/C.md`）后共享根零新增（find -newermt 22:41 排除 sessions/events/ticks/leases/scratch/control 核实为空）；"
    "`inbox/3号/` 无新文件（find 核实最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、"
    "`inbox/coordinator/` 21:57 后无新增（find 核实最新仍 21:57:39 TASK-09 post-merge decision，测试者/协调者范围，非 C），**无 C 新派单**；"
    "main HEAD `ca8730d`=origin/main 双核一致（rosbag-catalog rev-parse 核实）、"
    "wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 排除 .venv 核实为空）、ps 核实无 C 在途业务进程；"
    "leases 无 size>0 在途租约（find 核实为空）；C 本轮 owner `C-cron-poll-20261011-224353` claim 22:44，"
    "事件 `C-poll-20261011-224353-nochange` 落盘，控制动作结束释放；**保持空闲待派单**。前一条 22:38 巡检见下\n"
)
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
with open(path, "w", encoding="utf-8") as f:
    f.write(line + content)
print("session line prepended")