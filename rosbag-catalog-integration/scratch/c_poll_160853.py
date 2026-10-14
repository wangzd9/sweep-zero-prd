import pathlib

root = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")

sessions = root / "sessions" / "C.md"
old = sessions.read_text(encoding="utf-8")

new_line = (
    "- 最后更新：2026-10-11 16:09 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T16:08:53+08:00）、"
    "legacy_busy 空；16:04:00 后共享根唯一新增为 `scratch/a-heartbeat-1607.md` + `scratch/a_append_1607.py`"
    "（find -printf 核实，1号心跳材料，非 C 范围）；`inbox/3号/TASK-03B/` 无新文件（ls 核实最新仍 10-10 00:58 "
    "attempt-4-ocr-rework 已 ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、`inbox/coordinator/` 无面向 3号 新单"
    "（find 核实最新仍 15:48 TASK-05 i1-1-acceptance-decision，1号范围），**无 C 新派单**；"
    "main HEAD 仍 `f9bafb0`（rosbag-catalog rev-parse 核实 main=HEAD 一致）、wt-03b HEAD=`6f1a9ad` 干净"
    "（status --porcelain 排除 .venv 核实为空）、ps 核实无 C 在途进程、leases 无 size>0 在途租约"
    "（find 核实为空）；C 本轮短占用 owner `C-cron-poll-20261011-160853` claim 16:09:42，"
    "控制动作结束释放，事件 `C-poll-20261011-160853-nochange` 已落盘；03/05/06 聚合 DONE，"
    "后续=TASK-08 联调（2号 RUNNING，非 C 范围，联调如需 C 配合将另行派单，当前无单）；"
    "**保持空闲待派单**。前一条 16:04 巡检见下）\n"
)
if new_line.strip()[:40] in old:
    raise SystemExit("already recorded, skip")
sessions.write_text(new_line + old, encoding="utf-8")

event_dir = root / "events" / "C"
event_dir.mkdir(parents=True, exist_ok=True)
event = event_dir / "C-poll-20261011-160853-nochange.md"
event.write_text(
    "# C-poll-20261011-160853-nochange\n\n"
    "- role: C\n"
    "- checked_at: 2026-10-11T16:08:53+08:00\n"
    "- mode: poll\n"
    "- control: ACTIVE\n"
    "- task: 无 C 新派单\n"
    "- status: no_change\n"
    "- evidence: main HEAD f9bafb0; wt-03b 6f1a9ad 干净; inbox/3号 最新仍 10-10 00:58 ACCEPT_MERGED; "
    "inbox/coordinator 最新仍 15:48 TASK-05（1号范围）; 16:04 后共享根新增仅 scratch 1号心跳; 无在途租约/进程\n"
    "- next: 保持空闲待派单；TASK-08 联调（2号 RUNNING）如需 C 配合将另行派单\n",
    encoding="utf-8",
)
print("sessions+event written")