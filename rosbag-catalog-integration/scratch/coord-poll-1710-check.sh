#!/bin/sh
# 协调者 17:10 巡检核查脚本
ROOT=/home/wang/work/doc/prd/rosbag-catalog-integration
REPO=/home/wang/work/rosbag-catalog
SINCE='2026-10-11 17:04:00'

echo "== main HEAD (rev-parse 双核) =="
git -C $REPO rev-parse main
git -C $REPO rev-parse origin/main

echo "== 最近 5 条 main log =="
git -C $REPO log --oneline -5

echo "== SINCE($SINCE) 后共享根新增文件 =="
find $ROOT -newermt "$SINCE" -type f 2>/dev/null | grep -v -E '/runtime/|/ticks/' | sort

echo "== receipts/TASK-08 目录 =="
ls -la $ROOT/receipts/TASK-08/ 2>/dev/null
ls -la $ROOT/reports/TASK-08/ 2>/dev/null

echo "== inbox/2号/TASK-08 派单目录 =="
ls -la $ROOT/inbox/2号/TASK-08/ 2>/dev/null
ls -la $ROOT/inbox/2号/ 2>/dev/null | tail -20

echo "== t08c worktree 核活 =="
for wt in /home/wang/.local/state/rosbag-scene/wt-04a-t08c*; do
  echo "-- $wt"
  git -C $wt rev-parse HEAD 2>/dev/null
  git -C $wt status --short 2>/dev/null | head -10
  find $wt -newermt "$SINCE" -type f 2>/dev/null | grep -v -E '\.git/|__pycache__|\.pytest_cache' | head -15
done
ls -d /home/wang/.local/state/rosbag-scene/wt-04a* 2>/dev/null

echo "== pytest/ocr 业务进程 =="
ps aux | grep -E 'pytest|ocr ' | grep -v grep | head -10
echo "(end ps)"

echo "== events B 最新 =="
ls -t $ROOT/events/B/ 2>/dev/null | head -5
echo "== events A 最新 =="
ls -t $ROOT/events/A/ 2>/dev/null | head -3
echo "== events C 最新 =="
ls -t $ROOT/events/C/ 2>/dev/null | head -5
echo "== events COORDINATOR 最新 =="
ls -t $ROOT/events/COORDINATOR/ 2>/dev/null | head -3
echo "== events TESTER 最新 =="
ls -t $ROOT/events/TESTER/ 2>/dev/null | head -3

echo "== lock 文件 =="
ls -la $ROOT/inbox/ocr.lock $ROOT/inbox/coordinator.lock 2>/dev/null
echo "== runtime leases =="
ls -la $ROOT/inbox/control/ 2>/dev/null | head

echo "== 本地栈 =="
docker ps --format '{{.Names}} {{.Status}}' 2>/dev/null | head -10