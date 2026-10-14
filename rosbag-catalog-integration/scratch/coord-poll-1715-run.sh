#!/bin/sh
# 协调者 17:15 巡检：检查点+event 落盘（run 短控制），随后 release
RUNTIME=/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py
ROOT=/home/wang/work/doc/prd/rosbag-catalog-integration
TOKEN=88c98c3103744d21885c1494874be9f1
OWNER=cron-coord-poll-14ae4556629a-20261011-1715
python3 $RUNTIME run --project $ROOT --role COORDINATOR --token $TOKEN -- sh $ROOT/scratch/coord-poll-1715-docs.sh
python3 $RUNTIME event --project $ROOT --role COORDINATOR --token $TOKEN --event-id coord-poll-20261011-171553-t08c1-inflight-nochange --task TASK-08 --attempt t08c-1 --status IN_FLIGHT_NO_CHANGE --summary "17:10 后零业务交付，main 98f6c88=origin 双核一致；2号 t08c-1 在途（wt-04a-t08c 最后活动 pyc 17:07:36 pytest 重写、git status 仅 .venv 软链、HEAD f9bafb0 无 commit 无回执，B tick 17:08:53 report 存活），A/C/TESTER 空闲，无协调侧 ocr/pytest 业务进程，无新派单/合入/状态变更" --evidence "sessions/COORDINATOR.md 2026-10-11 17:15 巡检检查点" --next "下轮核 t08c-1 交付回执→机械核验→串行 OCR 增量→合入→9 红文件全绿复核→08 DONE"
python3 $RUNTIME release --project $ROOT --role COORDINATOR --token $TOKEN