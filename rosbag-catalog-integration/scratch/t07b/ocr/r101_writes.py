#!/usr/bin/env python3
"""r101 doc writes under coordinator lease. Read-then-write; no truncation."""
import io, os

ROOT = "/home/wang/work/doc/prd/rosbag-catalog-integration"
os.makedirs(ROOT + "/inbox/coordinator/TASK-07B", exist_ok=True)
def rd(p):
    with io.open(p, "r", encoding="utf-8") as f:
        return f.read()
def wr(p, s):
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(s)
def ap(p, s):
    with io.open(p, "a", encoding="utf-8") as f:
        f.write(s)

TS = "2026-10-12 21:5x"
SL = "{slope,flat,unknown}"          # _VALID_LABELS set literal
SL_LONG = "{LABEL_SLOPE, LABEL_FLAT, LABEL_UNKNOWN}"

# ---------- 1. ocr-batches.md ----------
ob = ROOT + "/reviews/TASK-07B/attempt-1/ocr-batches.md"
s = rd(ob)
s = s.replace(
    "| T07B-b9 | app/templates/detail.html | +36/-1 | r95 detached 在途（20:51:29 起，node pid 525278，detached 父 pid 464164 flock 持 `inbox/ocr.lock`） | 20:51 起 | INFLIGHT（detached） | 未审 |",
    "| T07B-b9 | app/templates/detail.html | +36/-1 | r95 detached session `0c62a8cc` **RC=0 1800s**（20:51→21:21，usage 792803 tokens） | 21:21 | COMPLETED | **3 findings**：① **[bug·HIGH]** detail.html:52 `corrected_label` 下拉提供 construction/congestion/night/rain/other 5 个模型不产出的标签，服务 `_VALID_LABELS`=" + SL + " 会 422，且合法 `unknown` 缺选项（**独立核实代码属实**=f4bfcf2 只改 service+tests 未改模板，模板仍列 7 项）=**CORRECTION**；② **[maintainability·LOW]** detail.html:72 审计时间列渲染 `created_at.isoformat()` 字符串（含 T/微秒/+08:00）非全站 `datetime_local` 口径；③ **[bug·LOW]** detail.html:52 select 缺 `required`，空串提交触发 422 往返。round2 LLM deadline 报 review_round_failed，但 core review 已 complete=3 findings 有效 |"
)
s = s.replace(
    "| T07B-b10 | app/web/bags.py | +77 | - | | QUEUED | |",
    "| T07B-b10 | app/web/bags.py | +77 | r95 detached session `0dd6c985` **RC=0 304s**（21:21→21:26，usage 97161 tokens） | 21:26 | COMPLETED | **0** |"
)
s = s.replace(
    "| T07B-b5 | app/services/scene_manual_revision_service.py | +383 | r95 detached 第 6 次尝试 session `81a66282` **RC=1 FAILED**（20:02:16→20:32:3x，1800s，core request timed out、compaction cancelled，usage 1186534 tokens/109 工具调用，vllm 4 并发饱和期；前 5 次 420s reap/回收全作废） | 20:02-20:32 | FAILED（第 6 次） | 未审；**重试政策=r99+ 等 detached 跑完 b7-b10 后低负载期 `--resume 81a66282` 最后一次，再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁，不无限重试** |",
    "| T07B-b5 | app/services/scene_manual_revision_service.py | +383 | r95 detached 第 6 次 session `81a66282` RC=1 FAILED（core request timed out）；**r101 低负载期 `--resume 81a66282` 最后一次 INFLIGHT**（21:59 起跑，detached pid 607379，flock 持 `inbox/ocr.lock`；起跑时 vllm running=4 waiting=1=低负载条件达成） | 21:59 起 | INFLIGHT（resume 最后一次） | 未审；再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁，不无限重试 |"
)
s = s.replace(
    "| T07B-b7 | app/static/bag-search.css | +12/-1 | r95 detached session `daa45a1c-e3d8-4af1-97b2-8ce2585bed95` **RC=1 FAILED**（20:33→20:39，250s，review failed 0 findings，usage 109893 tokens/14 工具调用，瞬态故障非 LLM 超时） | 20:33-20:39 | FAILED（第 1 次） | 未审；**重试政策=b8-b10 跑完后低负载期 `--resume daa45a1c` 最后一次（与 b5 同批），再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁，不无限重试** |",
    "| T07B-b7 | app/static/bag-search.css | +12/-1 | r95 detached session `daa45a1c` RC=1 FAILED（250s 瞬态）；**r101 低负载期 `--resume daa45a1c` 最后一次 INFLIGHT**（b5 resume 收口后串行，同 pid 607379） | b5 后排队 | INFLIGHT（resume 最后一次） | 未审；再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁，不无限重试 |"
)
oldprog = "**收口进度 r100（21:0x）**：7/10（b1 0 / b2 0 / b3 1 medium 待裁决 / b4 0 / b6 0 / b8 1 low 非阻塞）+ b5、b7 双双 FAILED 未审 + b9 在途 + b10 排队；契约批次 b10 后按结果定。"
newprog = ("**收口进度 r101（21:5x）**：r95 detached 已收口 8/10（b1 0 / b2 0 / b3 **1 medium=CONFIRMED CORRECTION 待返修** / b4 0 / b6 0 / b8 1 low 非阻塞 / **b9 3 findings=1 HIGH CORRECTION + 2 LOW** / b10 0）；"
    "**b5（核心服务 +383）/b7（css）r101 低负载期 `--resume` 最后一次 INFLIGHT**（detached pid 607379，21:59 起，progress `scratch/t07b/ocr/r101_resume_progress.txt`）；契约批次=b5/b7 收口后按结果定。\n\n"
    + oldprog +
    "\n\n**r101 裁决（21:5x，协调者独立核代码后落）**：b9 HIGH + b3 MEDIUM = **CONFIRMED CORRECTION**（详见 `inbox/coordinator/TASK-07B/ocr-r101-findings-ruling.md`）；b9 LOW×2 + b8 LOW = 非阻塞 maintainability，随同一返修合并。返修**暂缓派单**：b5/b7 resume 仍在途（review 范围锚定 `502bf8e..f4bfcf2`），此时移动 HEAD 会使在途 resume 失效并可能触发二次返修；等 b5/b7 收口后把全部 OCR findings 并入**一次最小返修**派 B，避免多轮。")
s = s.replace(oldprog, newprog)
wr(ob, s)

# ---------- 2. ruling decision ----------
ruling = (
"# TASK-07B attempt-1 OCR r101 findings 裁决（协调者）\n\n"
"- 时间：" + TS + " +08:00（r101 poll，preflight 2026-10-12T21:30:53+08:00）\n"
"- 被测：`502bf8ec..f4bfcf2a`（base main `502bf8e`，未合入）\n"
"- 依据：`reviews/TASK-07B/attempt-1/ocr-batches.md`（r101 更新）+ 协调者独立核代码（`wt-04a-t07b`）\n\n"
"## CONFIRMED CORRECTION（须返修）\n"
"- **b9-1 [bug·HIGH] detail.html:52 `corrected_label` 选项域与服务校验域不一致**：模板列出 slope/flat/construction/congestion/night/rain/other 共 7 项；服务 `scene_manual_revision_service.py:44 _VALID_LABELS = " + SL_LONG + "`（= " + SL + "，见 :198 校验 `corrected_label not in _VALID_LABELS` → 422）。f4bfcf2 只改了 service + tests 两处对齐，**漏改模板** → 用户选 construction/congestion/night/rain/other 五个必 422，且合法 `unknown` 无选项可勾。独立核实：`app/templates/detail.html:52` 现仍为 7 项列表；`app/scene/slope/segment.py:22-24` 权威常量 = slope/flat/unknown。**违反 AC-04「人工纠错」可用性**。最小修复：detail.html:52 选项改为 " + SL + "（或引用 service 常量）。\n"
"- **b3 [bug·MEDIUM] scene_manual_revision.py:26/:35 `request.json()` 后非 dict JSON（list/scalar）→ `body.get` AttributeError → 500**，与文档化 422 面不一致。独立核实：两接口 `body = await request.json()` 后直接 `service(..., body, ...)`，service 内 `body.get(...)`，无 isinstance 守卫。兄弟 API `ingest_submissions._parse_model` 有先例。最小修复：`isinstance(data, dict)` 守卫或 pydantic DTO，非 dict → 422。\n\n"
"## 非阻塞（随同一返修合并，不单独触发返修）\n"
"- **b9-2 [maintainability·LOW] detail.html:72** 审计「时间」列渲染 `r.created_at.isoformat()` 字符串（含 T/微秒/+08:00），全站其余用 `|datetime_local`（detail.html:86 等）；建议 service 侧改展示格式或保留 datetime 由模板过滤。\n"
"- **b9-3 [bug·LOW] detail.html:52** `corrected_label` select 缺 `required`，空串提交触发无效 422 往返；随 b9-1 修复一并加 `required`。\n"
"- **b8 [maintainability·LOW] bags.html:226** 状态三元 `'failed' if WITHDRAWN else 'failed'` 冗余分支 + 非 WITHDRAWN 切片行空 `title=\"\"`；功能正确（WITHDRAWN 红标/tooltip 测试已覆盖），可选简化。\n\n"
"## 返修派发决策\n"
"- **暂缓**：b5（核心 service +383）/b7（css）r101 低负载期 `--resume` 最后一次 **INFLIGHT**（detached pid 607379，21:59 起）。在途 resume 的 review 范围锚定 `..f4bfcf2`；此时若移动 B 的 HEAD，会使在途 resume 失效并可能引发二次返修。**等 b5/b7 收口后，把 CONFIRMED CORRECTION（b9-1 + b3）+ 非阻塞 LOW 全部并入一次最小返修派 B**（`wt-04a-t07b` 续 attempt），返修 commit 覆盖文件 = `app/templates/detail.html` + `app/api/scene_manual_revision.py`（b8 bags.html 可选）。返修后走增量 OCR + 强审查 pack + 合入 + TESTER 独立验证 → 07B DONE → 派 07C。\n"
"- b5/b7 若最后一次 resume 仍 FAILED → 该文件挂 NEEDS_REVIEW **冻结 07B 合入门禁**（未覆盖文件不得宣称收口），不无限重试。\n"
)
wr(ROOT + "/inbox/coordinator/TASK-07B/ocr-r101-findings-ruling.md", ruling)

# ---------- 3. TIMELINE append ----------
ap(ROOT + "/TIMELINE.md", (
"\n## 2026-10-12 21:5x 协调者 r101 poll（preflight 2026-10-12T21:30:53+08:00，排队约 12min 如实记录）：r95 detached 串行 OCR 21:26:34 跑完收尾——"
"**b9 detail.html RC=0 3 findings（1 HIGH + 2 LOW）+ b10 bags.py RC=0 0 findings**，收口推进至 8/10；协调者独立核代码确认 "
"**b9-1 HIGH（corrected_label 模板 7 选项 vs 服务 _VALID_LABELS=" + SL + "，f4bfcf2 漏改模板→5 项必 422+unknown 缺项）与 b3 MEDIUM（request.json 非 dict→500 非 422）=CONFIRMED CORRECTION**，"
"b9 LOW×2+b8 LOW 非阻塞；**b5（核心 service +383）/b7（css）以低负载期（vllm running=4 waiting=1）`--resume` 最后一次 INFLIGHT**（detached pid 607379，21:59 起，持 ocr.lock，progress r101_resume_progress.txt）；"
"返修**暂缓**待 b5/b7 收口后并入一次最小返修派 B（避免移动 HEAD 使在途 resume 失效+二次返修）；b5/b7 再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁。"
"main 本地 `c2018dd`/origin `502bf8e` 零漂移（07B base 祖先核通过，f4bfcf2 未合入）。强审查 AUTHORIZED（grant 31dcbabe，期限 2026-10-13 11:33:12，60min 0/5，累计 0，token/费用未知），07B 预判 REVIEW_NOW 待 OCR 收口+返修后 pack。"
"门禁：TASK-07 RUNNING（07B 不合入）/10 DONE/11 PRODUCTION BLOCKED/12-15 DEFERRED。裁决 `inbox/coordinator/TASK-07B/ocr-r101-findings-ruling.md`。event coord-poll-20261012-213053-r101-t07b-ocr-b9b10-done-b5b7-resume-inflight。\n"
))

# ---------- 4. DEVELOPMENT-LOG append ----------
ap(ROOT + "/DEVELOPMENT-LOG.md", (
"\n## 2026-10-12T21:55:00+08:00 TASK-07B attempt-1 OCR 收口推进 + CONFIRMED CORRECTION 裁决\n"
"- r95 detached 串行 OCR 21:26:34 收口收尾两批：b9 `app/templates/detail.html` RC=0（3 findings：1 HIGH + 2 LOW）+ b10 `app/web/bags.py` RC=0（0 findings）→ 累计收口 8/10。\n"
"- 协调者独立核代码确认两条 CONFIRMED CORRECTION：①b9-1 HIGH——detail.html:52 `corrected_label` 下拉列 7 选项（含 construction/congestion/night/rain/other），服务 `_VALID_LABELS`=" + SL + "，f4bfcf2 只改 service+tests 漏改模板 → 5 项提交必 422、合法 unknown 无选项（违反 AC-04 人工纠错可用性）；②b3 MEDIUM——scene_manual_revision.py `request.json()` 非 dict → 500 与文档化 422 面不一致。b9 LOW×2 + b8 LOW 非阻塞，随同一返修合并。\n"
"- b5（核心 service +383）/b7（css）低负载期（vllm running=4/waiting=1）`--resume` 最后一次 INFLIGHT（detached pid 607379，21:59 起）；再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁。\n"
"- 返修暂缓：等 b5/b7 收口后全部 findings 并入一次最小返修派 B（避免移动 HEAD 使在途 resume 失效）。\n"
"- 未生成正式功能 released 日志；无业务合入、无生产动作。\n"
))

# ---------- 5. sessions prepend ----------
sess_p = ROOT + "/inbox/sessions/COORDINATOR.md"
old = rd(sess_p)
cp = (
"## " + TS + " 巡检检查点（cron poll 14ae4556629a，preflight checked_at 2026-10-12T21:30:53+08:00，排队约 12min 如实记录，第 101 轮；**状态变化=r95 detached OCR 21:26:34 跑完收尾：b9 detail.html RC=0 3 findings（1 HIGH+2 LOW）+ b10 bags.py RC=0 0 → 收口 8/10；协调者独立核代码确认 b9-1 HIGH + b3 MEDIUM = CONFIRMED CORRECTION；b5/b7 低负载期 resume 最后一次 INFLIGHT（detached pid 607379 21:59 起）**）\n\n"
"- **r95 detached 串行 OCR 收口推进（pid 464164 已退出，ps+fuser 独立核实无残留持锁）**：`remaining_progress.txt` 21:26:34 落 `== r95 detached done ==`；**b9 `app/templates/detail.html` RC=0 1800s（session `0c62a8cc`，usage 792803 tokens，round2 LLM deadline 报 review_round_failed 但 core review complete=3 findings 有效）**：①**[bug·HIGH]** detail.html:52 `corrected_label` 下拉 7 选项 vs 服务 `_VALID_LABELS`=" + SL + "；②[maintainability·LOW] detail.html:72 审计时间列 `isoformat()` 字符串非 `datetime_local`；③[bug·LOW] detail.html:52 select 缺 `required`。**b10 `app/web/bags.py` RC=0 304s（session `0dd6c985`）0 findings**。累计收口 **8/10**（b1/b2/b4/b6 0 + b3 1 medium + b8 1 low + b9 3 + b10 0）+ b5/b7 未审。\n"
"- **协调者独立核代码（`wt-04a-t07b` HEAD `f4bfcf2`）=两条 CONFIRMED CORRECTION 裁决落盘** `inbox/coordinator/TASK-07B/ocr-r101-findings-ruling.md`：b9-1 HIGH 属实（f4bfcf2 只改 service+tests 未改模板，`detail.html:52` 现仍 7 项、`segment.py:22-24` 权威=slope/flat/unknown → 5 项必 422 + unknown 缺项，违反 AC-04）；b3 MEDIUM 属实（两接口 `request.json()` 后 `body.get` 无 isinstance 守卫）。b9 LOW×2+b8 LOW 非阻塞随同一返修合并。\n"
"- **b5/b7 最后一次 resume INFLIGHT（本轮发起，不无限重试）**：低负载窗口实测 vllm running=4 **waiting=1**（capacity）达成条件 → `r101_resume.py` detached（`start_new_session` pid **607379**，21:59 起，flock 持 `inbox/ocr.lock`，串行 b5 `--resume 81a66282`（核心 service +383）→ b7 `--resume daa45a1c`（css））；progress `scratch/t07b/ocr/r101_resume_progress.txt`，`ocr session list` 独立核实两 session 在盘 status=failed 可 resume。**再失败=挂 NEEDS_REVIEW 冻结 07B 合入门禁**（未覆盖文件不得宣称收口）。\n"
"- **返修暂缓（串行原因+解除条件）**：b5/b7 resume review 范围锚定 `502bf8e..f4bfcf2`，此时移动 B HEAD 会使在途 resume 失效并可能二次返修 → **等 b5/b7 收口后把全部 findings（b9-1 HIGH+b3 MEDIUM+LOW 合并）并入一次最小返修派 B**（覆盖 detail.html+scene_manual_revision.py，b8 可选）→ 增量 OCR → 强审查 pack → 合入 → TESTER 独立验证 → 07B DONE → 派 07C。B 维持交付冻结 REVIEW_PENDING（`f4bfcf2` 未合入）等返修单。\n"
"- main 本地 `c2018dd`（纯文档 v0.4）/origin `502bf8e`=07B base 祖先核通过零漂移（f4bfcf2 未合入，独立 rev-parse）；A/C/TESTER 空闲（legacy_busy 空），B 交付冻结；leases 仅本轮自身 COORDINATOR + C 21:31 自身例行短租约（无在途业务持有）。\n"
"- 强审查（授权账本口径，续 r100）：AUTHORIZATION=AUTHORIZED，grant `31dcbabe…`（用户 24h 授权 2026-10-12 11:33），绝对期限 **2026-10-13 11:33:12 +08:00**，范围=本项目 REVIEW_NOW 判定；滚动 60 分钟 **0/5**、本授权累计 **0 次**、在途 0、token/费用=**未知**。07B 写接口面+本次 2 条 CONFIRMED CORRECTION 预判 **REVIEW_NOW**，待 OCR 收口（b5/b7）+返修合入后按 pack 流程起跑，本轮不起跑。\n"
"- 门禁：TASK-07 维持 RUNNING（07A DONE main `caf385b`；**07B 不合入**=OCR b5/b7 未收口+2 条 CONFIRMED CORRECTION 待返修；07C 预览待 07B 收口后派）；TASK-10 DONE/P0 收口维持；TASK-11 生产启用**维持 PRODUCTION BLOCKED**；TASK-12/13/14/15 维持 DEFERRED；TASK-16 v0.4 PLANNED 待 07B 检查点释放 B 后按候选重算派（本轮不动）。changelog F-035~039 等用户审批不催。\n"
"- 本轮控制动作：claim（`cron-coord-poll-14ae4556629a-20261012-213053-r101`，21:39:27）→ 巡检核查（r95 done 标记+ps/fuser 核无残留 / b9+b10 日志独立复读 / `ocr session list` 核 b5/b7 session 在盘 / wt-04a-t07b 独立核 detail.html:52+segment.py+scene_manual_revision.py 确认 2 条 CORRECTION / vllm metrics 低负载实测 / fetch+rev-parse 双核 / strong_review 授权账本只读）→ 发起 r101 detached resume（b5+b7 最后一次，pid 607379）→ 裁决+账本+TIMELINE+sessions+HANDOFF+DEVLOG 落盘 → **控制租约 release（OCR 长批由 detached pid 607379 独立持 ocr.lock 续跑）**。**有状态变化（OCR 8/10 收口 + 2 条 CONFIRMED CORRECTION 裁决 + b5/b7 最后一次 resume 起跑）**，无合入、无返修派单（暂缓）。\n"
"- **下一步：** r102+ 核 b5/b7 resume 收口（`r101_resume_progress.txt` + `ocr session list` 核 status；再失败如实记账不无限重试）→ b5/b7 收口即全部 findings 并入**一次最小返修**派 B（detail.html corrected_label 域+required / scene_manual_revision.py isinstance 守卫 / 可选 bags.html 冗余三元）→ 增量 OCR → 强审查 pack 起跑（授权 0/5 期限 2026-10-13 11:33:12）→ 合入（核 base 漂移零冲突）→ TESTER 独立验证（API 四要素+corrected_label 域+非 dict 422+迁移往返+既有套件 0 红）→ 07B DONE → 派 07C；b5/b7 任一 NEEDS_REVIEW 则冻结 07B 合入门禁记停滞不自动接管。\n\n"
)
wr(sess_p, cp + old)

# ---------- 6. HANDOFF prepend ----------
hf = ROOT + "/HANDOFF.md"
oldh = rd(hf)
hfc = (
"## " + TS + " 巡检检查点（cron poll 14ae4556629a，第 101 轮，preflight checked_at 2026-10-12T21:30:53+08:00；**状态变化=r95 detached OCR 21:26:34 跑完收尾：b9 RC=0 3 findings（1 HIGH+2 LOW）+ b10 RC=0 0 → 收口 8/10；协调者独立核代码确认 b9-1 HIGH + b3 MEDIUM = CONFIRMED CORRECTION；b5/b7 低负载期 resume 最后一次 INFLIGHT（detached pid 607379 21:59 起）**）\n\n"
"- **OCR 收口 8/10**：b1/b2/b4/b6 0 / b3 **1 medium=CONFIRMED CORRECTION** / b8 1 low 非阻塞 / **b9 detail.html 3 findings（1 HIGH CORRECTION：corrected_label 模板 7 选项 vs 服务 " + SL + "，f4bfcf2 漏改模板→5 项必 422+unknown 缺项；2 LOW：审计时间列 isoformat 口径 + select 缺 required）** / b10 bags.py 0。b5（核心 service +383）/b7（css）**r101 低负载期（vllm running=4 waiting=1）`--resume` 最后一次 INFLIGHT**（detached pid 607379，持 ocr.lock，progress `r101_resume_progress.txt`）；再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁，不无限重试。\n"
"- **返修暂缓**：b5/b7 在途 resume 范围锚定 `..f4bfcf2`，移动 HEAD 会失效+二次返修 → 等 b5/b7 收口后全部 findings 并入**一次最小返修**派 B（detail.html+scene_manual_revision.py，b8 可选）→ 增量 OCR → 强审查 pack → 合入 → TESTER 独立验证 → 07B DONE → 派 07C。裁决 `inbox/coordinator/TASK-07B/ocr-r101-findings-ruling.md`。\n"
"- main 本地 `c2018dd`/origin `502bf8e` 零漂移（f4bfcf2 未合入）；07B 交付冻结 REVIEW_PENDING 不变；A/C/TESTER 空闲，B 冻结等返修单。\n"
"- 强审查授权在案（grant `31dcbabe…` 至 2026-10-13 11:33:12，滚动 60 分钟 0/5，累计 0，在途 0，token/费用未知）；07B 预判 REVIEW_NOW 待 OCR 收口+返修后 pack。\n"
"- 门禁：TASK-07 RUNNING（07B 不合入）；TASK-11 生产 BLOCKED；12-15 DEFERRED；16 v0.4 PLANNED 待 07B 检查点释放 B 后候选重算。\n\n"
)
wr(hf, hfc + oldh)

# ---------- 7. TODO TASK-07 line ----------
tp = ROOT + "/TODO.md"
oldt = rd(tp)
anchor = "**07B attempt-1 已派 B**（14:50 inbox/2号/TASK-07B/attempt-1-dispatch.md，base 502bf8e，纠错/下架写接口+审计+页面入口，DESIGN §7.2 口径）；07C 预览待 07B 收口后派"
if anchor in oldt:
    note = anchor + "；**【r101 2026-10-12 21:5x】07B attempt-1 已交付冻结 REVIEW_PENDING（HEAD f4bfcf2，base 502bf8e，17:15 receipts）→ 机械核验全绿 → 串行 OCR 收口 8/10（b9 detail.html 3 findings：1 HIGH=corrected_label 模板域 vs 服务 " + SL + " 漏改（f4bfcf2 只改 service）；b3 MEDIUM=request.json 非 dict→500 非 422，两条 CONFIRMED CORRECTION；b9 2 LOW+b8 1 LOW 非阻塞）+ b5（service +383）/b7（css）低负载期 resume 最后一次 INFLIGHT（detached pid 607379，21:59 起）→ 收口后全部 findings 并入一次最小返修派 B（返修暂缓避免移动 HEAD 失效在途 resume）→ 强审查 pack（授权 0/5 期限 2026-10-13 11:33:12）→ 合入 → TESTER 独立验证 → 07B DONE → 派 07C；裁决 inbox/coordinator/TASK-07B/ocr-r101-findings-ruling.md"
    oldt = oldt.replace(anchor, note, 1)
    wr(tp, oldt)

# ---------- 8. event ----------
evt = (
"# COORDINATOR event — r101 OCR 8/10 收口 + 2 CONFIRMED CORRECTION 裁决 + b5/b7 resume INFLIGHT\n"
"- event_id: coord-poll-20261012-213053-r101-t07b-ocr-b9b10-done-b5b7-resume-inflight\n"
"- role: COORDINATOR\n"
"- checked_at: 2026-10-12T21:30:53+08:00 (preflight)\n"
"- written_at: " + TS + "+08:00\n"
"- task: TASK-07B attempt-1\n"
"- status: REVIEW_PENDING（07B 交付冻结不变，f4bfcf2 未合入）\n"
"- summary: r95 detached 串行 OCR 21:26:34 跑完收尾（pid 464164 已退出，ps+fuser 核无残留持锁）：b9 detail.html RC=0 1800s（session 0c62a8cc，3 findings=1 HIGH+2 LOW，round2 LLM deadline 报 review_round_failed 但 core review complete）+ b10 bags.py RC=0 304s（session 0dd6c985，0）→ 收口 8/10；协调者独立核代码（wt-04a-t07b HEAD f4bfcf2）确认 b9-1 HIGH（corrected_label 模板 7 选项 vs 服务 _VALID_LABELS=" + SL + "，f4bfcf2 只改 service+tests 漏改模板）+ b3 MEDIUM（request.json 非 dict→500 非 422）=CONFIRMED CORRECTION，b9 LOW×2+b8 LOW 非阻塞；**b5（service +383）/b7（css）低负载期（vllm running=4 waiting=1）r101 detached `--resume` 最后一次 INFLIGHT（pid 607379，21:59 起，持 ocr.lock）**，再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁；返修暂缓待 b5/b7 收口后并入一次最小返修派 B。\n"
"- evidence: scratch/t07b/ocr/remaining_progress.txt（== r95 detached done 21:26:34 ==）；reviews/TASK-07B/attempt-1/ocr-batches.md（r101 更新）；inbox/coordinator/TASK-07B/ocr-r101-findings-ruling.md；scratch/t07b/ocr/r101_resume_progress.txt\n"
"- next: r102+ 核 b5/b7 resume 收口 → 全部 findings 并入一次最小返修派 B → 增量 OCR → 强审查 pack（授权 0/5 期限 2026-10-13 11:33:12）→ 合入 → TESTER 独立验证 → 07B DONE → 派 07C。\n"
)
wr(ROOT + "/inbox/events/COORDINATOR/coord-poll-20261012-213053-r101-t07b-ocr-b9b10-done-b5b7-resume-inflight.md", evt)

print("r101 doc writes OK")