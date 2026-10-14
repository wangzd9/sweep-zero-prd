#!/usr/bin/env python3
# TESTER 5-min poll 2026-10-13 03:54:53: claim -> prepend sessions -> event -> release (single script, token stays inside)
import json, subprocess, sys, pathlib, datetime

ROOT = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-tester-poll-167580c0500b-20261013-035453"
EVENT_ID = "tester-poll-20261013-035453-nochange"
BLOCK = """## 2026-10-13 03:55 巡检（poll，preflight checked_at 2026-10-13T03:54:53+08:00）

- **状态：空闲待命（无 TESTER 新派单）**。03:39:53 基线后 `inbox/TESTER/`、`test-receipts/` find -newermt 实测零新增业务文件；新增仅协调者 r116 事件与 A/B/C/COORDINATOR 租约 ticks，**属他角色面不接管**。
- 协调者面（r116 03:3x）核账：16A v2 OCR b12 `source_service.py` 0 findings 收口 13/14、b13 迁移在途，ps 实测 `ocr review --from c2018dd` pid 1111573（etime ~15 分钟）存活持 `ocr.lock`——**属协调者收口职责，不接管不催单**；无 TESTER 在途业务进程（pytest/e2e/scene_manual 命中 0，mysqld 3599918 为常驻容器非本回合资源）。
- fetch 实测 `origin/main`=`502bf8ec79690cf01e130cb0591121eb10e96af5` 未变（本地 main `c2018dd` 为文档/在途面），07B R3 `4baf79f` 与 16A/16B **未合入，合入门禁维持关闭**；07B post-r3（SR-05 真 MySQL 双连接并发 409 独立验证）**未派，不预占**。
- TASK-07A DONE 维持（`caf385b`，32/32 PASS 在案）；TASK-10 DONE 维持（`453da0c`）；TASK-11 生产门禁维持 **PRODUCTION BLOCKED** 待用户授权；TASK-16D 前置未齐（16A/16B OCR 未收口、16C 未派）不预占。
- 租约面：claim 前 `leases/` 无 TESTER 活跃租约；`TESTER.lock`/`C.lock` 零字节陈旧锁维持观察不删。
- 本回合 claim → 巡检核查 → sessions 更新 → event → release 闭环（单脚本执行，token 不出脚本）；完全无 TESTER 范围业务动作，未重复运行已完成测试。
- **下一步**：保持空闲待命；07B post-r3（SR-05）或 16D 派单收到即 ACK 固定快照/环境/AC 开工，不扩需求不重复自测。
"""

def sh(args, timeout=120):
    p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    print(f"[{args[2] if len(args) > 2 else '?'}] rc={p.returncode}")
    out = (p.stdout or "").strip(); err = (p.stderr or "").strip()
    if out: print("OUT:", out[:800])
    if err: print("ERR:", err[:800])
    return p

p = sh(["python3", RUNTIME, "claim", "--project", str(ROOT), "--role", "TESTER", "--owner", OWNER])
if p.returncode != 0:
    print("CLAIM_FAILED: not taking over, report only"); sys.exit(1)

token = None
lease = ROOT / "inbox/control/runtime/leases/TESTER.json"
if lease.exists():
    d = json.loads(lease.read_text())
    if d.get("owner") == OWNER:
        token = d.get("token")
if not token:
    print("NO_TOKEN: lease owner mismatch, abort writes"); sys.exit(2)

sess = ROOT / "inbox/sessions/TESTER.md"
if sess.read_text().startswith(BLOCK):
    print("sessions already has block, skip prepend")
else:
    bl = ROOT / "scratch/tester/block_035453.txt"
    bl.write_text(BLOCK)
    sh(["python3", RUNTIME, "run", "--project", str(ROOT), "--role", "TESTER", "--token", token,
        "--", "python3", "-c",
        "import pathlib;b=pathlib.Path('%s').read_text();h=pathlib.Path('%s');h.write_text(b+chr(10)+h.read_text())print('prepend-ok')" % (str(bl), str(sess))])
ok = sess.read_text().startswith(BLOCK)
print("sessions-block-landed:", ok)
if not ok:
    print("PREPEND_FAILED: keep lease for release only")

sh(["python3", RUNTIME, "event", "--project", str(ROOT), "--role", "TESTER", "--token", token,
    "--event-id", EVENT_ID, "--task", "IDLE-POLL", "--attempt", "1", "--status", "NO_CHANGE",
    "--summary", "空闲待命：03:39:53 基线后零 TESTER 新增派单/回执；16A v2 OCR b13 迁移在途 13/14（pid 1111573 持 ocr.lock，协调者面不接管）；origin/main 502bf8e 未变，07B/16A/16B 未合入门禁关闭；无 TESTER 业务进程",
    "--evidence", str(sess), "--next", "继续 5 分钟巡检；07B post-r3（SR-05）/16D 派单收到即 ACK 固定快照开工"])

sh(["python3", RUNTIME, "release", "--project", str(ROOT), "--role", "TESTER", "--token", token])
print("lease-gone:", not lease.exists())