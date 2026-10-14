# 派单：t10-defect2-storage-offset —— 06B 域 derive_storage_offset 真实 rosbag2 jitter 口径（TASK-10 缺口 #2 最小返修，优先）

- status: ACKED
- 派单时间：2026-10-12 00:0x +08:00（协调者 cron poll 00:00:53 回合）
- 任务：TASK-10 端到端闭环缺口 #2（2号取证单 `receipts/TASK-10/attempt-1.md` 定位，协调者独立核验属实）
- owner：2号（B；06B 发布链原 owner，TASK-10 取证单交付冻结后转本单；#1 由 1号并行，两单文件集无冲突）
- base：main `ca8730d`（= origin/main，2026-10-12 00:0x rev-parse 双核）
- worktree：按先例新建（如 `wt-04a-t10def2`，.venv 软链主仓）

## 一、缺陷事实（协调者已核，不重查）

- `app/services/scene_publish_service.py:77-114` `derive_storage_offset`：basis=header_stamp_ns 时要求**逐帧 (storage_ns − header_ns) bit 恒定**，`len(offsets)!=1 → None`。
- 实测全部 7 条真实 slope 袋 **NOT_CONSTANT**（row19 54 帧 54 种偏移 71.9–187.6ms=rosbag2 写入抖动，本质永不恒定）→ `derive=None` → **PUBLISH_BLOCKED**：真实坡道切片能识别但无法发布，P0 硬阻塞（2号 E2E 步骤 4 实测卡点）。

## 二、范围（最小修复，不扩）

1. **放宽口径**：bit 恒定 → **众数/中位数 offset + 有界容差**（容差取值需实测依据：7 袋全量偏移分布自证，同方向抖动带内一致才返回 offset）。
2. **fail-closed 语义保持**：仍不可判定（mixed basis/解码失败/容差内占比不足/无证据）→ 返回 None，不得当 0、不得猜测。
3. **真实样本自证**：用 `/mnt/nas_backup/data_slice/1165414093/slope/` 7 条袋（只读）逐袋复验 derive 结果（期望=全部可推导且 offset 稳定；记录每袋 offset+抖动带）。
4. 下游一致性：writer 切包用该 offset 后，切片时间映射/证据口径与 04B manifest（header 域）保持自洽（如影响 `SlicePublishSpec`/publish 路径字段，同 commit 最小接线+测试）。
5. 测试：SQLite 定向（常量偏移袋=精确返回 / jitter 袋=众数+容差返回 / 超容差=None / mixed=None / 解码失败=None）+ 真实 7 袋复验证据 + 全量（`--ignore=tests/test_devflow.py`）+ruff。

## 三、AC（验收口径）

- 真实 row19（及全 7 袋）`derive_storage_offset` 返回非 None 稳定 offset；E2E 步骤 4 发布不再因 offset BLOCKED（协调者合入后安排 `scratch/t10_e2e.py` 复跑，VLM ≤1 袋预算）。
- 负例仍 fail-closed（不可判定=None 用例全绿）；零越界（diff 范围=scene_publish_service+publish 接线+测试）。
- 回执 `receipts/TASK-06B/t10-defect2-storage-offset.md`（REVIEW_PENDING）。

## 四、边界

- 不改 03B（#1 在 1号）、不改 04B 适配器判定语义（只消费 offset）；NAS 只读；不重启 VLM 服务；发现跨模块依赖→记录回派不自行扩。

## 五、停止条件

交付 commit（单 commit 或最小集）+ 7 袋复验证据 + 自测全绿 + 回执落盘 → REVIEW_PENDING 冻结等协调者核验+OCR+合入。
