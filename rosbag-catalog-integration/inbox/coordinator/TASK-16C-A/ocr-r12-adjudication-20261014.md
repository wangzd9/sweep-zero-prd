# TASK-16C-A R1-2 增量 OCR 收口裁决（协调者，2026-10-14 18:55 +08:00）

## 运行身份
- run `66ca40d3`（`reviews/TASK-16C-A/ocr-run-20261014-r12`），base `bd0db1d2..1489bc6`，v1.13.0，provider vllm-local / qwen3.8-27b-fp8。
- **实际 2 批**（spec 为准，纠正 18:03 记账口径「单批」）：b01 `app/services/bag_search_service.py`（18:34 收口 REVIEW_COMPLETE，rc=0，coverage 1/1，batch_identity_matches=true）；b02 `app/services/scene_result_query.py`（18:34 起跑，本裁决时点仍 RUNNING）。b01/b02 互斥排除，tests 排除归 TESTER 16D。
- 注：b01 运行于 A 专属树 `wt-01-t16ca`，不含 B 叶 `bags.html` 改动（见 F2）。

## b01 findings 逐项裁决（协调者独立核 `29bd1f4` 集成树 + A 树 + seed，非采信 OCR 文本）

### F1（line 86，category=bug，severity=medium）— **CONFIRMED（防御性，须最小返修）**
- OCR 主张：`scene_original`/`self_built_original` SQL 谓词缺 NVIDIA 排除，与 Python 标签侧（`data_kind_context` 先判 `dataset_type==nvidia_physicalai` 即 `nvidia_original`、elif 链互斥）及顶部单源优先级注释（1)子包→2)NVIDIA→3)场景→4)自建）不一致。
- 独立核实：
  - 谓词面（`29bd1f4`/`1489bc6` 同）：`nvidia_original = and_(dataset_type==nvidia, ~_scene_slice_pred())`；`scene_original = and_(ORIGINAL, ~_scene_slice_pred(), _scene_basis_pred())`（**无 NVIDIA 排除**）；`self_built_original = and_(ORIGINAL, ~_scene_slice_pred(), or_(dataset_type==self_built, ~_scene_basis_pred()))`（**无 NVIDIA 排除**）。
  - 可达性：`create_scene_run` 仅校验 `bag_role in (None, ORIGINAL)` + `source_status==READY`，**不校验 dataset_type**；`_ensure_purpose_association` 给该 ORIGINAL 包挂 `scene_slice` 用途。故存在 `dataset_type=nvidia_physicalai, bag_role=ORIGINAL, 有 scene_slice 用途, 非子包` 的合法组合（迁移回填既有 NVIDIA 行为 NOT_APPLICABLE 非模型级约束，新造数不受限）。
  - 矛盾实证：该组合行 SQL 筛选 `scene_original` **命中**（ORIGINAL+~slice+scene_basis 全真），Python `data_kind_context` 因 `elif dataset_type==nvidia_physicalai` 先命中 → **仅渲染 `nvidia_original` 标签**；筛选命中与展示标签分叉 = C6 要消除的第二套真相形态。`self_built_original` 对「nvidia 且无场景用途」行同分叉（~scene_basis 真）。
  - 与本轮已修 A-OCR-2（scene_original 补 `~_scene_slice_pred` 堵 ORIGINAL+derivation 子）同一缺陷类（SQL 谓词 vs Python 标签单源优先级不一致），属 R1 修复面未覆盖到的对称缺口。
- 裁决：**CONFIRMED，最小返修 = `scene_original` 与 `self_built_original` 两谓词各补 `BagRecord.dataset_type != "nvidia_physicalai"`**（镜像 Python elif 优先级），一行/谓词、仅 `bag_search_service.py`，同步 docstring 优先级口径。非 CORRECTION 级阻断（当前无造数路径实际触发，防御性），但 C6 单源闭环须补。

### F2（line 664，category=maintainability，severity=medium）— **驳回（FALSE POSITIVE，隔离树盲区）**
- OCR 主张：chip 文案「原始数据/全部」与「同页 tab 旧名（bags.html:21/22 原始包/全部/历史）」不一致。
- 独立核实：OCR 运行于 A 专属树 `wt-01-t16ca`，该树 `bags.html` 仍为 seed 旧名（tab「原始包/全部/历史」）——**b01 看不到 B 叶 `e399daf` 的 tab 改名**。在集成树 `29bd1f4` 上 `bags.html` tab 已=B 叶新名「切片/原始数据/全部」，chip「视图：原始数据」与 tab「原始数据」**同叫法一致**；TESTER 16D 联合验收 18:3x 真实 headless Chrome 实证 `has_chip_view_label=true（视图：原始数据）+ has_old_view_label=false（原始包已消失）+ errors=[]`。
- 裁决：**驳回**，无返修。line 148 `BagSearchState.view` 行内注释「all=全部/历史」为陈旧文案，随 F1 返修一并同步为「all=全部」（零行为）。

### F3（line 109，category=documentation，severity=low）— **CONFIRMED（文档，随 F1 同包修，不单独烧 OCR）**
- OCR 主张：docstring「MySQL DATETIME(0) 四舍五入落 23:59:59」不准确。
- 独立核实：TESTER 16D 严格 MySQL 8.4.11 探针直接 SQL 佐证 `CAST('…23:59:59.999999' AS DATETIME)` = **次日 00:00:00**（frac≥0.5 进位），非 23:59:59；`'…23:59:59' <= '…23:59:59.999999'` = 1（比较语义仍成立，全天窗口含 23:59:59 行）。行为正确，仅注释声明与实际落值不符。
- 裁决：**CONFIRMED 文档级**，随 F1 返修同 commit 改 docstring 一行（注明「写入侧秒精度四舍五入可能进位到次日 00:00:00，比较语义按字符串边界仍含当日 23:59:59」），不改变任何谓词/行为，不单独烧 OCR。

## b02 面裁决（协调者独立核，b02 于 2026-10-14 18:45 +08:00 收口）
- b02 `app/services/scene_result_query.py` 18:45 收口 REVIEW_COMPLETE（rc=0，coverage 1/1，`batch_identity_matches=true`，terminal `complete`，234428 tokens / 11m17s）→ **0 findings**。
- 独立核实：b02 覆盖范围 `bd0db1d2..1489bc6` 内 `scene_result_query.py` 已带 c03/C5/C7 修复（`data_kind_case`→`data_kind_pred`、采集时间 `_parse_time` 422、cursor 上下文全字段归一校验、行内分类走 `data_kind_context` 单源），b02 OCR 对该最终态零问题 → 无返修、无 CORRECTION。
- 裁决：**b02 面 PASS（0 findings），无新增返修项**。

## 门禁结论
- **本 run `66ca40d3` 整体 gate 已全部评估**：b01 `bag_search_service.py` = F1 须最小返修 / F2 驳回 / F3 文档并入 F1；b02 `scene_result_query.py` = 0 findings PASS。
- **b01 面：F1 须最小返修（1 文件、2 谓词补 NVIDIA 排除 + docstring/注释同步）→ A 同冻结链续 commit → 协调者机械核验 → 增量 OCR 仅 `bag_search_service.py` 单文件（head 变化旧覆盖不续用）→ 零 CORRECTION 级 + TESTER A 增量面（补 F1 组合夹具：nvidia+scene 用途原包筛选 scene_original 不返回 / 标签仅 nvidia_original 一致性）→ A 叶接受。**
- **F2 驳回、F3 并入 F1 同包**，不扩需求、不重审 `scene_result_query.py` 全量（b02 已 PASS）。
- **合入 HOLD 维持**：`29bd1f4` 仍含 F1 未修缺陷，**16D PASS 授权合入挂起**，待 A F1 返修冻结 + 单文件增量 OCR 零 CORRECTION + TESTER F1 增量面齐后再重建集成候选并重新联合验收。b02 已无阻塞项。详见 `inbox/coordinator/TASK-16C/merge-authorization-20261014.md` 追加 HOLD 段。

## 证据
- `reviews/TASK-16C-A/ocr-run-20261014-r12/{spec.json, b01.log, b01-diagnosis.json, b02.log, b02-diagnosis.json, run/state.json}`（2 批身份、b01 3 findings、b02 0 findings、run 终态 AWAITING_DECISION=全覆盖完成）。
- `wt-coord-intcheck-16c@29bd1f4` / `wt-01-t16ca@1489bc6` / `seed bd0db1d2` 三处 `bag_search_service.py` 谓词与 `data_kind_context` 独立读取；`bags.html` seed vs `29bd1f4` tab 名对比；`scene_slice_service.py:140-200` create_scene_run 校验面。
- `test-receipts/TEST-TASK16D/attempt-1.md` 18:3x–18:5x 段（F2 chip/tab 浏览器实证 + F3 MySQL CAST 直接 SQL 佐证）。