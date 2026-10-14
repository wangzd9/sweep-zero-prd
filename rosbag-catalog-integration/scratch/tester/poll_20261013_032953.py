#!/usr/bin/env python3
# TESTER 5-min poll 2026-10-13 03:29:53: claim -> prepend sessions -> event -> release (single script, token stays inside)
import json, subprocess, sys, pathlib

ROOT = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
OWNER = "cron-tester-poll-167580c0500b-20261013-032953"
EVENT_ID = "tester-poll-20261013-032953-nochange"
BLOCK = """## 2026-10-13 03:30 巡检（poll，preflight checked_at 2026-10-13T03:29:53+08:00）

- **状态：空闲待命（无 TESTER 新派单）**。03:25 基线后 `inbox/TESTER/`、`test-receipts/`、`inbox/coordinator/`、`decision/` find -newermt 实测零新增；新增仅本角色 events 巡检面，不接管。
- 协调者 r115（03:20）核账：16A v2 OCR b11 收口、b12 在途——**属协调者面，不接管不催单**；ps 实测 `ocr review` pid 1085908 cwd `wt-01-t16a` 为 16A/16B v2 面，无 TESTER 在途业务进程（pytest/e2e 命中 0）。
- fetch 实测 `origin/main`=`502bf8ec79690cf01e130cb0591121eb10e96af5` 未变，07B R3 `4baf79f` 与 16A/16B **未合入，合入门禁维持关闭**；SR-05 真 MySQL 双连接并发 409 独立验证单**未派，不预占**。
- 租约面：无 TESTER 活跃租约；`TESTER.lock` 零字节陈旧锁维持观察不删；`C.json` 属 C 角色不接管。
- TASK-07A DONE 维持（`caf385b`，32/32 PASS 在案）；TASK-10 DONE 维持（`453da0c`）；TASK-11 生产门禁维持 **PRODUCTION BLOCKED** 待用户授权；TASK-16D 前置未齐（16A/16B OCR 收口在途）不预占。
- 本回合 claim → 巡检核查 → sessions 更新 → event → release 闭环（单脚本执行，token 不出脚本）；完全无 TESTER 范围业务动作，未重复运行已完成测试。
- **下一步**：保持空闲待命；07B post-r3（SR-05 真 MySQL 双连接 200/409）或 16D 派单收到即 ACK 固定快照/环境/AC 开工，不扩需求不重复自测。
"""

def sh(args, timeout=120):
    p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    tag = args[3] if len(args) > 3 else "?"
    print(f"[{tag}] rc={p.returncode}")
    out = (p.stdout or "").strip()
    err = (p.stderr or "").strip()
    if out:
        print("OUT:", out[:600])
    if err:
        print("ERR:", err[:600])
    return p

# 1) claim
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

# 2) prepend checkpoint via short control run
sess = ROOT / "sessions/TESTER.md"
if sess.read_text().startswith(BLOCK):
    print("sessions already has block, skip prepend")
else:
    sh(["python3", RUNTIME, "run", "--project", str(ROOT), "--role", "TESTER", "--token", token,
        "--", "python3", "-c",
        "import pathlib;b=pathlib.Path('%s').read_text();h=pathlib.Path('%s');b2=h.read_text();p=pathlib.Path('%s');p.write_text(b2+'\\n'+b)print('prepend-ok')" % (str(sess), str(pathlib.Path(__file__).parent / "block_032953.txt"), str(sess))])
ok = sess.read_text().startswith(BLOCK)
print("sessions-block-landed:", ok)
if not ok:
    print("PREPEND_FAILED: keep lease for release only")

# 3) event
sh(["python3", RUNTIME, "event", "--project", str(ROOT), "--role", "TESTER", "--token", token,
    "--event-id", EVENT_ID, "--task", "IDLE-POLL", "--attempt", "1", "--status", "NO_CHANGE",
    "--summary", "空闲待命：03:25 后零 TESTER 新增派单/回执；07B R3 4baf79f 与 16A/16B 未合入（origin/main 502bf8e 不变）；ocr pid 1085908 属 16A v2 面不接管；无 TESTER 业务进程",
    "--evidence", str(sess), "--next", "继续 5 分钟巡检；07B post-r3/16D 派单收到即 ACK 固定快照开工"])

# 4) release
sh(["python3", RUNTIME, "release", "--project", str(ROOT), "--role", "TESTER", "--token", token])
print("lease-gone:", not lease.exists())