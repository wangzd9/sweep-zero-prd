#!/usr/bin/env python3
"""r93 检查点 + OCR 批次账更新 + HANDOFF 段 + event 落盘（单脚本内完成，均在协调者租约内）。"""
import datetime, pathlib

ROOT = pathlib.Path("/home/wang/work/doc/prd/rosbag-catalog-integration")
NOW = "2026-10-12 19:2x"

cp = f"""## 2026-10-12 19:2x 巡检检查点（cron poll 14ae4556629a，preflight checked_at 2026-10-12T19:10:53+08:00，第 93 轮；**状态变化=b5 本轮 400s 第 5 次 reap → 按 r92 恢复入口预案降级 `--max-tokens 30000` 拆组，后台挂跑（pid 414832，flock 持 ocr.lock）+ b6-b10 接续在途**）

- main `30e55a3`=github/main（=origin/main `502bf8e`+1 纯文档 commit）；07B base `502bf8e` 祖先链有效，**未合入**；wt-04a-t07b 交付冻结 REVIEW_PENDING 不变。
- **串行 OCR 进度 4/10 收口维持**（b1 迁移 0 / b2 api注册 0 / b3 **1 medium 属实待裁决**（r92 独立核=CORRECTION 待裁决）/ b4 models 0）；**b5 本轮再 reap 1 次**（timeout 400 前台跑 19:12-19:19 空输出 0 字节，累计 5 次）——触发 r92 恢复入口预案「b5 再 2 轮 reap → 降组」，**改后台降组续跑**：`run_ocr_file_lowtok.py`（`--max-tokens 30000` 原 runner 同参数其余不变）pid 414832，flock 持 `inbox/ocr.lock`，输出 `scratch/t07b/ocr/b5_lowtok_out.txt` + log `…_lowtok.log`；b5 若再 reap（后台收口失败）→ 挂 NEEDS_MAIN_REVIEW 交长寿命会话，不无限重试。
- **队列实况**：19:12 实测 18002 仍 4 并发 running+1 waiting（其他 worker 抢占，b3 收口 415s/b5 全 reap 同因），降组为降低单轮 token 压力非解队列饱和；b6-b10（bag-detail.css/bag-search.css/bags.html/detail.html/web/bags.py）+ 契约批次待续跑，下一轮（r94+）核后台 pid 414832 收口态：收口=记账续跑 b6（CSS 13 行可前台短跑）；失败=预案升级 NEEDS_MAIN_REVIEW。
- **角色占用**：B=交付冻结 REVIEW_PENDING（等 OCR 收口+b3 裁决）；A/C/TESTER 空闲在跳（tick 19:03-19:10，legacy_busy 空）；leases 仅 C/TESTER 零字节陈旧锁；本轮后台 OCR 进程 pid 414832 为唯一在途业务进程。
- **强审查（strong_review.py status 账本口径，续 r92）**：AUTHORIZED，grant `31dcbabe…`，绝对期限 **2026-10-13 11:33:12 +08:00**，范围=本项目 REVIEW_NOW 判定；滚动 60 分钟 **0/5**、本授权累计 **0 次**、在途 0、token/费用=**未知**。07B 写接口面预判 **REVIEW_NOW**，待 OCR 收口后按 pack 流程判定，本轮不起跑。
- **门禁**：TASK-07 维持 RUNNING（07A DONE main `caf385b`；**07B 交付=机械核验过+OCR 4/10 未收口，不合入**；b3 medium 待裁决；07C 串行待 07B 收口）；TASK-10 DONE/P0 收口维持；TASK-11 生产维持 PRODUCTION BLOCKED；TASK-12/13/14/15 DEFERRED 不扩；`a100-multi-node/` 维持等显式启动；changelog F-035~039 等用户审批不催。
- 本轮控制动作：claim（`cron-coord-poll-14ae4556629a-20261012-191053-r93`，19:12:21，token 自 lease JSON）→巡检核查（fetch+rev-parse 双核 30e55a3/502bf8e/OCR 批次账独立复读/ticks 五角色/ps/vllm 队列 metrics 实测 4 running+1 waiting/18002 ping 200 0.44s）→**b5 前台 timeout 400 续跑 1 次 reap（第 5 次）→按恢复入口预案降级 `--max-tokens 30000` 后台挂跑（pid 414832，flock ocr.lock 独立持有，留检查点释放控制租约）**→OCR 批次账+event→**release 控制租约**（ocr.lock 由后台进程 flock 持有，不释放不删除）。
- **下一步：** r94+ 核后台 pid 414832 收口（`b5_lowtok_out.txt` 有 RC=0/Review complete=收口记账续 b6；再 reap=挂 NEEDS_MAIN_REVIEW 交长寿命会话不无限重试）→b6-b10+契约批次续跑→OCR 全收口后裁决 b3 medium（预判=回派 B 最小返修单文件 `app/api/scene_manual_revision.py` isinstance 守卫或 pydantic DTO，与 07B 返修链合并）→强审查 REVIEW_NOW pack 起跑（授权在案 0/5，期限 10-13 11:33）→合入→TESTER 独立验证→07B DONE→派 07C。

"""

# sessions/COORDINATOR.md prepend（先读后写防截断）
sf = ROOT / "sessions" / "COORDINATOR.md"
old = sf.read_text(encoding="utf-8")
sf.write_text(cp + old, encoding="utf-8")
print("sessions OK", len(old), "->", len(cp + old))

# OCR 批次账 b5 行更新
ob = ROOT / "reviews" / "TASK-07B" / "attempt-1" / "ocr-batches.md"
t = ob.read_text(encoding="utf-8")
t = t.replace(
    "| T07B-b5 | app/services/scene_manual_revision_service.py | +383 | `8b04806a`/`38715616` 等 4 次 420s reap（无 manifest 不可 resume） | 18:0x-18:5x | TIMEOUT×4（同因=本机 Qwen 18002 队列持续 3-4 并发饱和，非工具缺陷；log `ocr_app_services_scene_manual_revision_service.py.log` 每轮覆盖） | 未审 |",
    "| T07B-b5 | app/services/scene_manual_revision_service.py | +383 | `8b04806a`/`38715616` 等 4 次 420s reap（无 manifest 不可 resume）；19:2x 第 5 次 reap 后**按恢复入口预案降级 `--max-tokens 30000` 后台挂跑 pid 414832**（log `…_lowtok.log`，输出 `b5_lowtok_out.txt`，flock 持 ocr.lock） | 18:0x-19:2x | TIMEOUT×5→后台降组续跑（同因=18002 队列 4 并发饱和实测；b5 若再 reap=挂 NEEDS_MAIN_REVIEW 不无限重试） | 未审 |",
)
t = t.replace(
    "**恢复入口（r93+）**：续跑 b5-b10（b5 优先）；若 b5 再 2 轮 reap → 降组（`--max-tokens 30000` 拆多组逐组收口）或挂 NEEDS_MAIN_REVIEW 交长寿命会话；不无限重试。b3 finding 裁决前置=OCR 收口（避免返修后旧批作废）。",
    "**恢复入口（r94+）**：核 b5 后台 pid 414832（`b5_lowtok_out.txt`/`…_lowtok.log`）：收口=记账续跑 b6-b10（b6 13 行 CSS 可前台短跑）；再 reap=挂 NEEDS_MAIN_REVIEW 交长寿命会话，不无限重试。b3 finding 裁决前置=OCR 收口（避免返修后旧批作废）；b3 预判=回派 B 最小返修（`app/api/scene_manual_revision.py` 单文件 isinstance/pydantic 守卫）与 07B 返修链合并。",
)
ob.write_text(t, encoding="utf-8")
print("ocr-batches OK")

# HANDOFF.md 顶部追加本轮段（插在第一个 ## 之前）
hf = ROOT / "HANDOFF.md"
h = hf.read_text(encoding="utf-8")
seg = f"""## 2026-10-12 19:2x 巡检检查点（cron poll 14ae4556629a，r93，preflight checked_at 2026-10-12T19:10:53+08:00；**b5 第 5 次 reap 触发恢复入口预案，降组后台挂跑**）

- 07B attempt-1 交付冻结 REVIEW_PENDING 不变（`f4bfcf2`，base `502bf8e`，main 未合入）；机械核验全绿维持 r92 口径。
- 串行 OCR 4/10 收口（b1/b2/b4 0 findings + b3 1 medium 属实待裁决）；b5 本轮前台 timeout 400 再 reap（第 5 次，18002 队列 4 并发饱和实测）→ 按 r92 恢复入口预案降级 `--max-tokens 30000` **后台挂跑 pid 414832**（flock 持 `inbox/ocr.lock`，检查点见 sessions/COORDINATOR.md r93 段与 `reviews/TASK-07B/attempt-1/ocr-batches.md`）；r94+ 核收口：成功续 b6-b10，再 reap 挂 NEEDS_MAIN_REVIEW 不无限重试。
- 强审查授权在案（grant `31dcbabe…` 至 2026-10-13 11:33:12 +08:00，滚动 60 分钟 0/5，累计 0 次）；07B 写接口面预判 REVIEW_NOW，待 OCR 收口后 pack 起跑。
- 门禁：TASK-07 RUNNING（07A DONE；07B 未收口不合入；07C 串行待前置）；TASK-11 生产 PRODUCTION BLOCKED；12-15 DEFERRED 不扩。

"""
idx = h.find("## ")
hf.write_text(seg + h[idx:], encoding="utf-8")
print("handoff OK")

# event 落盘
ev = ROOT / "inbox" / "events" / "COORDINATOR" / "coord-poll-20261012-191053-r93-t07b-ocr-b5-reap5-lowtok-background.md"
ev.write_text(f"""# coord-poll-20261012-191053-r93-t07b-ocr-b5-reap5-lowtok-background

- role: COORDINATOR
- event_id: coord-poll-20261012-191053-r93-t07b-ocr-b5-reap5-lowtok-background
- task: TASK-07B
- attempt: 1
- status: REVIEW_PENDING
- checked_at: 2026-10-12T19:10:53+08:00
- summary: 巡检第 93 轮。b5（scene_manual_revision_service.py +383）本轮前台 timeout 400 第 5 次 reap（18002 队列 4 并发饱和实测 19:12）→ 按 r92 恢复入口预案降级 --max-tokens 30000 后台挂跑（pid 414832，flock 持 ocr.lock，输出 scratch/t07b/ocr/b5_lowtok_out.txt）。OCR 进度 4/10 收口维持（b1/b2/b4 0 findings，b3 1 medium 属实待裁决 CORRECTION）。B 交付冻结 REVIEW_PENDING，未合入。
- evidence: reviews/TASK-07B/attempt-1/ocr-batches.md; sessions/COORDINATOR.md r93 段; scratch/t07b/ocr/b5_lowtok_out.txt
- next: r94+ 核 pid 414832 收口（成功续 b6-b10；再 reap 挂 NEEDS_MAIN_REVIEW）→ OCR 收口后裁决 b3 → 强审查 REVIEW_NOW pack（授权在案 0/5）→ 合入 → TESTER 独立验证。
""", encoding="utf-8")
print("event OK")