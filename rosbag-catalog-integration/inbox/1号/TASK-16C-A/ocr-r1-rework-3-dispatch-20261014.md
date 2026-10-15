# TASK-16C-A OCR 增量 R1-3 最小返修单（协调者，2026-10-14 18:55 +08:00）

- 状态：REWORK_DISPATCHED。并入 TASK-16C-A attempt-1 同一冻结链（**不新开 attempt**，续 A 最终冻结 head `1489bc6`，同 branch `a/task-16c-a-query-api`、同 worktree `wt-01-t16ca`）。
- 来源：A 叶增量 OCR run `66ca40d3` b01（`bag_search_service.py`）收口裁决 `inbox/coordinator/TASK-16C-A/ocr-r12-adjudication-20261014.md`。**仅 F1 须返修**；F2 驳回（隔离树盲区，`29bd1f4` 集成面 chip/tab 已一致）；F3 文档随 F1 同包修。
- **只改一个文件 `app/services/bag_search_service.py`，禁止越界**（不动 `scene_result_query.py`/模板/tests/其他服务）。

## 改动项（打包一个最小 commit，base 续 `1489bc6`）

1. **F1（谓词单源对齐，防御性 medium）**：`data_kind_pred` 两分支各补 NVIDIA 排除，镜像 Python `data_kind_context` 的 `elif dataset_type=="nvidia_physicalai"` 优先级与顶部单源注释（1)子包→2)NVIDIA→3)场景→4)自建）：
   - `scene_original` 分支（现 `and_(ORIGINAL, ~_scene_slice_pred(), _scene_basis_pred())`）→ 补 `BagRecord.dataset_type != "nvidia_physicalai"`。
   - `self_built_original` 分支（现 `and_(ORIGINAL, ~_scene_slice_pred(), or_(dataset_type==self_built, ~_scene_basis_pred()))`）→ 补 `BagRecord.dataset_type != "nvidia_physicalai"`。
   - 同步 `data_kind_pred` docstring 与顶部 `# 分类优先级` 注释：`scene_original`/`self_built_original` 均「**且非 NVIDIA**（单源优先级第 2 条 NVIDIA 先命中，与 `data_kind_context` 一致）」。
2. **F3（文档，零行为）**：`_parse_time` 附近 docstring line 109「MySQL DATETIME(0) 四舍五入落 23:59:59」改为如实口径——写入侧秒精度四舍五入、`…59.999999` 可能进位到次日 `00:00:00`（TESTER 严格 MySQL 8.4.11 探针 `CAST('…59.999999' AS DATETIME)`=次日 00:00:00 已证），全天窗口比较语义按字符串边界仍含当日 23:59:59。不改任何谓词/逻辑。
3. **F2 附带（注释，零行为）**：`BagSearchState.view` 行内注释 line 148「all=全部/历史」→「all=全部」（陈旧文案随本次同步，无代码改动）。

## 复跑（提交前实测，回执给退出码）
- `ruff check app/services/bag_search_service.py` 全绿。
- `pytest tests/test_task16ca_query_api.py tests/test_task16c_ui_minimal.py tests/test_web.py -q` → 期望 74 passed + 1 seed 固有 bounded-query（stash 同口径），**零新增失败**。
- 自证 F1 不变量（可用最小 SQL/断言）：nvidia_physicalai 且非子包原包（无论有无 scene_slice 用途）→ 筛 `scene_original`/`self_built_original` **不命中**、筛 `nvidia_original` 命中；双用途（self_built+scene）原包两筛选仍都命中 UID 一条（F1 只加 NVIDIA 排除，不改双用途行为）。

## 交付与门禁
- 回执 `receipts/TASK-16C-A/attempt-1.md` 追加 R1-3 段（commit SHA + diff 摘要 + 复跑退出码），交付冻结 head。
- 冻结后：协调者机械核验 → **增量 OCR 仅 `bag_search_service.py` 单文件**（head 变化旧覆盖不续用；`scene_result_query.py` 由同 run b02 收口，未变不重跑）→ 零 CORRECTION 级 + **TESTER A 增量面**（F1 组合夹具：nvidia+scene 用途原包筛 scene_original 不返回 + 标签仅 nvidia_original 一致性）→ A 叶接受。
- **A 叶接受门禁维持关闭**至上述齐；`29bd1f4` 含本缺陷，16D 合入授权已挂 HOLD（`inbox/coordinator/TASK-16C/merge-authorization-20261014.md` 18:55 段），A 返修链收口前不合入。
- 本单不扩需求：不新增任务、不动其他文件、不重审 A 叶全量。