#!/bin/bash
set -euo pipefail
ROOT=/home/wang/work/doc/prd/rosbag-catalog-integration
LINE='- 最后更新：2026-10-12 03:13 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-12T03:13:53+08:00）、legacy_busy 空；03:08:53（前条 C 巡检 preflight 时点）后共享根 C 范围零新增（find -newermt 排除 sessions/events/ticks/leases/scratch/control 核实为空）；inbox/3号 最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED、inbox/coordinator 最新仍 02:08:34 e2e-reverify-v2 decision（ls --time-style 核实，均非 C 新单）、**无 C 新派单**；main HEAD 453da0c=origin/main 双核一致（rosbag-catalog rev-parse 实测，TASK-10 DONE 已收口，非 C）、wt-03b HEAD=6f1a9ad 分支 feature/scene-03b-ocr-rework 干净（status --porcelain 排除 .venv 实测 0）、ps 实测无 C 在途业务进程（wt-03b/scene-03b/task-03b/t03b 命中为空）；C 本轮 owner C-cron-poll-20261012-031353 claim 成功（token 整体 JSON 解析），事件 C-poll-20261012-031353-nochange 落盘后 release；**保持空闲待派单**（P0 已收口，如后续涉 C 将另行派单）。前一条 03:08 巡检见下）'
{
  echo "$LINE"
  tail -n +1 "$ROOT/sessions/C.md"
} > "$ROOT/sessions/C.md.new"
mv "$ROOT/sessions/C.md.new" "$ROOT/sessions/C.md"
echo APPEND_OK