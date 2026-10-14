import json, subprocess, sys, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261012-025353"

out = subprocess.run(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER],
                     capture_output=True, text=True)
sys.stdout.write("claim rc=%d\n" % out.returncode)
data = json.loads(out.stdout[out.stdout.index("{"):])
TOKEN = data["token"]
sys.stdout.write("token ok\n")

EVENT_ID = "C-poll-20261012-025353-nochange"

ev = subprocess.run(["python3", RUNTIME, "event", "--project", ROOT, "--role", "C", "--token", TOKEN,
                     "--event-id", EVENT_ID, "--task", "NONE", "--attempt", "0",
                     "--status", "IDLE_WAITING",
                     "--summary", "P0 收口后空转巡检：02:34:30 后共享根新增仅他角色巡检 events/sessions/ticks 心跳与记账，无业务文件；inbox/3号 最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED、inbox/coordinator 最新仍 02:08 e2e-reverify-v2 decision，均无 C 新派单；main HEAD 453da0c=origin/main 双核一致；wt-03b HEAD 6f1a9ad 干净；ps 无 C 在途业务进程；leases 无 size>0 在途租约",
                     "--evidence", "scratch/c_poll_0253.py",
                     "--next", "保持空闲待派单；如后续涉 C 由协调者另行派单"],
                    capture_output=True, text=True)
sys.stdout.write("event rc=%d %s\n" % (ev.returncode, (ev.stdout.strip() or ev.stderr.strip())[-200:]))

path = os.path.join(ROOT, "sessions/C.md")
with open(path, encoding="utf-8") as f:
    content = f.read()
old_lines = content.count("\n")
assert content.startswith("- 最后更新：2026-10-12 02:34 +08:00"), "first line changed, aborting"

sess_line = ("- 最后更新：2026-10-12 02:53 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T02:53:53+08:00）、legacy_busy 空；"
             "02:34:30（前条 C 巡检写入）后共享根新增核实均为**非 C 范围**：`events/B/` 5 条 + `events/C/` 3 条（前条 C 自身 nochange）+ `events/TESTER/` 1 条"
             " + `events/COORDINATOR/coord-poll-20261012-024053-nochange.md`（head 核实=JSON nochange 心跳，协调者 P0 收口后空转第 7 轮，协调者范围）"
             "+ `inbox/events/COORDINATOR/coord-poll-20261012-023553-nochange.md`（head 核实 02:35:53 检查点 nochange）"
             "+ 各角色 sessions/inbox-sessions 巡检刷新（find -newermt 02:34:30 核实，无业务文件新增）；"
             "`inbox/3号/` 实测最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED、`inbox/coordinator/` 实测最新仍 02:08:34 e2e-reverify-v2-acceptance-decision"
             "（find -printf 核实，均非 C 新单）、**无 C 新派单**；main HEAD `453da0c`=origin/main 双核一致（rosbag-catalog rev-parse 实测，TASK-10 DONE 已收口，非 C）、"
             "wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 实测 0）、"
             "ps 实测无 C 在途业务进程（wt-03b/scene-03b/t03b/task-03b 命中为空）；leases 实测无 size>0 在途租约（find 核实为空）；"
             "C 本轮 owner `%s` claim 成功（token 整体 JSON 解析），事件 `%s` 落盘后 release；"
             "**保持空闲待派单**（P0 已收口，如后续涉 C 将另行派单）。前一条 02:34 巡检见下）\n" % (OWNER, EVENT_ID))

rl = subprocess.run(["python3", RUNTIME, "run", "--project", ROOT, "--role", "C", "--token", TOKEN,
                     "--", "sh", "-c", "true"])
sys.stdout.write("run-guard rc=%d\n" % rl.returncode)

with open(path, "r+", encoding="utf-8") as f:
    c = f.read()
    assert c.startswith("- 最后更新：2026-10-12 02:34 +08:00"), "content changed mid-write, aborting"
    f.seek(0)
    f.write(sess_line + c)
    f.truncate()

with open(path, encoding="utf-8") as f:
    new_content = f.read()
sys.stdout.write("lines %d -> %d, head ok=%s\n" % (old_lines, new_content.count("\n"), new_content.startswith("- 最后更新：2026-10-12 02:53")))

release = subprocess.run(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", TOKEN],
                         capture_output=True, text=True)
sys.stdout.write("release rc=%d\n" % release.returncode)