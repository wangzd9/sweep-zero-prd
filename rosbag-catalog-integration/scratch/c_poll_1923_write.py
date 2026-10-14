#!/usr/bin/env python3
import subprocess, json, sys

RT = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "C-cron-poll-20261011-192353"

def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=90)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

rc, out, err = sh(f"python3 {RT} claim --project {ROOT} --role C --owner {OWNER}")
print("claim rc=", rc, "out:", out[:200], "err:", err[:200])
tok = None
try:
    data = json.loads(out)
    tok = data.get("token") or data.get("lease_token") or data.get("claim_token")
except Exception:
    pass
print("token?", bool(tok))
if not tok:
    sys.exit(1)

line = ("- 最后更新：2026-10-11 19:24 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T19:23:53+08:00）、legacy_busy 空；19:20:10 后共享根新增 4 文件均核实为**非 C 范围**：`TIMELINE.md`/`TODO.md` 协调者 19:21-19:23 记账刷新 + `HANDOFF.md` 19:23 检查点 + `inbox/TESTER/TASK-08/post-merge-0a8ca8a-red-files-ack.md` 19:22（head 核实=**TESTER ACK 合入后 9 红文件全绿复核**，被测 main `0a8ca8a`，真 MySQL 8.4.11 隔离库长测试在途留进程+快照检查点，**测试者范围，TESTER.json 租约在途，非 C**）；`inbox/3号/` 无新文件（find 核实最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、`inbox/coordinator/` 无面向 3号 新单（find 核实最新 19:19 t08c-1 decision 后无新增），**无 C 新派单**；main HEAD=`0a8ca8a`=origin/main 双核一致（rosbag-catalog rev-parse 核实，19:17 t08c-1 合入后未再推进，非 C 交付）、wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 排除 .venv 核实为空）；ps 核实无 C 在途业务进程（grep 命中仅微信 wxocr 非业务）；leases TESTER.json（19:22 测试者长测试业务）/B.json（19:24 2号巡检）在途均非 C 范围；C 本轮短占用 owner `C-cron-poll-20261011-192353` claim 19:24:55 控制动作结束释放；**保持空闲待派单**。前一条 19:20 巡检见下）")

p = f"{ROOT}/sessions/C.md"
with open(p) as f:
    content = f.read()
with open(p, "w") as f:
    f.write(line + "\n" + content)
print("session updated")

rc2, out2, err2 = sh(f"python3 {RT} event --project {ROOT} --role C --token {tok} --event-id C-poll-20261011-192353-nochange --task none --attempt 0 --status IDLE --summary 无C新派单 TESTER post-merge复核在途非C范围 保持空闲 --evidence sessions/C.md --next 继续5分钟巡检待派单")
print("event rc=", rc2, out2[:200], err2[:200])

rc3, out3, err3 = sh(f"python3 {RT} release --project {ROOT} --role C --token {tok}")
print("release rc=", rc3, out3[:200], err3[:200])