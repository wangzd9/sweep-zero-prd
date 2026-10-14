#!/usr/bin/env python3
"""r94: fix TIMELINE entry to role-event format (comment + dash line), not table row."""
p = "/home/wang/work/doc/prd/rosbag-catalog-integration/TIMELINE.md"
cur = open(p, encoding="utf-8").read()
bad = ('| 2026-10-12 19:3x | 协调者 r94 | TASK-07B | OCR b5 后台 pid 414832 核实随 r93 会话回收（0 字节双文件）；'
       '队列低负载（vllm 1 running/0 waiting）→ b5 Hermes 后台跟踪重启 `proc_7ea84d1aecc6` pid 434432'
       '（`--max-tokens 30000`，flock ocr.lock）；再 reap=挂 NEEDS_MAIN_REVIEW |\n\n')
assert bad in cur, "bad row not found"
good = ('<!-- role-event:coord-poll-20261012-192553-r94-t07b-b5-bg-restart -->\n'
        '- 2026-10-12 19:3x +08:00 | COORDINATOR | TASK-07B | r94 巡检：b5 后台 pid 414832 核实随 r93 会话回收'
        '（`b5_lowtok_out.txt`/`…_lowtok.log` 均 0 字节 19:20、进程不存在，kill -0 无此进程）如实记账；'
        '18002 vllm 队列反转实测 **1 running / 0 waiting**（r93 19:12 为 4 running+1 waiting 饱和）=低负载窗口；'
        '→ **b5 以 Hermes 后台跟踪重启**（`proc_7ea84d1aecc6` pid 434432，`run_ocr_file_lowtok.py`'
        ' `--max-tokens 30000`，flock 持 ocr.lock，19:36 核存活 Ss 态）；OCR 进度 4/10 维持'
        '（b1 0 / b2 0 / **b3 1 medium CORRECTION 待裁决** / b4 0；b6-b10+契约批次 QUEUED 待 b5）；'
        'r95+ 收口核=pid 434432 poll + `b5_lowtok_out.txt` 现 RC=/Review complete=记账续 b6；'
        '已退无 complete=**挂 NEEDS_MAIN_REVIEW 不无限重试**（b5 第 2 次 reap 触顶）；'
        '强审 AUTHORIZED 至 2026-10-13 11:33:12、60min 0/5 累计 0、token/费用未知；无新派单无合入。\n\n')
open(p, "w", encoding="utf-8").write(cur.replace(bad, good))
print("timeline fixed")