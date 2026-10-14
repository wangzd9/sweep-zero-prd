import json, subprocess, datetime, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-tester-poll-167580c0500b-20261012-180453"
LEASE = os.path.join(ROOT, "inbox/control/runtime/leases/TESTER.json")

def sh(args):
    return subprocess.run(args, capture_output=True, text=True)

r = sh(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "TESTER", "--owner", OWNER])
print("claim rc:", r.returncode)
print(r.stdout.strip()[-300:])
print(r.stderr.strip()[-300:])
if r.returncode != 0:
    # skill trap: token only on stdout but claim may still be ours; read lease
    if os.path.exists(LEASE):
        lease = json.load(open(LEASE))
        if lease.get("owner") == OWNER:
            token = lease["token"]
            print("using self-read lease token (skill trap path)")
        else:
            print("OWNER MISMATCH, abort without writes:", lease.get("owner"))
            raise SystemExit(2)
    else:
        raise SystemExit(3)
else:
    token = None
    for line in r.stdout.splitlines():
        m = line.strip()
        if m and m not in ("ok",) and len(m) >= 16 and all(c in "0123456789abcdef" for c in m):
            token = m
    if not token:
        lease = json.load(open(LEASE)) if os.path.exists(LEASE) else {}
        if lease.get("owner") == OWNER:
            token = lease["token"]
    if not token:
        print("no token found, abort")
        raise SystemExit(4)
    print("token acquired")

r2 = sh(["python3", RUNTIME, "run", "--project", ROOT, "--role", "TESTER", "--token", token, "--",
         "python3", os.path.abspath(__file__) + ".child"])
print("run rc:", r2.returncode)
print(r2.stdout.strip()[-200:])
print(r2.stderr.strip()[-200:])

r3 = sh(["python3", RUNTIME, "release", "--project", ROOT, "--role", "TESTER", "--token", token])
print("release rc:", r3.returncode)
print(r3.stdout.strip()[-200:])