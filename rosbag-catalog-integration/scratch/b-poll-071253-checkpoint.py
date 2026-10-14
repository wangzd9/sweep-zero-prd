#!/usr/bin/env python3
# 执行者B 07:12 巡检：claim -> prepend 检查点 -> release
import subprocess, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-poll-6f7471d8747c-071253"
SESSION = ROOT + "/sessions/B.md"

CKPT = """- 巡检 2026-10-11 07:12 +08:00（cron poll，真实 checked_at 2026-10-11T07:12:53+08:00）：**无新派单、无返修，与 07:07 巡检一致**——07:08 后新增仅各角色 runtime ticks（A/B/C/COORDINATOR/TESTER）与协调者 07:10 nochange 事件（`coord-poll-20261011-071053-nochange`，内容核实=main `6d30a68` 双核一致+强复审结果文件仍不存在+全角色空闲无在途进程+06 聚合门禁保持关闭），无本侧业务文件（find -newermt 核实）；main/origin HEAD rev-parse 实测 `6d30a68`（10-10 22:46，top2=`6d30a68`+`5c854ea`）一致无变化；inbox/2号 最新仍 10-10 22:39 `attempt-1-r2-rework-5`（已收口合入 main `6d30a68` 且 22:57 ACCEPT）；`reviews/strongmodel/` 目录最新 mtime 10-10 22:47 仅 pack，仍无 `R2I-20261010-06-result.md`（**READY_FOR_USER_TRIGGER 等用户手动触发**，pack `R2I-20261010-06-pack.md` target `6d30a68` 在案）；`B.lock` 空、leases 仅 `C.lock`/`TESTER.lock`（他角色零字节无在途 owner），本回合 claim 成功自持 token 落盘即释放；wt-04a（HEAD `4e2158e`）/wt-04a-r5（HEAD `5c854ea`）merge-base 实测均在 main 祖先链冻结，untracked 仅 `.venv`/`tests/test_r2_repro.py`/`.venv`，本侧无在途工作进程。维持 **IDLE_WAITING**：06 聚合放行剩余=强模型增量复审（用户手动）→ 03/05/06 聚合 DONE → TASK-08；空闲不扩需求。
"""

r = subprocess.run([sys.executable, RUNTIME, "claim", "--project", ROOT,
                    "--role", "B", "--owner", OWNER],
                   capture_output=True, text=True)
out = (r.stdout.strip() or r.stderr.strip())
print("claim:", out)
if r.returncode != 0:
    print("claim failed, aborting (no write)")
    sys.exit(1)

token = r.stdout.strip().splitlines()[-1].strip()
if not token or "error" in r.stdout.lower():
    print("no token, aborting (no write)")
    sys.exit(2)

try:
    with open(SESSION, "r", encoding="utf-8") as f:
        content = f.read()
    if "07:12:53+08:00）：" in content and "与 07:07 巡检一致" in content:
        print("checkpoint already present, skip prepend")
    else:
        with open(SESSION, "w", encoding="utf-8") as f:
            f.write(CKPT + content)
        print("checkpoint prepended")
finally:
    r2 = subprocess.run([sys.executable, RUNTIME, "release", "--project", ROOT,
                         "--role", "B", "--token", token],
                        capture_output=True, text=True)
    print("release:", r2.stdout.strip() or r2.stderr.strip())
    sys.exit(r2.returncode)