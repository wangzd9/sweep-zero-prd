#!/usr/bin/env python3
"""A 5min poll 01:51:53 — claim / heartbeat via runtime run / release"""
import json, os, subprocess, sys

RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
OWNER = "cron-a-poll-d5cb80cf2fc5-20261012-015153"

HB = ("- 心跳：2026-10-12 01:56 CST（5min 巡检 preflight checked_at 2026-10-12T01:51:53+08:00，ACTIVE，legacy_busy 空；"
      "git fetch 后 main=origin/main 前移 `a77aa45`→**`453da0c`**（01:51:19 --no-ff 合入 B `t10-defect3` 0943885，"
      "TASK-10 缺口 #3 06B 域发布边界，B/协调者收口链，本角色不代判）。01:48 后 find 核共享根：新增=B 01:46 交付事件 "
      "`b-deliver-20261012-014600-t10-defect3`（REVIEW_PENDING，3 文件 +166/-11，越界申报=E2E 驱动 336-339 未带 actual 边界，复跑 v2 前需补，属 TESTER/协调者）"
      "+ TESTER 01:48 poll 事件（待 merge+复跑 v2 派单）+ C 01:50 nochange + `receipts/TASK-10/t10-defect3-publish-bounds.md`，"
      "**inbox/1号 零新增无新派单/返修**（最新仍 00:12 t10-defect1 ACK 收口在案）。本角色 t10-defect1 已合入 main 收口，无在途待办；"
      "开发槽空闲，#3 已合入等 TESTER 复跑 v2 结论候选重算再派。TODO TASK-10 行仍注「#3 未合入不得 DONE」（01:51 合入后待协调者更新状态，以协调者口径为准）。"
      "wt-01-t10def1 冻结干净（HEAD 1b92ce6 已入 main）。claim（" + OWNER + "，token 整体 JSON 解析）→巡检+心跳记账→release）")

def run(args, env=None):
    return subprocess.run(args, capture_output=True, text=True, env=env)

out = run(["python3", RUNTIME, "claim", "--project", ROOT, "--role", "A", "--owner", OWNER])
print("CLAIM rc", out.returncode, out.stdout.strip(), out.stderr.strip())
if out.returncode != 0:
    sys.exit("claim failed, abort without write")
tok = json.loads(out.stdout).get("token")
print("TOKEN_OK", bool(tok))
if not tok:
    sys.exit("no token")

p = ROOT + "/sessions/A.md"
PREPEND = (
    "import os,sys\n"
    "hb=os.environ['A_HB']\n"
    "f=sys.argv[1]\n"
    "s=open(f,encoding='utf-8').read()\n"
    "line0=s.splitlines()[0]\n"
    "if '01:56 CST' in line0: print('HB_ALREADY_PRESENT')\n"
    "else: open(f,'w',encoding='utf-8').write(hb+chr(10)+s); print('HB_PREPENDED')\n"
)
env = dict(os.environ, A_HB=HB)
res = run(["python3", RUNTIME, "run", "--project", ROOT, "--role", "A", "--token", tok, "--",
           "python3", "-c", PREPEND, p], env=env)
print("RUN rc", res.returncode, res.stdout.strip()[:200], res.stderr.strip()[:300])

rel = run(["python3", RUNTIME, "release", "--project", ROOT, "--role", "A", "--token", tok])
print("RELEASE rc", rel.returncode, rel.stdout.strip()[:200], rel.stderr.strip()[:200])