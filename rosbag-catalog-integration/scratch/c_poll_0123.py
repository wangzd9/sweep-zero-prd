import json, subprocess, sys, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
TOKEN = "c61d86342e13495bbac44efe8477fc20"

line = ("2026-10-12T01:24 +08:00 v2 cron 巡检：preflight ACTIVE（checked_at "
        "2026-10-12T01:23:53+08:00）、legacy_busy 空；01:18:03（前条 C 事件 recorded_at）后共享根新增核实均为**非 C 范围**："
        "`inbox/2号/TASK-10/t10-defect3-publish-bounds-ack.md` 01:19（head 核实=**2号 ACK t10-defect3**，收件箱在 2号 目录）"
        "+ `events/B/` b-poll 011253 两条 + COORDINATOR event 1 条（find 核实）+ `HANDOFF.md`/`TODO.md`/`TIMELINE.md`/`sessions/B.md`/`sessions/A.md`/`sessions/TESTER.md` 他角色记账刷新（find 核实）"
        "+ `inbox/control/runtime/` ticks 为本轮 preflight 自身写入、leases 仅 `B.json`（01:19:14 2号巡检 owner cron-b-poll-…-011753，未到期不接管，非 C）；"
        "`inbox/3号/` 无新文件（ls 实测最新仍 10-10 00:58 TASK-03B attempt-4-ocr-rework ACCEPT_MERGED，C 名下全部派单已收口）、"
        "`inbox/coordinator/` 无新目录/文件（ls 实测最新仍 TASK-06B 01:01 defect2 decision 2号范围），**无 C 新派单**；"
        "main HEAD `a77aa45`=origin/main 双核一致（rosbag-catalog rev-parse 实测，defect3 未开工非 C）、"
        "wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 实测 0）、ps 实测无 C 在途业务进程（0）；"
        "C 本轮 owner `C-cron-poll-20261012-012353` claim 成功（token 整体 JSON 解析），sessions 更新+事件落盘，控制动作结束释放；"
        "**保持空闲待派单**（2号 t10-defect3 已 ACK 在途，如后续涉 C 将另行派单）")

sess_path = os.path.join(ROOT, "inbox/sessions/C.md")
with open(sess_path, "r", encoding="utf-8") as f:
    content = f.read()
old_prefix = "- 最后更新：2026-10-12 01:14"
if old_prefix not in content:
    print("FATAL: expected session prefix not found"); sys.exit(1)
content = "- 最后更新：" + line + "。前一条 01:14 巡检见下\n" + content[content.index(old_prefix) + len("- 最后更新："):]
# simpler: rebuild properly
