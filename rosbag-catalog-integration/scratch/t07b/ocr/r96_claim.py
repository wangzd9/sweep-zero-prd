import json, subprocess
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "cron-coord-poll-14ae4556629a-20261012-201553-r96"
out = subprocess.run(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER], capture_output=True, text=True)
print("RC", out.returncode)
print(out.stdout.strip()[-500:])
print("ERR", out.stderr.strip()[-300:])
lease = f"{ROOT}/inbox/control/runtime/leases/COORDINATOR.json"
try:
    print("TOKEN", json.load(open(lease)).get("token"))
except Exception as e:
    print("TOKEN-READ-FAIL", e)