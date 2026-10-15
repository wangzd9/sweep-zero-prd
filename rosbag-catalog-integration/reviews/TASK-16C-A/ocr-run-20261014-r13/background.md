# TASK-16C-A R1-3 增量 OCR 背景（协调者冻结）

- 任务：TASK-16C-A（查询/API 叶，父 TASK-16C）attempt-1 OCR 增量复审 R1-3；REQ-16/05、AC-16/05。
- 授权来源：用户 2026-10-14 恢复 v0.4 最小界面闭环（inbox/control/V04-UI-RESUME-20261014.md）+ OCR 仅协调者唯一入口在案口径。
- base/head：`1489bc6b58a20a57650831969c53e6af39d57f75`（R1-2 A 叶冻结 head）→ `8958291222dbad8fbf61e7802510ddf83ecbbce1`（R1-3 F1 返修新 head，19:03:26 落盘）。
- R1-3 变更内容（协调者已机械核验）：仅 `app/services/bag_search_service.py`（+18/-10）。
  - F1（核心，单源对齐）：`data_kind_pred` 的 `scene_original`/`self_built_original` 两谓词各补 `BagRecord.dataset_type != "nvidia_physicalai"`，镜像 Python `data_kind_context` 的 `elif dataset_type=="nvidia_physicalai"` 优先级与顶部「分类优先级」单源注释（1)子包→2)NVIDIA→3)场景→4)自建）。
  - F1 文档同步（零行为）：`data_kind_pred` docstring 第 3/4 条 + 顶部注释补「且非 NVIDIA」。
  - F3（文档，零行为）：`_parse_time` docstring 秒精度进位口径（frac≥0.5 可能进位次日 00:00:00，全天比较语义仍含当日 23:59:59，TESTER 严格 MySQL 探针已证）。
  - F2（文档，零行为）：`BagSearchState.view` 行内注释「all=全部/历史」→「all=全部」。
  - 零越界：不动 `scene_result_query.py`/模板/tests/其他服务。
- 本批仅审 `app/services/bag_search_service.py` 单文件（head 变化使旧 run `66ca40d3` 覆盖不自动续用；`scene_result_query.py` 已由 `66ca40d3` b02 收口 0 findings 且 R1-3 未变、tests 归 TESTER 16D 独立验证，均不重跑）。
- 审查重点：F1 两谓词 NVIDIA 排除是否与 `data_kind_context` 单源优先级一致（nvidia+ORIGINAL+scene_slice 用途+非子包组合不命中 scene_original/self_built_original、仅命中 nvidia_original；双用途原包两筛选行为不变）；确认 F3/F2 为纯文档零行为；确认无越界、无新引入缺陷。
- 交付身份：A（cron-a-poll 逻辑角色），专属 worktree `wt-01-t16ca`、分支 `a/task-16c-a-query-api`；协调者机械核验 + 独立 F1 不变量探针（内存 SQLite 8 断言 PASS）已完成，本 OCR 为 A 叶接受门禁之一（零 CORRECTION 级 + TESTER F1 增量面）。