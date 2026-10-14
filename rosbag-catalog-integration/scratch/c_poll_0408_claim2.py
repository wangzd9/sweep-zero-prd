import subprocess, json, sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261012-040853"

def run(args):
    r = subprocess.run(["python3", RUNTIME] + args, capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout, r.stderr

# Lease already claimed by previous step (owner matches); read token from lease file (same source)
lease = json.load(open(ROOT + "/inbox/control/runtime/leases/C.json"))
assert lease.get("owner") == OWNER, "lease owner mismatch: %s" % lease.get("owner")
token = lease["token"]
print("token read from lease, owner verified")

rc, out, err = run(["run", "--project", ROOT, "--role", "C", "--token", token, "--",
                    "sh", "-c", "cat %s/scratch/c_poll_0408_line.md >> %s/sessions/C.md" % (ROOT, ROOT)])
print("run append rc=%d %s" % (rc, (out + err).strip()[:200]))

rc, out, err = run(["event", "--project", ROOT, "--role", "C", "--token", token,
                    "--event-id", "C-poll-20261012-040853-nochange",
                    "--task", "IDLE", "--attempt", "0", "--status", "IDLE_NO_CHANGE",
                    "--summary", "P0 收口后空转巡检：零业务新增、无 C 新派单、main 453da0c 双核一致、wt-03b 干净、无在途进程/租约",
                    "--evidence", "scratch/c_poll_0408.py",
                    "--next", "保持空闲待派单"])
print("event rc=%d %s" % (rc, (out + err).strip()[:200]))

rc, out, err = run(["release", "--project", ROOT, "--role", "C", "--token", token])
print("release rc=%d %s" % (rc, (out + err).strip()[:200]))