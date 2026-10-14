#!/bin/bash
# B 巡检 04:22 记账：append sessions/B.md + event + release（只追加，禁覆盖）
set -e
ROOT=/home/wang/work/doc/prd/rosbag-catalog-integration
RUNTIME=/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py
TOKEN=a07b60c936204bf4984f1ac5f8353675
OWNER=cron-b-poll-6f7471d8747c-20261012-042253

cat >> $ROOT/sessions/B.md <<'EOF'
- 巡检 2026-10-12 04:22 +08:00（cron poll，真实 checked_at 2026-10-12T04:22:53+08:00 preflight）：**无新派单、无返修，TASK-10 已收口 DONE，P0 停止派发——本侧维持 IDLE_WAITING**——04:17 巡检后零业务变化：inbox/2号 01:20 后仍零新增（t10-defect3 ACK 已收口，无新派单/返修）；04:07:53 后 find 业务目录零命中（新增仅协调者 HANDOFF IDLE 巡检检查点，口径与本侧一致：main 453da0c 双核、全角色空闲、无业务进程）；origin/main fetch 实测 453da0c 双核不变（=TASK-10 收口合入点）；wt-04a-t10d3 HEAD=0943885 冻结干净（仅 .venv 软链）、ps 无本侧 pytest/ocr/e2e/derive 在途进程；leases 无 B 在途 owner，本回合 claim/release 正常（owner cron-b-poll-6f7471d8747c-20261012-042253，token JSON 整体解析）。维持 **IDLE_WAITING**，不占开发槽。事件 `b-poll-20261012-042253-nochange-task10-done-p0-idle` 落盘。下一步：仅按需巡检与事件接续；TASK-11 生产门禁未放行不自行启动。
EOF
echo APPEND_OK

python3 $RUNTIME event --project $ROOT --role B --token $TOKEN \
  --event-id b-poll-20261012-042253-nochange-task10-done-p0-idle \
  --task TASK-10 --attempt - --status IDLE_WAITING \
  --summary "夜间空转：无新派单/返修，main 453da0c 双核不变，P0 停止派发，本侧 IDLE_WAITING" \
  --evidence sessions/B.md --next "仅按需巡检与事件接续"
echo EVENT_OK

python3 $RUNTIME release --project $ROOT --role B --token $TOKEN
echo RELEASE_OK