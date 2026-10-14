import json, subprocess, sys

obs = "/home/wang/work/doc/prd/rosbag-catalog-integration/inbox/control/runtime/observer/COORDINATOR.json"
d = json.load(open(obs))
fp = d["observed"]["fingerprint"]
print("observed fp:", fp, "len:", len(fp))
p = d.get("pending", {})
print("pending fp:", p.get("fingerprint"))
print("pending changed:", p.get("changed_sources"))
r = subprocess.run(
    [sys.executable, "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_observer.py",
     "ack", "--project", "/home/wang/work/doc/prd/rosbag-catalog-integration",
     "--role", "COORDINATOR", "--fingerprint", fp],
    capture_output=True, text=True)
print("rc:", r.returncode)
print("out:", r.stdout.strip())
print("err:", r.stderr.strip())