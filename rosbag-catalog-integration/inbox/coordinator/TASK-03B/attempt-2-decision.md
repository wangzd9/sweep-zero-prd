---
task: TASK-03B
attempt: 2
status: REWORK
decided_by: 协调者（cron 验收）
updated: 2026-10-09 12:18
output_commit: 14b7a64（返修后 owner 已推进至 a8fac99，见下）
base: 8e97ef1
worktree: /home/wang/.local/state/rosbag-scene/wt-03b
note: >
  3号已自跑 ingest_service OCR（session 40c26be1，3 findings）并修复到 a8fac99
  （coord 独立核 3 条已落实：_active_profiles 折叠 / row_version 条件 UPDATE+rowcount==0→409 /
  _ensure_system_submission 死代码清理）。a8fac99 正在 3号 自跑 OCR。等 3号
  更新 receipts/TASK-03B/attempt-3.md 到 REVIEW_PENDING，协调者下一轮独立复跑
  pytest + 代跑 a8fac99 核心 OCR + 合入（或再返修，有界 2 轮上限已到）。
---

# TASK-03B attempt-2 验收结论：REWORK（第 2 轮返修，有界最后轮）——3号已返修至 a8fac99，待 REVIEW_PENDING 回执

## 协调者独立验收（不信任自报）

- **范围核对**：`git diff 8e97ef1 14b7a64 --stat` = 13 文件 +2286/-8，与 attempt-1 同范围（迁移/models/api/scanner/bootstrap/ingest_service/scene_capability_read/source_service + 3 测试文件），零越界、无 `.venv` 产物、base 正确。✅
- **测试复跑**（协调者 worktree 独立跑，借用主仓 venv）：
  - 全量 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q` → **664 passed, 10 skipped, 3 failed**。3 failed 全部 `tests/test_devflow.py` 沙箱用例（worktree `.git` 是文件非目录的已知环境问题，同文件主工作区全绿），与本任务改动无关。
  - 定向 ingest 三文件 → 自报 26 passed（协调者以全量覆盖确认无回归）。
- **OCR**：owner 自跑 ingest_service.py 核心补审（session 40c26be1，flock 串行、30m 单请求）→ **3 findings**（1 high / 1 medium / 1 low）。协调者逐条对照当前 HEAD 代码核实，**3 条全部成立**（详见下）。owner 自跑 ocr 属轻微越界（协议规定协调者代跑），但本轮结果经独立核实可用，不作返修事由；**下一轮起 OCR 严格由协调者代跑**。

## 逐条 OCR 意见核实（对照 HEAD 14b7a64 代码）

### 1. [bug · high] ingest_service.py:93 `match_profile_for_incoming` 未按活动版本折叠 —— **成立，必修**
L93 `rows = db.scalars(select(IngestProfile).where(IngestProfile.enabled.is_(True))).all()` 拉取**全部** enabled 行，随后 `_try` 循环按插入序匹配**第一个**命中前缀的行。同 `profile_id` 多个 enabled version 共存时（`IngestProfile` 模型 docstring 明确支持："同一 profile_id 可有多个 version 行，活动入口取 (profile_id, enabled=True) 中 version 最大者"；`uq_ingest_profile_id_version` 只约束 (id,version) 唯一、允许多版本），会命中**旧 version** 行。后果链：`_path_claim_key` 内嵌 `profile_row.version` → 用户按活动 version 建的 PENDING submission 的 claim 键 ≠ 旧 version 行的 claim 键 → `_find_pending_submission`(L457) 查不到 → `_ensure_system_submission` 建重复系统提交，且 `PurposeScheduleEvent` 盖错 `profile_version`，静默孤儿化用户配置。
**协调者独立佐证**：同文件 4 处同类查询**都**按活动版本折叠（`_active_profile` L52 `order_by(version.desc()).limit(1)`、`list_profiles` L193-205 max-version 折叠、`create_submission` L237、`patch_submission` L373-377 按 version 精查），唯独 `match_profile_for_incoming` 没有——自相矛盾，违反模型自身不变式。
**必修**：折叠到活动 version（复用 `list_profiles` 同口径 max-version-per-profile_id），或抽 `_active_profiles_all(db) -> list[IngestProfile]` helper 供本函数与 `list_profiles` 共用，消除第二份折叠逻辑。
**回归测试**：造同一 profile_id 两 enabled version（同/重叠前缀），用户 PENDING submission 挂在活动(高)version；`match_profile_for_incoming` 必须返回活动 version 行；绑定后不产生重复系统提交、事件 `profile_version` == 活动 version。撤折叠应 RED。

### 2. [other · medium] ingest_service.py:367 `patch_submission` row_version 乐观锁未 DB 强制 —— **成立，必修（有界最小修）**
L365-366 `if row_version != submission.row_version: raise 409` 是 read-compare-mutate（scalar 载入→内存比较→L412 `row_version += 1`→flush），无 `UPDATE ... WHERE row_version=:expected`、无 `versionid_col`。两个携同 `row_version` 的并发 PATCH 都过检查都提交，败者选择被静默覆盖却仍回 200——而 docstring 明写"携 row_version 乐观锁"。
**必修（最小）**：提交前用条件 UPDATE 强制——`update(IngestSubmission).where(submission_id==, row_version==expected).values(row_version=expected+1, ...)` 后查 `rowcount==0` 则 409 `ROW_VERSION_CONFLICT`；或给 `IngestSubmission.row_version` 加 `versionid_col`。二选一，保留 409 语义，不扩大范围。
**回归测试**：两 Session/连接同 expected row_version 并发 PATCH，一个成功 200、一个 409，败者写入不落库。

### 3. [other · low] ingest_service.py:490-497 `_ensure_system_submission` 首个查询不可达 + 注释误导 —— **成立，建议修**
首个 `select(...).where(profile_id, profile_version, path_claim_key==claim, source=="system-default")` 无 status 过滤，但 `_ensure_system_submission` 仅在 `_find_pending_submission`(L457，查任意 source 的 PENDING 占位) 返回 None 后才被调——此时该 claim 下**无**任何 PENDING 提交；而 bound/scheduled 提交绑定时 `path_claim_key` 已置 None（L652/L679 两分支均 `path_claim_key=None`）。故首个查询的 `path_claim_key==claim` 永不为真（claim 行的占位要么已被 `_find_pending_submission` 抓到、要么绑定时已释放为 None）。注释"先按占位键查 PENDING 系统提交"与实现（无 status 过滤、且实际查不到）不符。
**建议修**：删首个查询 + 修注释（保留 L499-505 的 relative_path+PENDING 兜底，那个可达）。纯死代码清理，不改行为。

## 裁决与边界

- attempt-2 的 2 medium（except 收窄）+ 2 high（bind 残留误报）+ 3 critical（隔离库裁决）此前已核实收敛，**不重开**。
- 本轮 3 条为 attempt-1 核心逻辑（profile 匹配/乐观锁/死代码）残留，均真实，**第 2 轮返修（有界最后轮）**。
- **验收门槛**：#1 #2 必修 + 各回归测试红绿；#3 建议顺手。全量 pytest 协调者独立复跑；ruff 全绿；commit 只含 ingest_service.py + 对应测试（`git diff 8e97ef1 HEAD --stat` 复核 13 文件范围不扩散、不引入 .venv）。
- 若 attempt-3 再出现同因问题 → 升级用户裁决（同因两轮返修上限）。

## 交付要求（3号 attempt-3）
- 在 worktree 改 `feature/scene-ingest-api`，`git commit`（可 amend 进 14b7a64 保持单 commit，或新 commit，回执写明 output_commit）。
- 回执 `receipts/TASK-03B/attempt-3.md`，status=REVIEW_PENDING，含 #1/#2 语义选择说明 + 回归测试名 + 全量真实退出码。
- **OCR 不要自跑**，交协调者代跑（flock 串行）。
- 完成后即停，不@用户。