#!/usr/bin/env python3
"""C poll 072353 control: claim -> run(append+event) -> release. Idempotent."""
import io, json, os, subprocess

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "C-cron-poll-20261012-072353"

def sh(args, timeout=120):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)

# 1. claim (reuse same-source lease if a partial run left one with matching owner)
p = sh(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "C", "--owner", OWNER])
out = p.stdout.strip()
token = None
try:
    token = json.loads(out).get("token")
except Exception:
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                token = json.loads(line).get("token")
            except Exception:
                pass
if not token:
    lease = ROOT + "/inbox/control/runtime/leases/C.json"
    if os.path.exists(lease) and os.path.getsize(lease) > 0:
        with io.open(lease, "r", encoding="utf-8") as f:
            lj = json.load(f)
        if lj.get("owner") == OWNER:
            token = lj.get("token")
        print("claim stdout:", out[-300:])
        print("claim stderr:", p.stderr[-300:])
    else:
        print("claim stdout:", out[-300:])
        print("claim stderr:", p.stderr[-300:])
assert token, "no token obtained; ABORT without touching shared files"
print("claim ok token_len=%d" % len(token))

# 2. run: sessions prepend (idempotent append script)
p = sh(["python3", RUNTIME, "run", "--project", ROOT, "--role", "C", "--token", token, "--",
        "python3", ROOT + "/scratch/c_poll_072353_append.py"])
print("run rc", p.returncode)
print(p.stdout[-400:])
if p.returncode != 0:
    print("run stderr", p.stderr[-400:])
    p = sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token])
    print("release-after-fail rc", p.returncode)
    raise SystemExit(1)

# 3. event (idempotent)
eid = "C-poll-20261012-072353-nochange"
evdir = ROOT + "/inbox/events/C"
exists = os.path.exists(os.path.join(evdir, eid + ".md"))
if exists:
    print("event already landed; skip")
else:
    ev = (
        "# C poll 20261012-072353 nochange\n\n"
        "- event_id: %s\n"
        "- role: C\n"
        "- owner: %s\n"
        "- checked_at: 2026-10-12T07:23:53+08:00\n"
        "- status: POLL_NO_CHANGE\n"
        "- summary: >-\n"
        "  07:18:53 后 C 范围零新增：inbox/3号 与 inbox/coordinator find -newermt 实测均无新文件，无 C 新派单；\n"
        "  共享根新增均为非 C 范围（HANDOFF 07:17=协调者 r51 空转检查点、TIMELINE 记账、B nochange 心跳 x2）；\n"
        "  main 453da0c=origin/main 双核一致（fetch rc=0 后 rev-parse 实测）、wt-03b 6f1a9ad 干净、\n"
        "  ps 无 C 在途业务进程、leases 无在途 .json；06:40:54 sessions 截断事故恢复已被协调者按最新磁盘抽查通过\n"
        "  （1 处格式残留不阻塞、不派单不返修），C 侧待核对事项解除；保持空闲待派单（P0 已收口、TASK-11 生产门禁待用户授权）。\n"
        "- evidence: scratch/c_poll_072353_append.py 干跑+写后行计数核验；rosbag-catalog rev-parse；wt-03b status；ps\n"
        "- next: 保持空闲待派单；如后续涉 C 由协调者另行派单\n"
    ) % (eid, OWNER)
    evtmp = ROOT + "/scratch/c_poll_072353_event.txt"
    io.open(evtmp, "w", encoding="utf-8").write(ev)
    p = sh(["python3", RUNTIME, "run", "--project", ROOT, "--role", "C", "--token", token, "--",
            "cp", evtmp, os.path.join(evdir, eid + ".md")])
    print("event rc", p.returncode, p.stderr[-200:])
    assert p.returncode == 0, "event write failed"
    assert os.path.getsize(os.path.join(evdir, eid + ".md")) > 0

# 4. release
p = sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "C", "--token", token])
print("release rc", p.returncode)
rel_out = p.stdout.strip()
try:
    print("released:", json.loads(rel_out).get("released"))
except Exception:
    print("release stdout:", rel_out[-200:], p.stderr[-200:])
print("DONE")