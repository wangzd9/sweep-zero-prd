#!/usr/bin/env python3
"""C poll 23:38: claim -> event -> release"""
import subprocess, json, sys, os

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261011-233853"

def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout, r.stderr

# claim
rc, out, err = sh(f"python3 {RUNTIME} claim --project {ROOT} --role C --owner {OWNER}")
if rc != 0:
    print("CLAIM_FAIL", rc, out, err)
    sys.exit(1)
token = json.loads(out)["token"] if "token" in out else None
if not token:
    # 尝试从输出里解析 JSON
    try:
        token = json.loads(out)["token"]
    except Exception:
        print("TOKEN_PARSE_FAIL", repr(out), err)
        sys.exit(1)
print("CLAIM_OK", token[:12])

# event
event_id = "C-poll-20261011-233853-nochange"
rc, out, err = sh(
    f"python3 {RUNTIME} event --project {ROOT} --role C --token {token} "
    f"--event-id {event_id} --task NONE --attempt 0 --status NO_CHANGE "
    f"--summary '23:38 巡检：无 C 新派单；HANDOFF 23:33 检查点=2号 TASK-10 驱动第4跑 3_analyze VLM 404 MODEL_UNAVAILABLE 在途排查（非 C 范围）；main ca8730d=origin/main；wt-03b 6f1a9ad 干净；无 C 进程/在途租约；保持空闲待派单' "
    f"--evidence 'scratch/c_poll_2338.py 核查输出' --next '继续 5min 巡检；C 无在途任务'"
)
if rc != 0:
    print("EVENT_FAIL", rc, out, err)
    # 事件失败不吞 token，继续释放
else:
    print("EVENT_OK")

# release
rc, out, err = sh(f"python3 {RUNTIME} release --project {ROOT} --role C --token {token}")
print("RELEASE", rc, out.strip() or "ok", err.strip())