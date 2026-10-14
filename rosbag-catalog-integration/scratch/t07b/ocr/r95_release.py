#!/usr/bin/env python3
"""r95: prepend TIMELINE entry (dedup by event id, prepend order) + release control lease."""
import subprocess
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
tp = f"{ROOT}/TIMELINE.md"
t = open(tp, encoding="utf-8").read()
eid = "coord-poll-20261012-195553-r95-t07b-ocr-detached-launch"
head = (f"<!-- role-event:{eid} -->\n"
        f"- 2026-10-12 20:02 +08:00 | COORDINATOR | TASK-07B | r95 巡检：r94 后台跟踪 pid 434432 核实随 cron 会话回收"
        f"（`b5_lowtok_out.txt`/`…_lowtok.log` 均 0 字节、ps 无进程）如实记账；18002 vllm 队列低负载实测 2 running/0 waiting"
        f"→ **b5-b10 改 detached 串行 OCR**（`r95_ocr_detached.py` `start_new_session` pid 464164，独立 session 20:02:16 起跨 cron 存活，"
        f"`--max-tokens 30000` 逐文件，flock 持 ocr.lock，进度 `scratch/t07b/ocr/remaining_progress.txt`）；OCR 已收口 4/10 不变"
        f"（b1 0 / b2 0 / b3 1 medium CORRECTION 待裁决 / b4 0）；交付 `f4bfcf2` 仍 REVIEW_PENDING **未合入**；"
        f"强审 AUTHORIZED 至 2026-10-13 11:33:12、60min 0/5 累计 0、token/费用未知；无新派单无合入。\n")
if eid not in t:
    open(tp, "w", encoding="utf-8").write(head + t)
    print("timeline prepended")
else:
    print("timeline dedup skip")

r = subprocess.run([
    "python3", "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py",
    "--project", ROOT, "--role", "COORDINATOR",
    "--token", "325bae64ec2c4b7cb6b0351d7ddf6ce5", "release",
], capture_output=True, text=True)
print("release rc=", r.returncode, r.stdout.strip()[:200], r.stderr.strip()[:200])