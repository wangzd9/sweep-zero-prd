import json, subprocess, sys, os

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "cron-poll-14ae4556629a-131053"

def sh(*a):
    r = subprocess.run(a, capture_output=True, text=True)
    print("CMD:", " ".join(a[:6]))
    if r.returncode != 0:
        print("RC:", r.returncode, "STDERR:", r.stderr[:500], "STDOUT:", r.stdout[:500])
    return r

tok = sh("python3", RUNTIME, "claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER)
token = tok.stdout.strip().splitlines()[-1].strip() if tok.returncode == 0 and tok.stdout.strip() else None
print("TOKEN_OK:", bool(token), "tail:", (token or "")[-8:])
if not token:
    sys.exit(1)

cp = f"""## 2026-10-11 13:10 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T13:10:53+08:00：13:00 后零业务变化）
- **13:00 后零业务变化**：main HEAD `65ca0beb0111a2d45065206886d432bd20eb76d0`（= main = origin/main，rev-parse 三核一致）；13:00:53 后业务目录新增仅 B 13:02/13:07 两条例行 IDLE_WAITING 心跳（`b-poll-20261011-130253-nochange`/`b-poll-20261011-130753-nochange`，均报无新派单无返修、强复审 result 仍缺，非业务交付）与各角色 runtime ticks。
- **强复审 R2I-20261010-06**：结果文件 `reviews/strongmodel/R2I-20261010-06-result.md` **仍不存在**（目录最新 12:31 pack，target `65ca0be`），维持 **READY_FOR_USER_TRIGGER，等用户手动触发**，不自行调用付费模型。
- **06 聚合放行门禁（唯一剩余，不变）**：强复审 R2I-20261010-06 → PASS 收口即 03/05/06 聚合 DONE → TASK-08 联调派单。
- **角色占用**：A/B/C/TESTER 全空闲（legacy_busy 空；B 13:02/13:07 例行心跳）；无在途 ocr/pytest 业务进程（ps 复核无匹配）；`ocr.lock`(12:28)/`coordinator.lock` 0 字节无他角色在途持有者。
- 本轮控制动作：claim→巡检核查（find -newermt/rev-parse/ps/locks/事件复核）→append 检查点→event→release，**无新派单、无状态变更、无 OCR**。
"""
sf = os.path.join(ROOT, "sessions/COORDINATOR.md")
with open(sf) as f: old = f.read()
with open(sf, "w") as f: f.write(cp + "\n" + old)
print("CHECKPOINT_WRITTEN")

sh("python3", RUNTIME, "event", "--project", ROOT, "--role", "COORDINATOR",
   "--token", token, "--event-id", "coord-poll-20261011-131053-nochange",
   "--task", "NONE", "--attempt", "0", "--status", "NOCHANGE",
   "--summary", "13:00后零业务变化；main 65ca0be 三核一致；强复审R2I-20261010-06 result仍缺维持READY_FOR_USER_TRIGGER；B 13:02/13:07例行心跳；无在途进程/锁",
   "--evidence", "sessions/COORDINATOR.md",
   "--next", "等强复审用户手动触发或新交付")
sh("python3", RUNTIME, "release", "--project", ROOT, "--role", "COORDINATOR", "--token", token)
print("DONE")