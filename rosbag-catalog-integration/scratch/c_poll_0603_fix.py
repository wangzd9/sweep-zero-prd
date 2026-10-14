#!/usr/bin/env python3
# 续跑：claim 已在本会话持有（lease 文件 owner 匹配），读 lease 取 token 完成写入
import io, json, os, subprocess, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261012-060353"
EVENT_ID = "C-poll-20261012-060353-nochange"
SESSIONS = os.path.join(ROOT, "sessions/C.md")

def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

# 读 lease 文件取 token（owner 匹配校验）
lf = os.path.join(ROOT, "inbox/control/runtime/leases/C.json")
with io.open(lf, "r", encoding="utf-8") as f:
    lease = json.load(f)
assert lease.get("owner") == OWNER, "OWNER_MISMATCH %s" % lease.get("owner")
token = lease.get("token")
assert token, "NO_TOKEN"
print("LEASE_OK")

ENTRY = (
    "- 最后更新：2026-10-12 06:06 +08:00（v2 cron 巡检：preflight ACTIVE"
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
    "leases 无 C 在途租约（find 实测仅 C.lock/TESTER.lock 0 字节历史空文件；"
    "TESTER.json 06:06 瞬时在途=测试者自身巡检业务非 C）；"
    "C 本轮 owner C-cron-poll-20261012-060353 claim 成功（首次脚本 claim 输出解析"
    "崩溃但 lease 已落盘 owner 匹配，从 lease 同源取 token 续跑，未二次 claim），"
    "事件 C-poll-20261012-060353-nochange 落盘后 release；**保持空闲待派单**"
    "（P0 已收口、TASK-11 生产门禁待用户授权，如后续涉 C 将另行派单）。"
    "前一条 05:38 巡检见下"
)

with io.open(SESSIONS, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()
first_sig = lines[0][:12] if lines else ""
new_content = ENTRY + "\n" + "\n".join(lines) + "\n"
if first_sig and first_sig not in new_content:
    print("ABORT_SIGN_MISSING")
    sh([sys.executable, RUNTIME, "release", "--project", ROOT,
        "--role", "C", "--token", token])
    sys.exit(4)
TMP = os.path.join(ROOT, "scratch", "C.md.new-0606")
with io.open(TMP, "w", encoding="utf-8") as f:
    f.write(new_content)
with io.open(TMP, "r", encoding="utf-8") as f:
    check = f.read().splitlines()
n2 = len(check)
assert n2 == len(lines) + 1, "LINECOUNT %d -> %d" % (len(lines), n2)
assert check[0].startswith(ENTRY[:30]), "HEAD_MISMATCH"
assert check[1] == lines[0], "SECOND_MISMATCH"
os.replace(TMP, SESSIONS)
print("SESSIONS_OK lines=%d" % n2)

ev_summary = ("06:03:53巡检（06:06落盘）：C范围零新增，inbox/3号与inbox/coordinator"
              "无新文件，无C新派单；HANDOFF 06:02=协调者06:00:53空转第38轮检查点（非C）；"
              "补记05:48:53事件在案但sessions条目缺失；main 453da0c=origin/main双核、"
              "wt-03b 6f1a9ad干净、无C在途进程")
rc, out, err = sh([sys.executable, RUNTIME, "event", "--project", ROOT,
                   "--role", "C", "--token", token,
                   "--event-id", EVENT_ID,
                   "--task", "TASK-03B", "--attempt", "0",
                   "--status", "POLL_NO_CHANGE",
                   "--summary", ev_summary,
                   "--evidence", "sessions/C.md",
                   "--next", "保持空闲待派单"])
if rc != 0:
    print("EVENT_FAILED rc=%d out=%s err=%s" % (rc, out, err))
    sys.exit(5)
print("EVENT_OK")

rc, out, err = sh([sys.executable, RUNTIME, "release", "--project", ROOT,
                   "--role", "C", "--token", token])
if rc != 0:
    print("RELEASE_FAILED rc=%d out=%s err=%s" % (rc, out, err))
    sys.exit(6)
print("RELEASE_OK")
print("DONE")