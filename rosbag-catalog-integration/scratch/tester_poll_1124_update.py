#!/usr/bin/env python3
"""TESTER poll 11:24 heartbeat: pack target updated to b7cee07, maintain IDLE."""
from pathlib import Path

ROOT = Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
sess = ROOT / "sessions" / "TESTER.md"
text = sess.read_text(encoding="utf-8")

new_line = (
    "- 心跳：2026-10-11 11:24 CST（本轮唤醒=v2 5分钟巡检 preflight checked_at 2026-10-11T11:24:53+08:00 "
    "control=ACTIVE、legacy_busy 空、无存活旧 owner；TESTER.lock claim cron-tester-poll-1124 短写即释放。"
    "11:21 后唯一实质变化=协调者 11:22 **pack_update_20261011_1125 已落盘**（reviews/strongmodel/R2I-20261010-06-pack.md，"
    "target 4697be0→`b7cee07`，增量 patch sha256 `27acb3a6f730…`，替代旧版）→ 上轮“pack target 待协调者更新”悬置项**解除**；"
    "`R2I-20261010-06-result.md` 仍不存在，强复审维持 **READY_FOR_USER_TRIGGER（target `b7cee07`，用户手动触发**）。"
    "git 独立复核 main HEAD `b7cee07`（= origin/main，11:18:57 合入，被测快照未再变，attempt-5 证据不失效）；"
    "find 11:19 后共享根变动仅协调者 pack 更新/decision/OCR 批次账与 events 巡检事件（非测试者派单）；"
    "inbox/TESTER/ 无新 PENDING（grep status: PENDING rc=1，r2-final 系列 6 单 TEST_REPORT_PENDING/ACCEPTED，attempt-5 已获协调者 10:07 ACCEPT）；"
    "docker ps -a 无 tester 容器残留 → **维持 IDLE**，不重复启动已完成测试，不自行触发强复审。"
    "下一步=等用户手动触发强复审 R2I-20261010-06 → 协调者裁决 03/05/06 聚合 DONE → TASK-08 联调派单届时 ACK 后按新 attempt 开工）\n"
)
if "cron-tester-poll-1124" in text:
    print("already written, skip")
    raise SystemExit(0)
idx = text.index("- 心跳：")
text = text[:idx] + new_line + text[idx:]
sess.write_text(text, encoding="utf-8")
print("heartbeat written")