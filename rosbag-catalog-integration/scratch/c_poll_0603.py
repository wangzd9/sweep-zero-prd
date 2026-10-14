#!/usr/bin/env python3
# C 轮询控制脚本：claim -> append sessions/C.md -> event -> release
import io, json, os, subprocess, sys, tempfile

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261012-060353"
EVENT_ID = "C-poll-20261012-060353-nochange"
SESSIONS = os.path.join(ROOT, "sessions/C.md")

def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

# 1. claim（token 整体 JSON 解析，禁止 tail/grep 截取）
rc, out, err = sh([sys.executable, RUNTIME, "claim", "--project", ROOT,
                   "--role", "C", "--owner", OWNER])
if rc != 0:
    print("CLAIM_FAILED rc=%d out=%s err=%s" % (rc, out, err))
    sys.exit(2)
data = json.loads(out.strip().splitlines()[-1]) if out.strip() else json.loads(out)
# claim 可能输出多行，取最后一个可解析 JSON 对象
token = None
for line in reversed(out.strip().splitlines()):
    line = line.strip()
    if line.startswith("{"):
        try:
            token = json.loads(line).get("token") or json.loads(line).get("lease", {}).get("token")
        except Exception:
            token = None
        if token:
            break
if not token:
    # 回退：读 lease 文件同源取 token
    lf = os.path.join(ROOT, "inbox/control/runtime/leases/C.json")
    with io.open(lf, "r", encoding="utf-8") as f:
        token = json.load(f).get("token")
if not token:
    print("NO_TOKEN out=%s" % out)
    sys.exit(3)
print("CLAIM_OK")

# 2. 组装新条目（正文无行内反引号，双引号内转义）
ENTRY = (
    "- 最后更新：2026-10-12 06:03 +08:00（v2 cron 巡检：preflight ACTIVE"
    "（checked_at 2026-10-12T06:03:53+08:00）、legacy_busy 空；05:53:32"
    "（上一在案 C 事件 occurred_at）后共享根 C 范围零新增（find -newermt 05:38"
    " 排除 sessions/events/ticks/leases/scratch/inbox-sessions/inbox-events 核实，"
    "唯一新增 HANDOFF.md 06:02:21=head 核实=协调者 06:00:53 巡检检查点 cron poll "
    "14ae4556629a：P0 收口后常规空转第 38 轮、05:55:53 后零业务变化、main "
    "453da0c 双核一致、五角色全空闲、TASK-11 生产门禁维持未放行，协调者范围非 C）；"
    "补记：05:48:53 巡检回合（另一 C cron 会话）事件 C-poll-20261012-054853-nochange"
    " 05:53:32 落盘（cat 核实=NO_CHANGE：C 范围零新增、main 453da0c1 双核、wt-03b "
    "6f1a9ad4 干净、无 C 在途进程）但其 sessions 条目未落盘（sessions/C.md 无 05:48"
    " 条目、grep 实测），本条补记，未重复该轮业务；"
    "inbox/3号 与 inbox/coordinator 05:38 后 find -newermt 核实均无新文件"
    "（inbox/3号 最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，"
    "C 名下全部派单已收口）、**无 C 新派单**；main HEAD 453da0c=origin/main"
    " 双核一致（rosbag-catalog rev-parse 实测 06:03，非 C 交付）、wt-03b HEAD="
    "6f1a9ad 分支 feature/scene-03b-ocr-rework 干净（status --porcelain 排除 "
    ".venv 实测 0）、ps 实测无 C 在途业务进程（wt-03b/scene-03b/t03b 命中 0）；"
    "leases 无 size>0 在途租约（find 实测仅 C.lock/TESTER.lock 0 字节历史空文件）；"
    "C 本轮 owner C-cron-poll-20261012-060353 claim 成功（token 整体 JSON 解析），"
    "事件 C-poll-20261012-060353-nochange 落盘后 release；**保持空闲待派单**"
    "（P0 已收口、TASK-11 生产门禁待用户授权，如后续涉 C 将另行派单）。"
    "前一条 05:38 巡检见下"
)

# 先读、先算、先校验——TARGET 最后一次性原子写入
with io.open(SESSIONS, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()
first_sig = lines[0][:12] if lines else ""
new_content = ENTRY + "\n" + "\n".join(lines) + "\n"
if first_sig and first_sig not in new_content:
    print("ABORT_SIGN_MISSING")
    sh([sys.executable, RUNTIME, "release", "--project", ROOT,
        "--role", "C", "--token", token])
    sys.exit(4)
# 临时 TARGET 干跑：写入 scratch 临时文件并做全部签名/行数核验
TMP = os.path.join(os.path.dirname(SESSIONS), "C.md.new-0603")
with io.open(TMP, "w", encoding="utf-8") as f:
    f.write(new_content)
with io.open(TMP, "r", encoding="utf-8") as f:
    check = f.read().splitlines()
n2 = len(check)
assert n2 == len(lines) + 1, "LINECOUNT %d -> %d" % (len(lines), n2)
assert check[0].startswith(ENTRY[:30]), "HEAD_MISMATCH"
assert check[1] == lines[0], "SECOND_MISMATCH"
# 核验通过后才原子替换真实文件
os.replace(TMP, SESSIONS)
print("SESSIONS_OK lines=%d" % n2)

# 3. event
ev = {
    "event_id": EVENT_ID,
    "occurred_at": "2026-10-12T06:03:53+08:00",
    "role": "C",
    "task": "TASK-03B",
    "attempt": "0",
    "status": "POLL_NO_CHANGE",
    "summary": "06:03:53巡检：C范围零新增，inbox/3号与inbox/coordinator无新文件，无C新派单；HANDOFF 06:02=协调者06:00:53空转第38轮检查点（非C）；补记05:48:53事件在案但sessions条目缺失；main 453da0c=origin/main双核、wt-03b 6f1a9ad干净、无C在途进程、leases无在途租约",
    "evidence": "sessions/C.md",
    "next": "保持空闲待派单",
}
rc, out, err = sh([sys.executable, RUNTIME, "event", "--project", ROOT,
                   "--role", "C", "--token", token,
                   "--event-id", EVENT_ID,
                   "--task", "TASK-03B", "--attempt", "0",
                   "--status", "POLL_NO_CHANGE",
                   "--summary", ev["summary"],
                   "--evidence", ev["evidence"],
                   "--next", ev["next"]])
if rc != 0:
    print("EVENT_FAILED rc=%d out=%s err=%s" % (rc, out, err))
    sys.exit(5)
print("EVENT_OK")

# 4. release
rc, out, err = sh([sys.executable, RUNTIME, "release", "--project", ROOT,
                   "--role", "C", "--token", token])
if rc != 0:
    print("RELEASE_FAILED rc=%d out=%s err=%s" % (rc, out, err))
    sys.exit(6)
print("RELEASE_OK")
print("DONE")