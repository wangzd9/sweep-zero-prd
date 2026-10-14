#!/usr/bin/env python3
"""TESTER 5-min poll: claim -> prepend heartbeat -> release."""
import json
import subprocess
import datetime
import sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "cron-tester-poll-20261012-043053"


def rt(*args):
    p = subprocess.run([sys.executable, RUNTIME, *args], capture_output=True, text=True)
    return p


out = rt("claim", "--project", ROOT, "--role", "TESTER", "--owner", OWNER)
data = json.loads(out.stdout) if out.stdout.strip().startswith("{") else {}
token = data.get("token", "")
print("claim rc=%d token8=%s owner=%s" % (out.returncode, token[:8], OWNER))
if not token:
    print("CLAIM FAILED:", out.stdout, out.stderr)
    sys.exit(1)

now = "2026-10-12 04:31 CST"
line = (
    f"- 心跳：{now}（本轮唤醒=v2 5分钟巡检 preflight checked_at 2026-10-12T04:29:53+08:00 "
    f"control=ACTIVE、legacy_busy 空；TESTER lease {OWNER} claim 成功、短写即释放。"
    f"04:24:53 后共享根 TESTER 范围内零新增（find 仅 runtime ticks 已排除、sessions 各角色心跳、"
    f"events B/C/COORDINATOR 例行 nochange 事件与 C scratch 巡检脚本 c_poll_042353.py——**非 TESTER 派单**）"
    f"+ inbox/TESTER grep status: PENDING rc=1（**无新派单**）。本 TESTER 独立复核：main HEAD "
    f"`453da0c1d88f`=origin/main fetch 双核一致（TASK-10 DONE 被测快照未变，attempt-2 PASS 回执与 "
    f"02:08 ACCEPT decision 持续有效）；协调者 04:25:53 事件 coord-poll-20261012-042553-p0-idle-nochange "
    f"口径=P0 收口空转第23轮五角色全空闲与本核一致；ps 无 t10/ocr/pytest 存活业务进程（ps_rc=1）；"
    f"docker ps -a 无 tester/t10/pm/r2i 残留（docker_rc=1）→ **维持 IDLE，P0 已收口**"
    f"（TASK-10 ✅ DONE 冻结交付不反复自测；TASK-11 生产门禁维持未放行不自动推进）。"
    f"下一步=继续 5 分钟巡检（P0 停止派发口径，无新派单预期；如协调者按 P1/TASK-11 新阶段发派单届时按新 attempt 开工）\n"
)

path = ROOT + "/sessions/TESTER.md"
with open(path) as f:
    content = f.read()
with open(path, "w") as f:
    f.write(line + content)
print("heartbeat written")

rel = rt("release", "--project", ROOT, "--role", "TESTER", "--token", token)
print("release rc=%d" % rel.returncode, rel.stdout.strip()[:120], rel.stderr.strip()[:120])