#!/usr/bin/env python3
# 补释放 05:20 巡检的 COORDINATOR 租约（token 解析修复）
import json, subprocess, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-poll-14ae4556629a-052053"
TOKEN = "3b0799fe34664349ae98d9095c398a97"

r = subprocess.run([sys.executable, RUNTIME, "release", "--project", ROOT,
                    "--role", "COORDINATOR", "--token", TOKEN],
                   capture_output=True, text=True)
out = (r.stdout or "").strip() or r.stderr.strip()
print("release:", out)
try:
    d = json.loads(out)
    print("released:", d.get("released"))
except Exception:
    pass
sys.exit(r.returncode)