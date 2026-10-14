#!/usr/bin/env python3
import json, subprocess, sys
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
TOKEN = "3c65a7c87e4940a989283b1cbfb37eb6"

handoff = """## 2026-10-11 21:07 巡检检查点（cron poll 14ae4556629a，checked_at 2026-10-11T21:05:53+08:00：TASK-09 2号 runner 已终态、交付回执未到）
- **TASK-09 2号 真实样本 runner 已 EXIT=0**：`/home/wang/.hermes/cache/scratch/t09-real/t09-real-verify.json` 21:04:53 落盘（endpoint/model/frames_per_sample_bound/samples/time_mapping 五键齐全），日志 `t09-real-verify.log` 尾部 `REAL-VERIFY DONE ... EXIT=0`；阳性/阴性（NO_MATCH flat-only）/边界（MODEL_UNAVAILABLE 如实报出）均有断言行。`wt-04a-t09` 三文件（adapter.py/vlm.py/test_slope_vlm_wiring.py）20:50:18–20:51:55 后未再改动，**未 commit、无交付回执** → B 下一步应 commit+断言核验+回归后落 `receipts/TASK-09/`。
- main `0a8ca8a`=origin 未动；无 OCR 在途；TASK-10 维持 WAITING（前置 09 未交付）；生产启用 TASK-11 门禁维持未放行。
- **下一步**：等 2号 commit+交付回执 → 机械核验（含图像 content 非空）→ 串行 OCR → 合入 → 09 DONE → 派 TASK-10。
"""

with open(ROOT + "/HANDOFF.md", "w") as f:
    f.write(handoff)

event = {
  "event_id": "coordinator-poll-20261011210553-task09-runner-done-no-receipt",
  "occurred_at": "2026-10-11T21:07:43+08:00",
  "recorded_at": "2026-10-11T21:07:43+08:00",
  "role": "COORDINATOR",
  "task": "TASK-09",
  "attempt": "1",
  "status": "RUNNING",
  "summary": "巡检：2号 TASK-09 真实样本 runner 21:04:53 EXIT=0 落 t09-real-verify.json（五键齐全，阳性/阴性NO_MATCH/边界MODEL_UNAVAILABLE 断言均在），wt-04a-t09 三文件 20:51 后未再改、未 commit 无交付回执；main 0a8ca8a=origin 未动，无 OCR 在途，TASK-10 维持 WAITING；等 2号 commit+回执后机械核验",
  "evidence": "/home/wang/.hermes/cache/scratch/t09-real/t09-real-verify.json; inbox/2号/TASK-09/attempt-1-ack.md",
  "next": "等 2号交付回执 → 机械核验(含图像 content 非空) → 串行 OCR → 合入 → 09 DONE → 派 TASK-10"
}
with open(ROOT + "/events/COORDINATOR/coordinator-poll-20261011210553-task09-runner-done.json", "w") as f:
    json.dump(event, f, ensure_ascii=False, indent=2)

print("HANDOFF+event written")