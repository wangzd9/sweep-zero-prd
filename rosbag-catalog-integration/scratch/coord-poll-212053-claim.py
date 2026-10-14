import json, subprocess, sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "cron-coord-poll-212053"

r = subprocess.run(
    ["python3", RUNTIME, "claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER],
    capture_output=True, text=True, timeout=120,
)
out = r.stdout.strip()
print("RC", r.returncode)
print("OUT", out[:2000])
if r.returncode != 0:
    print("ERR", r.stderr[:2000])
    sys.exit(1)
# token usually last whitespace-separated field on stdout
tok = out.split()[-1]
print("TOKEN", tok)
with open(ROOT + "/scratch/coord-poll-212053-token.txt", "w") as f:
    f.write(tok)