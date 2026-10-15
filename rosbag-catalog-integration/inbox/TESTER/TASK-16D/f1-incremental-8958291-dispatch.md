# TESTER TASK-16D F1 增量验证单（协调者，2026-10-14 19:12 +08:00）

- 状态：TESTER_F1_INCREMENTAL_DISPATCHED。并入 TASK-16D attempt-1 同一验证链（不新开 attempt），A 叶 R1-3 F1 返修的独立行为面。
- owner：TESTER（专属 worktree `wt-tester-16d-20261014` + 严格 MySQL 8.4.11 隔离库 `rosbag-t16d-mysql`，已就绪）。
- 被测冻结 head：A 叶 `8958291222dbad8fbf61e7802510ddf83ecbbce1`（`wt-01-t16ca` / 分支 `a/task-16c-a-query-api`，续 `1489bc6`，仅 `app/services/bag_search_service.py` +18/−10）。协调者已机械核验全绿（祖先链/diff 逐行核/74 passed+1 seed 固有/独立 F1 不变量探针 8 断言 PASS），**本单是 A 叶接受的 TESTER 独立行为面门禁**，不采信协调者探针、由 TESTER 独立复现。
- 并行说明：本单与协调者 A 叶 R1-3 增量 OCR `f7899cfc`（`bag_search_service.py` 单文件，19:10 起跑）并行不冲突——OCR 审代码、TESTER 验行为，均只读 A 树冻结 head、不改业务。

## 验证范围（仅 F1 增量面，不重复 16D 已 PASS 的联合面）

1. **F1 单源一致性（核心，严格 MySQL 8.4.11 方言，非 SQLite 外推）**：构造夹具
   - `F1N1`：`dataset_type=nvidia_physicalai, bag_role=ORIGINAL, 有 scene_slice 用途, 非子包`（无 derivation）——F1 前会误命中 scene_original 的可达组合。
   - `F1N2`：`dataset_type=nvidia_physicalai, bag_role=ORIGINAL, 无 scene 用途, 非子包`。
   - `F1SB`：`dataset_type=self_built, bag_role=ORIGINAL, 双用途(scene_slice+self_built), 非子包`（双用途行为回归基线）。
   断言：
   - 筛 `data_kind=scene_original` 经 `/api/v1/bags`（入口一）与 `search_scene_bags`（入口二）**均不返回 F1N1/F1N2**；
   - 筛 `data_kind=self_built_original` 同样**不返回 F1N1/F1N2**；
   - 筛 `data_kind=nvidia_original` **返回 F1N1/F1N2**、不返回 F1SB；
   - **F1SB 双用途回归**：scene_original 与 self_built_original 两筛选**都命中 F1SB** 且各集合恰含 F1SB（R1-3 只加 NVIDIA 排除、不改双用途）；
   - 页面行内 `data_kind` 标签（`data_kind_context`）：F1N1/F1N2 仅渲染 `nvidia_original`、F1SB 渲染 `scene_original`+`self_built_original` 双标——**筛选命中集与展示标签单源一致**（C6 消除第二套真相的 TESTER 实证）。
2. **F3 文档零行为核**：`_parse_time` docstring 改动不改变谓词/比较语义——复用 16D 已有 `date end=23:59:59.999999` 探针结论即可，不重跑（仅确认本 head 无 `_parse_time` 行为 diff，diff 已核）。
3. **零越界核**：确认 `8958291` 相对 `1489bc6` 仅 `bag_search_service.py` 改动（git diff --stat 独立复核），`scene_result_query.py`/模板/tests 未动。
4. 夹具 `F1N1/F1N2/F1SB` 自造自清（purge 后 `left bags=0/deriv=0` 实证），只读探针 + 自清，不改 A 树/seed/业务实现。

## 交付口径

- 回执落 `test-receipts/TEST-TASK16D/attempt-1.md`（F1 增量段，被测 head `8958291`）：pytest/MySQL 探针断言结果 + 筛选/标签一致性证据 + 自清核 + 零越界核。
- **PASS 条件**：F1 单源一致性 6 类断言全过 + F1SB 双用途回归保持 + 零越界核通过。任一 FAIL 即报具体断言/DB 值，不静默。
- 本单 PASS 是 A 叶接受门禁之一（另一为协调者 R1-3 增量 OCR 零 CORRECTION）；A 叶接受后协调者重建固定集成候选（含 B `e399daf`+C `ce5921d`+新 A head `8958291`）再做 16D 最终联合验收 → 解除合入 HOLD。
- 时间：本单发生 2026-10-14 19:12 +08:00（协调者派单落盘）。