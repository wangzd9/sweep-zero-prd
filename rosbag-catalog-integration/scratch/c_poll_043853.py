#!/usr/bin/env python3
# C 04:38 巡检：claim -> append sessions + event -> release
import json, subprocess, sys, os

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261012-043853"
EVENT_ID = "C-poll-20261012-043853-nochange"

def sh(args):
    r = subprocess.run(args, capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout, r.stderr

rc, out, err = sh(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
print("claim rc", rc)
if rc != 0:
    print("claim stdout:", out); print("claim stderr:", err)
    sys.exit(0)  # 拿不到租约只核查和报告
token = json.loads(out)["token"]

entry = (
    "- 最后更新：2026-10-12 04:39 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T04:38:53+08:00）、legacy_busy 空；"
    "04:23:53（前条 C 巡检 preflight 时点）后共享根新增核实均为**非 C 范围**：`HANDOFF.md`/`TIMELINE.md` 04:32-04:33（head 核实=协调者 04:25 巡检检查点 cron poll 14ae4556629a：P0 收口后常规空转第 22 轮、04:15:53 后零业务变化、main `453da0c` 双核一致、A/B/C/TESTER 全空闲、TASK-11 生产维持未放行，**协调者范围，非 C**）；"
    "`inbox/3号/` 实测最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED、`inbox/coordinator/` 实测最新仍 02:08:34 e2e-reverify-v2-acceptance-decision（find -printf 核实，均非 C 新单）、**无 C 新派单**；"
    "main HEAD `453da0c`=origin/main 双核一致（rosbag-catalog rev-parse 实测，TASK-10 DONE 已收口，非 C）、"
    "wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 实测 0）、"
    "ps 实测无 C 在途业务进程（wt-03b/scene-03b/t03b/task-03b 命中 0）；"
    "leases 仅 `B.json`（04:38）/`A.json`（04:37）在途（2号/1号巡检业务，非 C 范围，不接管）；"
    f"C 本轮 owner `{OWNER}` claim 成功（token 整体 JSON 解析），事件 `{EVENT_ID}` 落盘后 release；"
    "**保持空闲待派单**（P0 已收口、TASK-11 生产门禁待用户授权，如后续涉 C 将另行派单）。前一条 04:19 巡检见下"
)

rc, out, err = sh(["python3", RUNTIME, "run", "--project", ROOT, "--role", "C", "--token", token,
                   "--", "bash", "-c",
                   f"printf '%s\\n' {json.dumps(entry, ensure_ascii=False)} >> {ROOT}/sessions/C.md && "
                   f"printf '%s\\n' {json.dumps(entry, ensure_ascii=False)} >> {ROOT}/inbox/sessions/C.md"])
print("run append rc", rc, out, err)

rc, out, err = sh(["python3", RUNTIME, "event", "--project", ROOT, "--role", "C", "--token", token,
                   "--event-id", EVENT_ID, "--task", "IDLE", "--attempt", "1",
                   "--status", "IDLE_WAITING", "--summary", "C 04:38 巡检：无新派单，保持空闲待派单（P0 已收口）",
                   "--evidence", "sessions/C.md", "--next", "等协调者派单"])
print("event rc", rc, out, err)

rc, out, err = sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token])
print("release rc", rc, out, err)