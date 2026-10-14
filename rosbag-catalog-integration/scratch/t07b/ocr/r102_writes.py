#!/usr/bin/env python3
"""r102 doc writes under coordinator lease. Read-then-write; no truncation."""
import io, os, sys

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
TS = "2026-10-12 23:0x"
PRE = "2026-10-12T22:35:53+08:00"

# sanity: token file present
tok = io.open(ROOT + "/scratch/t07b/ocr/r102_token.txt").read().strip()
assert len(tok) == 32, "token missing"

def rd(p):
    with io.open(p, "r", encoding="utf-8") as f:
        return f.read()
def wr(p, s):
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(s)
def ap(p, s):
    with io.open(p, "a", encoding="utf-8") as f:
        f.write(s)
def assert_upd(old, new, tag):
    assert old != new, f"replace no-op: {tag}"

SL = "{slope,flat,unknown}"

# ---------- 1. ocr-batches.md: b5/b7 rows + closure + contract batch ----------
ob = ROOT + "/reviews/TASK-07B/attempt-1/ocr-batches.md"
s = rd(ob)

b5_old = "| T07B-b5 | app/services/scene_manual_revision_service.py | +383 | r95 detached 第 6 次 session `81a66282` RC=1 FAILED（core request timed out）；**r101 低负载期 `--resume 81a66282` 最后一次 INFLIGHT**（21:59 起跑，detached pid 607379，flock 持 `inbox/ocr.lock`；起跑时 vllm running=4 waiting=1=低负载条件达成） | 21:59 起 | INFLIGHT（resume 最后一次） | 未审；再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁，不无限重试 |"
b5_new = "| T07B-b5 | app/services/scene_manual_revision_service.py | +383 | r95 detached 第 6 次 session `81a66282` RC=1 FAILED（core request timed out）；**r101 `--resume 81a66282` 最后一次 COMPLETED RC=0 1800s**（21:59→22:29，session `7d703528` usage 995025 tokens；round2 又报 review_round_failed 但 core review complete=3 findings 有效） | 22:29 | COMPLETED（resume 最后一次） | **3 findings**：① **[bug·MEDIUM]** service:204-221（revise 守卫 204-206/写回 255；withdraw 同模式）`if bag.row_version != expected: 409` 后 ORM `bag.row_version += 1` flush=非守卫写入，真并发输方可 500/StaleDataError 或 lost-update，与文档化 409 面不一致（`ingest_service.update_submission` F2 注释=单条守卫 UPDATE 既有先例，独立核实属实）=**CONFIRMED CORRECTION**；② **[bug·MEDIUM]** service:215-221 `db.scalar(select(BagSceneLabelEvidence)…MANUAL)` 无 `.order_by().limit(1)`，该表无 (bag_uid,scene_id,label_source) 唯一约束（独立核实 models.py+迁移）→ 双 MANUAL 行时 MultipleResultsFound 500=**CONFIRMED CORRECTION**；③ [style·LOW] 文件尾缺换行。"
assert b5_old in s, "b5 row anchor"
s = s.replace(b5_old, b5_new, 1)

b7_old = "| T07B-b7 | app/static/bag-search.css | +12/-1 | r95 detached session `daa45a1c` RC=1 FAILED（250s 瞬态）；**r101 低负载期 `--resume daa45a1c` 最后一次 INFLIGHT**（b5 resume 收口后串行，同 pid 607379） | b5 后排队 | INFLIGHT（resume 最后一次） | 未审；再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁，不无限重试 |"
b7_new = "| T07B-b7 | app/static/bag-search.css | +12/-1 | r95 detached session `daa45a1c` RC=1 FAILED（250s 瞬态）；**r101 `--resume daa45a1c` 最后一次 COMPLETED RC=0 839s**（22:29→22:43:38，session `997d0ddd` usage 155479 tokens） | 22:43 | COMPLETED（resume 最后一次） | **3 findings**：① **[maintainability·MEDIUM]** bag-search.css:1376-1385 `.bag-scene-withdrawn` 无 `align-self: flex-start`（兄弟 `.bag-scene-badge`/:1336 与 `.bag-scene-history`/:1345 都有），在 `.bag-scene-cell` column-flex（:1328）内撑满宽度+`margin-left: 6px` 错位、`display: inline-block` 对 flex item 无效（独立核实属实）=**CONFIRMED CORRECTION**；② [style·LOW] :1384 `color: #d64545` 建议 `var(--red)`（app.css:10 定义，一致性）；③ [style·LOW] :1378 `margin-left: 6px` inline-flow 偏移对 flex 子项错位。"
assert b7_old in s, "b7 row anchor"
s = s.replace(b7_old, b7_new, 1)

cb_old = "| 契约批次 | 跨文件（API↔service↔迁移↔页面接线） | - | - | | QUEUED（b10 后按结果定） | |"
cb_new = "| 契约批次 | 跨文件（API↔service↔迁移↔页面接线） | - | - | | **CLOSED（r102：不单跑）** | 跨文件契约面已由逐文件审查+协调者独立代码核覆盖——b9-1 HIGH（模板选项域 vs service `_VALID_LABELS`）与 b5-1 MEDIUM（API 409 语义 vs service 守卫写入）本身即跨文件契约 finding，无剩余未覆盖接线面 |"
assert cb_old in s, "contract row anchor"
s = s.replace(cb_old, cb_new, 1)

prog_old = ("**收口进度 r101（21:5x）**：r95 detached 已收口 8/10（b1 0 / b2 0 / b3 **1 medium=CONFIRMED CORRECTION 待返修** / b4 0 / b6 0 / b8 1 low 非阻塞 / **b9 3 findings=1 HIGH CORRECTION + 2 LOW** / b10 0）；"
    "**b5（核心服务 +383）/b7（css）r101 低负载期 `--resume` 最后一次 INFLIGHT**（detached pid 607379，21:59 起，progress `scratch/t07b/ocr/r101_resume_progress.txt`）；契约批次=b5/b7 收口后按结果定。\n\n")
prog_new = ("**收口进度 r102（23:0x）=10/10 全收口**（b1 0 / b2 0 / b3 **1 medium=CONFIRMED** / b4 0 / **b5 3 findings=2 medium CONFIRMED + 1 low** / b6 0 / **b7 3 findings=1 medium CONFIRMED + 2 low** / b8 1 low / **b9 3 findings=1 high CONFIRMED + 2 low** / b10 0）；`== r101 resume done 2026-10-12 22:43:38 ==` 落盘（detached pid 607379 已退出，ps 核无残留，ocr.lock 无持有者）；契约批次 CLOSED 不单跑（跨文件面已由逐文件+独立代码核覆盖）。**合计 5 处 CONFIRMED CORRECTION（b9-1 high / b3 / b5-1 / b5-2 / b7-1）+ 6 处 LOW 非阻塞**，已并入一次最小返修 R2 派 B（`inbox/2号/TASK-07B/attempt-2-r2-dispatch.md` 23:0x）。\n\n" + prog_old)
assert prog_old in s, "prog r101 anchor"
s = s.replace(prog_old, prog_new, 1)
wr(ob, s)

# ---------- 2. ruling v2 ----------
ruling2 = (
"# TASK-07B attempt-1 OCR r102 收口裁决 v2（协调者）\n\n"
"- 时间：" + TS + " +08:00（r102 poll，preflight " + PRE + "，claim 23:05:46）\n"
"- 被测：`502bf8ec..f4bfcf2a`（base main `502bf8e`，未合入）\n"
"- 依据：`reviews/TASK-07B/attempt-1/ocr-batches.md`（r102 更新，10/10 全收口）+ 协调者独立核代码（`wt-04a-t07b` HEAD `f4bfcf2`）\n"
"- 续：`ocr-r101-findings-ruling.md`（b9-1 HIGH / b3 MEDIUM CONFIRMED 维持）\n\n"
"## 收口事实\n"
"- **OCR 10/10 全收口**：b5 resume 最后一次 RC=0 1800s（session `7d703528`，3 findings，round2 报 review_round_failed 但 core review complete=有效口径同 b9）；b7 resume 最后一次 RC=0 839s（session `997d0ddd`，3 findings）；22:43:38 `== done ==` 落盘，detached pid 607379 已退出、ocr.lock 无持有者（ps+fuser 核）。无 NEEDS_REVIEW 文件，**07B 合入门禁 OCR 面不再因覆盖缺口冻结**，改按 5 处 CONFIRMED CORRECTION 走 R2 最小返修。\n\n"
"## 新增 CONFIRMED CORRECTION（r102 独立核代码属实）\n"
"- **b5-1 [bug·MEDIUM] service revise:204-206 / withdraw:289-293 乐观锁非守卫写入**：`if bag.row_version != expected: raise 409` 后 ORM `bag.row_version += 1`（commit flush），真并发两个同 row_version 写方可先后都通过检查 → 一方修订静默丢失（lost-update）或 StaleDataError 500，与派单/文档化「row_version 冲突 409」语义不一致。仓库既有先例：`ingest_service.update_submission` F2 注释（单条 `UPDATE … WHERE row_version=:expected` 守卫，输方 rowcount==0→409）。最小修复：availability/row_version 变更改单条守卫 UPDATE（同 F2 模式），输方 409。\n"
"- **b5-2 [bug·MEDIUM] service:215-221 `db.scalar(select(BagSceneLabelEvidence)…label_source='MANUAL')` 无 `.order_by().limit(1)`**：该表无 (bag_uid, scene_id, label_source) 唯一约束（独立核 models.py:597-619 + 迁移 20261012_01）；历史数据或 b5-1 竞态窗口产生双 MANUAL 行时 `scalar()` 抛 MultipleResultsFound → 500。最小修复：`.order_by(BagSceneLabelEvidence.id).limit(1)`。\n"
"- **b7-1 [maintainability·MEDIUM] bag-search.css:1376-1385 `.bag-scene-withdrawn` 布局错位**：`.bag-scene-cell`（:1328）=column flex gap 4px，兄弟 `.bag-scene-badge`（:1336）/`.bag-scene-history`（:1345）均 `align-self: flex-start`，新徽章缺之 → 撑满单元格宽度（min 120px）且 `margin-left: 6px` 相对其他 pill 错位 6px；`display: inline-block` 对 flex item 无效（blockified）。最小修复：删 `display`/`margin-left`，加 `align-self: flex-start`（同规则块内 2 处 LOW 一并：:1384 `color: var(--red)` 一致性可选）。\n\n"
"## LOW 非阻塞（随 R2 同 commit 合并，不单独触发返修）\n"
"- b5-3 [style·LOW] service 文件尾缺换行。\n"
"- b7-2/b7-3 [style·LOW] css :1384 颜色 var(--red) 一致性与 :1378 margin 语义（与 b7-1 同规则块）。\n"
"- b9-2 [maintainability·LOW] detail.html:72 审计时间列 `isoformat()` 字符串非全站 `datetime_local` 口径（service 侧 `manual_revision_history`/`scene_manual_revisions_context` 返回 dict 处格式化或模板过滤，二选一，不新增依赖）。\n"
"- b8 [maintainability·LOW] bags.html:226 状态三元冗余分支 + 非 WITHDRAWN 切片行空 `title=\"\"`（可选简化）。\n\n"
"## 返修派发决策\n"
"- **R2 最小返修已派 B**（`inbox/2号/TASK-07B/attempt-2-r2-dispatch.md`）：CONFIRMED 5 处全修 + LOW 6 处随同 commit（同一文件块内顺手项）；覆盖文件 = `app/templates/detail.html`、`app/api/scene_manual_revision.py`、`app/services/scene_manual_revision_service.py`、`app/static/bag-search.css`（必改 4）+ `app/templates/bags.html`（b8 可选）；base 保持 `f4bfcf2` 之上续 commit（原 base `502bf8e` 不变，本地 main `c2018dd` 纯文档零 app 面零冲突）。R2 交付后：机械核验 → 增量 OCR（仅 R2 diff 文件）→ 强审查 pack（授权 0/5 期限 2026-10-13 11:33:12）→ 合入 → TESTER 独立验证（含 R2 新增语义：非 dict 422、守卫 UPDATE 并发 409 口径、corrected_label 域、下架徽章布局页面实测）→ 07B DONE → 派 07C/16C。\n"
)
wr(ROOT + "/inbox/coordinator/TASK-07B/ocr-r102-closure-ruling.md", ruling2)

# ---------- 3. R2 dispatch ----------
disp = (
"# 派单：TASK-07B attempt-2-r2 最小返修（OCR 收口 10/10 后一次性）\n\n"
"- status: DISPATCHED\n"
"- 派单时间：" + TS + " +08:00（r102 poll）\n"
"- 任务：TASK-07B R2 返修（REQ-04 / AC-04；原 attempt-1 交付 `f4bfcf2` 冻结面之上最小修正）\n"
"- owner：B（`wt-04a-t07b`，分支续 `scene/task-07b-manual-revision-withdraw`）\n"
"- base：`f4bfcf2`（原交付 HEAD，继续在其上 commit；原 base `502bf8e` 不变；本地 main `c2018dd` 纯文档 commit 零 app 面，合入时协调者处理，无需 rebase）\n\n"
"## 一、返修问题 ID 单（全部来自 OCR 收口 + 协调者独立核代码，裁决 `inbox/coordinator/TASK-07B/ocr-r102-closure-ruling.md`）\n\n"
"### 必改（CONFIRMED CORRECTION 5 处）\n"
"1. **R2-1（b9-1 HIGH）`app/templates/detail.html:52`**：`corrected_label` 下拉选项域与服务校验域对齐——现列 slope/flat/construction/congestion/night/rain/other 共 7 项，服务 `_VALID_LABELS`=" + SL + "（`segment.py:22-24` 权威常量），5 项必 422 且合法 `unknown` 无选项。修复：选项改为 " + SL + "（直接引用或字面一致）。\n"
"2. **R2-2（b3 MEDIUM）`app/api/scene_manual_revision.py`**（PATCH scene-labels 与 POST withdraw 两接口，:26/:35 附近）：`await request.json()` 后非 dict JSON（list/scalar）→ `body.get` AttributeError → 500，与文档化 422 面不一致。修复：`isinstance(data, dict)` 守卫（兄弟 API `ingest_submissions._parse_model` 先例），非 dict → 422 明确语义。\n"
"3. **R2-3（b5-1 MEDIUM）`app/services/scene_manual_revision_service.py`** revise（:204-206/:255）与 withdraw（:289-293/:310）：乐观锁改**单条守卫 UPDATE**（`UPDATE bag_record SET availability=…, row_version=row_version+1 WHERE id=… AND row_version=:expected`，输方 rowcount==0 → 409），对齐 `ingest_service.update_submission` F2 既有模式；消除真并发 lost-update/StaleDataError 500。注意 evidence/audit 写入顺序与守卫失败路径（409 前不落审计、不落 evidence 变更）。\n"
"4. **R2-4（b5-2 MEDIUM）同文件 :215-221**：MANUAL evidence 查询加 `.order_by(BagSceneLabelEvidence.id).limit(1)`，防双 MANUAL 行 MultipleResultsFound 500（表无该唯一约束，已核）。\n"
"5. **R2-5（b7-1 MEDIUM）`app/static/bag-search.css:1376-1385`**：`.bag-scene-withdrawn` 删 `display: inline-block` 与 `margin-left: 6px`，加 `align-self: flex-start`（对齐兄弟 `.bag-scene-badge`/`.bag-scene-history` 口径）。\n\n"
"### 随同 commit（LOW 非阻塞，同文件块顺手项）\n"
"- R2-6：detail.html:52 `corrected_label` select 加 `required`（空串提交不再无效 422 往返）。\n"
"- R2-7：service 文件尾补换行（POSIX）。\n"
"- R2-8：bag-search.css:1384 `color: #d64545` → `var(--red)`（app.css:10 已定义）。\n"
"- R2-9（可选，不扩面）：detail.html:72 审计时间列展示口径与全站 `datetime_local` 一致（service 返回 dict 处格式化或模板过滤，二选一）。\n"
"- R2-10（可选，不扩面）：bags.html:226 状态三元冗余分支 `'failed' if WITHDRAWN else 'failed'` 简化 + 非 WITHDRAWN 切片行空 `title=\"\"` 消除。\n\n"
"## 二、测试（最小增量，并入既有 `tests/test_task07b_manual_revision.py` 或新增同前缀文件）\n"
"- R2-1：corrected_label=construction 等 5 项提交仍 422（原断言）、unknown 提交成功（新增）；\n"
"- R2-2：两接口 body 为 JSON list/scalar → 422（新增，非 500）；\n"
"- R2-3：同 row_version 二次写 → 409（既有）；守卫 UPDATE 口径下并发输方 409 而非 500（如可用 SQLite 模拟同版本双会话则加，不能则声明留 TESTER 真 MySQL 口径）；\n"
"- R2-4：同 (bag_uid,scene_id,MANUAL) 双行夹具 → 修订成功且更新 id 最小行（新增）；\n"
"- 页面实测：下架徽章在 all 视图切片行不撑满宽度、与 scene 标签 pill 左对齐（截图或 DOM 断言，口径同 07A）；\n"
"- 既有定向 + 全量 0 红（基线 849 passed，3 devflow 环境性不算）、ruff 绿。\n\n"
"## 三、边界与禁止\n"
"- 只动上述 5 必改 + 4 可选文件块；不新增表/迁移/依赖；不动 03~06B 状态机/幂等/发布；不改生产 compose；不实现 07C/16C（B 后续 16C 在 07B 收口后另行派单）。\n"
"- 交付=commit + 回执 `receipts/TASK-07B/attempt-2-r2.md`（REVIEW_PENDING）+ 报告 `reports/TASK-07B/attempt-2-r2.md`；回执逐项列 R2-1~R2-10 处理与证据。\n"
"- 停止条件：回执落盘后冻结等审；不自行合入、不跑 OCR（OCR 归协调者）。\n\n"
"## 四、后续链（协调者侧，供 B 知悉）\n"
"R2 交付 → 机械核验 → 增量 OCR（仅 R2 diff）→ 强审查 pack（24h 授权在案，滚动 60min 0/5，期限 2026-10-13 11:33:12）→ 合入 main → TESTER 独立验证（API 四要素+R2 新语义+页面布局+既有 0 红）→ 07B DONE → 派 07C/16C。\n"
)
os.makedirs(ROOT + "/inbox/2号/TASK-07B", exist_ok=True)
wr(ROOT + "/inbox/2号/TASK-07B/attempt-2-r2-dispatch.md", disp)

# ---------- 4. TIMELINE append ----------
ap(ROOT + "/TIMELINE.md", (
"\n## " + TS + " 协调者 r102 poll（preflight " + PRE + "，claim 23:05:46）：**OCR 10/10 全收口（b5 resume RC=0 1800s 3 findings / b7 resume RC=0 839s 3 findings，22:43:38 done 落盘，pid 607379 已退出 ocr.lock 无持有）**；"
"协调者独立核代码新增 **3 处 CONFIRMED CORRECTION**（b5-1 乐观锁非守卫写入=lost-update/500 vs 文档化 409，ingest_service F2 先例；b5-2 MANUAL evidence 查询无 limit(1)=双行 500，表无唯一约束已核；b7-1 下架徽章缺 align-self 布局错位，兄弟规则口径已核）——合计 5 CONFIRMED + 6 LOW，"
"**R2 最小返修已派 B**（`inbox/2号/TASK-07B/attempt-2-r2-dispatch.md`，base f4bfcf2 续 commit，4 必改文件+1 可选）→ 后续：机械核验→增量 OCR→强审查 pack（授权 0/5 期限 2026-10-13 11:33:12）→合入→TESTER→07B DONE→派 07C/16C。"
"契约批次 CLOSED 不单跑（跨文件面已由逐文件+独立代码核覆盖）。main 本地 `c2018dd`/origin `502bf8e` 零 app 面漂移；A=16A RUNNING（ACK 22:41 已开工）/C=16B RUNNING（ACK 22:46 已开工）/TESTER 空闲；B 原交付冻结解除转 R2。裁决 `inbox/coordinator/TASK-07B/ocr-r102-closure-ruling.md`。event coord-poll-20261012-223553-r102-t07b-ocr-10of10-r2-dispatch。\n"
))

# ---------- 5. DEVELOPMENT-LOG append ----------
ap(ROOT + "/DEVELOPMENT-LOG.md", (
"\n## 2026-10-12T23:05:00+08:00 TASK-07B attempt-1 串行 OCR 10/10 全收口 + R2 最小返修派发\n\n"
"- OCR 收口闭环：b5 `scene_manual_revision_service.py`（+383 核心服务面）resume 最后一次 RC=0 1800s（session 7d703528，3 findings）+ b7 `bag-search.css` resume 最后一次 RC=0 839s（session 997d0ddd，3 findings），22:43:38 detached done 落盘、无 NEEDS_REVIEW 文件；10 批合计 5 处 CONFIRMED CORRECTION + 6 处 LOW（b9-1 模板选项域 vs 服务校验域 HIGH / b3 非 dict JSON 500 vs 422 / b5-1 乐观锁非守卫写入 / b5-2 evidence 查询无 limit(1) / b7-1 下架徽章布局错位）。\n"
"- 协调者独立核代码裁决 v2 落盘（`inbox/coordinator/TASK-07B/ocr-r102-closure-ruling.md`）；R2 最小返修一次派 B（问题 ID 单 R2-1~R2-10，4 必改文件+1 可选，base f4bfcf2 续 commit，零新迁移零新依赖）。\n"
"- 未合入：07B 维持 REVIEW_PENDING（f4bfcf2）等 R2 交付→增量 OCR→强审查（24h 授权在案 0/5 期限 2026-10-13 11:33:12）→合入→TESTER 独立验证。TASK-16A（A 已 ACK 开工）/16B（C 已 ACK 开工）并行推进。\n"
"- 未生成正式功能 released 日志；无业务合入、无生产动作。\n"
))

# ---------- 6. sessions canonical prepend ----------
sp = ROOT + "/sessions/COORDINATOR.md"
old = rd(sp)
cp = (
"## " + TS + " 巡检检查点（cron poll 14ae4556629a，第 102 轮，preflight " + PRE + "；**状态变化=OCR 10/10 全收口（b5/b7 resume 均 RC=0，22:43:38 done，pid 607379 已退出）→ 协调者独立核代码新增 3 处 CONFIRMED CORRECTION（合计 5+6 LOW）→ R2 最小返修已派 B**）\n\n"
"- **OCR 收口 10/10（r101 resume 链闭环）**：b5 `scene_manual_revision_service.py` resume 最后一次 **RC=0 1800s**（21:59→22:29，session `7d703528` usage 995025 tokens，round2 review_round_failed 但 core review complete=3 findings 有效，口径同 b9）；b7 `bag-search.css` resume 最后一次 **RC=0 839s**（22:29→22:43:38，session `997d0ddd`，3 findings）；`== r101 resume done 2026-10-12 22:43:38 ==` 落盘，ps 核 pid 607379/643555/643563 全退出、ocr.lock 无持有者。**无 NEEDS_REVIEW 文件**，07B 合入门禁 OCR 覆盖缺口解除，改按 CONFIRMED CORRECTION 走 R2。契约批次 CLOSED 不单跑（跨文件契约面已由逐文件审查+b9-1/b5-1 独立代码核覆盖，无剩余未覆盖接线面）。\n"
"- **独立核代码（wt-04a-t07b HEAD f4bfcf2）新增 3 处 CONFIRMED CORRECTION**：①b5-1 MEDIUM=revise:204-206/withdraw:289-293 乐观锁 check-then-ORM-flush 非守卫写入，真并发 lost-update 或 StaleDataError 500，与文档化 409 面不一致（`ingest_service.update_submission` F2 单条守卫 UPDATE 先例在案）；②b5-2 MEDIUM=service:215-221 MANUAL evidence `db.scalar` 无 `.order_by().limit(1)`，`bag_scene_label_evidence` 无 (bag_uid,scene_id,label_source) 唯一约束（models.py:597-619+迁移独立核）→ 双行 MultipleResultsFound 500；③b7-1 MEDIUM=`.bag-scene-withdrawn`（css:1376-1385）缺 `align-self: flex-start`（兄弟 :1336/:1345 均有），column-flex cell 内撑满+margin 错位、inline-block 对 flex item 无效。合计 **5 CONFIRMED（b9-1 high/b3/b5-1/b5-2/b7-1）+ 6 LOW 非阻塞**。\n"
"- **R2 最小返修已派 B**（`inbox/2号/TASK-07B/attempt-2-r2-dispatch.md`，23:0x 落盘）：问题 ID 单 R2-1~R2-10（5 必改=detail.html 选项域+required、scene_manual_revision.py 非 dict 422 守卫、service 守卫 UPDATE+limit(1)、css align-self；4 LOW 随同 commit；2 可选不扩面），base `f4bfcf2` 续 commit（原 base 502bf8e 不变，本地 main c2018dd 纯文档零冲突），最小测试增量 5 项（unknown 提交/非 dict 422/并发 409 口径/双 MANUAL 行夹具/下架徽章页面实测）。B 原交付冻结解除转 R2。\n"
"- 角色占用（本轮核）：**A=16A RUNNING**（ACK 22:41，wt-01-t16a 自 c2018dd 新建，冻结 wt-01/wt-01-t10def1 不动）；**C=16B RUNNING**（ACK 22:46，wt-03b-t16b 分支 c/task-16b-scene-host-proxy，据冻结契约自测、最终接线待 16A 产物）；B=07B R2 返修（待 ACK）；TESTER 空闲（16D WAITING 三前置）。\n"
"- main 本地 `c2018dd`（纯文档 v0.4）/origin `502bf8e` 零 app 面漂移（f4bfcf2 未合入，独立 rev-parse）；vllm 18002 running=4/waiting=4（capacity，OCR 已收口无影响）。\n"
"- **强审查（strong_review.py status 本轮只读实测 23:0x）**：AUTHORIZED，grant `31dcbabe…`（用户 24h 授权 2026-10-12 11:33），绝对期限 **2026-10-13 11:33:12 +08:00**，范围=本项目 REVIEW_NOW 判定；滚动 60 分钟 **0/5**、本授权累计 **0 次**、在途 0、token/费用=**未知**。07B 写接口面+5 处 CONFIRMED 预判 **REVIEW_NOW**，待 R2 交付+增量 OCR 后 pack 起跑（本轮不起跑，报告回合只读）。\n"
"- 门禁：TASK-07 RUNNING（07A DONE main `caf385b`；**07B R2 返修在途，不合入**；07C 待 07B DONE 后派）；TASK-16 聚合 RUNNING（16A/16B 开发中，16C 待 B 释放后派，16D WAITING）；TASK-10 DONE；TASK-11 生产 **PRODUCTION BLOCKED**；12-15 DEFERRED；changelog F-035~039 等用户审批不催。\n"
"- 本轮控制动作：claim（`cron-coord-poll-14ae4556629a-20261012-223553-r102-…`，23:05:46）→巡检核查（r101_resume_progress done 标记+b5/b7 resume 日志独立复读/ps+fuser 核进程退出与锁释放/wt-04a-t07b 独立核 3 处新 finding 代码事实含 models 唯一约束+ingest F2 先例+css 兄弟规则/TODO §8 16A/16B ACK 核/sessions A/C 开工核/strong_review status 只读/vllm metrics）→OCR 批次账+ruling v2+R2 派单+TIMELINE+DEVLOG+本 checkpoint+event 落盘→release。**有状态变化（OCR 10/10 全收口 + 3 处新 CONFIRMED + R2 派单）**，无合入、无强审查调用。\n"
"- **下一步：** r103+ 核 B R2 ACK/交付（wt-04a-t07b 新 commit+回执 `receipts/TASK-07B/attempt-2-r2.md`）→机械核验→增量 OCR（仅 R2 diff，起跑前 §3.6 尺寸预检）→强审查 pack（0/5 期限 2026-10-13 11:33:12）→合入→TESTER 独立验证→07B DONE→派 07C/16C；A 16A/C 16B 开发在途观察（不催单不接管）。\n\n"
)
wr(sp, cp + old)

# mirror (inbox/sessions) append-only sync
mp = ROOT + "/inbox/sessions/COORDINATOR.md"
mold = rd(mp)
wr(mp, cp + mold)

# ---------- 7. HANDOFF prepend ----------
hf = ROOT + "/HANDOFF.md"
oldh = rd(hf)
hfc = (
"## " + TS + " 巡检检查点（cron poll 14ae4556629a，第 102 轮，preflight " + PRE + "；**状态变化=OCR 10/10 全收口 + 新增 3 处 CONFIRMED CORRECTION（合计 5+6 LOW）+ R2 最小返修已派 B**）\n\n"
"- **OCR 收口 10/10**：b5 resume RC=0 1800s（3 findings：2 medium+1 low）+ b7 resume RC=0 839s（3 findings：1 medium+2 low），22:43:38 done、pid 607379 退出、ocr.lock 无持有；无 NEEDS_REVIEW，合入门禁 OCR 面不冻结。契约批次 CLOSED 不单跑（跨文件面已覆盖）。\n"
"- **5 处 CONFIRMED CORRECTION**（协调者独立核代码属实）：b9-1 HIGH（detail.html:52 corrected_label 7 选项 vs 服务 " + SL + "）/ b3 MEDIUM（非 dict JSON→500 非 422）/ b5-1 MEDIUM（revise/withdraw 乐观锁非守卫写入，F2 先例口径）/ b5-2 MEDIUM（MANUAL evidence 查询无 limit(1)，表无唯一约束）/ b7-1 MEDIUM（.bag-scene-withdrawn 缺 align-self 布局错位）+ 6 LOW 随同 commit。裁决 `inbox/coordinator/TASK-07B/ocr-r102-closure-ruling.md`。\n"
"- **R2 最小返修已派 B**（`inbox/2号/TASK-07B/attempt-2-r2-dispatch.md`）：R2-1~R2-10，base f4bfcf2 续 commit，零新迁移零新依赖；后续=机械核验→增量 OCR→强审查 pack（授权 0/5 期限 2026-10-13 11:33:12）→合入→TESTER→07B DONE→派 07C/16C。\n"
"- 角色占用：A=16A RUNNING（ACK 22:41 已开工 wt-01-t16a）、C=16B RUNNING（ACK 22:46 已开工 wt-03b-t16b）、B=07B R2（待 ACK）、TESTER 空闲；main 本地 c2018dd/origin 502bf8e 零 app 面漂移。\n"
"- 门禁：TASK-07 RUNNING（07B 不合入）；TASK-16 聚合 RUNNING（16C 待 B 释放，16D WAITING）；TASK-11 生产 PRODUCTION BLOCKED；12-15 DEFERRED。\n\n"
)
wr(hf, hfc + oldh)

# ---------- 8. TODO TASK-07 line append note ----------
tp = ROOT + "/TODO.md"
oldt = rd(tp)
anchor = "裁决 inbox/coordinator/TASK-07B/ocr-r101-findings-ruling.md** | 2号 / 07B attempt-1（待 ACK）"
if anchor in oldt:
    note = anchor.replace(
        "裁决 inbox/coordinator/TASK-07B/ocr-r101-findings-ruling.md** | 2号 / 07B attempt-1（待 ACK）",
        "裁决 inbox/coordinator/TASK-07B/ocr-r101-findings-ruling.md；**【r102 " + TS + "】OCR 10/10 全收口（b5 resume RC=0 3 findings / b7 resume RC=0 3 findings，22:43:38 done）→ 独立核代码新增 3 处 CONFIRMED（b5-1 守卫 UPDATE 口径 / b5-2 evidence limit(1) / b7-1 徽章 align-self，合计 5 CONFIRMED+6 LOW）→ **R2 最小返修已派 B**（inbox/2号/TASK-07B/attempt-2-r2-dispatch.md，base f4bfcf2 续 commit）→ 增量 OCR → 强审查 pack（授权 0/5 期限 2026-10-13 11:33:12）→ 合入 → TESTER 独立验证 → 07B DONE → 派 07C/16C；裁决 v2 inbox/coordinator/TASK-07B/ocr-r102-closure-ruling.md** | 2号 / 07B attempt-2-r2（待 ACK）"
    )
    assert note != anchor
    oldt = oldt.replace(anchor, note, 1)
    wr(tp, oldt)
    print("TODO updated")
else:
    print("WARN: TODO anchor not found, skipped")

# TODO 16A/16B ACK status
t16a_old = "**RUNNING（2026-10-12 22:40 派 A，base c2018dd，`inbox/1号/TASK-16A/attempt-1-dispatch.md`；待 ACK）**"
t16a_new = "**RUNNING（2026-10-12 22:40 派 A，base c2018dd，`inbox/1号/TASK-16A/attempt-1-dispatch.md`；A ACK 22:41 ACCEPTED，wt-01-t16a 已开工）**"
if t16a_old in oldt:
    oldt = oldt.replace(t16a_old, t16a_new, 1)
t16b_old = "最终接线消费 16A 产物；待 ACK）**"
t16b_new = "最终接线消费 16A 产物；C ACK 22:46 ACCEPTED，wt-03b-t16b 已开工）**"
if t16b_old in oldt:
    oldt = oldt.replace(t16b_old, t16b_new, 1)
wr(tp, oldt)

# ---------- 9. event ----------
evt = (
"# COORDINATOR event — r102 OCR 10/10 全收口 + 3 处新 CONFIRMED CORRECTION + R2 最小返修派 B\n"
"- event_id: coord-poll-20261012-223553-r102-t07b-ocr-10of10-r2-dispatch\n"
"- role: COORDINATOR\n"
"- checked_at: " + PRE + " (preflight)\n"
"- written_at: " + TS + "+08:00\n"
"- task: TASK-07B attempt-2-r2\n"
"- status: REVIEW_PENDING→R2_DISPATCHED（07B f4bfcf2 未合入，R2 返修已派）\n"
"- summary: r101 resume 链 22:43:38 全收口（b5 RC=0 1800s 3 findings + b7 RC=0 839s 3 findings，pid 607379 退出 ocr.lock 无持有，ps/fuser 独立核）→ OCR 10/10，无 NEEDS_REVIEW；协调者独立核代码新增 3 处 CONFIRMED CORRECTION（b5-1 乐观锁非守卫写入 lost-update/500 vs 409，ingest F2 先例；b5-2 MANUAL evidence 查询无 limit(1) 双行 500，表无唯一约束已核；b7-1 .bag-scene-withdrawn 缺 align-self 布局错位，兄弟规则已核），合计 5 CONFIRMED+6 LOW；契约批次 CLOSED 不单跑（跨文件面已覆盖）。**R2 最小返修派 B**（attempt-2-r2-dispatch.md，R2-1~R2-10，base f4bfcf2 续 commit，4 必改+1 可选文件，最小测试 5 项）→ 后续 机械核验→增量 OCR→强审查 pack（0/5 期限 2026-10-13 11:33:12）→合入→TESTER→07B DONE→派 07C/16C。\n"
"- evidence: scratch/t07b/ocr/r101_resume_progress.txt（== r101 resume done 2026-10-12 22:43:38 ==）；reviews/TASK-07B/attempt-1/ocr-batches.md（r102 更新）；inbox/coordinator/TASK-07B/ocr-r102-closure-ruling.md；inbox/2号/TASK-07B/attempt-2-r2-dispatch.md\n"
"- next: r103+ 核 B R2 ACK/交付；A 16A/C 16B 开发在途观察。\n"
)
wr(ROOT + "/inbox/events/COORDINATOR/coord-poll-20261012-223553-r102-t07b-ocr-10of10-r2-dispatch.md", evt)

print("r102 doc writes OK")