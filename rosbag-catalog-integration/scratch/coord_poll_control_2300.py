import json
import subprocess
import sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "cron-poll-14ae4556629a-230053"


def run_cmd(args):
    out = subprocess.run(
        [sys.executable, RUNTIME] + args,
        capture_output=True, text=True, cwd=ROOT
    )
    return out.stdout.strip(), out.stderr.strip(), out.returncode


out, err, rc = run_cmd([
    "claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER
])
if rc != 0:
    print("claim failed rc=%d err=%s" % (rc, err))
    sys.exit(1)
token = json.loads(out)["token"]
print("token acquired: " + token[:8])

out2, err2, rc2 = run_cmd([
    "run", "--project", ROOT, "--role", "COORDINATOR", "--token", token,
    "--", sys.executable, "scratch/coord_update_sessions_2300.py"
])
print("run rc=%d" % rc2)
print(out2)
if err2:
    print("run err: " + err2)

out3, err3, rc3 = run_cmd([
    "release", "--project", ROOT, "--role", "COORDINATOR", "--token", token
])
print("release rc=%d" % rc3)