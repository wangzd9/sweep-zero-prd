---
task: TASK-05
attempt: 1
status: ACCEPT_MERGED
decided_by: 协调者（cron 验收）
updated: 2026-10-09 14:0x
base: eaf632a（origin/main 合入前）
output_commit: 2d4a6fa（dccc867 + 1946718 + d1f2eba + 2d4a6fa，主工作区例外协议）
worktree: /home/wang/work/rosbag-catalog（主工作区，例外）
merge_commit: b3280c9（--no-ff 合入 03B a8fac99 同一主线；05 四 commit 原样保留在历史中）
pushed: origin/main = b3280c9（GitLab 已推）
---

# TASK-05 attempt-1 验收结论：ACCEPT（例外任务，commit 已在本地 main，验收+推送）

## 例外协议适用
1号在主工作区提交（第 2 次例外，协议 v1 起禁止新发生）——已核 d1f2eba 与
2d4a6fa 均为纯 05 scope，无越界文件，予以接受但记录在案。后续返修/新任务
必须走 wt-01 worktree（1号已在回执确认该约定）。

## 协调者独立验收（不信任自报）

### 范围核对
- `git diff eaf632a 2d4a6fa --name-only` = 14 文件，全部 05 scope（api/scene_analysis_runs、
  api/pipelines、config、domain/enums、domain/transitions、orchestrator、
  schemas/requests、services/pipeline_service、services/scene_schedule_consumer、
  services/scene_slice_service、api/__init__、schemas/__init__、tests/test_scene_slice_scheduling、
  HANDOFF.md）。HANDOFF.md 的 +1/-1 为 cb0198c（并行会话文档修正，非 05 交付）。
- 无 .venv/环境产物；`cb0198c` 单文件 docs，已核。
- 2d4a6fa（回执晚到的基线前移）：`git show 2d4a6fa --stat` = 2 文件
  （scene_schedule_consumer.py +44/-22 区域、test +1 断言），纯 05 scope。✅

### 测试复跑（协调者主工作区独立跑）
- 全量 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q` @ 2d4a6fa
  → **703 passed, 10 skipped**，退出码 0（与自报一致）。
- 03B a8fac99 --no-ff 合入后（b3280c9）复跑 → **730 passed, 10 skipped**，
  零回归（03B 新增 27 项测试并入，05 场景 28 项含在 703 内）。
- `ruff check app tests` → All checks passed；`ruff format --check` → 192 files formatted。

### OCR 意见核实（8 条：dccc867 6 条 + e573bdbe 2 条，全部已修）
对照 HEAD b3280c9 逐条验证修复落地：
1. **[high] orchestrator 直连库越写边界** → 已修：`grep SessionLocal app/orchestrator.py`
   无引用；orchestrator 现走 `POST /api/v1/orchestrator/purpose-events/consume`
   （api/pipelines.py:86 端点存在）。✅
2. **[medium] per-event 事务隔离** → 已修：consume_purpose_events 内
   `try: _consume_one(...); db.commit() except: db.rollback()` 每事件独立固化。✅
3. **[low] GET 跨模块私有调用** → 已修（d1f2eba，unlocked read helper）。✅
4. **[low] scenes 无上限** → 已修（MAX_SCENE_SELECTIONS 封顶）。✅
5. **[low] SCENE_SLICE 字面量** → 已修（PIPELINE_TYPE_SCENE_SLICE 常量）。✅
6. **[low] 相关字面量** → 已修（共享常量引用）。✅
7. **[low·bug, e573bdbe] queued_run_ids_sample 混历史 run** → 已修（2d4a6fa）：
   `affected_run_ids` 随 create/reuse 逐事件收集，样本限定本批实际影响的 run。✅
8. **[low·perf, e573bdbe] 每事件 reflect outbox 表存在性** → 已修（2d4a6fa）：
   `_outbox_table_exists(db)` 批内算一次，`outbox_exists` 传入 `_consume_one`/`_mark`。✅

1946718（SCENE_DISABLED 422 契约修正）自跑 0 findings；d1f2eba 自跑复查 0 findings
（超时 3 文件已 resume 补齐 = #7/#8）。测试文件未过 OCR（工具 default_path 排除），
以 703 passed 全量为证据——接受。

## 裁决
- **ACCEPT**。05 四 commit 保留在主工作区历史（例外协议），随本次 push origin
  同步共享基线；与 03B 合入（b3280c9）后全量 730 passed 零回归。
- 下游解锁：06B 依赖 05 的 RunContext/租约验证通道已可用（06B 仍在 WAITING，
  06A attempt-2 先行，按 §6.3 优先序）。
- **主工作区例外 2 次**，再犯即 REWORK 回 wt-01 重做；已在回执确认返修约定。