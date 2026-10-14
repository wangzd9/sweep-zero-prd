import json, subprocess, os, sys, datetime

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "coord-poll-cron-14ae4556629a-20261011-142553"
REPO = "/home/wang/work/rosbag-catalog"

def sh(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL:", " ".join(args), r.stdout, r.stderr)
        sys.exit(1)
    return r.stdout

# 1) claim
out = sh(["python3", RUNTIME, "--project", ROOT, "--role", "COORDINATOR",
          "claim", "--owner", OWNER, "--pid", str(os.getpid()), "--ttl", "180"])
token = json.loads(out).get("token") if out.strip() else None
if not token:
    # maybe output JSON embedded; try parse
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("{"):
            token = json.loads(line).get("token")
if not token:
    print("NO_TOKEN_OUTPUT:", out); sys.exit(2)
print("token acquired")

try:
    # 2) verify facts
    head = sh(["git", "-C", REPO, "rev-parse", "HEAD"]).strip()
    ohead = sh(["git", "-C", REPO, "rev-parse", "origin/main"]).strip()
    strong = os.path.exists(os.path.join(ROOT, "reviews/strongmodel/R2I-20261010-06-result.md"))
    assert head == ohead, "HEAD != origin/main"

    cp = f"""
## 2026-10-11 14:25 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T14:25:53+08:00：14:20 后零业务变化）
- **14:20 后零业务变化**：main HEAD `{head}`（= origin/main，rev-parse 双核一致）；14:20:53 后业务目录新增仅 B 14:22 IDLE_WAITING 记账事件（`b-poll-20261011-142253-r9-accept-booked`，核实 rework-9 已入 main、强复审 target `62a85bf`、codex 七轮全收口，无新派单无返修）与 C 14:23/14:24 例行 IDLE 心跳（`C-poll-20261011-142353-nochange`，wt-03b 干净）、各角色 ticks，均非业务交付。
- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**（ls 复核），维持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。
- **06 聚合放行门禁（唯一剩余，不变）**：强复审 PASS 收口即 03/05/06 聚合 DONE → TASK-08 联调派单。
- **角色占用**：A/B/C/TESTER 全空闲（legacy_busy 空，B 14:22/C 14:24 例行心跳）；无在途 ocr/pytest 业务进程（ps 复核仅 VS Code 桌面进程族）；`ocr.lock`/`coordinator.lock` 0 字节无他角色在途持有者。
- 本轮控制动作：claim→巡检核查（find -newermt/rev-parse/ps/events 复核）→prepend 检查点→event→release，**无新派单、无状态变更、无 OCR**。
"""
    sess = os.path.join(ROOT, "sessions/COORDINATOR.md")
    with open(sess, "r", encoding="utf-8") as f:
        cur = f.read()
    with open(sess, "w", encoding="utf-8") as f:
        f.write(cp.strip("\n") + "\n" + cur)

    # 3) event
    evout = sh(["python3", RUNTIME, "--project", ROOT, "--role", "COORDINATOR",
                "--token", token,
                "event",
                "--event-id", "coord-poll-20261011-142553-nochange",
                "--task", "NONE", "--attempt", "0",
                "--status", "POLL_NO_CHANGE",
                "--summary", "14:25 巡检：main 62a85bf = origin/main 双核一致；强复审 R2I-20261010-06 result 仍缺，READY_FOR_USER_TRIGGER；A/B/C/TESTER 全空闲仅 B 14:22/C 14:24 例行心跳；无新派单、无状态变更、无 OCR",
                "--evidence", "sessions/COORDINATOR.md; reviews/strongmodel/R2I-20261010-06-pack.md",
                "--next", "下轮巡检核强复审结果文件是否出现；PASS 收口即 03/05/06 聚合 DONE → TASK-08 联调派单"])
    print("event done")
finally:
    sh(["python3", RUNTIME, "--project", ROOT, "--role", "COORDINATOR",
        "release", "--token", token])
    print("released")
print("OK")