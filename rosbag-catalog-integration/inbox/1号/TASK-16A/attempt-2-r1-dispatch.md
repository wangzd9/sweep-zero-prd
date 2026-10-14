# TASK-16A attempt-2-r1 最小返修单（协调者 r116 派发，2026-10-13 03:4x）

- **角色/owner**：执行者 A（1号）｜**attempt**：attempt-2-r1（OCR 收口后合并返修，沿 07B r102 先例）
- **固定 base**：`c30f048`（你 attempt-1 交付冻结 HEAD，`wt-01-t16a` 续 commit；禁止 rebase/reset，新 commit 1 笔收口）
- **范围**：仅以下 6 项，全部 low/2 行量级；**零新表、零新迁移文件、零新依赖、不碰 07B 冻结文件、不碰 `app/scanner/clients.py`（medium 已裁决非 AC 违例，随合入备注）**
- **AC**（对应 OCR 批次账 `reviews/TASK-16/16A-16B-ocr-batches.md` r112/r115/r116b）：
  1. **R1-1（runner.py M2，bug·medium）**：`_scene_context()` 的启用条件由 `settings.scene_roots_configured()` 改为显式要求 `settings.scene_nas_scan_root and settings.scene_nas_ready_root`（scanner 实际只消费这两根），部分配置 fail closed 返回 None；补 1 条定向测试（只设 `SCENE_SLICE_PUBLISH_ROOT` 时 scanner 不建场景根上下文）。
  2. **R1-2（runner.py L1，low）**：`_recover_moves` 恢复路径 cross-check `marker["root_id"]` vs `ctx.root_id`：缺失=旧 journal 兼容放行；矛盾=记 failed 跳过该条不 KeyError、不静默吞；字段保留（重启保持快照口径，DESIGN §1.5/§7.3.1）。
  3. **R1-3（ingest_service.py L1，low，r116b 新裁决 CORRECTION）**：`list_profiles` 不再默认继承 self_built-only 过滤——显式传 all-roots 口径使 scene 入口出现在 `GET /api/v1/ingest-profiles`（DESIGN.md:157 返回字段已含 `intake_root_id`）；**匹配路径 `_active_profiles(db, root_id)` 跨根隔离语义不动**（补 1 条定向测试：scene 入口 list 可见 + 匹配仍按 root 隔离）。
  4. **R1-4（scene_intake.py L1+L2，low）**：`incoming_path` 参数 docstring 显式注 reserved（不影响 root 派生）；补文件尾换行。
  5. **R1-5（迁移 `20261013_01_scene_intake.py`，low）**：补文件尾换行（无逻辑改动）。
  6. **R1-6（可选卫生）**：无其他；R7-M1（CLI 出口码）已裁决 OUT_OF_SCOPE 不改。
- **自测要求**：定向新增/变更用例 + 16A 既有定向 25 passed 口径复跑 + `ruff` + `alembic heads` 单头 + 全量 SQLite 口径（web 性能计时 1 failed=base 复现环境性，如实申报即可）。
- **停止条件**：6 项完成+自测全绿即交付冻结 REVIEW_PENDING（回执 `receipts/TASK-16A/attempt-2-r1.md`）；发现任何项需扩面（>2 行/新文件/语义变化）立即停并回报协调者，不自行扩。
- **后续**：机械核验 → 增量 OCR（`--from c30f048 --to <你的新HEAD>`）→ 合入（07B 整链先合入后 16A 迁移 rebase 双头，协调者执行）→ TESTER 16D 前独立验证。
- **注意**：16B OCR 仍在途（协调者串行，不占你）；你交付后等 OCR 增量收口，不自行合入。