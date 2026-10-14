#!/usr/bin/env python3
import subprocess, json, sys
RUNTIME="/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT="/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER="cron-coord-poll-234053-retry"
def sh(cmd):
    r=subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=120)
    return r.returncode,r.stdout,r.stderr
rc,out,err=sh(f"python3 {RUNTIME} claim --project {ROOT} --role COORDINATOR --owner {OWNER}")
print("CLAIM",rc,out[:200],err[:200])
try:
    tok=json.loads(out)["token"]
except Exception:
    tok=None
if not tok:
    print("NO TOKEN, abort"); sys.exit(1)
ev=f"python3 {RUNTIME} event --project {ROOT} --role COORDINATOR --token {tok} --event-id coord-poll-20261011-234053-t10-vlm-404-probing --task TASK-10 --attempt 1 --status RUNNING --summary '2号TASK-10驱动第4跑推进:3_analyze失败形态变化=VLM根路径404(非requests缺依赖),B在途排查;零交付零合入' --evidence 'scratch/t10/t10-run.log' --next '等2号定位404(endpoint配置或adapter面),交付即核验+OCR+合入'"
rc2,o2,e2=sh(ev)
print("EVENT",rc2,o2[:300],e2[:300])
rc3,o3,e3=sh(f"python3 {RUNTIME} release --project {ROOT} --role COORDINATOR --token {tok}")
print("RELEASE",rc3,o3[:200],e3[:200])
print("DONE")