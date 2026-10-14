---
task: TASK-06B
attempt: 1-r2-rework-3（同返修单内 low 小修，不占新轮次）
item: 9325155 OCR low（dead code，1 行级）
owner: 2号（执行者 B）
status: REVIEW_PENDING
base: wt-04a 9325155（r6 medium 小修之上续做，同分支 scene/task-06b-r2-rework）
output_commit: 86b2cc1
worktree: /home/wang/.local/state/rosbag-scene/wt-04a
received: 2026-10-10 16:09（派单 inbox/2号/TASK-06B/attempt-1-r2-rework-3.md 落盘时间）
delivered: 2026-10-10 16:14:50+08:00（git commit 86b2cc1）
---

# TASK-06B attempt-1-r2-rework-3 回执（OCR low 死代码小修）

## 交付行为

- 删除 `_verify_source_identity` 中 `if not manifest.source_fingerprint: raise 409`
  不可达分支（原 :276-277）：M-2 新增父包指纹 guard（:265）+ 等值检查（:270）已覆盖
  "manifest 缺指纹"情形（parent 非空 + manifest 空 ⇒ 等值不成立 ⇒ :270 先 409）。
  与派单处置一致；函数 docstring 已覆盖"缺失/不等 → 409"，无需改。
- 测试断言核对：全仓 grep 无测试断言该分支专属消息（"manifest 缺少源指纹"零引用）；
  现有 r6-m2 回归断言 detail 含 `SOURCE_FINGERPRINT_MISMATCH` +（`fast_fingerprint`
  或 `缺少`）——走父包 guard 路径不变。"manifest 空指纹"独立用例不存在，按派单
  处置无需改断；等值 mismatch 路径行为与消息未动。

## 文件清单（1 文件，零越界）

- `app/services/scene_result_report_service.py`（-2）：仅删上述 2 行死分支。

## 验证（真实退出码，环境 worktree 86b2cc1，SQLite 隔离库）

- 定向：`pytest tests/test_scene_result_report.py` → **31 passed**（3.64s，与交付前同集）。
- 全量 SQLite：`pytest tests/` → **812 passed / 3 failed / 7 errors / 10 skipped**
  （3 failed = test_devflow 沙箱环境性、7 errors = test_r2_repro 需
  `/tmp/r2-review-*` 隔离库，与 r6 交付及 main 基线同集，非本次变更引入）。
- ruff：`ruff check app/services/scene_result_report_service.py` → **All checks passed**。
- 提交范围：`git show 86b2cc1 --stat` = 1 文件 -2 行。

## 越界申报

无。

## 下一步

等协调者：对 `9325155..tip`（86b2cc1）增量 OCR 无 high/critical →
f088c2b + c67600d + a07c181 + 9325155 + 86b2cc1 同批 --no-ff 合入
（R2-05 契约互锁）→ TESTER MySQL 终测 + R2-05 交错联调。OCR 按派单由协调者代跑。