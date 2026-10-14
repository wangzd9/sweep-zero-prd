#!/usr/bin/env python3
"""Prepend one C poll checkpoint line into sessions/C.md after the v2 marker."""
from pathlib import Path

root = Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
p = root / "sessions" / "C.md"
text = p.read_text(encoding="utf-8")
marker = "<!-- five-role-v2 -->\n"
assert marker in text, "v2 marker not found"

line = (
    "- 最后更新：2026-10-11 09:04 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T09:03:53+08:00）、"
    "legacy_busy 空；08:58:53 后共享根变更仅 2号 范围（`reviews/codex-r6-fullchain-20261010-verdict.md` 裁决 + "
    "`inbox/2号/TASK-06B/attempt-1-r2-rework-6.md` 派单，owner 2号，非 C 范围）；`inbox/3号/` 无新文件"
    "（find -newermt 2026-10-10 00:59 核实为空，仍仅已收口目录 TASK-03B 4 个旧单，最新 10-10 00:58 "
    "attempt-4-ocr-rework 已 ACCEPT_MERGED），**无 C 新派单**；main HEAD 仍 `6d30a68`（rosbag-catalog "
    "rev-parse 核实）；wt-03b HEAD=`6f1a9ad` 干净（仅 .venv untracked）、ps 核实无 C 在途进程；"
    "锁文件均 0 字节、无在途租约（本轮 C 巡检短占用 owner `C-cron-poll-20261011-090353`，控制动作结束释放）；"
    "06 聚合唯一剩余门禁=强复审 R2I-20261010-06（target `6d30a68`）等用户手动触发，非 C 范围；"
    "**保持空闲待派单**。前一条 08:59 巡检见下）\n"
)

idx = text.index(marker) + len(marker)
new_text = text[:idx] + line + text[idx:]
p.write_text(new_text, encoding="utf-8")
print("OK: appended C poll checkpoint to sessions/C.md")