import subprocess
tok = open("/home/wang/work/doc/prd/rosbag-catalog-integration/scratch/c_claim_015353_token.txt").read().strip()
out = subprocess.run(
    ["python3", "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py",
     "--project", "/home/wang/work/doc/prd/rosbag-catalog-integration",
     "--role", "C", "--mode", "poll",
     "--owner", "C-cron-poll-20261012-015353", "--token", tok,
     "release"],
    capture_output=True, text=True)
print("EXIT:", out.returncode)
print("STDOUT:", out.stdout)
print("STDERR:", out.stderr)