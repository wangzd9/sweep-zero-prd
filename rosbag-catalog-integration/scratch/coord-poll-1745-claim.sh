#!/bin/sh
# 协调者 17:45 巡检 claim 短控制 run
RUNTIME=/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py
ROOT=/home/wang/work/doc/prd/rosbag-catalog-integration
OWNER="cron-coord-poll-14ae4556629a-20261011-1740"
python3 $RUNTIME claim --project $ROOT --role COORDINATOR --owner $OWNER