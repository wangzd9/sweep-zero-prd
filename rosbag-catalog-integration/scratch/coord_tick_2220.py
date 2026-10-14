#!/usr/bin/env python3
"""Coordinator 22:20 poll: record inspection checkpoint in sessions/COORDINATOR.md."""
import pathlib

ROOT = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
p = ROOT / "sessions" / "COORDINATOR.md"
t = p.read_text(encoding="utf-8")

NEW_CHECKPOINT = (
    "- 巡检：2026-10-10 22:20 +08:00（cron poll 14ae4556629a，真实 checked_at 22:20:53，"
    "ACTIVE，legacy_busy 空）：与 22:15 检查点**零业务变化**——main HEAD `5f0124b`（=origin/main）"
    "git 复核不变（untracked 诊断脚本与 app.db 为既有环境残留，非业务交付）；"
    "强复审结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` 仍不存在"
    "（reviews/strongmodel 最新 mtime 仅 pack，等用户手动触发，不自行调用付费模型）；"
    "22:15 后业务目录零新文件（find -newermt 复核，仅 sessions/ticks 例行心跳）；"
    "A/B/C/TESTER 全空闲无在途进程（ps 无 ocr/pytest 业务进程），"
    "`ocr.lock`/`coordinator.lock` 无在途；06 聚合放行仍卡强复审一项**保持关闭**。"
    "本轮控制动作：claim→巡检记账→release，无状态变更、无新派单。\n"
)

lines = t.split("\n")
assert lines[0] == "<!-- five-role-v2 -->", "header changed, abort"
assert lines[3].startswith("- 巡检：2026-10-10 22:15"), "line 4 not 22:15 checkpoint, abort"

lines[3] = NEW_CHECKPOINT.rstrip("\n") + "\n" + "## 历史检查点（2026-10-10 22:15，cron poll 14ae4556629a，真实 checked_at 22:15:53）\n" + lines[3].rstrip("\n") + "\n" + "\n".join(lines[4:6])
p.write_text("\n".join(lines), encoding="utf-8")
print("OK checkpoint recorded")