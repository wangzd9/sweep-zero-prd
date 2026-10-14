#!/usr/bin/env python3
# 协调者 18:05 巡检：claim → append 检查点 → event → release
import subprocess, json, sys
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-coord-poll-180553"

def rt(*args):
    r = subprocess.run(["python3", RUNTIME, *args], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

rc, out, err = rt("claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER)
print("claim RC", rc, out[-300:], err[-200:])
tok = None
try:
    tok = json.loads(out).get("token")
except Exception:
    pass
if not tok:
    print("NO TOKEN", out, err); sys.exit(1)

head = subprocess.run("git -C /home/wang/work/rosbag-catalog rev-parse HEAD", shell=True, capture_output=True, text=True).stdout.strip()
origin = subprocess.run("git -C /home/wang/work/rosbag-catalog rev-parse origin/main", shell=True, capture_output=True, text=True).stdout.strip()
assert head == origin, "main/origin mismatch: %s %s" % (head, origin)

cp = f"""
## 2026-10-11 18:05 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T18:05:53+08:00：17:45 后零业务交付，2号 t08c-1 编码继续实质推进未 commit）
- **17:45 后零业务交付**：main HEAD `{head}`（= origin/main，rev-parse 双核一致，top1=c3-1 合入 `98f6c88` 已在案）；17:45 后共享根新增仅 C 17:48 nochange 心跳、TESTER 18:05 例行心跳与上轮协调者 event/scratch 记账，**无新回执/派单/decision/合入**（find -newermt 核实）。
- **2号 t08c-1（C1/C2 秒精度专项）编码继续实质推进（不催单不接管，非停滞）**：`wt-04a-t08c` 最新业务写入 `app/services/bootstrap.py` mtime **18:02:27**（本检查 18:05:53 前约 3.5 分钟，活跃），tracked diff 已扩至 **7 文件 +91/-18**（bag_cleanup_service/catalog_ingest/source_service/artifact_service/bootstrap/scripts/clone_published_dataset_records/test_bag_cleanup_concurrency）；HEAD 仍 `f9bafb0` **未 commit**、`receipts/TASK-08/` 仍仅 attempt-1 + c3-1 两份**无交付回执**。注意：diff 已含 `bootstrap.py`/`artifact_service.py`（超出 17:45 检查点记的 2 文件），文件集扩面/秒精度归属**待交付后逐点核对**，本轮不代判。
- **角色占用**：B=RUNNING（t08c-1 编码中，18:02 活跃）；A/C/TESTER 空闲（C 17:48 / TESTER 18:05 例行心跳）；leases 无在途业务持有者；`ocr.lock`/`coordinator.lock` 无他角色在途；ps 无协调侧 ocr/pytest 业务进程。
- **门禁**：生产启用/真实样本（TASK-09/10/11）维持未放行；强复审 R2I-20261010-06 已 PASS 收口（15:18，无新增门禁）；TASK-08 收口 1/2（c3-1 已合入 `98f6c88`），剩 t08c-1 交付→机械核验（C1/C2 全修复点+文件集逐点核对）→串行 OCR 增量（app 行为面）→合入→9 红文件全绿复核→08 DONE→TASK-10 候选重算。
- 本轮控制动作：claim→巡检核查（rev-parse 双核/find -newermt/wt-04a-t08c 全文件 mtime+diff --stat/receipts/ps 复核）→append 检查点+event→release。**无新派单、无状态变更、无合入、无 OCR**。
"""
with open(ROOT + "/sessions/COORDINATOR.md", "a") as f:
    f.write(cp)
print("cp appended")

summary = "17:45后零业务交付(main %s=origin不变)；2号 t08c-1 编码继续实质推进(bootstrap.py mtime 18:02:27 活跃, 7文件+91/-18 含 bootstrap/artifact_service 扩面), 未commit无回执, 越界/秒精度归属待交付逐点核; A/C/TESTER 空闲; 不催单不接管, 无新派单/OCR" % head[:7]
rc, out, err = rt("event", "--project", ROOT, "--role", "COORDINATOR", "--token", tok,
                  "--event-id", "coord-poll-20261011-180553-t08c1-coding-active-nochange",
                  "--task", "TASK-08", "--attempt", "t08c-1", "--status", "RUNNING",
                  "--summary", summary,
                  "--evidence", "wt-04a-t08c git diff --stat 7files +91/-18; bootstrap.py mtime 18:02:27; receipts/TASK-08 无新回执",
                  "--next", "等2号 t08c-1 commit+真MySQL A/B交付回执→机械核验(含C1/C2全修复点+文件集逐点)→串行OCR增量→合入→9红文件全绿复核→TASK-08 DONE→TASK-10候选重算")
print("event RC", rc, out[-200:], err[-300:])

rc, out, err = rt("release", "--project", ROOT, "--role", "COORDINATOR", "--token", tok)
print("release RC", rc, out[-200:], err[-200:])