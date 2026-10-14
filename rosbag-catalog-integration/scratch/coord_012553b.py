#!/usr/bin/env python3
import os, subprocess, hashlib, json, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
TOKEN = "eb63b21183c14e1bb4bbdc49433a23d2"
os.chdir(ROOT)

CP = '''## 2026-10-12 01:25 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-12T01:25:53+08:00：01:11 检查点后唯一业务变化=2号 t10-defect3-publish-bounds 01:20 ACK 已开工，编码在途）

- **2号 t10-defect3-publish-bounds ACK 已开工（01:20，RUNNING，不催单不接管）**：`inbox/2号/TASK-10/t10-defect3-publish-bounds-ack.md`（base `a77aa45` fetch 双核一致，新建 `wt-04a-t10d3`@`scene/task-10-defect3-publish-bounds`）；独立实测 `wt-04a-t10d3` 已有 2 个 app 文件修改未 commit（`scene_publish_service.py`+`scene_result_report_service.py`，git status 双核），无 commit、无回执=编码/自测阶段正常在途。
- **main 不变 `a77aa45`**（= origin/main，rev-parse 双核一致）；01:11 后业务目录新增仅 B ACK+worktree 活动（find -newermt 核实）；无 OCR 在途（`ocr.lock` 无持有者、ps 无 ocr/pytest 业务进程）。
- **TESTER 侧不变**：第 1 跑已收口 FAIL（回执 `test-receipts/TEST-TASK10-e2e-reverify/attempt-1.md` 在案），按通知等 #3 合入后复跑 v2（VLM 累计 ≤2 袋，防双跑）；驱动 step5 NameError 已修复，不重启。
- **角色占用**：B=RUNNING（t10-defect3）；A/C/TESTER 空闲（C 01:13 nochange 心跳）；legacy_busy 空。
- **门禁**：TASK-10 维持 🏃 RUNNING（#3 未合入、E2E 复跑 v2 未全绿不得写 DONE）；#3 收口链=2号交付→机械核验→串行 OCR（§3.6 预检）→合入 main（核 base 漂移零冲突）→TESTER 复跑 v2 全绿→**TASK-10 DONE→P0 收口**；TASK-11 生产维持未放行；TASK-07/12/13/14/15 维持 DEFERRED 不扩。
- 本轮控制动作：claim（`cron-coord-poll-20261012-012553`，01:30:29）→巡检核查（rev-parse 双核/wt-04a-t10d3 status+log/ACK 文件/find -newermt 01:15/ps/locks 独立复核）→prepend 检查点（sessions+HANDOFF）+TIMELINE+event→release。**无新派单、无合入、无 OCR、无状态变更**（B ACK 01:20 已落盘，本轮记账）。
- **下一步**：核 2号 t10-defect3 交付回执（`receipts/TASK-10/t10-defect3-publish-bounds.md`+commit）；交付即机械核验→串行 OCR→合入 main（核 base 漂移零冲突）→派 TESTER 复跑 v2 全绿→**TASK-10 DONE→P0 收口**；若连续多轮零活动记停滞告警，不自动接管。
'''

EV = {
    "event_id": "coord-poll-20261012-012553-t10-defect3-ack-running",
    "occurred_at": "2026-10-12T01:30:35+08:00",
    "recorded_at": "2026-10-12T01:30:35+08:00",
    "role": "COORDINATOR",
    "task": "TASK-10",
    "attempt": "t10-defect3-publish-bounds/1",
    "status": "RUNNING_ACKED",
    "summary": "2号 t10-defect3-publish-bounds 01:20 ACK 已开工（base a77aa45 fetch 双核一致，wt-04a-t10d3 新建，2 app 文件已改未 commit=编码在途独立核）；main 不变 a77aa45；TESTER 第 1 跑 FAIL 回执在案，等 #3 合入后复跑 v2；TASK-10 维持 RUNNING",
    "evidence": "inbox/2号/TASK-10/t10-defect3-publish-bounds-ack.md + wt-04a-t10d3 git status 独立核 + test-receipts/TEST-TASK10-e2e-reverify/attempt-1.md",
    "next": "核 2号交付回执→机械核验→串行 OCR→合入 main（核 base 漂移）→TESTER 复跑 v2→TASK-10 DONE→P0 收口"
}

TL = '''
## 2026-10-12 01:30 +08:00（coord-poll-20261012-012553-t10-defect3-ack-running）
- COORDINATOR：01:25:53 preflight 巡检——**2号 t10-defect3-publish-bounds 01:20 ACK 已开工**（base `a77aa45` fetch 双核一致，`wt-04a-t10d3` 新建，`scene_publish_service.py`/`scene_result_report_service.py` 已改未 commit=编码在途独立核）；main 不变 `a77aa45`=origin 双核；无 OCR 在途（`ocr.lock` 无持有者、ps 无业务进程）；TESTER 第 1 跑 FAIL 回执在案（#3 409 定位+step5 NameError 已修），按通知等 #3 合入后复跑 v2（VLM 累计 ≤2 袋）；TASK-10 维持 🏃 RUNNING；A/C 空闲（C 01:13 nochange 心跳）。**无新派单、无合入、无状态变更**；下轮核 2号交付。
'''

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

# sessions/COORDINATOR.md: prepend after first line
s = open("sessions/COORDINATOR.md", encoding="utf-8").read()
first_nl = s.index("\n")
open("sessions/COORDINATOR.md", "w", encoding="utf-8").write(s[:first_nl + 1] + CP + s[first_nl + 1:])

# HANDOFF.md: insert after first line
h = open("HANDOFF.md", encoding="utf-8").read()
lines = h.split("\n", 1)
rest = lines[1] if len(lines) > 1 else ""
open("HANDOFF.md", "w", encoding="utf-8").write(lines[0] + "\n" + CP.strip("\n") + "\n\n" + rest)

# TIMELINE append
with open("TIMELINE.md", "a", encoding="utf-8") as f:
    f.write(TL)

# event by sha256(json) filename convention
evbody = json.dumps(EV, ensure_ascii=False, indent=2)
hname = hashlib.sha256(evbody.encode()).hexdigest()
evpath = os.path.join("events", "COORDINATOR", hname + ".json")
if not os.path.exists(evpath):
    with open(evpath, "w", encoding="utf-8") as f:
        f.write(evbody + "\n")
print("CHECKPOINT_WRITTEN")
print("EVENT", hname)

rc, out, err = run(["python3", RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN])
print("RELEASE", rc, out.strip(), err.strip())