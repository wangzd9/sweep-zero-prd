#!/usr/bin/env python3
import io, json, os, subprocess, sys, time

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261012-064853"
SESSIONS = os.path.join(ROOT, "sessions/C.md")
ENTRY = os.path.join(ROOT, "scratch/c_poll_064853_entry.txt")
DRY = os.path.join(ROOT, "scratch/c_poll_064853_dry.md")
EVID = os.path.join(ROOT, "scratch/c_poll_064853_evidence.txt")

def sh(cmd, **kw):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)
    return p

ev = []
def log(msg):
    ev.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
    print(msg, flush=True)

def finish(rc=0):
    with io.open(EVID, "a", encoding="utf-8") as f:
        f.write("\n".join(ev) + "\n")
    sys.exit(rc)

# 1) pre-state verification (read-only, before any write)
cur = sh(f"wc -l < {SESSIONS}").stdout.strip()
stat = sh(f"stat -c '%Y %s' {SESSIONS}").stdout.split()
cur_grep0638 = sh(f"grep -c '063853' {SESSIONS}").stdout.strip()
log(f"pre: lines={cur} size={stat[1]} mtime={stat[0]} grep063853={cur_grep0638}")
if cur != "382":
    log("ABORT: pre-state mismatch (expect 382 lines); not writing")
    finish(3)

# 2) claim (multi-line JSON -> parse whole); if already held by same owner, read token from lease
claim = sh(f"python3 {RUNTIME} claim --project {ROOT} --role C --owner {OWNER}")
TOKEN = None
if claim.returncode == 0:
    try:
        data = json.loads(claim.stdout)
        TOKEN = data["token"]
        log(f"claim ok owner={data.get('owner')} token_set={bool(TOKEN)}")
    except Exception as e:
        log(f"claim rc=0 but parse failed: {e}")
if not TOKEN:
    lease = os.path.join(ROOT, "inbox/control/runtime/leases/C.json")
    try:
        ld = json.load(io.open(lease, encoding="utf-8"))
        if ld.get("owner") == OWNER:
            TOKEN = ld["token"]
            log(f"reuse same-owner lease token (claim rc={claim.returncode})")
        else:
            log(f"ABORT: lease held by other owner={ld.get('owner')}; not writing")
            finish(4)
    except Exception as e:
        log(f"ABORT: no usable lease: claim rc={claim.returncode} err={e}")
        finish(4)

def run_tok(args_desc, argv):
    p = sh(["python3", RUNTIME, "run", "--project", ROOT, "--role", "C", "--token", TOKEN] + argv)
    return p

# 3) build entry text (replace placeholder HHMM)
txt = io.open(ENTRY, encoding="utf-8").read()
if not txt.startswith("- 最后更新：2026-10-12 {HHMM}"):
    log("ABORT: entry signature missing")
    finish(5)
now = time.strftime("%H:%M")
entry = txt.replace("{HHMM}", now, 1).rstrip("\n") + "\n"

# 4) DRY RUN to temp TARGET (same logic, different path) — compute & verify BEFORE touching real file
orig = io.open(SESSIONS, encoding="utf-8").read().splitlines(keepends=True)
dry_lines = [entry] + orig
with io.open(DRY, "w", encoding="utf-8") as f:
    f.writelines(dry_lines)
d = sh(f"wc -l < {DRY}").stdout.strip()
d0 = sh(f"head -1 {DRY}").stdout
d1 = sh(f"tail -1 {DRY}").stdout
dg = sh(f"grep -c '063853' {DRY}").stdout.strip()
ok = (d == "383" and d0.startswith("- 最后更新：2026-10-12 %s" % now)
      and "06:39 +08:00" in d1 and "C-cron-poll-20261012-063853" in d1 and dg == "4")
log(f"dry: lines={d} grep063853={dg} head_ok={d0.startswith('- 最后更新：2026-10-12 %s' % now)} tail_sig_ok={'06:39 +08:00' in d1 and 'C-cron-poll-20261012-063853' in d1}")
if not ok:
    log("ABORT: dry-run verification failed; NOT writing real file")
    finish(6)

# 5) real write under run: cp dry target -> sessions (single open, after all checks)
p = run_tok("cp dry->sessions", ["--", "cp", DRY, SESSIONS])
if p.returncode != 0:
    log(f"cp rc={p.returncode}: {p.stderr[-300:]}")
    finish(7)

# 6) post-verify real file
q_lines = sh(f"wc -l < {SESSIONS}").stdout.strip()
q_head = sh(f"head -1 {SESSIONS}").stdout
q_grep = sh(f"grep -c '063853' {SESSIONS}").stdout.strip()
q_tail = sh(f"tail -1 {SESSIONS}").stdout
log(f"post: lines={q_lines} grep063853={q_grep} head_is_entry={q_head.startswith('- 最后更新：2026-10-12 %s' % now)} tail_0638_survives={'C-cron-poll-20261012-063853' in q_tail}")
if not (q_lines == "383" and q_grep == "4" and "06:39 +08:00" in q_tail):
    log("ABORT: post-verify mismatch")
    finish(8)

# 7) event file
EVDIR = os.path.join(ROOT, "inbox/events/C")
evfile = os.path.join(EVDIR, "C-poll-20261012-064853-nochange.md")
evcontent = (
    "# C poll 20261012-064853 nochange\n\n"
    f"- event_id: C-poll-20261012-064853-nochange\n"
    f"- role: C\n"
    f"- owner: {OWNER}\n"
    f"- occurred_at: 2026-10-12T{now}:53+08:00\n"
    f"- preflight_checked_at: 2026-10-12T06:48:53+08:00\n"
    "- status: NO_CHANGE\n"
    "- summary: >-\n"
    "  C 范围零新增业务：inbox/3号 与 inbox/coordinator 无新文件（无 C 新派单）；main 453da0c=origin/main 双核一致；\n"
    "  wt-03b 6f1a9ad 干净；无 C 在途业务进程；leases 无 C 在途租约。HANDOFF 06:48 协调者第 47 轮检查点（非 C 范围）。\n"
    "  复核：协调者 06:45 抽查口径（24 行/mtime 06:35:40/grep 063853 零命中）本轮实测已过期——\n"
    "  sessions/C.md 现 382→383 行/mtime 2026-10-12 06:46:32 后为本轮写入，06:38 巡检条目在盘（末行，grep 命中）；\n"
    "  恢复完整性=快照口径，待协调者按最新磁盘复核，不擅自宣称全闭环。\n"
    "- evidence: >-\n"
    "  scratch/c_poll_064853_evidence.txt（pre/dry/post 计数与签名）；幸存事件 C-poll-20261012-063853-nochange 在案。\n"
    "- next: 保持空闲待派单；如协调者正式派 sessions 返修单则按派单执行最小返修。\n"
)
open_tmp = os.path.join(ROOT, "scratch", "c_poll_064853_event.txt")
io.open(open_tmp, "w", encoding="utf-8").write(evcontent)
pe = run_tok("cp event", ["--", "cp", open_tmp, evfile])
if pe.returncode != 0:
    log(f"event cp rc={pe.returncode}: {pe.stderr[-200:]}")
    finish(9)
eg = sh(f"test -s {evfile} && echo OK || echo MISSING").stdout.strip()
log(f"event: {eg}")

# 8) release
rel = sh(f"python3 {RUNTIME} release --project {ROOT} --role C --token {TOKEN}")
log(f"release rc={rel.returncode}")
finish(0 if rel.returncode == 0 else 10)