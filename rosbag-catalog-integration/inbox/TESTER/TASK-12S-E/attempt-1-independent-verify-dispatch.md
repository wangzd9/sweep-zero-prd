# TESTER TASK-12S-E attempt-1 独立验证派单（协调者，2026-10-14 23:44 +08:00）

- status: **TESTER_DISPATCHED**（A 交付冻结后例行独立验证；与协调者 OCR run 617b9375 并行不冲突——OCR 审代码、TESTER 验行为，均只读冻结 head）
- 任务：TASK-12S-E 接收/登记/绑定自动闭环，REQ-20 / AC-20.1 / AC-20.2（契约细节见 `inbox/1号/TASK-12S-E/attempt-1-dispatch.md` 与 A 回执 `inbox/1号/TASK-12S-E/receipts/TASK-12S-E/attempt-1.md`）
- **被测固定 SHA**：`b39a3ecc76da1f578d32f4e3c88a6ce989cf749d`（分支 `a/task-12s-e-auto-bind`，worktree `/home/wang/.local/state/rosbag-scene/wt-01-t12se`，base `16a154fff6f23e20b15498d1285a783713859647`）
- 变更面：4 文件（`app/services/pending_binding.py` 新增 / `app/services/scene_schedule_consumer.py` / `app/services/source_service.py` / `tests/test_task12se_auto_bind.py` 新增）

## 验证要求（A 回执自测段口径，重点独立项）

1. **MySQL 隔离库固定 SHA 重放**（A 机械用例为 SQLite）：两种先后（先提交/先登记）、交错并发、commit/响应丢失窗口、重启/重复扫描/重复提交/重复恢复；断言 source/run/attempt/分析版本/outbox 消费副作用及模型调用（桩计数）不重复增长——`scene_identity_key` 持久唯一键在 MySQL 方言下承载幂等。
2. **身份判定三档**：同快指纹父子重登记放行且归并同一 UID；同名跨根 ROOT_MISMATCH 不绑；歧义源 409 AMBIGUOUS_SOURCE 可追溯；切片路径保留 TASK-02 409。
3. **冲突隔离**：车辆冲突 → 既有 409 fail-closed ERROR:*；代次漂移 → GENERATION_DRIFT；资料不齐留痕待补，不制造成功绑定。
4. **回归**：incoming→ready 归并既有语义（12S-C）、旧自建/NVIDIA/坡道与派生保护必要回归；`PENDING_BINDING_RECONCILE=0` 时 consume 返回体与旧口径逐键相等（零活动无 pending_reconciled 键）。
5. **零越界核**：b39a3ec 相对 16a154f 仅上述 4 文件，未触 `app/api/ingest_submissions.py`、models、迁移、算法、UI、部署。

## 边界

- 只读被测 worktree（.venv 未跟踪）；不烧模型、不重放生产 1012 三包（既有证据复用 REPORT.md binding-repair）、不碰生产/处理机；发现失败项出 RED 证据交协调者回派 A 最小返修。
- 交付回执：`test-receipts/TASK-12S-E/attempt-1.md`（含命令、退出码、关键断言原文、未执行项）+ TESTER 事件。
- PASS 是 E 接受门禁之一（另一为协调者 OCR run 617b9375 零 CORRECTION 级裁决）。