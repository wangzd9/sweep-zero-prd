# 裁决：t10-defect2-storage-offset（`d4719f6`）验收——ACCEPT_MERGED

- 时间：2026-10-12 00:5x +08:00
- 角色：协调者（cron poll 14ae4556629a）
- 交付：2号 `wt-04a-t10d2`@`scene/task-06b-t10-defect2-storage-offset`，commit `d4719f6`（base `ca8730d`）
- 状态：**ACCEPT_MERGED**（--no-ff 合入 main `a77aa45`，推 origin 277e40f..a77aa45，rev-parse 双核一致）

## 机械核验（协调者独立复跑，非信任回执）

- **base/head**：`git merge-base --is-ancestor ca8730d d4719f6` = base_ok；HEAD `d4719f6` 与回执一致。
- **diff 范围**：2 文件 +82/−12 = `app/services/scene_publish_service.py`（+45）+ `tests/test_scene_result_report.py`（+49）。**零越界**（未碰 03B/#1 域、04B 判定语义、writer 过滤/校验语义、NAS、VLM、生产容器）。
- **语义核对**：`derive_storage_offset` header 分支——bit 恒定保留原精确语义直返；非常定取中位数+`STORAGE_OFFSET_JITTER_TOL_NS(100ms)` 容差，`in_band/len ≥ STORAGE_OFFSET_MIN_COVERAGE(0.9)` 才返回**最接近中位数实际观测值**（真实数据点，非中位数本身非猜测）；占比不足/mixed/解码失败/topic 缺失仍 `None`（**fail-closed 保持**，不当 0）。契约签名 `int|None` 不变、writer 消费口径不变（同基准自洽，无需改）。
- **容差取值实测依据**（dispatch §二.1 要求）：回执 §二 7 条真实 slope 袋逐帧偏移分布表（脚本+证据 `scratch/t10d2/b_t10d2_probe2.py/.out`）——相对中位数最大偏差 30.7–86.5ms（row19=86.5ms），±100ms 占比 7 袋全 1.0 → TOL=100ms 覆盖全带留裕量；MIN_COVERAGE=0.9 真实数据下充分通过、真分散时仍 fail-closed。
- **独立复跑（worktree 内实测 RC=0）**：定向 `tests/test_scene_result_report.py test_scene_result_storage.py test_slope_vlm_wiring.py test_slope_adapter.py` → **106 passed**；ruff 2 文件 → All checks passed。
- **7 袋复验证据复核**：`scratch/t10d2/b_t10d2_reverify.out` = `derive_ok all: True (7/7)`，row19 → 100.382ms（中位 101.036ms），每袋 offset 为中位数±100ms 内真实数据点。修复前 7/7=None→PUBLISH_BLOCKED 已坐实解除。
- **OCR**：T10D2-r1 独立批次（`reviews/TASK-06B/t10-defect2-storage-offset/ocr-batches.md`）入选 1 文件 `scene_publish_service.py`（303L<500 单批，tests default_path 排除）→ **0 findings**（session `94c9673e`，EXIT=0，120s）。
- **合入后 sanity（main `a77aa45`）**：alembic 单头 `20261009_02_ingest_frozen` / ruff 2 文件 All checks passed / 定向 `test_scene_result_report.py + test_t10def1_source_ready.py` **42 passed** RC=0。

## 强审查门禁

- **NOT_REQUIRED**：单文件 45 行行为面改动（offset 推导口径），fail-closed 语义保持、无 DDL/迁移/并发/安全面，符合弱模型 OCR 已覆盖 + 独立复跑全绿 + 7 袋真实数据复验的先例口径。不自动增加实现前/功能前强审查。

## 未执行项（非本单能力缺口，如实申报）

- **E2E 端到端复跑**：依赖 #1（`277e40f`）+本单（`a77aa45`）双双合入后由协调者统一驱动，非开发单范围。已派测试者 `inbox/TESTER/TASK-10/e2e-reverify-after-merges-dispatch.md`（被测快照 main `a77aa45`，row19 VLM ≤1 袋）。
- 未跑 MySQL 隔离库：本单 0 数据库语义改动（`derive_storage_offset` 纯读 bag+计算，无 ORM/迁移面），回执 §五 如实申报。

## 结论

- **ACCEPT_MERGED** → main `a77aa45`。TASK-10 缺口 #2 已收口，**剩 E2E 复跑全绿即 TASK-10 DONE→P0 收口**。