#!/usr/bin/env python3
"""COORDINATOR 10:50 控制回合：claim → run(checkpoint) → event → release。"""
import json
import subprocess
import sys

R = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "cron-poll-14ae4556629a-105053"


def call(args):
    p = subprocess.run([sys.executable, R] + args, capture_output=True, text=True, timeout=180)
    out = (p.stdout or "").strip()
    err = (p.stderr or "").strip()
    if p.returncode != 0:
        print("FAIL", args[0], "rc=", p.returncode, "\nSTDOUT:", out[-800:], "\nSTDERR:", err[-800:])
        sys.exit(1)
    return out


raw = call(["claim", "--project", ROOT, "--role", "COORDINATOR", "--owner", OWNER, "--ttl", "120"])
data = json.loads(raw[raw.find("{"):])
assert data.get("claimed") is True, f"claim failed: {data}"
token = data["token"]
print("CLAIM_OK token_len", len(token))

out = call(["run", "--project", ROOT, "--role", "COORDINATOR", "--token", token,
            "--", sys.executable, ROOT + "/scratch/coord_1050_checkpoint.py"])
print("RUN:", out[-300:])

out = call(["event", "--project", ROOT, "--role", "COORDINATOR", "--token", token,
            "--event-id", "coord-poll-20261011-105053-nochange",
            "--task", "NONE", "--attempt", "0", "--status", "NO_CHANGE",
            "--summary", "巡检10:45后零业务变化 main 4697be0 不变 强复审R2I-20261010-06 result仍不存在 等用户手动触发 06门禁不变",
            "--evidence", "sessions/COORDINATOR.md",
            "--next", "下轮5分钟巡检并核强复审结果文件 reviews/strongmodel/R2I-20261010-06-result.md"])
print("EVENT:", out[-200:])

call(["release", "--project", ROOT, "--role", "COORDINATOR", "--token", token])
print("RELEASED")