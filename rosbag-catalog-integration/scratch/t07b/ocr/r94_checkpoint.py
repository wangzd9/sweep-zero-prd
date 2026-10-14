#!/usr/bin/env python3
"""r94: append checkpoint to sessions/COORDINATOR.md + HANDOFF.md (read then write, no truncate-read bug)."""
import os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"

CHECKPOINT = """## 2026-10-12 19:3x 巡检检查点（cron poll 14ae4556629a，preflight checked_at 2026-10-12T19:25:53+08:00，第 94 轮；**状态变化=b5 后台 pid 414832 核实已随 r93 会话回收（19:33 核 0 字节双文件）→ 队列低负载实测（vllm 1 running/0 waiting）→ b5 以 Hermes 后台跟踪重启（`proc_7ea84d1aecc6` pid 434432，`--max-tokens 30000`，flock 持 ocr.lock）**）

- main `30e55a3`=github/main（origin/main `502bf8e`+1 纯文档 commit）；07B base `502bf8e` 祖先链有效，**未合入**，wt-04a-t07b 交付冻结 REVIEW_PENDING 不变（`f4bfcf2`，机械核验全绿口径续 r92）。
- **b5 后台进程核实（r93 留口）**：r93 声明后台挂跑 pid 414832——r94 实测进程不存在（`kill -0` 无此进程，`ps` 无 run_ocr/ocr review 业务进程，`b5_lowtok_out.txt` 与 `…_lowtok.log` 均 0 字节 19:20）=**r93 回合结束时后台进程被随会话回收，非运行中**，如实记账不粉饰；b5 累计失败 5 次前台 reap + 1 次后台回收。
- **队列实况（r94 19:3x 实测，与 r93 反转）**：`18002/metrics` vllm num_requests_running=**1** / waiting=**0**（r93 19:12 为 4 running+1 waiting=其他 worker 饱和）——**低负载窗口**，b6 的 reap 日志尾部（session `cda37180` 84977 tokens/7m0s usage 齐全后 `context canceled`）证实 reap=外层 420s 杀进程非 LLM 失败。
- **控制动作=b5 重启**：按 r93 恢复入口预案，`run_ocr_file_lowtok.py app/services/scene_manual_revision_service.py`（`--max-tokens 30000`，flock 持 `inbox/ocr.lock`）以 **Hermes 后台跟踪**起跑（session `proc_7ea84d1aecc6`，pid 434432，19:36 核存活 Ss 态）——进程脱离单轮 420s 硬上限；r95+ 核收口：`b5_lowtok_out.txt` 出现 `RC=`/`Review complete`=记账续 b6-b10（b6 13 行 CSS 可前台短跑）；**pid 434432 已退且无 Review complete=挂 NEEDS_MAIN_REVIEW 交长寿命会话，不无限重试**（b5 至此第 2 次 reap 即触顶）。
- **角色占用**：B=交付冻结 REVIEW_PENDING（等 OCR 收口+b3 medium 裁决）；A/C/TESTER 空闲在跳（legacy_busy 空，leases 仅 C/TESTER 零字节陈旧锁）；pid 434432 为唯一在途业务进程。
- **强审查（账本口径续 r93）**：AUTHORIZED，grant `31dcbabe…`，绝对期限 **2026-10-13 11:33:12 +08:00**，范围=本项目 REVIEW_NOW 判定；滚动 60 分钟 **0/5**、本授权累计 **0 次**、在途 0、token/费用=**未知**。07B 写接口面预判 **REVIEW_NOW**，待 OCR 收口后 pack 起跑，本轮不起跑。
- **门禁**：TASK-07 维持 RUNNING（07A DONE main `caf385b`；**07B 机械核验过+OCR 4/10 未收口，不合入**；b3 medium CORRECTION 待裁决；07C 串行待 07B 收口）；TASK-10 DONE/P0 收口维持；TASK-11 生产维持 PRODUCTION BLOCKED；TASK-12/13/14/15 DEFERRED 不扩；`a100-multi-node/` 等显式启动；changelog F-035~039 等用户审批不催。
- 本轮控制动作：claim（`cron-coord-poll-14ae4556629a-20261012-192553-r94`，19:28:05）→巡检核查（pid 414832 三核已死/ocr-batches 账复读/18002 vllm metrics 实测队列反转/b6 reap 日志尾核）→**b5 后台跟踪重启（pid 434432，flock 独立持有）+OCR 批次账更新**→checkpoint（sessions+HANDOFF）+event→**release 控制租约**（ocr.lock 由 434432 flock 持有，不释放不删除）。
- **下一步：** r95+ 核 pid 434432 收口（`proc_7ea84d1aecc6` poll：存活=再核；`b5_lowtok_out.txt` 有 RC=/Review complete=记账续 b6-b10+契约批次；已退无 complete=挂 NEEDS_MAIN_REVIEW）→OCR 全收口后裁决 b3 medium（预判回派 B 最小返修单文件 isinstance/pydantic 守卫）→强审查 REVIEW_NOW pack（授权在案 0/5，期限 10-13 11:33:12）→合入→TESTER 独立验证→07B DONE→派 07C。
"""

sp = os.path.join(ROOT, "sessions/COORDINATOR.md")
cur = open(sp, encoding="utf-8").read()
open(sp, "w", encoding="utf-8").write(CHECKPOINT + "\n" + cur)
print("sessions/COORDINATOR.md checkpoint written, new len:", len(CHECKPOINT + cur))

hp = os.path.join(ROOT, "HANDOFF.md")
curh = open(hp, encoding="utf-8").read()
HANDOFF = CHECKPOINT.replace("## 2026-10-12 19:3x 巡检检查点", "## 2026-10-12 19:3x 巡检检查点（cron poll 14ae4556629a，r94，preflight checked_at 2026-10-12T19:25:53+08:00）")
HANDOFF = HANDOFF.split("\n", 1)[0] + "\n\n" + [
    "- main `30e55a3`=github/main；07B 交付冻结 REVIEW_PENDING 不变（`f4bfcf2` 未合入）。",
    "- **b5 后台 pid 414832 核实已随 r93 会话回收（0 字节双文件，进程不存在）如实记账**；r94 队列低负载实测（vllm 1 running/0 waiting）→ b5 以 Hermes 后台跟踪重启（`proc_7ea84d1aecc6` pid 434432，`--max-tokens 30000`，flock 持 `inbox/ocr.lock`，19:36 核存活）。",
    "- OCR 进度 4/10 维持（b1 0 / b2 0 / b3 **1 medium CORRECTION 待裁决** / b4 0）；b6 reap 日志证实=外层 420s 杀进程（usage 84977 tokens 齐全后 context canceled）非 LLM 失败；b6-b10+契约批次 QUEUED 待 b5 收口。",
    "- r95+ 收口核法：pid 434432 poll + `b5_lowtok_out.txt` 现 RC=/Review complete=记账续 b6；已退无 complete=**挂 NEEDS_MAIN_REVIEW 不无限重试**（b5 第 2 次 reap 触顶）。",
    "- 强审查授权在案（grant `31dcbabe…` 至 2026-10-13 11:33:12，滚动 60 分钟 0/5，累计 0，token/费用未知）；07B 预判 REVIEW_NOW 待 OCR 收口。",
    "- 门禁：TASK-07 RUNNING（07B 不合入）；TASK-11 生产 BLOCKED；12-15 DEFERRED；A/C/TESTER 空闲；B 交付冻结。",
].join("\n") + "\n"
open(hp, "w", encoding="utf-8").write(HANDOFF + curh)
print("HANDOFF.md checkpoint written")
print("handoff line:", HANDOFF.split("\n",1)[0])