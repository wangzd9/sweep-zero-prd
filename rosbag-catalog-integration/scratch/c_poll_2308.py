import json, subprocess

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261011-230853"

out = subprocess.run(
    ["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER],
    capture_output=True, text=True,
)
print("claim rc:", out.returncode)
print("claim stdout:", out.stdout.strip()[:500])
print("claim stderr:", out.stderr.strip()[:500])

token = None
try:
    token = json.loads(out.stdout)["token"]
except Exception:
    for ln in out.stdout.strip().splitlines():
        ln = ln.strip()
        if ln.startswith("{"):
            try:
                token = json.loads(ln)["token"]
            except Exception:
                pass
print("token:", token)
if not token:
    raise SystemExit("claim failed, abort")

# event file
event = """# C-poll-20261011-230853-nochange
- event_id: C-poll-20261011-230853-nochange
- role: C
- at: 2026-10-11T23:08:53+08:00
- task: none
- attempt: none
- status: NO_CHANGE
- summary: 22:58:53（前条 C 事件）后共享根新增核实均为非 C 范围：HANDOFF.md 23:05 协调者检查点（2号 TASK-10 attempt-1 端到端驱动首跑 1b register source dir 400 \"NAS path resolves outside NAS_LOCAL_ROOT\" 排查中，wt-04a-t10 零 commit 干净）+ 协调者事件 coord-poll-20261011-225553-t10-driver-building + 各角色 sessions/ticks 巡检刷新；inbox/3号 无新文件（最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 全部派单已收口）、inbox/coordinator 无面向 3号 新单（最新仍 21:57:39 TASK-09 post-merge decision），无 C 新派单；main HEAD ca8730d=origin/main 双核一致（2号 TASK-10 在途未交付，非 C）、wt-03b HEAD 6f1a9ad 干净、ps 无 C 在途业务进程、leases 无 size>0 在途租约；保持空闲待派单
- evidence: sessions/C.md
- next: 等待协调者派单
"""
for evdir in (ROOT + "/events/C", ROOT + "/inbox/events/C"):
    with open(evdir + "/C-poll-20261011-230853-nochange.md", "w") as f:
        f.write(event)

# sessions/C.md: prepend (newest first)
entry = (
    "- 最后更新：2026-10-11 23:08 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T23:08:53+08:00）、legacy_busy 空；"
    "22:58:53（前条 C 事件落盘）后共享根新增核实均为**非 C 范围**：`HANDOFF.md` 23:05（head 核实=协调者 23:05 巡检检查点：2号 TASK-10 attempt-1 端到端驱动首跑——"
    "1a submission 201 冻结 config_hash `0845b402…`、1b register source dir 400 \"NAS path resolves outside NAS_LOCAL_ROOT\" 排查中、"
    "wt-04a-t10 零 commit 干净 HEAD `ca8730d`，属 2号/协调者范围）+ `events/COORDINATOR/coord-poll-20261011-225553-t10-driver-building.md`（22:58 协调者事件：t10_e2e.py 构建中、offset 扫描 7 条 NOT_CONSTANT 观察在案、不催单不接管）"
    "+ 各角色 sessions/ticks 巡检刷新（find 核实）；`inbox/3号/` 无新文件（find -printf 核实最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、"
    "`inbox/coordinator/` 无面向 3号 新单（find 核实最新仍 21:57:39 TASK-09 post-merge decision，测试者/协调者范围），**无 C 新派单**；"
    "main HEAD `ca8730d`=origin/main 双核一致（rosbag-catalog rev-parse 核实，2号 TASK-10 在途未交付，非 C 交付）、"
    "wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 排除 .venv 核实为空）、ps 核实无 C 在途业务进程；"
    "leases 无 size>0 在途租约（find 核实为空）；C 本轮 owner `%s` claim 23:08，事件 `C-poll-20261011-230853-nochange` 落盘，控制动作结束释放；"
    "**保持空闲待派单**。前一条 22:58 巡检见下" % OWNER
)
path = ROOT + "/sessions/C.md"
with open(path) as f:
    old = f.read()
with open(path, "w") as f:
    f.write(entry + "\n" + old)

rel = subprocess.run(
    ["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token],
    capture_output=True, text=True,
)
print("release rc:", rel.returncode)
print("release stdout:", rel.stdout.strip()[:300])
print("release stderr:", rel.stderr.strip()[:300])
print("DONE")