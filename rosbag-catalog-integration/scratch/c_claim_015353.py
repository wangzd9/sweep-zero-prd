import json, subprocess, sys
out = subprocess.run(
    ["python3", "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py",
     "--project", "/home/wang/work/doc/prd/rosbag-catalog-integration",
     "--role", "C", "--mode", "poll",
     "--owner", "C-cron-poll-20261012-015353",
     "claim"],
    capture_output=True, text=True)
print("STDOUT:", out.stdout)
print("STDERR:", out.stderr)
tok = None
for line in out.stdout.strip().splitlines():
    line = line.strip()
    if line.startswith("{"):
        tok = json.loads(line).get("token")
if tok is None:
    tok = json.loads(out.stdout).get("token")
print("TOKEN:", tok)
with open("/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/c_claim_015353_token.txt", "w") as f:
    f.write(tok or "")