#!/usr/bin/env python3
"""r95 checkpoint: ledger b5 row + sessions/COORDINATOR.md + HANDOFF.md (read-then-write)."""
import re, time
ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
now = time.strftime("%F %T %z")

# 1) ledger
lp = f"{ROOT}/reviews/TASK-07B/attempt-1/ocr-batches.md"
txt = open(lp, encoding="utf-8").read()
m = re.search(r"\| T07B-b5 \|[^\n]*", txt)
new_b5 = ("| T07B-b5 | app/services/scene_manual_revision_service.py | +383 | 前台 5 次 420s reap + r93 后台 pid 414832 随会话回收 + r94 后台跟踪 pid 434432 亦随 cron 会话回收"
          "（19:55 核 0 字节双文件、进程不存在）；**r95 20:02 起 detached 串行 OCR（`start_new_session` pid 464164，"
          "`r95_ocr_detached.py` `--max-tokens 30000`，flock 持 `inbox/ocr.lock`，逐文件跑 b5→b10 六批，"
          "进度 `scratch/t07b/ocr/remaining_progress.txt`）；r96+ 直接核 progress 文件收口态** | 20:02 起 | DETACHED | 未审 |")
txt = txt.replace(m.group(0), new_b5)
open(lp, "w", encoding="utf-8").write(txt)
print("ledger ok")

# 2) sessions/COORDINATOR.md (prepend)
sp = f"{ROOT}/sessions/COORDINATOR.md"
s = open(sp, encoding="utf-8").read()
seg = f"""## 2026-10-12 20:0x r95（preflight checked_at 2026-10-12T19:55:53+08:00，第 95 轮）

- **状态变化**：r94 重启的 b5 后台跟踪 `proc_7ea84d1aecc6` pid 434432 核已随 cron 会话回收（20:0x 核 0 字节双文件 `b5_lowtok_out.txt`/`_lowtok.log`，ps 无进程）——Hermes 后台跟踪仍不能跨会话存活。
- **恢复动作（本轮实际执行）**：18002 队列低负载实测（2 running/0 waiting，fuser 核 ocr.lock 无旧持有者）→ claim（owner `cron-coord-poll-14ae4556629a-20261012-195553-r95-t07b-b5b10-detached-launch`，20:01:09，token 自 lease JSON）→ 改 **detached 串行 OCR**：`r95_launch.py` 经 `start_new_session=True` 拉起 `r95_ocr_detached.py` **pid 464164**（独立 session 20:02:16 起，setsid 后存活已核 ps PGID=464164），逐文件 `--max-tokens 30000` 跑 b5→b10 六批（flock 全程持 `inbox/ocr.lock`），b1-b4 已完成批次排除，进度文件 `scratch/t07b/ocr/remaining_progress.txt`（20:02:16 起始行已核）。
- 交付冻结 REVIEW_PENDING 不变：`f4bfcf2`（base `502bf8e`，main 未合入）；OCR 已收口 4/10（b1 0 / b2 0 / b3 **1 medium CORRECTION 待裁决** / b4 0）。
- **强审查**：授权在案 grant `31dcbabe…` 至 2026-10-13 11:33:12 +08:00，滚动 60 分钟 0/5，累计 0，在途 0，token/费用未知；07B 预判 REVIEW_NOW 待 OCR 收口。
- **门禁**：TASK-07 RUNNING（07B 不合入）；TASK-11 生产 BLOCKED；12-15 DEFERRED；A/C/TESTER 空闲；B 交付冻结。
- **下一步（r96+）**：核 `remaining_progress.txt` 逐批收口（RC=0 + Review complete=过；再 reap/超时如实记账）→ 收口后裁决 b3 medium（最小返修 vs 并入 TESTER 验证口径）→ 强审查 pack 起跑（授权 0/5 期限 2026-10-13 11:33:12）→ 合入 → TESTER 独立验证 → 07B DONE → 派 07C。
- 控制租约已 release（detached OCR 只占 ocr.lock，与 r94 口径一致）。
"""
if "r95（preflight checked_at 2026-10-12T19:55:53" not in s:
    s = seg + "\n" + s
    open(sp, "w", encoding="utf-8").write(s)
    print("sessions ok")
else:
    print("sessions already present")

# 3) HANDOFF.md (prepend, below nothing — file starts with old checkpoint header)
hp = f"{ROOT}/HANDOFF.md"
h = open(hp, encoding="utf-8").read()
hseg = f"""## 2026-10-12 20:0x 巡检检查点（cron poll 14ae4556629a，第 95 轮，preflight checked_at 2026-10-12T19:55:53+08:00；**状态变化=r94 后台跟踪 pid 434432 核实随 cron 会话回收（0 字节双文件）→ r95 改 detached 串行 OCR（`start_new_session` pid 464164，20:02:16 起，`--max-tokens 30000` 逐文件跑 b5→b10 六批，flock 持 `inbox/ocr.lock`）**）

- 07B attempt-1 交付冻结 REVIEW_PENDING 不变（`f4bfcf2`，base `502bf8e`，main 未合入）；OCR 已收口 4/10（b1 迁移 0 / b2 api 注册 0 / b3 **1 medium CORRECTION 待裁决** / b4 models 0）。
- **r95 恢复入口**：Hermes 后台跟踪进程两次均随 cron 会话结束回收（r93 pid 414832、r94 pid 434432，本轮 0 字节双文件+ps 核）→ 改 **detached（`start_new_session=True`）pid 464164**，独立 session 跨 cron 存活；进度文件 `scratch/t07b/ocr/remaining_progress.txt`，r96+ 直接核该文件（RC=0+Review complete=收口；再 reap/超时如实记账，不无限重试）。
- 强审查授权在案（grant `31dcbabe…` 至 2026-10-13 11:33:12，滚动 60 分钟 0/5，累计 0，在途 0，token/费用未知）；07B 预判 REVIEW_NOW 待 OCR 收口。
- 门禁：TASK-07 RUNNING（07B 不合入）；TASK-11 生产 BLOCKED；12-15 DEFERRED；A/C/TESTER 空闲；B 交付冻结。
"""
if "第 95 轮，preflight checked_at 2026-10-12T19:55:53" not in h:
    h = hseg + h
    open(hp, "w", encoding="utf-8").write(h)
    print("handoff ok")
else:
    print("handoff already present")
print("checkpoint done", now)