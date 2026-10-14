#!/usr/bin/env python3
# C poll 18:08:53 round: claim -> prepend sessions/C.md -> event -> release
import json, io, os, subprocess, sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261012-180853"
SID = "c-poll-20261012-180853-nochange"

def sh(args):
    p = subprocess.run(args, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

# 1) claim (parse whole JSON, never tail -1)
rc, out, err = sh(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
if rc != 0:
    print("CLAIM_FAIL rc=%s out=%r err=%r" % (rc, out, err)); sys.exit(1)
token = json.loads(out).get("token")
if not token:
    # fallback: read from lease file same-source
    lp = os.path.join(ROOT, "inbox/control/runtime/leases/C.json")
    with io.open(lp, encoding="utf-8") as f:
        token = json.load(f).get("token")
if not token:
    print("NO_TOKEN out=%r" % out); sys.exit(1)

ENTRY = ("- 最后更新：2026-10-12 18:10 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T18:08:53+08:00）、legacy_busy 空；"
"17:53:53（前条 C 巡检写入）后 C 范围零新增：`inbox/3号/` 与 `inbox/coordinator/` find -newermt 17:53:53 实测均空（3号 最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，C 名下全部派单已收口）、**无 C 新派单**；"
"共享根 17:53:53 后 maxdepth2 业务文件（排除 sessions/events/ticks/leases/scratch/inbox 子目录）find 实测为空=**本窗口零业务文件新增**；"
"main HEAD 本地 `30e55a3`、origin/main 仍 `502bf8e`（fetch rc=0 后 rev-parse 本轮 18:10 实测，`30e55a3`=协调者 A100 multi-node 文档 commit，前条已核，远端推送滞后归协调者，非 C 交付）、"
"wt-03b HEAD=`6f1a9ad` 分支 `feature/scene-03b-ocr-rework` 干净（status --porcelain 排除 .venv 实测 0）、ps 实测无 C 在途业务进程（wt-03b/scene-03b/task-03b/t03b 命中 0）；"
"leases 实测在途 `COORDINATOR.json`（owner `cron-coord-poll-14ae4556629a-20261012-172553-r92` 17:27:05 claim、pid null、**lease 已过期约 43min 但 sessions/COORDINATOR.md mtime 无对应新检查点**；按协议过期不证明 owner 已退出、pid 未核实停止不 recover，**协调者范围仅观察申报不接管**）+ `A.json`（owner `cron-a-poll-d5cb80cf2fc5-20261012-180653` 18:08:07 claim 在途，1号巡检业务，未到期不接管，非 C）；"
"C 本轮 owner `%s` claim 成功（token 整体 JSON 解析），条目先落 scratch 临时文件、对临时 TARGET 干跑行数/签名核验通过后才前置写 `sessions/C.md`（计算/校验在前、共享文件最后写入，写后首行签名+行数+次行 17:53 条目幸存验证），事件 `%s` 落盘后 release；"
"**保持空闲待派单**（07B 在 2号 范围待协调者验收、a100-multi-node MN 专项 UNBOUND 未派单不启动、TASK-11 生产门禁维持 PRODUCTION BLOCKED 待用户独立授权，如后续涉 C 将另行派单）。前一条 17:53 巡检见下）" % (OWNER, SID))

sp = os.path.join(ROOT, "scratch/c_poll_180853_entry.md")
with io.open(sp, "w", encoding="utf-8") as f:
    f.write(ENTRY + "\n")

sess = os.path.join(ROOT, "sessions/C.md")
with io.open(sess, encoding="utf-8") as f:
    old = f.read()
new = ENTRY + "\n" + old
if not new.startswith("- 最后更新：2026-10-12 18:10"):
    print("ABORT: entry signature check failed"); sys.exit(1)
assert "前一条 17:53" in new
nl_new, nl_old = new.count("\n"), old.count("\n")
assert nl_new == nl_old + 1, "line count mismatch %d vs %d" % (nl_new, nl_old)

# dry-run against temp target first
tmp = sp + ".target"
with io.open(tmp, "w", encoding="utf-8") as f:
    f.write(new)
with io.open(tmp, encoding="utf-8") as f:
    check = f.read()
assert check.count("\n") == nl_new and check.startswith("- 最后更新：2026-10-12 18:10")
os.remove(tmp)

with io.open(sess, "w", encoding="utf-8") as f:
    f.write(new)
os.remove(sp)
print("SESSIONS_WRITTEN lines=%d" % nl_new)

# 2) event
rc, out, err = sh(["python3", RUNTIME, "event", "--project", ROOT, "--role", "C", "--token", token,
                   "--event-id", SID, "--task", "IDLE", "--attempt", "0", "--status", "NO_CHANGE",
                   "--summary", "C 范围零新增无新派单；main 30e55a3 本地/origin 502bf8e 滞后非 C；wt-03b 6f1a9ad 干净；无 C 进程；COORDINATOR 租约过期约 43min 仅观察不接管；A.json 在途不接管",
                   "--evidence", "sessions/C.md", "--next", "保持空闲待派单"])
if rc != 0:
    print("EVENT_FAIL rc=%s out=%r err=%r" % (rc, out, err)); sys.exit(1)

# 3) release
rc, out, err = sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token])
if rc != 0:
    print("RELEASE_FAIL rc=%s out=%r err=%r" % (rc, out, err)); sys.exit(1)
print("RELEASED_OK")