import json, subprocess, os, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "coord-poll-cron-14ae4556629a-20261011-161553"

def sh(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL:", " ".join(args), r.stdout, r.stderr)
        sys.exit(1)
    return r.stdout

out = sh(["python3", RUNTIME, "--project", ROOT, "--role", "COORDINATOR",
          "claim", "--owner", OWNER, "--pid", str(os.getpid()), "--ttl", "300"])
data = json.loads(out[out.index("{"):out.rindex("}") + 1])
token = data.get("token")
if not data.get("claimed") or not token:
    print("CLAIM_FAILED:", out)
    sys.exit(2)
print("token acquired")

try:
    cp = """## 2026-10-11 16:20 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T16:15:53+08:00：16:10 后零业务变化，2号 TASK-08 静默窗口约 38 分钟待核活）
- **16:10 后零业务交付**：main HEAD `f9bafb0b44e70e275ba0dd91ca3f0e078e002004`（= origin/main，rev-parse 双核一致）；16:10:53 后共享根新增仅自身 16:15 checkpoint/event 与 A/TESTER 例行心跳，**无新回执/派单/decision/合入**（find -newermt 核实）。
- **2号 TASK-08 attempt-1 静默窗口待核活（不催单不重派，不接管）**：`wt-04a-t08` 15:42:03（pytest 全量 814 nodeids，lastfailed 37）后**零文件变更（约 38 分钟）**；B 最新 events/sessions 停留 15:32/15:25（ACK+开工），但 B cron tick 仍在跳（last_tick 16:08:53 report 模式）、**lease 空无持有**、ps 无 B 侧 pytest 进程、`receipts/TASK-08/` 与 `reports/TASK-08/` 均未出现；B 无在途租约且无存活 PID 可定位，但 5 分钟心跳节奏的 tick 仍在 → 判 **联调在途但活动信号停滞，不能断言已停止**；下轮核：① `wt-04a-t08` 文件 mtime/`__pycache__` 是否恢复推进 ② B 是否落 ACK 后进展事件 ③ 若连续 2 轮（约 10 分钟）仍零活动+零事件，按协议记「活动停滞告警」并核 B 群会话状态，仍不自动接管。base 仍 `62a85bf` 未 rebase `f9bafb0`（I-1 口径联调收尾核对）。
- **角色占用**：B=TASK-08 联调在途（活动信号停滞待核活）；A/C/TESTER 空闲（A 16:07 / C 16:08 / TESTER 16:07-16:10 例行心跳）；无在途 ocr/pytest 业务进程；`ocr.lock`/`coordinator.lock` 0 字节无他角色持有。
- **门禁**：生产启用/真实样本（TASK-09/10/11）维持未放行；强复审 R2I-20261010-06 已 PASS 收口（I-1 已随 `f9bafb0` 关闭）；TASK-08 交付→验收→DONE 后 TASK-10 候选重算。
- 本轮控制动作：claim→巡检核查（find -newermt/rev-parse 双核/wt-04a-t08 mtime+B lease/tick/ps 核活/B events 复核）→prepend 检查点+event→release，**无新派单、无合入、无 OCR、无状态变更**。
- **下一步**：下轮核 2号 TASK-08 活动信号是否恢复（文件 mtime/进展事件/回执）；停滞满 2 轮则记告警核 B 群会话，不自动接管。"""
    sess = os.path.join(ROOT, "sessions/COORDINATOR.md")
    with open(sess, "r", encoding="utf-8") as f:
        cur = f.read()
    with open(sess, "w", encoding="utf-8") as f:
        f.write(cp.strip("\n") + "\n" + cur)
    print("checkpoint written")

    evout = sh(["python3", RUNTIME, "--project", ROOT, "--role", "COORDINATOR",
                "--token", token,
                "event",
                "--event-id", "coord-poll-20261011-161553-t08-silent-window",
                "--task", "TASK-08", "--attempt", "1",
                "--status", "RUNNING",
                "--summary", "巡检：16:10 后零业务变化；main f9bafb0=origin 双核；2号 TASK-08 联调 in-flight 但 wt-04a-t08 自 15:42:03 零文件变更（静默约 38min），B lease 空/tick 16:08 仍在跳/无 pytest 进程/无回执——不催单不接管，下轮核活，停滞 2 轮则记告警",
                "--evidence", "sessions/COORDINATOR.md 16:20 检查点; git rev-parse main f9bafb0; wt-04a-t08 find -newermt 15:42:04 零命中",
                "--next", "下轮核 2号 TASK-08 文件 mtime/进展事件/回执；停滞满 2 轮记活动停滞告警核 B 群会话，不自动接管"])
    print("event done")
finally:
    sh(["python3", RUNTIME, "--project", ROOT, "--role", "COORDINATOR",
        "--token", token, "release"])
    print("released")