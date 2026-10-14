#!/bin/bash
# C 执行者 19:08 巡检短控制 run：claim → 写 checkpoint → release
set -u
ROOT=/home/wang/work/doc/prd/rosbag-catalog-integration
RUNTIME=/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py
OWNER=C-cron-poll-20261011-190853

TOKEN=$(python3 "$RUNTIME" claim --project "$ROOT" --role C --owner "$OWNER" 2>&1)
echo "CLAIM_RESULT: $TOKEN"
# token 是 JSON 里的字段
TOK=$(echo "$TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null)
if [ -z "$TOK" ]; then
  echo "CLAIM_FAILED - 只报告不写入"
  exit 0
fi

python3 "$RUNTIME" run --project "$ROOT" --role C --token "$TOK" -- \
  python3 - "$ROOT" <<'EOF'
import sys, datetime
root = sys.argv[1]
p = f"{root}/sessions/C.md"
new = ("- 最后更新：2026-10-11 19:08 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T19:08:53+08:00）、legacy_busy 空；"
"19:03:53 后共享根**零 C 范围新增**（find inbox -newermt 排除 ticks 核实为空，仅各角色 ticks 刷新）；`inbox/3号/` 无新文件（最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、`inbox/coordinator/` 无面向 3号 新单（最新仍 17:01:40 c3-1 decision，1号范围），**无 C 新派单**；"
"main HEAD 未变（`98f6c88`，rosbag-catalog rev-parse 核实）、wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 核实无修改）；"
"**前轮记录更正（只读核实）**：`leases/COORDINATOR.json` 实际 mtime 18:26:32、`expires_at` epoch 1791714692 换算=**2026-10-11 18:31:32 +08:00 已过期**（19:07 巡检误记为 20:24 未到期），owner `cron-coord-poll-182053-t08c1-review` pid null 无法定位进程，**未接管、未删除锁 inode**，待协调者按协议 renew 或 recover 核实后处理，非 C 范围；"
"ps 核实无 C 在途业务进程；C 本轮短占用 owner `C-cron-poll-20261011-190853` 控制动作结束释放；**保持空闲待派单**。前一条 19:07 巡检见下）\n")
with open(p, "r", encoding="utf-8") as f:
    content = f.read()
lines = content.splitlines(keepends=True)
assert lines and lines[0].startswith("- 最后更新：2026-10-11 19:07"), "首行非 19:07 巡检，中止写入"
lines.insert(0, new)
with open(p, "w", encoding="utf-8") as f:
    f.write("".join(lines))
print("CHECKPOINT_WRITTEN")
EOF
echo "RUN_EXIT: $?"

python3 "$RUNTIME" release --project "$ROOT" --role C --token "$TOK" 2>&1
echo "RELEASE_DONE"