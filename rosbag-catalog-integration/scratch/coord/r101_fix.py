#!/usr/bin/env python3
"""r101 fix: undo wrong append in inbox/sessions, append to root sessions + HANDOFF, emit event, release lease."""
import pathlib, subprocess, sys

root = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
MARKER = "\n## 2026-10-12 21:16 \u5de1\u68c0\u68c0\u67e5\u70b9\uff08cron poll 14ae4556629a\uff0c\u771f\u5b9e checked_at 2026-10-12T21:10:53+08:00\uff0cr101\uff09"

# 1. undo wrong append in inbox/sessions/COORDINATOR.md
ib = root / "inbox/sessions/COORDINATOR.md"
text = ib.read_text(encoding="utf-8")
if MARKER in text:
    ib.write_text(text.split(MARKER)[0] + "\n", encoding="utf-8")
    print("inbox/sessions reverted, size:", ib.stat().st_size)
else:
    print("inbox/sessions: marker not found, left as-is")

# 2. append checkpoint to root sessions/COORDINATOR.md (read-first)
sp = root / "sessions/COORDINATOR.md"
prev = sp.read_text(encoding="utf-8")
if "2026-10-12 21:16 \u5de1\u68c0\u68c0\u67e5\u70b9" in prev:
    print("root sessions: r101 checkpoint already present, skip")
else:
    ckpt = MARKER + """
- **20:55 \u540e\u96f6\u4e1a\u52a1\u4ea4\u4ed8**\uff1amain HEAD `502bf8e`\uff08= origin/main\uff0crev-parse \u53cc\u6838\u4e00\u81f4\uff0c07B \u672a\u5408\u5165\uff09\uff1b\u5171\u4eab\u6839 20:55:53 \u540e\u65b0\u589e\u4ec5\u5404\u89d2\u8272\u4f8b\u884c tick/\u5fc3\u8df3\uff0c\u65e0\u65b0\u56de\u6267/\u6d3e\u5355/decision/\u5408\u5165\u3002
- **T07B r95 detached OCR \u5728\u9014\u4e0d\u53d8**\uff1ab9 `app/templates/detail.html` INFLIGHT\uff08node pid 525278 \u8d77 20:51\uff0celapsed 23:34 \u6d3b\u6027\u786e\u8ba4\uff0c\u7236 pid 464164 flock \u6301 `inbox/ocr.lock`\uff09\uff1bb10+\u5951\u7ea6\u6279 QUEUED\uff1b\u6536\u53e3 7/10\uff08b1/b2/b4/b6 0 findings\u3001b3 1 medium \u5f85\u88c1\u51b3\u3001b8 1 low \u975e\u963b\u585e\u3001b5/b7 FAILED \u5f85\u4f4e\u8d1f\u8f7d resume \u6700\u540e\u4e00\u8bd5\uff09\u3002vllm \u8d1f\u8f7d\u5b9e\u6d4b 4 running/2 waiting\uff08capacity\uff09=\u975e\u4f4e\u8d1f\u8f7d\u671f\uff0c**\u672c\u8f6e\u4e0d\u542f\u52a8 b5/b7 resume**\uff0c\u7b49\u961f\u5217\u8d8b\u96f6\u3002
- **\u89d2\u8272\u5360\u7528**\uff1aA/B/C/TESTER \u5168\u7a7a\u95f2\uff08B 21:08 nochange \u5fc3\u8df3\u62a5 T07B \u51bb\u7ed3\u7b49 OCR \u6536\u53e3\uff09\uff1bleases `A.json`/`C.json` \u4e3a\u5404\u89d2\u8272\u4f8b\u884c\u77ed\u79df\u7ea6\uff1b\u65e0\u4ed6\u89d2\u8272\u5728\u9014\u4e1a\u52a1\u6301\u6709\u3002
- **\u5f3a\u5ba1\u67e5**\uff1a\u6388\u6743\u5728\u671f\u81f3 2026-10-13 11:33:12\uff08grant `31dcbabe\u2026`\uff0cTASK-07B \u8303\u56f4\uff09\uff1b\u6eda\u52a8 60 \u5206\u949f 0/5\u3001\u672c\u6388\u6743\u7d2f\u8ba1 0 \u6b21\u3001\u65e0\u5728\u9014\u8c03\u7528\uff1bpack \u524d\u7f6e=OCR \u6536\u53e3+b3 \u88c1\u51b3\uff0c\u672c\u8f6e\u672a\u8d77\u8dd1\uff08\u5de1\u68c0\u56de\u5408\u53ea\u8bfb\uff09\u3002
- \u672c\u8f6e\u63a7\u5236\u52a8\u4f5c\uff1aclam\uff08`cron-coord-poll-14ae4556629a-20261012-211053-r101`\uff09\u2192\u5de1\u68c0\u6838\u67e5\uff08rev-parse \u53cc\u6838/vllm \u8d1f\u8f7d/ps 525278 \u6d3b\u6027/ocr.lock/leases\uff09\u2192append \u68c0\u67e5\u70b9+event\u2192release\u3002**\u65e0\u65b0\u6d3e\u5355\u3001\u65e0\u5408\u5165\u3001\u65e0 OCR \u8d77\u8dd1\u3001\u65e0\u72b6\u6001\u53d8\u66f4**\u3002
- **\u4e0b\u4e00\u6b65\uff1a** r102+ \u6838 `scratch/t07b/ocr/remaining_progress.txt` b9 \u6536\u53e3\u2192b10+\u5951\u7ea6\u6279\u4e32\u884c\u2192vllm \u961f\u5217\u8d8b\u96f6\u540e b5/b7 resume \u6700\u540e\u4e00\u8bd5\u2192b3 medium \u88c1\u51b3\uff08\u9884\u5224\u56de\u6d3e B \u5355\u6587\u4ef6\u5b88\u536b\u6700\u5c0f\u8fd4\u4fee\uff09\u2192\u5f3a\u5ba1\u67e5 pack\u2192\u5408\u5165\u2192TESTER \u9a8c\u8bc1\u219207B DONE\u2192\u6d3e 07C\u3002
"""
    sp.write_text(prev.rstrip("\n") + "\n" + ckpt, encoding="utf-8")
    print("root sessions appended, size:", sp.stat().st_size)

# 3. HANDOFF recovery checkpoint line (root-level, read-first)
hp = root / "HANDOFF.md"
hprev = hp.read_text(encoding="utf-8")
hl = "- **2026-10-12 21:16 r101 \u5de1\u68c0**\uff08checked_at 2026-10-12T21:10:53+08:00\uff09\uff1a20:55 \u540e\u96f6\u4e1a\u52a1\u4ea4\u4ed8\uff1bmain `502bf8e`=\u539f origin \u53cc\u6838\u4e00\u81f4\uff1bT07B r95 detached OCR b9 `detail.html` \u5728\u9014\uff08pid 525278 \u6d3b\u6027\u786e\u8ba4\uff09\uff0cb10+\u5951\u7ea6\u6279 QUEUED\uff0c\u6536\u53e3 7/10\uff1bvllm 4 running/2 waiting \u975e\u4f4e\u8d1f\u8f7d\u671f\uff0cb5/b7 resume \u987a\u5ef6\uff1bA/B/C/TESTER \u5168\u7a7a\u95f2\uff1b\u5f3a\u5ba1\u67e5\u6388\u6743\u5728\u671f\u81f3 2026-10-13 11:33:12\uff0c60min 0/5\uff1b\u65e0\u65b0\u6d3e\u5355/\u5408\u5165/OCR \u8d77\u8dd1\u3002"
if "r101" in hprev:
    print("HANDOFF: r101 already present, skip")
else:
    hp.write_text(hprev.rstrip("\n") + "\n" + hl + "\n", encoding="utf-8")
    print("HANDOFF appended")

# 4. emit event via runtime script
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
r = subprocess.run([
    "python3", RUNTIME, "event",
    "--project", str(root), "--role", "COORDINATOR",
    "--token", "80bc8584b5b3465a8e1d8255deac693e",
    "--event-id", "coord-poll-20261012-211053-r101-t07b-ocr-b9-inflight-nochange",
    "--task", "TASK-07B", "--attempt", "1",
    "--status", "OCR_INFLIGHT",
    "--summary", "r101\uff1a20:55\u540e\u96f6\u4e1a\u52a1\u4ea4\u4ed8\uff1bb9 detail.html \u5728\u9014\uff08pid 525278 \u6d3b\u6027\u786e\u8ba4\uff09\uff1bvllm 4 running/2 waiting \u975e\u4f4e\u8d1f\u8f7d\uff0cb5/b7 resume \u987a\u5ef6\uff1bA/B/C/TESTER \u5168\u7a7a\u95f2\uff1b\u5f3a\u5ba1\u67e5\u6388\u6743\u5728\u671f\u81f3 2026-10-13 11:33:12\uff0c60min 0/5\uff0c\u65e0\u5728\u9014\u8c03\u7528",
    "--evidence", "sessions/COORDINATOR.md r101 \u68c0\u67e5\u70b9; reviews/TASK-07B/attempt-1/ocr-batches.md",
    "--next", "r102 \u6838 b9 \u6536\u53e3\u2192b10+\u5951\u7ea6\u6279\u2192\u4f4e\u8d1f\u8f7d\u671f b5/b7 resume",
], capture_output=True, text=True)
print("event rc:", r.returncode)
print(r.stdout[-800:] if r.stdout else "")
if r.returncode != 0:
    print(r.stderr[-800:] if r.stderr else "")

# 5. release lease
r2 = subprocess.run([
    "python3", RUNTIME, "release",
    "--project", str(root), "--role", "COORDINATOR",
    "--token", "80bc8584b5b3465a8e1d8255deac693e",
], capture_output=True, text=True)
print("release rc:", r2.returncode, r2.stdout[-200:] if r2.stdout else r2.stderr[-200:])
sys.exit(0 if r.returncode == 0 and r2.returncode == 0 else 1)