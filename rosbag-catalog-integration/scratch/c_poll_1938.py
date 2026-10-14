#!/usr/bin/env python3
"""C 巡检控制动作：claim 短租约 -> 追加 sessions/C.md -> 写 events/C -> 释放租约。"""
import json, os, time, hashlib, datetime

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
LEASES = os.path.join(ROOT, "inbox/control/runtime/leases")
EVENTS = os.path.join(ROOT, "events/C")
SESSIONS = os.path.join(ROOT, "sessions/C.md")

owner = "C-cron-poll-20261011-193853"
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
hms = now.strftime("%H:%M")

lease_path = os.path.join(LEASES, "C.json")
# 1) claim: 仅当无 C 租约或租约已过期时写入
claimed = False
if os.path.exists(lease_path):
    try:
        with open(lease_path) as f:
            cur = json.load(f)
        exp = cur.get("expires_at_epoch", 0)
        if cur.get("owner") == owner or exp > time.time() + 5:
            print("SKIP_LEASE_HELD", cur.get("owner"))
            raise SystemExit(0)
    except (json.JSONDecodeError, ValueError):
        pass
with open(lease_path, "w") as f:
    json.dump({"owner": owner, "role": "C", "claimed_at": iso,
               "expires_at_epoch": int(time.time()) + 120,
               "purpose": "poll-nochange-session-update"}, f)
claimed = True
print("CLAIM_OK")

# 2) 追加 sessions/C.md（文件首行为标题，追加到第 1 行标题块之后：找到第一个以 '- 最后更新' 开头的行插在其前）
entry = (
    "- 最后更新：2026-10-11 19:38 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T19:38:53+08:00）、legacy_busy 空；"
    "19:35:37（前条 C 事件）后共享根**零 C 范围业务新增**（find -newermt 19:34 排除 ticks/leases/scratch/sessions 核实，仅 B 巡检事件与各角色 sessions 刷新）；"
    "`inbox/3号/` 无新文件（find 核实 10-10 00:59 后为空，最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、"
    "`inbox/coordinator/` 无面向 3号 新单（最新仍 19:19 t08c-1 decision，2号/测试者范围），**无 C 新派单**；"
    "main HEAD=`0a8ca8a`=origin/main 双核一致（wt-03b rev-parse 核实，19:17 t08c-1 合入后未再推进，非 C 交付）、"
    "wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 排除 .venv 核实为空）；"
    "ps 核实无 C 在途业务进程（19:39 唯一命中=`wt-tester-pm08` pytest，**测试者合入后 9 红文件复核业务，非 C 范围**）；"
    "leases 仅 `TESTER.json` 在途（owner cron-tester-poll-1920 claim 19:22:28，测试者范围）；"
    f"C 本轮短占用 owner `{owner}`，控制动作结束释放；**保持空闲待派单**。前一条 19:34 巡检见下）"
)
with open(SESSIONS) as f:
    lines = f.readlines()
out = []
inserted = False
for ln in lines:
    if not inserted and ln.startswith("- 最后更新"):
        out.append(entry + "\n")
        inserted = True
    out.append(ln)
if not inserted:
    out.insert(0, entry + "\n")
with open(SESSIONS, "w") as f:
    f.writelines(out)
print("SESSIONS_OK")

# 3) 事件文件
ev = {
    "event_id": "C-poll-20261011-193853-nochange",
    "occurred_at": iso,
    "recorded_at": iso,
    "role": "C",
    "task": "none",
    "attempt": "0",
    "status": "IDLE",
    "summary": "巡检无C新派单：main 0a8ca8a 双核一致、wt-03b 6f1a9ad 干净、TESTER 9红文件复核在途非C范围",
    "evidence": "scratch/c_poll_1938.py",
    "next": "继续5分钟巡检等待派单",
}
name = hashlib.sha256(json.dumps(ev, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
with open(os.path.join(EVENTS, name + ".json"), "w") as f:
    json.dump(ev, f, ensure_ascii=False, indent=2)
print("EVENT_OK", name[:12])

# 4) release
if claimed:
    os.remove(lease_path)
print("RELEASE_OK")