#!/usr/bin/env python3
# 07:05 轮消费完毕后 ack observer pending（prerun 指纹 a11f5a2f…）
import json, os, subprocess
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
FP = "a11f5a2fafbef8ee1e8c129d7716056ba31df1c37a57e687eee25ac8e57de584"
# 先确认 pending 仍是该指纹
obs = os.path.join(ROOT, "inbox", "control", "runtime", "observer", "COORDINATOR.json")
try:
    data = json.load(open(obs, encoding="utf-8"))
    pend = data.get("pending", {})
    print("observer pending fp:", pend.get("fingerprint", "none"),
          "| changed:", len(pend.get("changed_sources", [])))
    assert pend.get("fingerprint") == FP, "pending fingerprint changed, do NOT ack stale"
except FileNotFoundError:
    print("no observer file, acking prerun fp directly")
r = subprocess.run(["python3", "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_observer.py",
                    "ack", "--project", ROOT, "--role", "COORDINATOR", "--fingerprint", FP],
                   capture_output=True, text=True)
print("ack exit:", r.returncode)
print(r.stdout.strip()[:400])
print(r.stderr.strip()[:400])