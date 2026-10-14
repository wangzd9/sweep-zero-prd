#!/usr/bin/env python3
"""r94: devlog note + event + release control lease."""
import subprocess
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
script = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
TOKEN = "e7ad5ee5c0c742c19f2e1928bda6ea35"

# development log append (pending candidate only, read-then-write)
dp = f"{ROOT}/DEVELOPMENT-LOG.md"
cur = open(dp, encoding="utf-8").read()
note = ("- [2026-10-12 19:3x pending] TASK-07B 串行 OCR b5（`scene_manual_revision_service.py` +383）：前台 5 次 420s reap + "
        "r93 后台 pid 414832 随会话回收后，r94 于低负载窗口（18002 vllm 1 running/0 waiting 实测）以 Hermes 后台跟踪重启"
        "（`proc_7ea84d1aecc6` pid 434432，`--max-tokens 30000`，flock 持 `inbox/ocr.lock`）；OCR 4/10 收口不变"
        "（b1 迁移 0 / b2 api 注册 0 / b3 **1 medium CORRECTION 待裁决** / b4 models 0）；交付 `f4bfcf2` 仍 REVIEW_PENDING 未合入。\n")
if note not in cur:
    open(dp, "w", encoding="utf-8").write(cur + note)
    print("devlog appended")
else:
    print("devlog already present")

# event
r = subprocess.run([
    "python3", script, "--project", ROOT, "--role", "COORDINATOR",
    "--event-id", "coord-poll-20261012-192553-r94-t07b-b5-bg-restart",
    "--task", "TASK-07B", "--attempt", "attempt-1", "--status", "IN_PROGRESS",
    "--summary", "r94: b5 后台 pid 414832 核实随 r93 会话回收（0 字节双文件）；队列低负载（vllm 1/0）→ b5 Hermes 后台跟踪重启 proc_7ea84d1aecc6 pid 434432；再 reap=挂 NEEDS_MAIN_REVIEW",
    "--evidence", "scratch/t07b/ocr/b5_lowtok_out.txt;reviews/TASK-07B/attempt-1/ocr-batches.md",
    "--next", "r95+ poll pid 434432 与 b5_lowtok_out.txt 收口态",
    "event",
], capture_output=True, text=True)
print("event rc=", r.returncode, r.stdout.strip()[:300], r.stderr.strip()[:200])

# release control lease (ocr.lock held by pid 434432 flock, untouched)
r2 = subprocess.run([
    "python3", script, "--project", ROOT, "--role", "COORDINATOR",
    "--token", TOKEN, "release",
], capture_output=True, text=True)
print("release rc=", r2.returncode, r2.stdout.strip()[:300], r2.stderr.strip()[:200])