#!/usr/bin/env python3
import subprocess, json, sys
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-coord-poll-175053"

def rt(*args):
    r = subprocess.run(["python3", RUNTIME, *args], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

# re-claim
rc, out, err = rt("claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER)
print("claim RC", rc, out[-300:], err[-200:])
tok = json.loads(out).get("token") if out.strip().startswith("{") else None
if not tok:
    # maybe renew path: try parsing any json
    print("NO TOKEN", out, err); sys.exit(1)

head = subprocess.run("git -C /home/wang/work/rosbag-catalog rev-parse HEAD", shell=True, capture_output=True, text=True).stdout.strip()
origin = subprocess.run("git -C /home/wang/work/rosbag-catalog rev-parse origin/main", shell=True, capture_output=True, text=True).stdout.strip()
assert head == origin

cp = f"""## 2026-10-11 17:55 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T17:50:53+08:00）
- **零业务变化**：main HEAD `{head[:7]}`（= origin/main，rev-parse 双核一致）；17:45 后共享根新增仅 C 17:48 nochange 心跳与上轮协调者 scratch/事件记账（无派单/返修/交付）。
- **2号 t08c-1（C1/C2 秒精度专项）编码继续**：`wt-04a-t08c` 最新业务写入 `tests/test_bag_cleanup_concurrency.py` 17:48:51 / `tests/test_t08c_probe8.py` 17:48:02（活跃，17:45 停滞告警维持解除）；当前 4 业务文件改动 + 1 新 probe 夹具，未 commit 无回执，等交付。
- **08 收口进度**：c3-1 已合入 `98f6c88`（1/2）；剩 t08c-1 交付→机械核验→串行 OCR 增量→合入→9 红文件全绿复核。
- **强复审 R2I-20261010-06**：result 15:18 已收口 **PASS**（CORRECTION 0 / VERIFICATION_GAP I-1 已修复合入 / OUT_OF_SCOPE 0），无新增门禁。
- **角色占用**：B=t08c-1 编码在途；A/C/TESTER 空闲（A 17:28 / C 17:48 nochange 心跳）；leases 无在途持有者；`ocr.lock`/`coordinator.lock` 无他角色在途；无在途 ocr/pytest 业务进程（ps 复核仅 wxocr 桌面）。
- 本轮控制动作：claim→巡检核查→append 检查点+event→release，**无新派单、无状态变更、无 OCR**。
"""
with open(ROOT + "/sessions/COORDINATOR.md", "a") as f:
    f.write(cp)
print("cp appended")

summary = "17:45 后零业务变化：main %s=origin；2号 t08c-1 编码继续（17:48 test_bag_cleanup_concurrency.py/test_t08c_probe8.py 活跃写入，4文件+probe 未commit）；A/C/TESTER 空闲；无新派单/OCR" % head[:7]
rc, out, err = rt("event", "--project", ROOT, "--role", "COORDINATOR", "--token", tok,
                  "--event-id", "coord-poll-20261011-175053-t08c1-encoding-active-nochange",
                  "--task", "TASK-08", "--attempt", "1", "--status", "RUNNING",
                  "--summary", summary,
                  "--evidence", "sessions/COORDINATOR.md",
                  "--next", "等 t08c-1 交付后机械核验+串行 OCR")
print("event RC", rc, out[-200:], err[-300:])

rc, out, err = rt("release", "--project", ROOT, "--role", "COORDINATOR", "--token", tok)
print("release RC", rc, out[-200:], err[-200:])