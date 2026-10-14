# 派单：TASK-06B / attempt-1-r2-final-fixture（测试夹具 uid 超长最小修复）

- status: REVIEW_PENDING（2号 18:41 ACK；18:51 交付 commit 6ee858b，回执 receipts/TASK-06B/attempt-1-r2-final-fixture.md）
- 下达：协调者 2026-10-10 18:24
- 依据：TESTER 终测报告 `test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-1.md` §缺陷2（中低，测试夹具，非应用代码）。

## 基线

- base：**main 74ba3bf**（wt-04a 在 86b2cc1，开工前 merge 到 main 74ba3bf）
- worktree：`/home/wang/.local/state/rosbag-scene/wt-04a`
- 文件范围：仅 `tests/test_scene_result_report.py`（该文件 owner=你）；**不改任何 app 代码**。

## 问题与根因（测试者实测）

- `_parent(db, tag)` 生成 uid = `T06B{tag}-{uuid.hex[:12]}`；`tag='gate-other'`（10 字符）/`'multi-scene'`（11）→ uid 27/28 字符，越出 `bag_record.bag_uid VARCHAR(26)`：
  - MySQL strict 模式：setup 阶段 1406 Data too long 拒绝（`test_identity_gates`、`test_multi_scene_run_partial_complete_does_not_deadlock` 直接败于 setup）；
  - `test_reconcile_backfills_after_publish_without_report`：uid 被截断落库后，ORM 幂等二次调用按内存 27 字符值 update 0 行 → StaleDataError（应用 reconcile 逻辑本身 MySQL 成立，首调 200 证据在报告 §S6/总账）。
- SQLite 静默截断掩盖此问题，本地 823 全绿不反映该缺陷。

## 修复范围（最小，单一 commit）

- `_parent` uid 生成收敛到 **≤26 字符**：对 tag 截断/缩短 hex 均可，但须保证同库内 uid 唯一性不劣化（uuid 部分至少保留可区分长度）；在 `_parent` 内加 `assert len(uid) <= 26` 防再越界。
- 核对同文件所有 uid 生成点（`_child_uid` 等）确认均 ≤26（测试者已确认 `_child_uid` 19 字符安全，无需改）。
- 不改测试断言语义、不删用例；三用例在 SQLite 下保持原逻辑跑通。

## 验收（AC）

- AC1：该文件全部 uid 生成点输出 ≤26 字符（含 assert 防护）。
- AC2：`test_identity_gates` / `test_multi_scene_run_partial_complete_does_not_deadlock` / `test_reconcile_backfills_after_publish_without_report` 三用例 SQLite 定向 PASS；真实 MySQL 8.4 复测由 TESTER 随 1号 S1 修复的新 attempt 一并验证（你侧不需起 MySQL）。
- AC3：全量 SQLite 基线不回归（823 passed 口径）+ ruff 绿。

## 停止条件与交付

- 单 commit 交付 + 回执 `receipts/TASK-06B/attempt-1-r2-final-fixture.md`（REVIEW_PENDING，含 diff/命令/RC/AC 对照）；**不跑 OCR、不合入 main**。
- 与 1号 attempt-5-r2-final-s1 文件无重叠（迁移链 vs 06B 测试文件），可并行；两笔交付后由协调者统一 OCR/合入/复测排程。