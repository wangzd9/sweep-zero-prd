import json, subprocess, sys, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261011-231353"

out = subprocess.run([sys.executable, RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER],
                     capture_output=True, text=True, timeout=120)
sys.stdout.write("CLAIM_STDOUT:\n" + out.stdout + "\nCLAIM_STDERR:\n" + out.stderr + "\n")
if out.returncode != 0:
    print("claim failed, rc=%d" % out.returncode)
    sys.exit(1)

token = json.loads(out.stdout)["token"]

# prepend new sessions/C.md checkpoint line
new_line = ("- 最后更新：2026-10-11 23:13 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T23:13:53+08:00）、legacy_busy 空；"
            "23:08:51（前条 C 巡检写入）后共享根唯一新增=`HANDOFF.md` 23:08:51（head 核实=协调者 23:05 巡检检查点：2号 TASK-10 attempt-1 端到端驱动首跑"
            "——1a submission 201 冻结 config_hash `0845b402…`（OK_FROZEN，row19 袋）、1b register source dir 400 \"NAS path resolves outside NAS_LOCAL_ROOT\" "
            "23:05:25 重跑同一失败排查中、wt-04a-t10 零 commit HEAD `ca8730d` 干净、**2号/协调者范围，非 C**）；"
            "`inbox/3号/` 无新文件（find -printf 核实最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、"
            "`inbox/coordinator/` 21:58 后无新增（find 核实为空），**无 C 新派单**；"
            "main HEAD `ca8730d`=origin/main 双核一致（rosbag-catalog rev-parse 核实，2号 TASK-10 在途未交付，非 C 交付）、"
            "wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 排除 .venv 核实为空）、ps 核实无 C 在途业务进程（wt-03b/pytest/ocr review 命中为空）；"
            "leases 无 size>0 在途租约（find -size +0c 核实为空）；"
            "C 本轮 owner `C-cron-poll-20261011-231353` claim 23:13，事件 `C-poll-20261011-231353-nochange` 落盘，控制动作结束释放；"
            "**保持空闲待派单**。前一条 23:08 巡检见下\n")

sp = os.path.join(ROOT, "sessions", "C.md")
with open(sp, "r", encoding="utf-8") as f:
    old = f.read()
assert old.startswith("- 最后更新：2026-10-11 23:08 +08:00"), "sessions head changed unexpectedly"
with open(sp, "w", encoding="utf-8") as f:
    f.write(new_line + old)
print("sessions/C.md updated OK")

evt = os.path.join(ROOT, "events", "C", "C-poll-20261011-231353-nochange.md")
ev = subprocess.run([sys.executable, RUNTIME, "run", "--project", ROOT, "--role", "C", "--token", token,
                     "--", sys.executable, RUNTIME, "event", "--project", ROOT, "--role", "C", "--token", token,
                     "--event-id", "C-poll-20261011-231353-nochange", "--task", "none", "--attempt", "0",
                     "--status", "NO_CHANGE", "--summary", "巡检：23:08 后共享根唯一新增=HANDOFF 协调者 23:05 检查点（2号 TASK-10 在途 1b 400 排查，非 C）；无 C 新派单；main ca8730d 双核一致；wt-03b 干净；无在途进程与租约",
                     "--evidence", "scratch/c_poll_2313.py", "--next", "保持空闲待派单"],
                    capture_output=True, text=True, timeout=120)
sys.stdout.write("EVENT_RC=%d\nEVENT_STDOUT:\n%s\nEVENT_STDERR:\n%s\n" % (ev.returncode, ev.stdout, ev.stderr))
evfile = os.path.join(ROOT, "events", "C", "C-poll-20261011-231353-nochange.md")
print("event file exists:", os.path.exists(evfile))

rel = subprocess.run([sys.executable, RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token],
                     capture_output=True, text=True, timeout=120)
print("RELEASE_RC=%d" % rel.returncode, rel.stdout.strip()[:200], rel.stderr.strip()[:200])