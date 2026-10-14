---
task: TASK-06B
item: attempt-1-r2-rework-7
owner: 2号
status: REVIEW_PENDING
dispatched_by: 协调者
delivered_at: 2026-10-11T11:12:00+08:00
base: main 4697be0
commit: 9e5455f
branch: scene/task-06b-codex-rework7
worktree: /home/wang/.local/state/rosbag-scene/wt-04a-r7
裁决: reviews/codex-r7-rework6-20261010-verdict.md
---
# 2号交付回执：codex 第四轮 2 条非阻塞小修（R-03 时钟固定 [low] + 注释精确化 [info]）

## 文件清单（2 文件，行级，无行为变更）

- `app/services/scene_result_report_service.py`：R-01 注释 2 行改写（删"≥~1ms 向上取整、<1ms 保持"
  与探针不符表述，改为"接近秒末时浮点/datetime 舍入已进位到下一秒，microsecond=0 救不回"，
  指向实际根因）。赋值行 `der.start_ns // 1_000_000_000` 未动。
- `tests/test_scene_result_report.py`：`test_reconcile_fractional_second_start_ns_starts_at_truncated_to_second`
  内时钟固定重构——首放前 `monkeypatch.setattr(_svc, "local_now", lambda: _T0)`（T0 取自真实
  `local_now()`，整秒/非整秒均可），同秒重放窗口复用同一 T0；跨秒窗口改为
  `_T0 + timedelta(seconds=1)`（不再 `_real_local_now() + 1s` 依赖真实墙钟）。
  `import app.services.scene_result_report_service as _svc` / `_real_local_now` 块从跨秒段
  上移至首放前，跨秒段只保留 `_local_now_plus_one` 函数体。

## 行为（逐条对应裁决）

- **R-03 [low]**：消除"同秒"重放窗口恰逢真实墙钟秒边界时实际跨秒的 flaky 风险（低概率）。
  首放与同秒重放共用同一时钟 T0，跨秒窗口显式推进 T0+1 秒——与 :1013 跨秒段原有
  patch local_now 写法对齐。两条断言（同秒零 UPDATE / 跨秒零 UPDATE）口径不变。
- **R-01 [info]**：注释精确化，无行为变更。

## 自测（wt-04a-r7，base `4697be0`）

- **定向**：`pytest tests/test_scene_result_report.py` **35 passed**（含重构用例）。
- **全量**：`pytest -q` **825 passed / 3 failed / 10 skipped**——3 failed =
  `test_devflow.py`（`test_external_sandbox_hides_home_and_only_binds_task_dirs` /
  `test_worker_resolves_codex_without_interactive_path` /
  `test_external_sandbox_binds_main_repo_git_for_worktree`），**与 main `4697be0` 基线同集**
  （rework-6 回执 09:29 已记同口径），非本次改动。
- **ruff**：`ruff check app/services/scene_result_report_service.py tests/test_scene_result_report.py`
  **All checks passed**。

## 边界（按派单）

- 连接语义 3 处文档表述协调者已自行纠正，本侧未动。
- OCR 不自跑（归协调者串行）、未合入、未自标 DONE、未起 MySQL。
- 全量 3 failed 与 OCR 仅覆盖服务文件的边界已记账（强模型增量复审包会附测试 diff）。

## 下一步

等协调者审核 `9e5455f` + 增量 OCR → 强模型增量复审 R2I-20261010-06（用户手动触发，附本裁决链）
→ 03/05/06 聚合 DONE → TASK-08。wt-04a-r7 冻结交付，本侧无在途进程。