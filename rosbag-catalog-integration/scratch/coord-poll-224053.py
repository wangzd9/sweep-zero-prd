#!/usr/bin/env python3
"""coord poll 22:40:53 短控制run：claim→巡检记录→checkpoint+event→release"""
import json, subprocess, sys, datetime

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "cron-coord-poll-224053"

def sh(args):
    r = subprocess.run(args, capture_output=True, text=True)
    print("$", " ".join(args), file=sys.stderr)
    if r.stdout.strip():
        print(r.stdout)
    if r.returncode != 0:
        print("STDERR:", r.stderr, file=sys.stderr)
    return r

# 1) claim
r = sh([sys.executable, RUNTIME, "claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER, "--pid", "0"])
out = r.stdout.strip()
token = None
try:
    d = json.loads(out)
    token = d.get("token")
except Exception:
    idx = out.find("{")
    if idx >= 0:
        try:
            token = json.loads(out[idx:]).get("token")
        except Exception:
            pass
if not token:
    print("CLAIM_FAILED no token", file=sys.stderr)
    sys.exit(1)

def run_tok(args_after):
    return sh([sys.executable, RUNTIME, "run", "--project", ROOT, "--role", "COORDINATOR", "--token", token, "--"] + args_after)

# 2) checkpoint append (via small python through run)
ckpt = f'''## 2026-10-11 22:40 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T22:40:53+08:00：2号 TASK-10 attempt-1 在途预检/起步，零交付零合入）
- **22:38:30 后零业务交付**：main HEAD `ca8730d`（= origin/main，rev-parse 双核一致）；共享根 22:38:30 后新增仅 C 22:38:53 nochange 心跳与 TESTER/A 例行 tick，**无新回执/派单/decision/合入**（find -newermt 核实）。
- **2号 TASK-10 attempt-1 在途（B=RUNNING）**：ACK 22:04 后推进链=wt-04a-t10 建立 22:04 → scratch 探针 t10-probe-api/t10-probe2（22:23）→ t10-vlm-reach（22:31）→ t10-import-check（22:32，wt 内 slope 模块 pyc 编译 22:32），**零 commit、worktree 干净（仅 .venv 软链）**；B 最后 tick 22:28:53（report），距本轮检查约 12min、距最后工作产物约 9min——**未达停滞告警口径（连续 3 轮巡检零变更），不催单不接管**；ps 无 t10 专属 python 业务进程在途（长任务后台驱动未起或处于非 python 步骤，下轮继续核）。
- **角色占用**：B=RUNNING（TASK-10）；A/C/TESTER 空闲（例行 tick 22:34/22:38/22:41）；leases 无他角色在途业务持有（C/TESTER 空文件属例行）；`ocr.lock`/`coordinator.lock` 无在途；ps 无协调侧 ocr/pytest 业务进程。
- **门禁**：TASK-10 为 P0 收尾单，交付即机械核验→串行 OCR（如有 app 面）→验收合入→TESTER 合入后验证→**P0 停止派发**；TASK-11 生产门禁维持未放行（外部 VLM 500 帧缺陷已记 TASK-11 前置事实）。
- 本轮控制动作：claim→巡检核查（rev-parse 双核/find -newermt/wt-04a-t10 mtime+status/ps/locks/B 探针链复核）→append 检查点+event→release。**无新派单、无状态变更、无合入、无 OCR**。
'''
with open(ROOT + "/sessions/COORDINATOR.md", "a") as f:
    f.write("\n" + ckpt)

# 3) event
ev = {
    "event_id": "coord-poll-20261011-224053-t10-probes-continuing",
    "role": "COORDINATOR",
    "task": "TASK-10",
    "attempt": 1,
    "status": "POLL_NO_CHANGE",
    "summary": "5分钟巡检：22:38:30后零交付零合入，main ca8730d 双核一致；2号 TASK-10 attempt-1 在途（探针链至 t10-import-check 22:32，wt-04a-t10 零 commit 干净，距最后工作产物约9min 未达停滞告警口径）；B=RUNNING 不催单不接管；A/C/TESTER 空闲；无在途 ocr/pytest 业务进程。无新派单、无合入、无 OCR。",
    "evidence": "sessions/COORDINATOR.md",
    "next": "下轮核 2号 TASK-10 commit/回执 receipts/TASK-10/；若再连续约2轮巡检零变更且 B tick 缺失则记活动停滞告警（不催单不接管）；交付即机械核验→串行 OCR→合入→TESTER 验证→P0 收口。",
}
run_tok(["event", "--project", ROOT, "--role", "COORDINATOR",
         "--owner", OWNER, "--event-id", ev["event_id"], "--task", ev["task"],
         "--attempt", str(ev["attempt"]), "--status", ev["status"],
         "--summary", ev["summary"], "--evidence", ev["evidence"], "--next", ev["next"]])

# 4) release
sh([sys.executable, RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER, "--token", token])
print("OK done")