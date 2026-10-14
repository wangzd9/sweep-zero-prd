#!/usr/bin/env python3
"""TESTER poll 13:34:53 — claim -> update sessions/TESTER.md -> event -> release. Single script to keep claim token safe in cron."""
import json, subprocess, sys, os, datetime

RUN = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
INBOX = os.path.join(ROOT, "inbox")
OWNER = "cron-tester-poll-167580c0500b-20261012-133453"
CHECKED = "2026-10-12T13:34:53+08:00"

def sh(args):
    p = subprocess.run(args, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

# 1) claim
rc, out, err = sh(["python3", RUN, "--project", ROOT, "--role", "TESTER", "--mode", "poll", "--owner", OWNER, "claim"])
if rc != 0:
    print("CLAIM_FAILED rc=%s out=%s err=%s" % (rc, out, err))
    sys.exit(1)
token = out.splitlines()[-1].strip()
print("claim ok, token=%s..." % token[:8])

# 2) sanity: lease owner is this run
lp = os.path.join(INBOX, "control/runtime/leases/TESTER.json")
lease = json.load(open(lp))
assert lease.get("owner") == OWNER, "lease owner mismatch: %s" % lease.get("owner")

# 3) append new checkpoint to top of sessions/TESTER.md (below header block? convention: newest at top after '## 角色' lines — prior entries are newest-first starting line 1). Insert after the '# 测试者会话状态' header? Existing file has newest entries at the very top, then header further down. To keep newest-first at top:
sp = os.path.join(INBOX, "sessions/TESTER.md")
content = open(sp).read()
new_block = """## 2026-10-12 13:34 巡检（poll，checked_at 2026-10-12T13:34:53+08:00）

- **状态：空闲待命（维持 13:04 基线，无 TESTER 新派单）**。13:04:50 后 find 实测共享根新增均为 TASK-07A attempt-2-r1 返修链（owner=2号/B，`f94d006` 基线）与例行心跳；`inbox/TESTER/` 零新增，无 TESTER PENDING 派单/返修。
- **07A attempt-2-r1 在途（非 TESTER 资源，不接管不催单）**：协调者 r80（13:25:53）确认 B 13:19 ACK 领单在编码（base `f94d006`，范围 `bags.html`+`bag-search.css`+定向测试）；13:15 裁决 `ACCEPT_REPORT_WITH_REWORK`，attempt-1 **未合入**；OCR 增量门禁与合入均在协调者面，TESTER 页面+API 独立验证属下游门禁、未派单即不预占不启动。
- **main `453da0c` = origin/main 双核一致**（rev-parse 实测，被测快照未变）；TESTER 无在途 pytest/业务进程，租约本回合领取后释放。
- **TASK-10 DONE 维持**；TASK-11 生产门禁维持 **PRODUCTION BLOCKED** 待用户授权；TASK-07 其余/12/13/14/15 维持 DEFERRED。
- 本回合 claim `%s` → 巡检核查 → sessions 更新 → release。
- **下一步**：保持空闲待命；等 B attempt-2-r1 交付→机械核验→增量 OCR→合入 main 后，如派 TESTER 页面+API 独立验证单（含 finding #1/#2 行为断言）再 ACK 固定快照开工，不扩需求不重复自测。

""" % OWNER
content = new_block + content
open(sp, "w").write(content)
print("sessions updated")

# 4) release
rc, out, err = sh(["python3", RUN, "--project", ROOT, "--role", "TESTER", "--owner", OWNER, "--token", token, "release"])
if rc != 0:
    print("RELEASE_FAILED rc=%s out=%s err=%s" % (rc, out, err))
    sys.exit(1)
print("release ok")
print("DONE")