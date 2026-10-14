# 交付回执：t10-defect3-publish-bounds（TASK-10 / r1）

- status: REVIEW_PENDING
- 交付时间: 2026-10-12 01:46 +08:00
- owner: cron-b-poll-6f7471d8747c-20261012-013253（执行者 B，前端功能开发群）
- base: `a77aa45`（= origin/main，含 #1 `277e40f` + #2 `d4719f6`；ACK 时 fetch 双核一致）
- head: `0943885`（`0943885753b8aa32b4d1147d693295894574b24f`）
- 分支/worktree: `scene/task-10-defect3-publish-bounds` @ `wt-04a-t10d3`

## 一、文件清单（3 文件 +166/-11，逐文件行为）

1. `app/services/scene_publish_service.py`（+10）
   - `SlicePublishSpec` 增加 `actual_start_ns: int | None`、`actual_end_ns: int | None`（默认 None，向后兼容旧调用方）；
   - `_write_slice_manifest` 把这对存储域实际边界随 `slice_manifest.json` 落位（字符串口径与现有 start_ns/end_ns 一致；None 落 null）。
2. `app/services/scene_result_report_service.py`（+36/-10）
   - `_verify_published_files` 区间身份复核改读记录 `actual_start_ns/actual_end_ns` 作 lo/hi（原误用 header 域 start_ns/end_ns，offset≠0 时与 db3 存储轴消息基准不一致 → 真包必 409）；
   - **fail-closed**：记录缺 `actual_start_ns` 或 `actual_end_ns`（旧发布物/旧调用方未落）→ 409 `INCOMPLETE: …发布记录缺存储域实际边界…（旧发布物无法证明区间身份，不得放行）`，不回退 header 边界；
   - docstring 与实现对齐（区间身份口径改写）。
3. `tests/test_scene_result_report.py`（+131）
   - 既有真实链助手 `_stage_and_publish` 与 `_spec` 同步补 `actual_start_ns/actual_end_ns=result.*`（writer 同源，保持既有 complete/reconcile 用例语义不弱化）；
   - 新增 `TestT10Defect3PublishBounds` 两条定向断言（派单 AC 1）：
     - `test_offset_nonzero_complete_scene_available`：恒定 offset=150ms 自构造 CompressedImage bag → `derive_storage_offset`==150ms → 04B writer 存储域切片（断言 actual 边界 ≠ header 边界，暴露面成立）→ 06B 原子发布（记录落 actual 边界）→ `/results` 200 → `/complete-scene` **200**，outcome SUCCESS、available_children 命中、DB availability=AVAILABLE；
     - `test_old_record_missing_actual_bounds_fails_closed`：同一链但 spec 不落 actual 边界（模拟旧发布物）→ `/complete-scene` **409**，detail 含"缺存储域实际边界"，子包不推进 AVAILABLE；
   - fixture 全部仓库内自构造（`tests/scene_fixture.build_single_db3` 真实 ROS2 CDR 封装），未用真实袋。

## 二、行为（修复口径逐条对应）

- 派单 §二.1：per-slice 记录补存储域实际边界（writer `SliceWriteResult.actual_start_ns/actual_end_ns` 同源，manifest 落位）✅；
- 派单 §二.2：`_verify_published_files` 改用记录存储域边界 + 缺字段 fail-closed 409、不回退 header 边界 ✅；
- 派单 §二.3：offset≠0 发布→`/results`→`/complete-scene` 200 可置 AVAILABLE + 旧记录 409 两断言 ✅；
- 派单 §二.4：未弱化 writer 校验、未删既有断言、`derive_storage_offset` fail-closed 语义保持（writer 文件 0 改动）✅；
- 禁碰面核实：`source_service.py`/`app/scene/slope/writer.py`/04B/05 域 0 改动（`git diff a77aa45..HEAD --stat` 仅 3 文件）✅。

## 三、验证证据（命令 / 退出码 / 环境）

环境：`wt-04a-t10d3`，`.venv`（python 3.10，软链主仓），SQLite 本地测试栈（`tests/conftest.py` 临时库，sessionfinish 清理，0 残留）。

| 命令 | 结果 |
|---|---|
| `.venv/bin/python -m pytest tests/test_scene_result_report.py -k "TestT10Defect3PublishBounds" -x -q` | **2 passed**（1.75s） |
| `.venv/bin/python -m pytest tests/test_scene_result_report.py -q` | **39 passed**（4.24s） |
| `.venv/bin/ruff check app/services/scene_publish_service.py app/services/scene_result_report_service.py tests/test_scene_result_report.py` | **All checks passed!** |
| `.venv/bin/python -m pytest tests/ -q -k "scene"` | **204 passed, 652 deselected**（12.40s，scene 面回归全绿） |

关键断言：offset≠0 全链 200 置 AVAILABLE（非仅记录字段存在性——走 `/complete-scene` 正式 API 复核路径）；旧记录 409 fail-closed 且 detail 明示"不得放行"。

## 四、未执行项 / 越界申报

- **未执行**：真实袋 E2E 复跑（`scratch/t10_e2e_reverify.py`，VLM ≤1 袋）——按 AC 3 属 TESTER/协调者链路，非本单自测范围；
- **未执行**：OCR、合入 main——协调者门禁，本侧不介入；
- **越界申报（重要）**：E2E 驱动 `scratch/t10_e2e_reverify.py:336-339`（协调者 harness 面）构造 `SlicePublishSpec` 时**未带 `actual_start_ns/actual_end_ns`**——复跑 v2 前须补 `actual_start_ns=res.actual_start_ns, actual_end_ns=res.actual_end_ns`（该处已有 `res` 变量），否则按本修复 fail-closed 语义 E2E 将 409（属预期拦截，非修复未生效）。本单禁碰面不含 scratch/，未代为修改，在此明确申报供复跑前处理；
- 同根因两轮：本单为 r1，无返修历史。

## 五、状态

交付冻结，**REVIEW_PENDING**，等协调者机械核验 → 串行 OCR → 合入 → TESTER E2E 复跑 v2。