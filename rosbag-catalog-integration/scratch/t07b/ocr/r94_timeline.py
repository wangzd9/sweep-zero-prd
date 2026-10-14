#!/usr/bin/env python3
"""r94: append TIMELINE row."""
p = "/home/wang/work/doc/prd/rosbag-catalog-integration/TIMELINE.md"
cur = open(p, encoding="utf-8").read()
line = ("| 2026-10-12 19:3x | 协调者 r94 | TASK-07B | OCR b5 后台 pid 414832 核实随 r93 会话回收（0 字节双文件）；"
        "队列低负载（vllm 1 running/0 waiting）→ b5 Hermes 后台跟踪重启 `proc_7ea84d1aecc6` pid 434432"
        "（`--max-tokens 30000`，flock ocr.lock）；再 reap=挂 NEEDS_MAIN_REVIEW |\n")
open(p, "w", encoding="utf-8").write(line + cur)
print("timeline ok")