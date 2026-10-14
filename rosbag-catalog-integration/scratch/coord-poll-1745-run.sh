#!/bin/sh
# 协调者 17:45 巡检 run：写检查点+TODO 注记 → event
set -e
RUNTIME=/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py
ROOT=/home/wang/work/doc/prd/rosbag-catalog-integration
TOKEN=14ff9ccb7cf942f19c7d498910e90b62
python3 $RUNTIME run --project $ROOT --role COORDINATOR --token $TOKEN -- python3 $ROOT/scratch/coord-poll-1745-write.py
python3 $RUNTIME event --project $ROOT --role COORDINATOR --token $TOKEN \
  --event-id coord-poll-20261011-174053-t08c1-stall-cleared-encoding \
  --task TASK-08 --attempt t08c-1 --status RUNNING \
  --summary "2号 t08c-1 活动停滞告警解除：wt-04a-t08c 17:38/17:41 恢复业务编码（bag_cleanup_service.py +58/-11 含 run_inspection 7 分支 _bump_if_changed + worker_heartbeat 整秒幂等；catalog_ingest.py upsert_bag 整数除秒 + 业务字段变化才推进 updated_at），未 commit 无回执，继续不催单不接管" \
  --evidence "wt-04a-t08c git diff --stat 2 files +58/-11; stat mtime 17:38:10/17:41:51" \
  --next "等 2号 commit+真 MySQL A/B 交付回执 receipts/TASK-08/；交付即机械核验→串行 OCR 增量→合入→9 红文件全绿复核→TASK-08 DONE"