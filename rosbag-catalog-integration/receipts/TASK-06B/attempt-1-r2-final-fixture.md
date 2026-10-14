---
task: TASK-06B
item: attempt-1-r2-final-fixture
owner: 2号（执行者B）
status: REVIEW_PENDING
base: wt-04a 86b2cc1（main 74ba3bf 之上无新提交，86b2cc1 为其祖先，直接续任务分支 scene/task-06b-r2-rework）
output_commit: 6ee858b
branch: scene/task-06b-r2-rework
worktree: /home/wang/.local/state/rosbag-scene/wt-04a
delivered_at: 2026-10-10 18:50 +08:00
---
# 回执：attempt-1-r2-final-fixture（测试夹具 uid ≤26 字符最小修复）

## 派单
`inbox/2号/TASK-06B/attempt-1-r2-final-fixture-fix.md`（协调者 18:24 下达，ACK 18:41）

## 改动（单 commit `6ee858b`，1 文件 +4/-1）
仅 `tests/test_scene_result_report.py`（不改任何 app 代码）：
- `_parent(db, tag)`：uid 生成 `T06B{tag}-{hex[:12]}` → `T06B{tag}-{hex[:10]}`；最长 tag `multi-scene`(11) 下 uid=4+11+1+10=**26** 字符，不越 `bag_record.bag_uid VARCHAR(26)`。
- 同函数内新增 `assert len(uid) <= 26`（带 len/tag 诊断）防再越界。
- 唯一性：hex 保留 10 位（40bit），同库内碰撞概率不劣于原 12 位的量级可接受（每测试独立 db 且 tag 区分，无退化）。
- 核对同文件其余 uid 生成点：`_child_uid`=`T06Bc-{hex13}`=19 字符、`test_r6_m2` 内联 `T06Br6m2-{hex12}`=21 字符，**均 ≤26，无需改**（与测试者确认一致）。
- 未改任何测试断言语义、未删用例。

## diff 要点
```diff
 def _parent(db, tag: str, *, generation: int = 1) -> BagRecord:
-    uid = f"{T06B}{tag}-{uuid.uuid4().hex[:12]}"
+    # uid 必须 ≤26 字符（bag_record.bag_uid VARCHAR(26)）：4+tag(≤11)+1+hex(10)=26；
+    # hex 保留 10 位（40bit）防同库内碰撞。SQLite 静默截断曾掩盖该约束，MySQL strict 下超长直接 1406。
+    uid = f"{T06B}{tag}-{uuid.uuid4().hex[:10]}"
+    assert len(uid) <= 26, f"bag_uid 越出 VARCHAR(26)：len={len(uid)} tag={tag!r}"
```

## 验证（环境：wt-04a `.venv` python3.10，SQLite，无 MySQL）
- 定向：`.venv/bin/python -m pytest tests/test_scene_result_report.py -q` → **31 passed**（RC 0）
  - 含三 AC 用例：`test_identity_gates` / `test_multi_scene_run_partial_complete_does_not_deadlock` / `test_reconcile_backfills_after_publish_without_report`
- 全量：`.venv/bin/python -m pytest tests -q --ignore=tests/test_r2_repro.py` → **811 passed, 3 failed, 10 skipped**
  - 3 failed = `tests/test_devflow.py` 沙箱环境性（test_external_sandbox_hides_home_and_only_binds_task_dirs / test_worker_resolves_codex_without_interactive_path / test_external_sandbox_binds_main_repo_git_for_worktree），**与 main 74ba3bf 基线同集**（sessions 记录 823 passed 口径下亦为同 3 failed）；10 skipped = MySQL 独占容器用例；`test_r2_repro.py` 需 `/tmp/r2-review-*` 隔离库，按基线惯例排除。
- lint：`.venv/bin/python -m ruff check tests/test_scene_result_report.py` → **All checks passed**

## AC 对照
- AC1 ✅ 该文件全部 uid 生成点 ≤26（`_parent` 修复+assert；`_child_uid`/r6m2 已核安全）。
- AC2 ✅ SQLite 定向三用例 PASS；**真实 MySQL 8.4 复测未执行**（按派单随 1号 S1 修复的新 attempt 由 TESTER 一并验证，本侧不起 MySQL）。
- AC3 ✅ 全量 SQLite 无回归（同基线 3 环境性 failed）+ ruff 绿。

## 未执行项 / 越界申报
- 未跑 OCR、未合入 main（按停止条件）；未改 app 代码；无越界。
- 与 1号 attempt-5-r2-final-s1 文件无重叠，可并行；两笔交付后由协调者统一 OCR/合入/复测排程。