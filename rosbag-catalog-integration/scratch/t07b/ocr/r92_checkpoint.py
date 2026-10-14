#!/usr/bin/env python3
"""r92 检查点落盘：sessions/COORDINATOR.md 与 HANDOFF.md 顶部插入新检查点（先读后写，防截断）。"""
import pathlib

ROOT = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")

CP = """## 2026-10-12 19:0x 巡检检查点（cron poll 14ae4556629a，preflight checked_at 2026-10-12T17:25:53+08:00，实际 19:0x 完成=排队+OCR 长占约 95min 如实记录，第 92 轮；**状态变化=B TASK-07B attempt-1 17:15 正式交付（`f4bfcf2`，2 commit，11 文件 +1235/-4）→机械核验全绿→串行 OCR 4/10 收口（迁移/api注册/models 0 findings + 1 处 medium 属实待裁决），LLM 队列饱和 4 并发致 b5 起每批 420s reap，b5-b10 待续**）

- main `30e55a3`=github/main（=origin/main `502bf8e` + 1 纯文档 commit，r91 已记）；07B base `502bf8e` 在其祖先链内有效，**未合入**。
- **B 07B attempt-1 交付（17:15）`receipts/TASK-07B/attempt-1.md` + `reports/TASK-07B/attempt-1.md`**：HEAD `f4bfcf2`（`5fa0942` 主体 + `f4bfcf2` corrected_label 域契约修正，base `502bf8e` 双核，`merge-base --is-ancestor` 独立核 ANCESTOR_OK），worktree 洁净仅 .venv 软链，11 文件与派单范围一致。
- **协调者独立机械核验全绿（非复述回执）**：定向 `pytest tests/test_task07b_manual_revision.py tests/test_task07a_visibility.py`=**10 passed**（wt venv 独立复跑）；`ruff check` 交付 app 6 文件 **All checks passed**（独立复跑；首轮 3669 errors 系误把 html/css 全目录传入，按文件精确核已纠正）；`alembic heads` 单头 `20261012_01_scene_manual`；真 MySQL 8.4 隔离库往返证据独立复读 `scratch/t07b/mysql_roundtrip_out.txt`（UPGRADE/边界 INSERT/超宽 1406 真实生效/DOWNGRADE/RE-UPGRADE/CLEANUP 全 PASS）；页面实测 `page_smoke_out.txt` 26/26 PASS（17:12 收口）；lastfailed 独立核=4 项既有环境性（test_devflow×3 + test_web 响应时间×1），B 已申报 base 复现同口径，交付时口径核过=**非本侧回归**。
- **串行 OCR（flock 持 `inbox/ocr.lock`，逐文件单审防 reap，账 `reviews/TASK-07B/attempt-1/ocr-batches.md`）**：✅ T07B-b1 迁移 `20261012_01_scene_manual.py` **0 findings**（session `fc11be06` 329s；前 2 次 420s reap 无 manifest 不可 resume 作废 `fe1d6fee`/`9ae3219f`）/ ✅ b2 `app/api/__init__.py` 0 findings（`ad7c44c4` 25s）/ ⚠️ b3 `app/api/scene_manual_revision.py` **1 处 medium**（`request.json()` 后非 dict JSON → `body.get` AttributeError 500，与文档化 422 面不一致；协调者独立核代码属实=**CORRECTION 待裁决**：最小修复可并入 07B 返修或 TESTER 独立验证后按强审查/门禁口径定）/ ✅ b4 `app/models.py` 0 findings（`8b4086bd` 87s）；❌ **b5 `scene_manual_revision_service.py`（383 行）4 轮 420s reap 未收口**（`8b04806a`/`38715616` 等无 manifest）/ ❌ b6 `bag-detail.css` 1 轮 reap——**根因=本机 Qwen 18002 持续 3-4 并发队列饱和（其他 worker 抢占，vllm metrics 实测），单轮 cron 420s 硬上限内无法出结果**，非工具缺陷；b7-b10 未起跑。
- **角色占用**：B=交付冻结 REVIEW_PENDING（等 OCR 收口+裁决）；A/C/TESTER 空闲在跳（legacy_busy 空）；leases 仅 C/TESTER 零字节陈旧锁；ps 无 ocr 业务进程（本轮 reap 后已退出）。
- **强审查（strong_review.py status 只读账本口径，续 r91）**：AUTHORIZED，grant `31dcbabe…`，绝对期限 **2026-10-13 11:33:12 +08:00**，范围=本项目 REVIEW_NOW 判定；滚动 60 分钟 **0/5**、本授权累计 **0 次**、在途 0、token/费用=**未知**。07B 写接口面预判 **REVIEW_NOW**，待 OCR 收口后按 pack 流程判定，本轮不起跑。
- **门禁**：TASK-07 维持 RUNNING（07A DONE main `caf385b`；**07B 交付=机械核验过+OCR 4/10 未收口，不合入**；b3 medium finding 待裁决；07C 串行待 07B 收口）；TASK-10 DONE/P0 收口维持；TASK-11 生产维持 PRODUCTION BLOCKED；TASK-12/13/14/15 DEFERRED 不扩；`a100-multi-node/` 维持等显式启动；changelog F-035~039 等用户审批不催。
- 本轮控制动作：claim（`cron-coord-poll-14ae4556629a-20261012-172553-r92`，17:27:05，token 自 lease JSON）→巡检核查（发现 B 17:15 正式交付/find -newermt 16:39 核）→独立机械核验（ancestor 核/定向 10 passed/ruff/alembic heads/MySQL 往返+smoke 证据独立复读/lastfailed 核）→**串行 OCR 逐文件（4 收口+1 finding+5 reap 如实记账）**→OCR 批次账+event→**release 控制租约**（ocr.lock 由脚本 flock 自动释放，ps 已核无残留进程）。**有状态变化（07B 交付+核验全绿+OCR 部分收口）**。
- **下一步：** 后续轮低负载期续跑 b5-b10（b5 383 行优先；若再 2 轮 reap 改单文件拆组 `--max-tokens` 降组或挂 NEEDS_MAIN_REVIEW 交长寿命会话，不无限重试）→OCR 收口后裁决 b3 medium（预判=最小返修 b 单文件 py 或并入 TESTER 验证口径，由协调者定）→强审查 REVIEW_NOW pack 起跑（授权在案 0/5）→合入→TESTER 独立验证（派单第四节口径：API 四要素逐项/模型原结果仍在库/下架检索语义/迁移往返/既有套件 0 红）→07B DONE→派 07C。

"""

for name in ("sessions/COORDINATOR.md", "HANDOFF.md"):
    p = ROOT / name
    old = p.read_text(encoding="utf-8")
    if "第 92 轮" in old.split("\n")[0]:
        print(f"{name}: already written, skip")
        continue
    p.write_text(CP + old, encoding="utf-8")
    print(f"{name}: checkpoint prepended, now {len(CP+old)} bytes")