import subprocess, json, os, time

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
REPO = "/home/wang/work/rosbag-catalog"
SINCE = "2026-10-12 06:40:53"

def sh(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=120)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

out = {}

rc, local, _ = sh("git -C %s rev-parse main" % REPO)
rc2, origin, _ = sh("git -C %s rev-parse origin/main" % REPO)
out["main_head"] = local
out["origin_main"] = origin
out["dual_core_match"] = local == origin

# fetch (short timeout, best effort)
rcf, outf, errf = sh("git -C %s fetch origin --quiet" % REPO)
rc3, origin2, _ = sh("git -C %s rev-parse origin/main" % REPO)
out["fetch_rc"] = rcf
out["origin_main_after_fetch"] = origin2
out["dual_core_match_after_fetch"] = local == origin2

# new business files since last checkpoint
biz = []
for d in ["receipts", "test-receipts", "reports", "reviews", "decision", "dispatches"]:
    p = os.path.join(ROOT, d)
    if os.path.isdir(p):
        rc, o, e = sh("find %s -type f -newermt '%s'" % (p, SINCE))
        biz += [l for l in o.splitlines() if l.strip()]
for role in ["1号", "2号", "3号", "TESTER", "coordinator"]:
    p = os.path.join(ROOT, "inbox", role)
    if os.path.isdir(p):
        rc, o, e = sh("find %s -type f -newermt '%s'" % (p, SINCE))
        biz += [l for l in o.splitlines() if l.strip()]
# events dir (all roles) new since last checkpoint
rc, o, e = sh("find %s/events -type f -newermt '%s'" % (ROOT, SINCE))
out["events_new"] = [l for l in o.splitlines() if l.strip()]
# inbox events new
rc, o, e = sh("find %s/inbox/events -type f -newermt '%s'" % (ROOT, SINCE))
out["inbox_events_new"] = [l for l in o.splitlines() if l.strip()]
out["biz_new"] = biz

# ticks
ticks = {}
tdir = os.path.join(ROOT, "inbox/control/runtime/ticks")
for f in sorted(os.listdir(tdir)) if os.path.isdir(tdir) else []:
    try:
        ticks[f] = json.load(open(os.path.join(tdir, f)))
    except Exception as ex:
        ticks[f] = str(ex)
out["ticks"] = ticks

# leases
leases = {}
ldir = os.path.join(ROOT, "inbox/control/runtime/leases")
for f in sorted(os.listdir(ldir)) if os.path.isdir(ldir) else []:
    try:
        leases[f] = json.load(open(os.path.join(ldir, f)))
    except Exception as ex:
        leases[f] = str(ex)
out["leases"] = leases
out["now"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")

print(json.dumps(out, ensure_ascii=False, indent=1))