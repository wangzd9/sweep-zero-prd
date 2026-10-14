#!/usr/bin/env python3
"""补落 22:40 巡检 event（claim 已释放，直接 event 子命令带 owner 记录）"""
import subprocess, sys
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
r = subprocess.run([sys.executable, RUNTIME, "event", "--project", ROOT,
    "--role", "COORDINATOR", "--owner", "cron-coord-poll-224053",
    "--event-id", "coord-poll-20261011-224053-t10-probes-continuing",
    "--task", "TASK-10", "--attempt", "1", "--status", "POLL_NO_CHANGE",
    "--summary", "5分钟巡检：22:38:30后零交付零合入，main ca8730d 双核一致；2号 TASK-10 attempt-1 在途（探针链至 t10-import-check 22:32，wt-04a-t10 零 commit 干净，距最后工作产物约9min 未达停滞告警口径）；B=RUNNING 不催单不接管；A/C/TESTER 空闲；无在途 ocr/pytest 业务进程。无新派单、无合入、无 OCR。",
    "--evidence", "sessions/COORDINATOR.md",
    "--next", "下轮核 2号 TASK-10 commit/回执 receipts/TASK-10/；若再连续约2轮巡检零变更且 B tick 缺失则记活动停滞告警（不催单不接管）；交付即机械核验→串行 OCR→合入→TESTER 验证→P0 收口。"],
    capture_output=True, text=True)
print(r.stdout)
print("RC", r.returncode, r.stderr[:300], file=sys.stderr)