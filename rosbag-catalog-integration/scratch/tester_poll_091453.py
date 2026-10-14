#!/usr/bin/env python3
"""TESTER 09:14 巡检单脚本闭环：claim→只读核查(sessions更新)→event→release。"""
import json, subprocess, sys, time, os

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
ROLE = "TESTER"
OWNER = "cron-tester-poll-167580c0500b-20261013-091453"
EVID = ROOT + "/inbox/sessions/TESTER.md"
NOW = time.strftime("%Y-%m-%d %H:%M")

def run_rt(*args):
    p = subprocess.run(["python3", RUNTIME, *args], capture_output=True, text=True)
    out = (p.stdout or "").strip()
    err = (p.stderr or "").strip()
    return p.returncode, out, err

rc, out, err = run_rt("claim", "--project", ROOT, "--role", ROLE, "--owner", OWNER)
if rc != 0:
    print(json.dumps({"stage": "claim", "rc": rc, "out": out, "err": err}, ensure_ascii=False))
    sys.exit(0)
token = None
try:
    token = json.loads(out).get("token")
except Exception:
    pass
if not token:
    lp = os.path.join(ROOT, "inbox/control/runtime/leases/TESTER.json")
    if os.path.exists(lp):
        lj = json.load(open(lp))
        if lj.get("owner") == OWNER:
            token = lj.get("token")
if not token:
    print(json.dumps({"stage": "claim-parse", "rc": rc, "out": out, "err": err}, ensure_ascii=False))
    sys.exit(0)

entry = f"""## 2026-10-13 09:14 巡检（poll，preflight checked_at 2026-10-13T09:14:53+08:00）

- **状态：无 TESTER 新派单、无在途任务**。09:10 基线后 `inbox/TESTER/`、`test-receipts/`、`decision/`、`inbox/coordinator/` find -newermt 实测零 TESTER 范围新增（窗口内仅 C.json 租约 09:11 属 C 面，不接管）。
- fetch 实测 `origin/main`=`3d2a075fd95fd179511aea0244878a277dddc5a3` 未变（07B 整链已合入维持）；ps 实测 TESTER 在途业务进程零（pytest/ocr/e2e/scene_manual 命中 0）；16B proxy OCR 4/4 连败维持 **NEEDS_REVIEW 升级用户裁决待答**（C/协调者面不接管）；TASK-11 生产门禁维持 **PRODUCTION BLOCKED** 待用户授权；16A 独立验证/16D 等测试单均未派不预占。
- 租约面：claim 前 `leases/` 仅 `C.json`（owner `C-cron-poll-20261013-090853` 属 C 面不接管）+ 零字节陈旧 `C.lock`/`TESTER.lock` 维持观察不删。
- 本回合 claim `{OWNER}` → 只读巡检核查 → sessions 更新（canonical+inbox 副本同步）→ event → release 闭环（单脚本执行，token 不出脚本）；无 TESTER 范围业务动作，未重复运行已完成测试。
- **下一步：** 保持待命；协调者派 16A 独立验证（真 MySQL 8.4 迁移往返+AC-14/08）/16D 或其他测试单即 ACK 固定快照/环境/AC 开工，不扩需求不重复自测。
"""

# prepend：先读后写（防截断陷阱）
files = [ROOT + "/sessions/TESTER.md", ROOT + "/inbox/sessions/TESTER.md"]
for f in files:
    old = open(f).read()
    open(f, "w").write(entry + old)

ev_args = ["event", "--project", ROOT, "--role", ROLE, "--token", token,
           "--event-id", "tester-poll-20261013-091453-nochange",
           "--task", "NONE", "--attempt", "0", "--status", "IDLE_POLL",
           "--summary", "09:14 巡检：无 TESTER 新派单/无在途；origin/main=3d2a075 未变；16B NEEDS_REVIEW 待用户裁决维持；TASK-11 生产 BLOCKED 维持；租约面仅 C.json 属他角色不接管",
           "--evidence", EVID, "--next", "保持待命，等 16A/16D 或其他测试派单"]
rc2, out2, err2 = run_rt(*ev_args)
if rc2 != 0:
    print(json.dumps({"stage": "event", "rc": rc2, "out": out2, "err": err2}, ensure_ascii=False))
rc3, out3, err3 = run_rt("release", "--project", ROOT, "--role", ROLE, "--token", token)
print(json.dumps({"stage": "done", "event_rc": rc2, "release_rc": rc3,
                  "event_out": out2[:200], "release_out": out3[:200]}, ensure_ascii=False))