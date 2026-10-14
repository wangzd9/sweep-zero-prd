# -*- coding: utf-8 -*-
import io, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
SESSIONS = os.path.join(ROOT, "sessions", "C.md")

entry = (
    "- 最后更新：2026-10-11 19:20 +08:00（v2 cron 巡检：preflight ACTIVE（checked_at 2026-10-11T19:18:53+08:00）、legacy_busy 空；"
    "19:13:53 后共享根唯一 C 范围外新增=`reviews/TASK-08/t08c-1/ocr-batches.md`（find 核实，OCR C1C2-r1 批次账刷新：status **COMPLETED 6/6 app 文件 0 findings**，"
    "逐文件单审 bag_cleanup 1213 行 session `6d53233c` 5m36s 等 6 组全部收口，ps 核实无在途 ocr 进程，**协调者/2号范围非 C，不跨群通报**）；"
    "**main HEAD 已推进 `98f6c88`→`0a8ca8a`**（rosbag-catalog 核实：2号 t08c-1 `bf48a45` 19:17:23 --no-ff 合入，7 文件 +91/-18 C1/C2 秒精度专项，"
    "origin/main 同 `0a8ca8a` 已推，**非 C 交付**）→ TASK-08 收口 2/2 代码面合入完成（c3-1 `98f6c88` + t08c-1 `0a8ca8a`），"
    "剩 9 红文件全绿复核（TESTER/合入后验证）均非 C 范围；"
    "`inbox/3号/` 无新文件（find -printf 核实最新仍 10-10 00:58 attempt-4-ocr-rework ACCEPT_MERGED，TASK-03B 名下全部派单已收口）、"
    "`inbox/coordinator/` 无面向 3号 新单（find -printf 核实最新仍 17:01:40 c3-1 decision，1号范围），**无 C 新派单**；"
    "wt-03b HEAD=`6f1a9ad` 干净（status --porcelain 核实仅 .venv untracked）；"
    "**前轮遗留解除（只读核实，非 C 范围）**：`leases/COORDINATOR.json` 18:31:32 过期租约本轮核实 leases 目录已无文件（清空/recover 完成），不再挂待处理；"
    "ps 核实无 C 在途业务进程；C 本轮短占用 owner `C-cron-poll-20261011-191853` claim 19:20:10，控制动作结束释放；**保持空闲待派单**。前一条 19:13 巡检见下）\n"
)

with io.open(SESSIONS, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 插入到第一个 "- 最后更新" 行之前
idx = None
for i, ln in enumerate(lines):
    if ln.startswith("- 最后更新"):
        idx = i
        break
if idx is None:
    idx = 0
lines.insert(idx, entry)

with io.open(SESSIONS, "w", encoding="utf-8") as f:
    f.writelines(lines)
print("sessions/C.md updated, entry inserted at line", idx + 1)