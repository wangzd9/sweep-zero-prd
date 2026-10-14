#!/usr/bin/env python3
"""r94: append HANDOFF checkpoint (sessions part already written by r94_checkpoint.py)."""
import os
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
sp = os.path.join(ROOT, "sessions/COORDINATOR.md")
cur = open(sp, encoding="utf-8").read()
idx = cur.find("## 2026-10-12 19:3x 巡检检查点")
assert idx != -1, "checkpoint missing"
checkpoint = cur[: idx + cur[idx:].find("\n")]
# rebuild HANDOFF from the same checkpoint body
title = checkpoint + "\n"
bullets = [
    "- main `30e55a3`=github/main；07B 交付冻结 REVIEW_PENDING 不变（`f4bfcf2` 未合入）。",
    "- **b5 后台 pid 414832 核实已随 r93 会话回收（0 字节双文件，进程不存在）如实记账**；r94 队列低负载实测（vllm 1 running/0 waiting）→ b5 以 Hermes 后台跟踪重启（`proc_7ea84d1aecc6` pid 434432，`--max-tokens 30000`，flock 持 `inbox/ocr.lock`，19:36 核存活）。",
    "- OCR 进度 4/10 维持（b1 0 / b2 0 / b3 **1 medium CORRECTION 待裁决** / b4 0）；b6 reap 日志证实=外层 420s 杀进程（usage 84977 tokens 齐全后 context canceled）非 LLM 失败；b6-b10+契约批次 QUEUED 待 b5 收口。",
    "- r95+ 收口核法：pid 434432 poll + `b5_lowtok_out.txt` 现 RC=/Review complete=记账续 b6；已退无 complete=**挂 NEEDS_MAIN_REVIEW 不无限重试**（b5 第 2 次 reap 触顶）。",
    "- 强审查授权在案（grant `31dcbabe…` 至 2026-10-13 11:33:12，滚动 60 分钟 0/5，累计 0，token/费用未知）；07B 预判 REVIEW_NOW 待 OCR 收口。",
    "- 门禁：TASK-07 RUNNING（07B 不合入）；TASK-11 生产 BLOCKED；12-15 DEFERRED；A/C/TESTER 空闲；B 交付冻结。",
]
HANDOFF = title + "\n" + "\n".join(bullets) + "\n"
hp = os.path.join(ROOT, "HANDOFF.md")
curh = open(hp, encoding="utf-8").read()
open(hp, "w", encoding="utf-8").write(HANDOFF + curh)
print("HANDOFF.md checkpoint written")