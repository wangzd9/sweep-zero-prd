#!/usr/bin/env python3
import io, json, os, subprocess, time
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
S = ROOT + "/sessions/C.md"

def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True)

ev = []
def log(m):
    ev.append(m); print(m, flush=True)

lines = sh(f"wc -l < {S}").stdout.strip()
grep = sh(f"grep -c '063853' {S}").stdout.strip()
head = sh(f"head -1 {S}").stdout
tail = sh(f"tail -1 {S}").stdout
log(f"verify: lines={lines} grep063853={grep} head_start_ok={head.startswith('- 最后更新：2026-10-12 06:59')} tail_0638_ok={'C-cron-poll-20261012-063853' in tail and '06:39 +08:00' in tail}")
if not (lines == "383" and grep == "4" and "06:39 +08:00" in tail):
    log("ABORT verify mismatch, no release decision; exit 20")
    with io.open(ROOT + "/scratch/c_poll_064853_evidence.txt", "a", encoding="utf-8") as f:
        f.write("\n".join(ev) + "\n")
    raise SystemExit(20)

# event file under run
now = time.strftime("%H:%M")
EVDIR = ROOT + "/inbox/events/C"
os.makedirs(EVDIR, exist_ok=True)
evtmp = ROOT + "/scratch/c_poll_064853_event.txt"
evcontent = (
    "# C poll 20261012-064853 nochange\n\n"
    "- event_id: C-poll-20261012-064853-nochange\n"
    "- role: C\n"
    "- owner: C-cron-poll-20261012-064853\n"
    f"- occurred_at: 2026-10-12T{now}:53+08:00\n"
    "- preflight_checked_at: 2026-10-12T06:48:53+08:00\n"
    "- status: NO_CHANGE\n"
    "- summary: >-\n"
    "  C 范围零新增业务：inbox/3号 与 inbox/coordinator 无新文件（无 C 新派单）；main 453da0c=origin/main 双核一致；\n"
    "  wt-03b 6f1a9ad 干净；无 C 在途业务进程；leases 无 C 在途租约。HANDOFF 06:48 协调者第 47 轮检查点（非 C 范围）。\n"
    "  复核：协调者 06:45 抽查口径（24 行/mtime 06:35:40/grep 063853 零命中）本轮（06:59）实测已不符——\n"
    "  sessions/C.md 恢复前 382 行/mtime 2026-10-12 06:46:32，06:38 巡检条目已在盘（末行，grep 063853 计 3），\n"
    "  幸存事件 C-poll-20261012-063853-nochange 与事故事件 C-sessions-truncation-20261012-064054 均在案；\n"
    "  本轮按干跑核验后补写自身条目（382→383 行、grep 4、末行 06:38 条目幸存三核），恢复完整性=快照口径，\n"
    "  待协调者按最新磁盘复核，不擅自宣称全闭环。\n"
    "- evidence: >-\n"
    "  scratch/c_poll_064853_evidence.txt（pre/dry/post 计数与签名）。\n"
    "- next: 保持空闲待派单；如协调者正式派 sessions 返修单则按派单执行最小返修。\n"
)
io.open(evtmp, "w", encoding="utf-8").write(evcontent)
p = subprocess.run(["python3", RUNTIME, "run", "--project", ROOT, "--role", "C",
                    "--token", "ae012f1ecc3341168be07284620d8e14",
                    "--", "cp", evtmp, os.path.join(EVDIR, "C-poll-20261012-064853-nochange.md")],
                   capture_output=True, text=True, timeout=120)
log(f"event cp rc={p.returncode} err={p.stderr[-200:]!r}")
if p.returncode != 0:
    raise SystemExit(21)
eg = sh(f"test -s {EVDIR}/C-poll-20261012-064853-nochange.md && echo OK || echo MISSING").stdout.strip()
log(f"event on disk: {eg}")

rel = sh(f"python3 {RUNTIME} release --project {ROOT} --role C --token ae012f1ecc3341168be07284620d8e14")
log(f"release rc={rel.returncode} out={rel.stdout[-120:]!r}")
with io.open(ROOT + "/scratch/c_poll_064853_evidence.txt", "a", encoding="utf-8") as f:
    f.write("\n".join(ev) + "\n")
raise SystemExit(0 if rel.returncode == 0 else 22)