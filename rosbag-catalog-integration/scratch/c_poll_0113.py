#!/usr/bin/env python3
"""C poll control: claim, sessions append, event, release."""
import json, subprocess, sys

RT = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
INBOX = "/home/wang/work/doc/prd/rosbag-catalog-integration/inbox"
OWNER = "C-cron-poll-20261012-011353"

PROJ = "/home/wang/work/doc/prd/rosbag-catalog-integration"

def rt(*args):
    p = subprocess.run([sys.executable, RT, "--project", PROJ, *args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

claim_out, claim_err = None, ""
for attempt in range(3):
    rc, out, err = rt("--role", "C", "claim", "--owner", OWNER, "--ttl", "300")
    if rc == 0:
        try:
            data = json.loads(out)
            if data.get("claimed"):
                claim_out = data
                break
            raise SystemExit(f"claim not granted: {out} {err}")
        except json.JSONDecodeError:
            raise SystemExit(f"claim non-json: {out} {err}")
    if attempt < 2 and ("BUSY" in err or "BUSY" in out):
        import time; time.sleep(5)
        continue
    raise SystemExit(f"claim fail rc={rc}: {out} {err}")
token = claim_out["token"]
print("claimed", token[:8])

line = (
    "- 最后更新：2026-10-12 01:14 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T01:13:53+08:00）、legacy_busy 空；"
    "01:08:53（前条 C 巡检 preflight 时点）后共享根新增核实均为**非 C 范围**：`inbox/TESTER/TASK-10/e2e-reverify-notice-v1-fail-defect3.md` 01:14"
    "（head 核实=**协调者收口 TESTER E2E 复跑 attempt-1 第 1 跑 FAIL**：/complete-scene 409 根因=**新缺口 #3 app 06B 域**——"
    "`scene_result_report_service.py:895` 区间身份复核误用 header 采集域 start_ns/end_ns 当界而 db3 为存储域（offset≠0 真包必 409），"
    "**已派 2号 `t10-defect3-publish-bounds`（base `a77aa45`）**；驱动 step5 未执行为 harness 已修，复跑 v2 留 #3 合入后，测试者/协调者/2号范围）"
    "+ `inbox/2号/TASK-10/t10-defect3-publish-bounds.md` 01:14（head 通读核实=**2号 P0 最小返修单 PENDING_ACK**：SlicePublishSpec 补 "
    "actual_start_ns/actual_end_ns 存储域边界、_verify_published_files 改用存储域边界+旧记录 fail-closed 409、offset≠0 定向测试，"
    "**收件箱在 2号 目录，非 C**）+ `inbox/coordinator/TASK-06B/t10-defect2-acceptance-decision.md` 01:01（前条已核实=defect2 ACCEPT_MERGED，非 C）"
    "+ `TODO.md` 01:02/`HANDOFF.md` 01:03/`TIMELINE.md` 01:04（协调者记账刷新，find 核实）+ 各角色 sessions/ticks/leases 巡检刷新（find 核实）；"
    "`inbox/3号/` 无新文件（find -newermt 01:08:53 核实为空，最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、"
    "`inbox/coordinator/` 01:08:53 后无新文件（find 核实为空，最新仍 01:01 defect2 decision 2号范围），**无 C 新派单**；"
    "main HEAD `a77aa45`=origin/main 双核一致（rosbag-catalog rev-parse 实测，defect3 未开工非 C）、"
    "wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 实测为空）、ps 实测无 C 在途业务进程；"
    "leases 在途 `A.json`/`B.json`/`COORDINATOR.json`（01:10-01:14 他角色巡检/defect3 ACK 业务，均未到期不接管，非 C 范围）；"
    f"C 本轮 owner `{OWNER}` claim 成功（token 整体 JSON 解析），sessions 更新+事件落盘，控制动作结束释放；"
    "**保持空闲待派单**（2号 t10-defect3 返修在途，如后续涉 C 将另行派单）。前一条 01:08 巡检见下"
)

sess = INBOX + "/sessions/C.md"
with open(sess, encoding="utf-8") as f:
    old = f.read()
with open(sess, "w", encoding="utf-8") as f:
    f.write(line + "\n" + old)
print("sessions appended")

rc, out, err = rt(
    "--role", "C", "event", "--token", token,
    "--event-id", "C-poll-20261012-011353-nochange",
    "--task", "TASK-10", "--attempt", "poll",
    "--status", "NO_CHANGE",
    "--summary", "C 巡检：inbox/3号 与 inbox/coordinator 01:08:53 后无新文件，无 C 派单；共享根新增（defect3 派单/TESTER notice 01:14、defect2 decision 01:01、TODO/HANDOFF/TIMELINE 记账）核实均非 C 范围；main a77aa45=origin/main，wt-03b 6f1a9ad 干净，无 C 在途进程；保持空闲待派单。",
    "--evidence", "find -newermt 01:08:53；rosbag-catalog rev-parse HEAD/origin/main；wt-03b status --porcelain 排除 .venv 空；ps 无 C 进程；leases A/B/COORDINATOR 在途未接管",
    "--next", "继续 5 分钟巡检；defect3 归 2号 不催单不接管",
)
print("event", rc, out.strip()[:300], err.strip()[:300])
if rc != 0:
    raise SystemExit("event failed")

rc, out, err = rt("--role", "C", "release", "--token", token)
print("release", rc, out.strip()[:200], err.strip()[:200])
if rc != 0:
    raise SystemExit("release failed")
print("DONE")