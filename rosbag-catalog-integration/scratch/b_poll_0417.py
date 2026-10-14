#!/usr/bin/env python3
import json, subprocess, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-b-poll-6f7471d8747c-20261012-041753"
EV = "b-poll-20261012-041753-nochange-task10-done-p0-idle"

def sh(args, **kw):
    r = subprocess.run(args, capture_output=True, text=True, **kw)
    return r

# 1. claim（token 必须整体 JSON 解析）
c = sh(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "B", "--owner", OWNER])
sys.stderr.write("claim rc=%d\n%s\n" % (c.returncode, c.stdout[-800:] + c.stderr[-400:]))
if c.returncode != 0:
    print(json.dumps({"ok": False, "stage": "claim"}))
    sys.exit(1)
data = json.loads(c.stdout)
token = data.get("token") or data.get("lease", {}).get("token")
if not token:
    print(json.dumps({"ok": False, "stage": "claim-parse", "raw": c.stdout[:400]}))
    sys.exit(1)

line = ("- 巡检 2026-10-12 04:17 +08:00（cron poll，真实 checked_at 2026-10-12T04:17:53+08:00 preflight）："
        "**无新派单、无返修，TASK-10 已收口 DONE，P0 停止派发——本侧维持 IDLE_WAITING**——"
        "04:07 巡检后零业务变化：inbox/2号 01:20 后仍零新增（t10-defect3 ACK 已收口，无新派单/返修）；"
        "04:07:53 后 find 业务目录零命中（新增仅协调者 04:15 HANDOFF IDLE 巡检检查点，口径与本侧一致：main 453da0c 双核、全角色空闲、无业务进程）；"
        "origin/main fetch 实测 453da0c 双核不变（=TASK-10 收口合入点）；"
        "wt-04a-t10d3 HEAD=0943885 冻结干净（仅 .venv 软链）、ps 无本侧 pytest/ocr/e2e 在途进程；"
        "leases 无 B 在途 owner（仅 C/TESTER 陈旧零字节锁），本回合 claim/release 正常（owner " + OWNER + "，token JSON 整体解析）。"
        "维持 **IDLE_WAITING**，不占开发槽。事件 `" + EV + "` 落盘。"
        "下一步：仅按需巡检与事件接续；TASK-11 生产门禁未放行不自行启动。")

# 2. run：追加 sessions/B.md（仅追加，禁止覆盖）
cmd = 'cat >> "sessions/B.md" <<' + "'" + 'EOL' + "'" + '\n' + line + '\nEOL\n'
r = sh(["python3", RUNTIME, "run", "--project", ROOT, "--role", "B", "--token", token, "--", "bash", "-c", cmd])
sys.stderr.write("run rc=%d\n%s\n" % (r.returncode, (r.stdout + r.stderr)[-600:]))
if r.returncode != 0:
    print(json.dumps({"ok": False, "stage": "run-append"}))
    sys.exit(1)

# 3. event
e = sh(["python3", RUNTIME, "event", "--project", ROOT, "--role", "B", "--token", token,
        "--event-id", EV, "--task", "TASK-10", "--attempt", "1", "--status", "IDLE_WAITING",
        "--summary", "04:07后零业务变化：无新派单无返修，main 453da0c双核，wt-04a-t10d3冻结干净，IDLE_WAITING",
        "--evidence", "sessions/B.md", "--next", "按需巡检；TASK-11生产门禁未放行不自行启动"])
sys.stderr.write("event rc=%d\n%s\n" % (e.returncode, (e.stdout + e.stderr)[-400:]))

# 4. release
rel = sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "B", "--token", token])
sys.stderr.write("release rc=%d\n%s\n" % (rel.returncode, (rel.stdout + rel.stderr)[-300:]))

print(json.dumps({"ok": rel.returncode == 0 and e.returncode == 0, "owner": OWNER, "event": EV}))