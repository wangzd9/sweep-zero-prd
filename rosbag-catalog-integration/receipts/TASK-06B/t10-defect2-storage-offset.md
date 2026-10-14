# 回执：t10-defect2-storage-offset —— 06B 域 derive_storage_offset 真实 rosbag2 jitter 口径（TASK-10 缺口 #2 最小返修）

- owner：2号（B）
- task/attempt：TASK-10 缺口 #2 / t10-defect2-storage-offset（最小返修单，优先）
- base：main `ca8730d`（= origin/main，00:09 ACK 时 rev-parse 双核一致实测）
- head：**`d4719f6`**（分支 `scene/task-06b-t10-defect2-storage-offset`，worktree `wt-04a-t10d2`）
- 交付时间：2026-10-12 00:0x +08:00
- 交付状态：**REVIEW_PENDING（交付冻结，等协调者机械核验+串行 OCR+合入）**

## 一、行为（本单最小改动）

`app/services/scene_publish_service.py::derive_storage_offset` header 域→存储域 offset 推导口径放宽：

- **旧**：要求逐帧 `(storage_ns − header_ns)` **bit 恒定**（`len(set(offsets))==1`）才返回，否则 `None`。
- **新**：bit 恒定 → 直接返回（保留确定性 fixture 原精确语义）；非常定 → 取**中位数 offset + 有界抖动容差**：
  - 偏移在 `中位数 ± STORAGE_OFFSET_JITTER_TOL_NS(=100ms)` 内占比 ≥ `STORAGE_OFFSET_MIN_COVERAGE(=0.9)` → 返回**最接近中位数的实际观测值**（真实数据点，不当猜测）；
  - 占比不足（偏移真正分散）→ `None`（**fail-closed 语义保持**：mixed basis/解码失败/topic 缺失/证据缺失/占比不足仍返回 None，不当 0）。
- 契约签名 `int | None` 不变；下游 `writer.slice_bag_to_staging(storage_offset_ns)` 消费口径不变（存储轴过滤窗口 `[start+off, end+off]` 与校验界同基准自洽，恒通过，无需改 writer）。
- **零越界**：diff 范围 = `scene_publish_service.py` + `tests/test_scene_result_report.py`（2 文件 +82/−12）；未改 03B（#1 在 1号）、未改 04B 判定语义、NAS 只读、未重启 VLM。

## 二、容差取值的实测依据（dispatch §二.1「需实测依据」）

对 `/mnt/nas_backup/data_slice/1165414093/slope/` 7 条真实袋逐帧解码 `/bev/cam_front_8m_jpg`，统计 `(storage−header)` 偏移分布（脚本+证据 `scratch/t10d2/b_t10d2_probe2.py` / `scratch/t10d2/b_t10d2_probe2.out`）：

| 袋 | 帧数 | 偏移带(ms) | 相对中位数最大偏差(ms) | ±100ms 占比 |
|---|---|---|---|---|
| 105105_105120 (row19) | 54 | 71.9–187.6 | 86.5 | 1.0 |
| 105117_105132 | 55 | 71.1–175.1 | 76.2 | 1.0 |
| 105129_105148 | 82 | 59.6–141.5 | 68.2 | 1.0 |
| 105541_105556 | 66 | 62.3–120.2 | 44.3 | 1.0 |
| 105553_105608 | 67 | 61.7–120.2 | 44.9 | 1.0 |
| 105605_105620 | 67 | 61.2–103.2 | 30.7 | 1.0 |
| 105617_105632 | 68 | 60.1–121.8 | 48.6 | 1.0 |

- 相对中位数最大偏差 30.7–86.5ms（row19 最大 86.5ms）→ `TOL=100ms` 覆盖全部真实抖动带且留裕量。
- 全部袋 unique_offsets=帧数（永不 bit 恒定，坐实旧假设与真实数据冲突）；`±100ms` 占比 7 袋全 1.0、`±50ms` 0.951–1.0 → `MIN_COVERAGE=0.9` 在真实数据下充分通过、在偏移真分散时仍 fail-closed。

## 三、关键断言（AC 核验）

- **真实 row19 + 全 7 袋 `derive_storage_offset` 返回非 None 稳定 offset**（复验脚本 `scratch/t10d2/b_t10d2_reverify.py`，证据 `scratch/t10d2/b_t10d2_reverify.out`）：
  - row19 → `100.382ms`（中位 101.036ms，最接近中位数真实观测值）；
  - 7/7 `derive_ok=True`（修复前 7/7 = `None` → `PUBLISH_BLOCKED`）；每袋 offset 均在 `中位数±100ms` 内、为真实数据点。
  - **E2E 步骤 4 发布不再因 offset BLOCKED**（协调者合入后安排 `scratch/t10_e2e.py` 复跑，VLM ≤1 袋预算）。
- **负例仍 fail-closed**：`test_scattered_beyond_tolerance_blocks`（两帧差 1s=真分散）/`test_jitter_mostly_out_of_band_blocks`（占比<0.9）/`test_corrupt_frame_blocks`/`test_mixed_basis_blocks`/`test_missing_camera_topic_blocks` 全绿。

## 四、文件清单（diff 2 文件）

- `app/services/scene_publish_service.py`（+45/−…：新增 `STORAGE_OFFSET_JITTER_TOL_NS`/`STORAGE_OFFSET_MIN_COVERAGE` 常量+实测依据注释、`import statistics`、`derive_storage_offset` header 分支中位数+容差、模块/函数 docstring 同步）
- `tests/test_scene_result_report.py`（`test_non_constant_offset_blocks`→`test_scattered_beyond_tolerance_blocks` 语义重命名+新增 `test_jitter_within_tolerance_returns_stable_offset`/`test_jitter_mostly_out_of_band_blocks`）

## 五、命令 / 退出码 / 环境

- 定向：`.venv/bin/python -m pytest tests/test_scene_result_report.py tests/test_scene_result_storage.py tests/test_slope_vlm_wiring.py tests/test_slope_adapter.py` → **106 passed**（原 104 + 2 新抖动用例）RC=0（5.42s，SQLite 口径）
- 全量：`.venv/bin/python -m pytest --ignore=tests/test_devflow.py` → **815 passed / 10 skipped** RC=0（55.94s；基线 813 + 2 新，10 skipped=MySQL 独占容器用例非本单范围）
- ruff：`.venv/bin/ruff check app/services/scene_publish_service.py tests/test_scene_result_report.py` → **All checks passed** RC=0
- 7 袋复验：`.venv/bin/python ~/.hermes/cache/scratch/b_t10d2_reverify.py`（已固化项目 `scratch/t10d2/b_t10d2_reverify.py`）→ **7/7 derive_ok**（只读 NAS，无 VLM/无容器/无 DB）
- 环境：worktree `wt-04a-t10d2`（base `ca8730d`，.venv 软链主仓）；SQLite 定向/全量；**未跑 MySQL 隔离库**（本单 0 数据库语义改动，`derive_storage_offset` 纯读 bag+计算，无 ORM/迁移面）；NAS 只读、无 VLM 调用（offset 推导只解码 header，不触发模型）。

## 六、未执行项 / 风险如实申报

- **E2E 端到端复跑未执行**（dispatch AC 明确「协调者合入后安排 `scratch/t10_e2e.py` 复跑，VLM ≤1 袋预算」）——本单交付=offset 推导口径修复+真实 7 袋复验证明 derive 非 None；完整 E2E（步骤 4 发布+步骤 5 API 获取+子包登记）依赖 #1（1号 source_ready）+本单**双双合入后**由协调者统一复跑，非本单能力/意愿缺口。
- 未跑 MySQL 隔离库（0 数据库语义改动，纯 bag 读+计算）；未跑全量 813 之外的 devflow 沙箱（环境性 skip 先例口径）。
- **下游一致性（dispatch §二.4）**：writer `slice_bag_to_staging` 以单一 offset 平移 header 边界到存储轴，过滤窗口与校验界同基准（`_validate_slice` bounds=(lo,hi)=写入窗口），故中位数 offset 不引入校验回归；真实抖动带宽（≤86.5ms）相对切片时长（row19 ≈14.4s）可忽略，边界帧无丢失风险。**04B manifest（header 域）自洽保持**（offset 只用于存储轴过滤，不改 header 域段边界/证据口径）。无跨模块接线需改。
- offset 取「最接近中位数的实际观测值」而非中位数本身（中位数可能非整数观测点）：保证返回值是真实数据点、跨帧稳定、可复现；对 writer 平移窗口无实质差异（偏差 < 半帧抖动）。

## 七、越界申报

- **零越界**：未改 03B（#1 1号域）、未改 04B 适配器判定语义（仅消费 offset）、未改 writer 过滤/校验语义、NAS 只读、未重启/未调用 VLM、未动生产/共享 8 容器栈。diff 严格 = `scene_publish_service.py` + `tests/test_scene_result_report.py`。

## 八、交付冻结

commit `d4719f6`（base `ca8730d`）已冻结，不重复自测。等协调者：机械核验（rev-parse 双核/逐行 diff/独立复跑 106+815+ruff/7 袋复验证据复核）→ 串行 OCR（app 1 文件 `scene_publish_service.py`，§3.6 尺寸预检）→ 验收合入（--no-ff，推 origin）→ 与 #1 一并 `scratch/t10_e2e.py` 复跑全绿 → **TASK-10 DONE → P0 收口**。