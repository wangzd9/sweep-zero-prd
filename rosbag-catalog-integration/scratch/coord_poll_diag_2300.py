import json
import subprocess
import sys
import time

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "cron-poll-14ae4556629a-230053"


def run_cmd(args):
    out = subprocess.run(
        [sys.executable, RUNTIME] + args,
        capture_output=True, text=True, cwd=ROOT
    )
    return out.stdout.strip(), out.stderr.strip(), out.returncode


print("now:", time.time())
out, err, rc = run_cmd([
    "claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER
])
print("claim rc=", rc)
print("claim out:", out)
if err:
    print("claim err:", err)
try:
    d = json.loads(out)
    print("keys:", list(d.keys()))
    print("claimed:", d.get("claimed"))
    if d.get("claimed"):
        token = d.get("token")
        print("got token: " + str(token)[:8])
        out2, err2, rc2 = run_cmd([
            "run", "--project", ROOT, "--role", "COORDINATOR", "--token", token,
            "--", sys.executable, "scratch/coord_update_sessions_2300.py"
        ])
        print("run rc=", rc2)
        print("run out:", out2)
        if err2:
            print("run err:", err2)
        out3, err3, rc3 = run_cmd([
            "release", "--project", ROOT, "--role", "COORDINATOR", "--token", token
        ])
        print("release rc=", rc3)
        print("release out:", out3)
except Exception as e:
    print("parse error:", e)