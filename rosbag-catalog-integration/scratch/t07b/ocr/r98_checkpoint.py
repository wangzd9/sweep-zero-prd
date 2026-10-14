#!/usr/bin/env python3
"""r98: OCR batch ledger update (b5 FAILED / b6 COMPLETED / b7 INFLIGHT) + checkpoint prepend."""
import time

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"

# 1) ocr-batches.md 账更新
ledger = f"{ROOT}/reviews/TASK-07B/attempt-1/ocr-batches.md"
with open(ledger, "r", encoding="utf-8") as f:
    t = f.read()

b5_row_old = t[t.index("| T07B-b5 |"):t.index("| T07B-b6 |")]
b5_row_new = (
    "| T07B-b5 | app/services/scene_manual_revision_service.py | +383 | "
    "r95 detached 第 6 次尝试 session `81a66282` **RC=1 FAILED**（20:02:16→20:32:3x，1800s，core request timed out、compaction cancelled，usage 1186534 tokens/109 工具调用，vllm 4 并发饱和期；前 5 次 420s reap/回收全作废）"
    " | 20:02-20:32 | FAILED（第 6 次） | 未审；**重试政策=r99+ 等 detached 跑完 b7-b10 后低负载期 `--resume 81a66282` 最后一次，再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁，不无限重试** |\n"
)
t = t.replace(b5_row_old, b5_row_new)

b6_row_old = t[t.index("| T07B-b6 |"):t.index("| T07B-b7 |")]
b6_row_new = (
    "| T07B-b6 | app/static/bag-detail.css | +13 | r95 detached session `c010afa4-105c-4b4e-83c5-f71ae8c21c08` **RC=0 79s**（20:32:3x→20:33:1x） | 20:33 | COMPLETED | **0** |\n"
)
t = t.replace(b6_row_old, b6_row_new)

b7_row_old = t[t.index("| T07B-b7 |"):t.index("| T07B-b8 |")]
b7_row_new = (
    "| T07B-b7 | app/static/bag-search.css | +12/-1 | r95 detached 在途（20:33 起，node pid 503788，flock 持 `inbox/ocr.lock`） | 20:33 起 | INFLIGHT（detached） | 未审 |\n"
)
t = t.replace(b7_row_old, b7_row_new)

t = t.replace(
    "**恢复入口（r94+）**：核 b5 后台 pid 414832（`b5_lowtok_out.txt`/`…_lowtok.log`）：收口=记账续跑 b6-b10（b6 13 行 CSS 可前台短跑）；再 reap=挂 NEEDS_MAIN_REVIEW 交长寿命会话，不无限重试。b3 finding 裁决前置=OCR 收口（避免返修后旧批作废）；b3 预判=回派 B 最小返修（`app/api/scene_manual_revision.py` 单文件 isinstance/pydantic 守卫）与 07B 返修链合并。",
    "**恢复入口（r99+）**：detached pid 464164 跑完 b7-b10 后（progress 文件 `== r95 detached done ==` 标记）核 b8-b10 收口态；**b5 唯一剩余动作=低负载期（vllm waiting 趋 0）`ocr review --from 502bf8e --to f4bfcf2 --audience agent --max-tokens 30000 --exclude <其余 9 文件> --resume 81a66282-6ab7-4a78-a3d5-f309033d8dde` 最后一次尝试**，再失败=挂 NEEDS_REVIEW 冻结 07B 合入门禁（b5 为核心服务面，OCR 未覆盖不得宣称收口）；不无限重试。b3 finding 裁决前置=OCR 收口（避免返修后旧批作废）；b3 预判=回派 B 最小返修（`app/api/scene_manual_revision.py` 单文件 isinstance/pydantic 守卫）与 07B 返修链合并。"
)
with open(ledger, "w", encoding="utf-8") as f:
    f.write(t)
print("ledger updated")

# 2) sessions/COORDINATOR.md 顶部 prepend 检查点
sess = f"{ROOT}/sessions/COORDINATOR.md"
with open(sess, "r", encoding="utf-8") as f:
    s = f.read()
cp = """## 2026-10-12 20:3x 巡检检查点（cron poll 14ae4556629a，第 98 轮，preflight checked_at 2026-10-12T20:30:53+08:00；**状态变化=r95 detached OCR：b5 第 6 次 FAILED（RC=1 timeout 1800s，usage 1186534 tokens）+ b6 COMPLETED 0 findings（79s）+ b7 在途**）

- **b5 `scene_manual_revision_service.py`（+383 核心服务面）r95 detached 第 6 次尝试失败**：20:02:16 起跑→20:32 收口 RC=1（core request **timed out**、context compaction cancelled，1800s/109 工具调用/1186534 tokens，vllm 4 并发饱和期排队所致；session `81a66282`）。累计=前台 5 次 420s reap + 本轮 timeout，**重试政策落账：detached 跑完 b7-b10 后低负载期 `--resume 81a66282` 最后一次，再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁，不无限重试**。
- **b6 `bag-detail.css`（+13）COMPLETED 0 findings**（session `c010afa4`，RC=0 79s，20:32:3x→20:33:1x）；**b7 `bag-search.css`（+12/-1）INFLIGHT**（20:33 起 node pid 503788，detached 父 pid 464164 flock 持 `inbox/ocr.lock`，正常推进不干预）。
- OCR 收口进度 5/10（b1 0 / b2 0 / b3 1 medium 待裁决 / b4 0 / b6 0）+ b5 FAILED + b7 在途 + b8-b10/契约批次 QUEUED。
- main 不变：本地 `c2018dd` / origin `502bf8e`（07B base 零漂移）；07B 交付冻结 REVIEW_PENDING 不变（`f4bfcf2` 未合入）；18002 可达（HTTP 200，running=4 仍饱和）。
- 角色占用：B=交付冻结；A/C/TESTER 空闲（legacy_busy 空）；detached pid 464164 为唯一在途业务进程。
- **强审查（续 r97 只读账本口径）**：AUTHORIZED，grant `31dcbabe…`，期限 **2026-10-13 11:33:12 +08:00**，滚动 60 分钟 0/5、累计 0、在途 0、token/费用未知；07B 预判 REVIEW_NOW 待 OCR 收口。
- 门禁：TASK-07 RUNNING（07B 不合入）；TASK-11 生产 BLOCKED；12-15 DEFERRED。
- 本轮控制动作：claim（`cron-coord-poll-14ae4556629a-20261012-203053-r98-b5fail-b6inflight`，20:33:33）→巡检核查（ps/fuser/progress 文件独立核 b5 FAILED+b6 PASS+b7 在途/vllm metrics/18002 可达性）→OCR 批次账+本 checkpoint+event→release。**无新派单、无合入、无强审查调用**。
- **下一步：** r99+ 核 detached b7-b10 收口（progress 文件）→b5 `--resume 81a66282` 低负载最后一次→裁决 b3 medium（最小返修预判）→OCR 收口后强审查 pack（0/5，期限 2026-10-13 11:33:12）→合入→TESTER 独立验证→07B DONE→派 07C。
"""
with open(sess, "w", encoding="utf-8") as f:
    f.write(cp + s)
print("sessions checkpoint prepended")

# 3) HANDOFF.md 顶部 prepend 短检查点
hand = f"{ROOT}/HANDOFF.md"
with open(hand, "r", encoding="utf-8") as f:
    h = f.read()
hcp = """## 2026-10-12 20:3x 巡检检查点（cron poll 14ae4556629a，第 98 轮，preflight checked_at 2026-10-12T20:30:53+08:00；**状态变化=r95 detached OCR：b5 第 6 次 FAILED（timeout 1800s）+ b6 COMPLETED 0 findings + b7 在途**）

- b5（+383 核心服务面）累计 6 次未收口（前台 5 次 420s reap + r95 timeout RC=1，session `81a66282` usage 1186534 tokens，vllm 4 并发饱和）→**重试政策落账：b7-b10 跑完后低负载期 `--resume 81a66282` 最后一次，再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁，不无限重试**；b6 0 findings（79s）；b7 在途（pid 503788，flock 持 `inbox/ocr.lock`）。
- OCR 收口 5/10（b1/b2/b4/b6 0 + b3 1 medium 待裁决）+ b5 FAILED + b7 在途 + b8-b10 QUEUED；main 本地 `c2018dd`/origin `502bf8e`（07B base 零漂移）；07B 交付冻结 REVIEW_PENDING 不变（`f4bfcf2` 未合入）。
- 强审查授权在案（grant `31dcbabe…` 至 2026-10-13 11:33:12，滚动 60 分钟 0/5，累计 0，在途 0，token/费用未知）；07B 预判 REVIEW_NOW 待 OCR 收口。
- 门禁：TASK-07 RUNNING（07B 不合入）；TASK-11 生产 BLOCKED；12-15 DEFERRED；A/C/TESTER 空闲；B 交付冻结。
"""
with open(hand, "w", encoding="utf-8") as f:
    f.write(hcp + h)
print("handoff checkpoint prepended")

# 4) event 落盘
evdir = f"{ROOT}/inbox/events/COORDINATOR"
import os
os.makedirs(evdir, exist_ok=True)
ev = f"""event_id: coord-poll-20261012-203053-r98-b5-failed-b6-pass-b7-inflight
role: COORDINATOR
task: TASK-07B
attempt: 1
status: OCR_INFLIGHT
time: {time.strftime('%Y-%m-%dT%H:%M:%S%z')}
summary: r95 detached 串行 OCR 核账：b5 scene_manual_revision_service.py 第 6 次 FAILED（RC=1 timeout 1800s，session 81a66282，usage 1186534 tokens，vllm 4 并发饱和）；b6 bag-detail.css COMPLETED 0 findings（c010afa4，79s）；b7 bag-search.css INFLIGHT（pid 503788）。重试政策落账=b7-b10 后低负载期 --resume 81a66282 最后一次，再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁，不无限重试。
evidence: scratch/t07b/ocr/remaining_progress.txt; reviews/TASK-07B/attempt-1/ocr-batches.md
next: r99+ 核 detached b7-b10 收口→b5 resume 最后一次→b3 medium 裁决→强审查 pack（授权 0/5 至 2026-10-13 11:33:12）→合入→TESTER 验证→07B DONE→派 07C
"""
with open(f"{evdir}/coord-poll-20261012-203053-r98-b5-failed-b6-pass-b7-inflight.md", "w", encoding="utf-8") as f:
    f.write(ev)
print("event written")