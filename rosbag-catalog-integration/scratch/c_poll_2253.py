import json, subprocess, sys, os
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261011-225353"
EVENT_ID = "C-poll-20261011-225353-nochange"
SUMMARY = "22:49 后共享根新增核实均为非 C 范围：COORDINATOR 巡检事件 t10-offset-all-running（2号 TASK-10 attempt-1 时间偏移全量扫描在途）+ 各角色 sessions/ticks 巡检刷新；inbox/3号 无新文件（最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 全部派单已收口）、inbox/coordinator 无面向 3号 新单（最新仍 21:57 TASK-09 post-merge decision），无 C 新派单；main HEAD ca8730d=origin/main 双核一致、wt-03b HEAD 6f1a9ad 干净、ps 无 C 在途业务进程、leases 无 size>0 在途租约；保持空闲待派单"

def run(args):
    p = subprocess.run(args, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

rc, out, err = run(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
if rc != 0:
    print("CLAIM_FAIL", rc, out, err)
    sys.exit(0)
token = json.loads(out.strip().splitlines()[-1]) if out.strip() else {}
if isinstance(token, dict):
    token = token.get("token") or token
print("claimed token ok")

# write event file
ev_dir = os.path.join(ROOT, "events", "C")
ev_path = os.path.join(ev_dir, f"{EVENT_ID}.md")
with open(ev_path, "w") as f:
    f.write(f"""# {EVENT_ID}
- event_id: {EVENT_ID}
- role: C
- at: 2026-10-11T22:53:53+08:00
- task: -
- attempt: -
- status: NO_CHANGE
- summary: {SUMMARY}
- evidence: sessions/C.md
- next: 等待协调者派单
""")

# update sessions/C.md: prepend new line
sess = os.path.join(ROOT, "sessions", "C.md")
with open(sess) as f:
    lines = f.readlines()
new_line = (f"- 最后更新：2026-10-11 22:53 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T22:53:53+08:00）、legacy_busy 空；"
            f"22:49（前条 C 事件落盘）后共享根新增核实均为**非 C 范围**：`events/COORDINATOR/coord-poll-20261011-225053-t10-offset-all-running.md`（read 核实=22:35:53 后零交付零合入、main `ca8730d` 双核一致、2号 TASK-10 attempt-1 预检推进至时间偏移全量扫描 `t10-offset-all.py` 22:48 起跑进程实测存活、不催单不接管，协调者/2号范围非 C）+ 各角色 sessions/ticks 巡检刷新；"
            f"`inbox/3号/` 无新文件（find -printf 核实最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、`inbox/coordinator/` 无面向 3号 新单（find 核实最新仍 21:57:39 TASK-09 post-merge decision，非 C），**无 C 新派单**；"
            f"main HEAD `ca8730d`=origin/main 双核一致（rosbag-catalog rev-parse 核实，2号 TASK-10 在途未交付，非 C 交付）、wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 排除 .venv 核实为空）、ps 核实无 C 在途业务进程；"
            f"leases 无 size>0 在途租约（仅 C.lock/TESTER.lock 0 字节历史空文件）；C 本轮 owner `{OWNER}` claim 22:53，事件 `{EVENT_ID}` 落盘，控制动作结束释放；**保持空闲待派单**。前一条 22:49 巡检见下\n")
with open(sess, "w") as f:
    f.write(new_line + "".join(lines))
print("session updated")

rc2, out2, err2 = run(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--owner", OWNER, "--token", str(token)])
print("release", rc2, out2.strip(), err2.strip())