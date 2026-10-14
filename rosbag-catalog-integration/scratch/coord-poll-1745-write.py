#!/usr/bin/env python3
# 协调者 17:45 巡检：prepend sessions 检查点 + TODO TASK-08 行停滞解除注记
import pathlib, re
root = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")

cp = """## 2026-10-11 17:45 巡检检查点（cron poll 14ae4556629a，真实 checked_at 2026-10-11T17:40:53+08:00：17:35 后零交付，2号 t08c-1 停滞告警解除、业务编码恢复推进）

- **17:35 后零业务交付**：main HEAD `98f6c885dcd4681c63b39bec6e7d2836649c87d2`（= origin/main，rev-parse 双核一致，top1=c3-1 合入 17:02 已在案）；17:30:53 后共享根新增仅 A 17:41 / C 17:38 / TESTER 17:39 例行 tick 与上轮自身 event，**无新回执/派单/decision/合入**（find -newermt 核实）。
- **2号 t08c-1（C1/C2 秒精度专项）活动停滞告警解除，编码实质推进中（不催单不接管）**：`wt-04a-t08c` 自 17:07:36 零变更的**连续 17:10/17:15/17:20/17:25/17:30 五轮停滞状态于 17:38/17:41 解除**——`app/services/bag_cleanup_service.py`（mtime 17:38:10，+58/-11：run_inspection 7 分支 `_bump_if_changed` 业务字段变化才推进 updated_at + worker_heartbeat 整秒 `replace(microsecond=0)` 幂等零 UPDATE）与 `app/services/catalog_ingest.py`（mtime 17:41:51，upsert_bag `start_ns // 1e9` 整数除秒修 codex M-1 同型 + 业务字段 old/new 元组比较才推进 updated_at）正在写；HEAD 仍 `f9bafb0` **未 commit**、`receipts/TASK-08/` 仍仅 attempt-1 + c3-1 两份**无交付回执**；ps 无 pytest 进程（编码间隙）。注意：当前 diff 只覆盖 2 文件，C2 面 5 文件 9 用例（source_service/clone/pipeline_api 等）与 C1 面 4 文件修复是否全到位**待交付后逐点核对**，本轮不代判。
- **角色占用**：B=RUNNING（t08c-1 编码中，tick 17:28:53 report 已恢复跳）；A 17:41 / C 17:38 / TESTER 17:39 tick 正常空闲；leases 仅 A 17:42 短租约（例行瞬态）+ C 05:19 / TESTER 12:46 零字节例行租约，无在途业务持有者；`ocr.lock`(16:59)/`coordinator.lock` 0 字节，ps 无协调侧 ocr/pytest 业务进程。
- **门禁**：生产启用/真实样本（TASK-09/10/11）维持未放行；TASK-08 收口 1/2（c3-1 已合入 `98f6c88`），剩 t08c-1 交付→机械核验（含 C1/C2 逐修复点覆盖核对）→串行 OCR 增量（app 行为面）→合入→9 红文件全绿复核→08 DONE→TASK-10 候选重算。
- 本轮控制动作：claim（`cron-coord-poll-14ae4556629a-20261011-1740`）→巡检核查（rev-parse 双核/find -newermt/wt-04a-t08c mtime+diff 复核+ticks/leases/ps 核对）→TODO 注记+prepend 检查点+event→release。**有状态变更（停滞告警解除），无新派单、无合入、无 OCR**。
- **下一步**：下轮核 2号 t08c-1 交付信号（wt-04a-t08c 新 commit/回执 `receipts/TASK-08/`）；交付即机械核验（C1/C2 全修复点覆盖+真 MySQL A/B 证据）→串行 OCR 增量→合入→9 红文件全绿复核→TASK-08 DONE；若交付前再次多轮零活动则恢复停滞告警口径。
"""

p = root / "sessions" / "COORDINATOR.md"
p.write_text(cp + p.read_text(encoding="utf-8"), encoding="utf-8")

# TODO TASK-08 行：在 17:20 停滞告警注记后追加停滞解除注记
t = root / "TODO.md"
text = t.read_text(encoding="utf-8")
anchor = "17:20 巡检：t08c-1 **活动停滞告警**（`wt-04a-t08c` 自 17:07:36 起连续 3 轮巡检零文件变更、无 commit/回执、无 pytest 业务进程；B 自身 cron tick 停 17:08:53 已约 14 分钟未跳）——不催单不接管，等 B 下轮自报或会话核活；main `98f6c88`=origin 不变"
note = "→【17:45 巡检：t08c-1 活动停滞告警**解除**（17:38/17:41 `wt-04a-t08c` 业务编码恢复：bag_cleanup_service.py run_inspection 7 分支 _bump_if_changed+worker_heartbeat 整秒幂等、catalog_ingest.py upsert_bag 整数除秒+业务字段变化才推进 updated_at，2 文件 +58/-11 未 commit 无回执，C1/C2 全修复点覆盖待交付后逐点核）——继续不催单不接管，等 commit+真 MySQL A/B 交付；main `98f6c88`=origin 不变"
assert anchor in text, "TODO anchor not found"
text = text.replace(anchor, anchor + note, 1)
t.write_text(text, encoding="utf-8")
print("TODO note appended; checkpoint prepended OK")