#!/usr/bin/env python3
"""TESTER 5-min poll heartbeat prepend for sessions/TESTER.md (2026-10-11 18:05)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sessions = ROOT / "sessions" / "TESTER.md"

entry = (
    "- 心跳：2026-10-11 18:05 CST（本轮唤醒=v2 5分钟巡检 preflight checked_at 2026-10-11T18:04:53+08:00 "
    "control=ACTIVE、legacy_busy 空、无存活旧 owner；TESTER lease claim cron-tester-poll-1805"
    "（token 42d46943…）短写即释放。18:00 后共享根变动仅 HANDOFF 协调者巡检检查点与各角色 runtime ticks"
    "（find 18:00:30 后排除 runtime/sessions/events/scratch/lock 核对），**非测试者派单**；"
    "git 独立复核 main HEAD `98f6c88`（= origin/main fetch 双核一致，17:02 c3-1 合入后未再变、纯 tests 面、"
    "attempt-5 PASS 4/4 被测 app 行为面快照不变、**证据不失效**）；`wt-04a-t08c` HEAD 仍 `f9bafb0`，"
    "2号 t08c-1（C1/C2 秒精度专项，**app 行为面**）持续在途推进：app 行为面改动 6 文件"
    "（18:02:27 `M app/services/bootstrap.py`、18:00:05 artifact_service.py、17:59:50 source_service.py、"
    "17:43:56 catalog_ingest.py、17:38:10 bag_cleanup_service.py + scripts/clone 17:45:49）"
    "+ 测试面 test_bag_cleanup_concurrency.py 17:53:41 + untracked test_t08c_probe8.py——实质活动、非停滞，"
    "t08c-1 未交付 commit、receipts/reports/test-receipts 17:55 后无新增（find 核对为空），不代审核、不预跑复测；"
    "inbox/TESTER/ 无新 PENDING（grep status: PENDING 无命中）；docker ps -a 无 tester/t08/r2i 容器残留"
    "（count=0）→ **维持 IDLE**。下一步=等协调者 t08c-1 交付→机械核验→串行 OCR 增量→合入 + 08 收口核 "
    "9 红文件全绿复核口径明确后，如发 TESTER 新派单届时 ACK 后按新 attempt 真 MySQL 隔离库开工）\n"
)

lines = sessions.read_text(encoding="utf-8").splitlines(keepends=True)
sessions.write_text(entry + "".join(lines), encoding="utf-8")
print("heartbeat prepended, new first line bytes:", len(entry.encode("utf-8")))