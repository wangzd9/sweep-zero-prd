#!/usr/bin/env python3
"""r94: update ocr-batches ledger b5/b6 rows (read-modify-write, never truncate-then-read)."""
import re
p = "/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/TASK-07B/attempt-1/ocr-batches.md"
txt = open(p, encoding="utf-8").read()

old_b5 = re.search(r"\| T07B-b5 \|[^\n]*", txt).group(0)
new_b5 = ("| T07B-b5 | app/services/scene_manual_revision_service.py | +383 | 前台 5 次 420s reap + r93 后台 pid 414832 随会话回收（19:33 核 0 字节双文件）；"
          "**r94 19:36 队列低负载实测（vllm 1 running/0 waiting）重启 Hermes 后台跟踪 `proc_7ea84d1aecc6` pid 434432**"
          "（`run_ocr_file_lowtok.py` `--max-tokens 30000`，flock 持 `inbox/ocr.lock`，输出 `b5_lowtok_out.txt`）；"
          "若再 reap（r95+ 核 pid 434432 已退且无 Review complete）=挂 NEEDS_MAIN_REVIEW 不无限重试 | 19:36 起 | BACKGROUND | 未审 |")
txt = txt.replace(old_b5, new_b5)

old_b6 = re.search(r"\| T07B-b6 \|[^\n]*", txt).group(0)
new_b6 = ("| T07B-b6 | app/static/bag-detail.css | +13 | 1 次 420s reap（session `cda37180` usage 84977 tokens 7m0s 后 context canceled=外层 reap 杀进程）；"
          "r94 队列低负载期 b5 收口后前台短跑 | 18:5x | QUEUED（b5 后） | 未审 |")
txt = txt.replace(old_b6, new_b6)

open(p, "w", encoding="utf-8").write(txt)
print("ledger updated ok")