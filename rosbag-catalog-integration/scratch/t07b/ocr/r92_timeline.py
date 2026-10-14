#!/usr/bin/env python3
"""r92 TIMELINE 追加（先读后写）。"""
import pathlib

ROOT = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")

ENTRY = """
## 2026-10-12 19:0x 协调者 r92 巡检（preflight 2026-10-12T17:25:53+08:00，OCR 长占约 95min 如实记录）：main `30e55a3`=github/main（=origin `502bf8e`+1 纯文档，07B base 祖先链内有效）；**B TASK-07B attempt-1 17:15 正式交付**（`receipts/TASK-07B/attempt-1.md`，HEAD `f4bfcf2` 2 commit 11 文件 +1235/-4，base `502bf8e` 祖先核 ANCESTOR_OK，worktree 洁净仅 .venv）→协调者独立机械核验**全绿**（定向 10 passed 独立复跑 / ruff app 6 文件 All checks passed / alembic 单头 `20261012_01_scene_manual` / 真 MySQL 8.4 隔离库往返 UPGRADE+超宽 1406 真实生效+DOWNGRADE+RE-UPGRADE 全 PASS 独立复读 `scratch/t07b/mysql_roundtrip_out.txt` / 页面 smoke 26/26 / lastfailed 4 项=既有环境性口径核）→**串行 OCR 4/10 收口**：b1 迁移 0 findings（`fc11be06` 329s，前 2 次 reap 无 manifest 作废）/ b2 `app/api/__init__.py` 0（`ad7c44c4`）/ b3 API **1 medium 属实待裁决**（非 dict JSON→`body.get` 500 与文档化 422 面不一致，CORRECTION 口径，最小修复面=`scene_manual_revision.py` 单文件）/ b4 models 0（`8b4086bd`）；**b5 service 383 行 4 轮 420s reap + b6 CSS 1 轮 reap=本机 Qwen 18002 队列 3-4 并发饱和**（vllm metrics 实测，非工具缺陷），b7-b10 未起跑；账 `reviews/TASK-07B/attempt-1/ocr-batches.md`（恢复入口：b5 再 2 轮 reap→`--max-tokens 30000` 降组拆收口或 NEEDS_MAIN_REVIEW 交长寿命会话，不无限重试；b3 裁决前置=OCR 收口）。**07B 不合入**（OCR 未收口）；B=交付冻结 REVIEW_PENDING，A/C/TESTER 空闲在跳，ps 无 ocr 残留。强审查 AUTHORIZED（grant `31dcbabe`，期限 2026-10-13 11:33:12，60min 0/5，累计 0，token 未知），预判 REVIEW_NOW 待 OCR 收口后 pack 起跑，本轮不起跑。门禁：TASK-07 RUNNING（07A DONE main `caf385b`）/ TASK-10 DONE / TASK-11 PRODUCTION BLOCKED / 12-15 DEFERRED 不变；a100-multi-node 等显式启动；changelog F-035~039 等用户审批。event coord-poll-20261012-172553-r92-t07b-delivered-ocr-partial。
"""

p = ROOT / "TIMELINE.md"
old = p.read_text(encoding="utf-8")
if "r92-t07b-delivered-ocr-partial" in old:
    print("already in TIMELINE, skip")
else:
    p.write_text(old + ENTRY, encoding="utf-8")
    print("appended, now", len(old + ENTRY), "bytes")