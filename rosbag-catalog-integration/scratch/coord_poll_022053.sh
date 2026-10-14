#!/bin/bash
set -e
RUNTIME=/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py
ROOT=/home/wang/work/doc/prd/rosbag-catalog-integration
OWNER=cron-coord-poll-20261012-022053-p0-idle
python3 "$RUNTIME" claim --project "$ROOT" --role COORDINATOR --owner "$OWNER"