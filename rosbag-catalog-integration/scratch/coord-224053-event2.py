#!/usr/bin/env python3
"""claim→event(带token)→release，一次跑完"""
import json, subprocess, sys
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "cron-coord-poll-224053"

def sh(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL rc=%d: %s %s" % (r.returncode, " ".join(args[:6]), r.stderr[:200]), file=sys.stderr)
    return r

r = sh([sys.executable, RUNTIME, "claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER, "--pid", "0"])
try:
    token = json.loads(r.stdout.strip()).get("token")
except Exception:
    idx = r.stdout.find("{")
    token = json.loads(r.stdout[idx:]).get("token") if idx >= 0 else None
if not token:
    print("CLAIM FAILED", file=sys.stderr); sys.exit(1)

ev = sh([sys.executable, RUNTIME, "event", "--project", ROOT, "--role", "COORDINATOR",
    "--owner", OWNER, "--token", token,
    "--event-id", "coord-poll-20261011-224053-t10-probes-continuing",
    "--task", "TASK-10", "--attempt", "1", "--status", "POLL_NO_CHANGE",
    "--summary", "5分钟巡检：22:38:30后零交付零合入，main ca8730d 双核一致；2号 TASK-10 attempt-1 在途（探针链至 t10-import-check 22:32，wt-04a-t10 零 commit 干净，距最后工作产物约9min 未达停滞告警口径）；B=RUNNING 不催单不接管；A/C/TESTER 空闲；无在途 ocr/pytest 业务进程。无新派单、无合入、无 OCR。",
    "--evidence", "sessions/COORDINATOR.md",
    "--next", "下轮核 2号 TASK-10 commit/回执 receipts/TASK-10/；若再连续约2轮巡检零变更且 B tick 缺失则记活动停滞告警（不催单不接管）；交付即机械核验→串行 OCR→合入→TESTER 验证→P0 收口。"])
print("EVENT:", ev.stdout.strip() or ev.stderr.strip()[:200])

sh([sys.executable, RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER, "--token", token])
print("OK")