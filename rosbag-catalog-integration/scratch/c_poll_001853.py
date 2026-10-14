import json, subprocess, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
TOKEN = "c185428b579e4f38ad5eab6b56020a7c"
OWNER = "C-cron-poll-20261012-001853"
EID = "C-poll-20261012-001853-nochange"

new_line = ("- 最后更新：2026-10-12 00:18 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T00:18:53+08:00）、legacy_busy 空；"
            "00:13:53（前条 C 巡检 preflight 时点）后共享根 C 范围零新增：`inbox/3号/`、`inbox/coordinator/` find -newermt 核实均为空，**无 C 新派单**（TASK-03B 名下全部派单仍已收口）；"
            "leases 在途 `A.json`/`B.json`（225 字节，1号/2号业务，非 C 范围）；"
            "main HEAD `ca8730d`=origin/main 双核一致（rosbag-catalog rev-parse 实测，1号 t10-defect1/2号 t10-defect2 返修均未合入，非 C）、"
            "wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（git status 实测排除 .venv 为空）、ps 实测无 C 在途业务进程；"
            f"C 本轮 owner `{OWNER}` claim 成功（token 整体 JSON 解析），事件 `{EID}` 落盘，控制动作结束释放；"
            "**保持空闲待派单**。前一条 00:13 巡检见下）")

p = f"{ROOT}/sessions/C.md"
text = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(new_line + "\n" + text)
print("sessions ok")

def rt(*args):
    r = subprocess.run([sys.executable, RUNTIME, *args], capture_output=True, text=True, cwd=ROOT)
    print(r.returncode, args[0], r.stdout.strip()[:400], r.stderr.strip()[:400])

rt("event", "--project", ROOT, "--role", "C", "--token", TOKEN,
   "--event-id", EID, "--task", "none", "--attempt", "0",
   "--status", "NO_CHANGE", "--summary", "00:13:53 后 C 范围零新增，无新派单，保持空闲",
   "--evidence", "find inbox/3号 inbox/coordinator -newermt 00:13:53 为空；main ca8730d 双核；wt-03b 6f1a9ad 干净；ps 无 C 进程",
   "--next", "继续 5 分钟巡检；如协调者派 C 单再 ACK")

rt("release", "--project", ROOT, "--role", "C", "--token", TOKEN)