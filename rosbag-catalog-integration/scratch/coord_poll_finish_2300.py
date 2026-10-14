import json
import subprocess
import sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "cron-poll-14ae4556629a-230053"
TOKEN = "163214111de740b6aeb32d94c1ddb724"


def run_cmd(args):
    out = subprocess.run(
        [sys.executable, RUNTIME] + args,
        capture_output=True, text=True, cwd=ROOT
    )
    return out.stdout.strip(), out.stderr.strip(), out.returncode


# verify lease still belongs to us
out, err, rc = run_cmd(["claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER])
print("claim recheck rc=", rc, out, err)

out2, err2, rc2 = run_cmd([
    "run", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN,
    "--", sys.executable, "scratch/coord_update_sessions_2300.py"
])
print("run rc=", rc2)
print("run out:", out2)
if err2:
    print("run err:", err2)

out3, err3, rc3 = run_cmd([
    "release", "--project", ROOT, "--role", "COORDINATOR", "--token", TOKEN
])
print("release rc=", rc3)
print("release out:", out3)
if err3:
    print("release err:", err3)