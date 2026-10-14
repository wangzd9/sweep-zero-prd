---
task: TASK-06B
attempt: 1-r2-rework-2（同返修单内 medium 小修，不占新轮次）
item: r6 OCR 两条 medium（M-1 写库口径 / M-2 指纹 fail-open）
owner: 2号（执行者 B）
status: REVIEW_PENDING
base: wt-04a a07c181（B8c high 小修之上续做，同分支 scene/task-06b-r2-rework）
output_commit: 9325155
worktree: /home/wang/.local/state/rosbag-scene/wt-04a
received: 2026-10-10 15:51（派单 inbox/2号/TASK-06B/attempt-1-r2-rework-2.md 落盘时间）
delivered: 2026-10-10 15:58（git commit 时间）
---

# TASK-06B attempt-1-r2-rework-2 回执（r6 两条 medium 小修）

## 交付行为

r6（scene_result_report_service.py 补审，session ce42f0e4）收口 3 findings，
high（vehicle 路径注入）已由 a07c181 修复并验收认可；本单修剩余 2 条 medium，
与 a07c181 同批交协调者对 `a07c181..tip` 增量 OCR：

- **M-1 写库 aware_now → local_now**：`_mark_children_available` 回填子包
  `child.updated_at` 由 `aware_now()`（展示时区感知）改 `local_now()`
  （`app.clock.now`，naive 业务时区写库口径，与 bag_record 表 `default=now`
  一致）；只改落库处，本文件对外响应/日志的 aware 用法未动；`:501` docstring
  同步更正；移除本文件已无用途的 `from app.clock import aware_now` import。
- **M-2 父包指纹 fail-open → fail-closed**：源指纹校验由
  `if parent.fast_fingerprint and …不等…`（父包无指纹时静默跳过）改为
  `if not parent.fast_fingerprint: raise 409 SOURCE_FINGERPRINT_MISMATCH
  （父包缺少 fast_fingerprint，无法核对源身份（不覆盖不猜测））` +
  独立不等分支，与函数 docstring（"缺失/不等 → 409"）及 R2-08 契约一致。

## 文件清单（2 文件，零越界）

- `app/services/scene_result_report_service.py`（+10/-5）：M-1（:563 落库处 +
  :501 docstring + import 清理）、M-2（:266 fail-closed 分支）。
- `tests/test_scene_result_report.py`（+87/-0）：新增 2 例定向回归——
  - `test_r6_m1_child_updated_at_is_naive_local`：完整链（create→claim→真实
    staging 发布→/results→complete-scene）后断言 child.updated_at
    **naive**（tzinfo is None，与 bag_record 表同口径）且与业务时区 naive
    墙钟漂移 <120s（aware 口径只允许出现在对外响应/日志）。
  - `test_r6_m2_parent_without_fingerprint_fail_closed`：父包
    `fast_fingerprint=None` + manifest 带指纹 → `/results` **409
    SOURCE_FINGERPRINT_MISMATCH**（detail 含"缺少/fast_fingerprint"），
    不再静默通过。

未执行项：无（自测/全量/ruff 全做）；OCR 按派单由协调者对 a07c181..tip
同批跑，本单不自跑。

## 验证（真实退出码，环境 worktree 9325155，SQLite 隔离库）

- 定向：`pytest tests/test_scene_result_report.py` → **31 passed**
  （含 r6-m1/r6-m2 2 新增；3.6s）。
- 全量 SQLite：`pytest tests/` → **812 passed / 3 failed / 7 errors / 10 skipped**
  （812 = 上单 810 + 本单 2 新增；3 failed = test_devflow 沙箱环境性、
  7 errors = test_r2_repro 需 /tmp/r2-review-* 隔离库，均与 main 基线同集，
  非本次变更引入）。
- ruff：`ruff check` 2 文件 → **All checks passed**。
- 提交范围：`git diff a07c181..9325155 --stat` = 2 文件 +97/-5（service 15 行、
  tests 87 行）；`.venv`、`tests/test_r2_repro.py` 仍未纳入（worktree 原有未跟踪）。

## 越界申报

无。2 文件全在派单允许范围（report 服务 + 本任务测试）；M-1 只改落库处，
未动对外响应/日志的 aware 用法（派单明确边界）。

## 下一步

等协调者：对 `a07c181..tip`（本 commit 9325155，尺寸预检拆批）增量 OCR
无 high/critical → f088c2b + c67600d + a07c181 + 9325155 同批 --no-ff 合入
（R2-05 契约互锁）→ TESTER MySQL 终测 + R2-05 交错联调。