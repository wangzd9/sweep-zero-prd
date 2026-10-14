#!/usr/bin/env python3
"""r97: prepend checkpoint to sessions/COORDINATOR.md + HANDOFF.md, write event, release lease."""
import json, subprocess, sys, time
from pathlib import Path

ROOT = Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
RUNTIME = "/home/wang/.codex/skills/complex-task-coordinator/scripts/role_runtime.py"
TOKEN = "d5bb0b9634ba41af927fbf551ff29476"
OWNER = "cron-coord-poll-14ae4556629a-20261012-202053-r97"

CHECKPOINT = """## 2026-10-12 20:2x 巡检检查点（cron poll 14ae4556629a，preflight checked_at 2026-10-12T20:20:53+08:00，第 97 轮；r95 detached OCR 在途正常，零业务变化）

- **r95 detached 串行 OCR 在途核（20:22 实测）**：pid 464164（PGID=464164 Ss，20:02:16 起，ELAPSED 19:47）存活，`fuser` 核 `inbox/ocr.lock` 由其 flock 持有；子进程 node `ocr review`（pid 464166）仍在 **b5 `scene_manual_revision_service.py`**（`--max-tokens 30000`，`--from 502bf8e --to f4bfcf2`）；`remaining_progress.txt` 仍 1 行起始标记、b5 日志 0 字节=首文件在途未收口（约 20 分钟，r92 同尺寸单文件 329-415s 口径外，因队列饱和拉长，detached 无外层 420s 上限，不 reap 不重启）。
- **队列实况（20:22/20:23 vllm metrics 实测）**：`18002` num_requests_running=**4**、waiting=2-3（capacity）=其他 worker 抢占窗口持续，b5 收口时间不可精确预估；脚本逐文件续跑 b6-b10 直至 `== r95 detached done ==` 标记。
- main 双核实测：本地 main `c2018dd`（HANDOFF 0.4 规划段已记录=github 侧 `30e55a3`+1 纯文档 commit，零 app 面）；**origin/main 仍 `502bf8e`=07B base，零漂移**；交付冻结 REVIEW_PENDING 不变（`f4bfcf2` 未合入）。
- OCR 已收口 4/10（b1 0 / b2 0 / b3 **1 medium CORRECTION 待裁决** / b4 0）；角色占用：B=交付冻结；A/C/TESTER 空闲（preflight legacy_busy 空）；pid 464164/464166 为唯一在途业务进程。
- **强审查（strong_review.py status 本轮只读实测 20:2x）**：AUTHORIZED，grant `31dcbabe…`，绝对期限 **2026-10-13 11:33:12 +08:00**，滚动 60 分钟 **0/5**、本授权累计 **0 次**、在途 0、token/费用=**未知**；07B 预判 REVIEW_NOW 待 OCR 收口。
- 门禁：TASK-07 RUNNING（07B 不合入）；TASK-11 生产 BLOCKED；12-15 DEFERRED；changelog F-035~039 等用户审批不催。
- 本轮控制动作：preflight（20:20:53）+claim（20:24:14，token 自输出）→巡检核查（ps+fuser 核 detached 存活与锁/remaining_progress+b5 日志核/vllm metrics 双时点/main rev-parse 双核/strong_review status 只读）→checkpoint+event→release。**无新派单、无合入、无门禁变更**。
- **下一步：** r98+ 核 `remaining_progress.txt`（FILE=b5 RC=0+Review complete=记账续 b6-b10；pid 464164 已退且无 done 标记=异常如实记账，按 r95 预案不无限重启，挂 NEEDS_MAIN_REVIEW 交长寿命会话）→全收口后裁决 b3 medium→强审查 pack 起跑（授权 0/5，期限 2026-10-13 11:33:12）→合入→TESTER 独立验证→07B DONE→派 07C。
"""

# sessions/COORDINATOR.md: read first, then rewrite with prepend (never open "w" before read)
s = ROOT / "sessions/COORDINATOR.md"
old = s.read_text(encoding="utf-8")
if "20:2x 巡检检查点（cron poll 14ae4556629a，preflight checked_at 2026-10-12T20:20:53+08:00，第 97 轮" in old:
    print("SKIP sessions: already written")
else:
    s.write_text(CHECKPOINT + old, encoding="utf-8")
    print("sessions: prepended OK, size now", s.stat().st_size)

# HANDOFF.md: append r97 line to the top section (prepend a compact checkpoint block)
h = ROOT / "HANDOFF.md"
oldh = h.read_text(encoding="utf-8")
HLINE = """## 2026-10-12 20:2x 巡检检查点（cron poll 14ae4556629a，第 97 轮，preflight checked_at 2026-10-12T20:20:53+08:00；r95 detached OCR 在途正常，零业务变化）

- r95 detached 串行 OCR 在途核：pid 464164 存活（20:02:16 起，fuser 核 flock 持 `inbox/ocr.lock`），b5 `scene_manual_revision_service.py` 未收口（progress 文件仍起始行、日志 0 字节，约 20min，队列 4 running+2-3 waiting 饱和拉长，无外层上限不 reap）；`remaining_progress.txt` 为 r98+ 唯一收口核点。
- main 双核：本地 `c2018dd`（纯文档，零 app 面）/ **origin/main 仍 `502bf8e`=07B base 零漂移**；07B 交付冻结 REVIEW_PENDING 不变；OCR 收口 4/10（b3 1 medium 待裁决）。
- 强审查授权在案（grant `31dcbabe…` 至 2026-10-13 11:33:12，滚动 60 分钟 0/5，累计 0，在途 0，token/费用未知）；07B 预判 REVIEW_NOW 待 OCR 收口。
- 门禁：TASK-07 RUNNING（07B 不合入）；TASK-11 生产 BLOCKED；12-15 DEFERRED；A/C/TESTER 空闲；B 交付冻结。
"""
if "第 97 轮，preflight checked_at 2026-10-12T20:20:53+08:00" in oldh:
    print("SKIP handoff: already written")
else:
    h.write_text(HLINE + oldh, encoding="utf-8")
    print("handoff: prepended OK, size now", h.stat().st_size)

# event file
evdir = ROOT / "inbox/events/COORDINATOR"
evdir.mkdir(parents=True, exist_ok=True)
ev = evdir / "coord-poll-20261012-202053-r97-ocr-inflight-nochange.md"
if not ev.exists():
    ev.write_text(f"""# event: coord-poll-20261012-202053-r97-ocr-inflight-nochange

- owner: {OWNER}
- task: TASK-07B
- attempt: 1
- status: NO_CHANGE
- summary: r97 巡检：r95 detached OCR pid 464164 存活在途（b5 未收口，progress 起始行+日志 0 字节），origin/main 502bf8e 零漂移，交付冻结 REVIEW_PENDING 不变；零新派单/零合入/零门禁变更。
- evidence: ps+fuser 20:22 实测、remaining_progress.txt、strong_review.py status 20:2x（0/5，授权至 2026-10-13 11:33:12）
- next: r98+ 核 remaining_progress.txt b5 收口
- recorded_at: {time.strftime('%F %T %z')}
""", encoding="utf-8")
    print("event: written", ev)

# release control lease
out = subprocess.run([sys.executable, RUNTIME, "release", "--project", str(ROOT),
                      "--role", "COORDINATOR", "--token", TOKEN],
                     capture_output=True, text=True, timeout=60)
print("release RC=", out.returncode)
print(out.stdout[-300:])
print(out.stderr[-300:])