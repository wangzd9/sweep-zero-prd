# TASK-16C-B attempt-1 回执 — 执行者B（REVIEW_PENDING）

交付时间：2026-10-14T12:0x +08:00；owner：cron-b-poll-6f7471d8747c（执行者 B）

## 1. base / head

- 固定 seed（base）：`bd0db1d2a0fc293cb4562e2079e741739bacb0de`（未接受、带已知缺陷，仅消费冻结契约）
- 交付 head：`e399daf`（单 commit，leaf 增量 = seed..e399daf）
- 分支/worktree：`b/task-16c-b-bag-views` @ `/home/wang/.local/state/rosbag-scene/wt-04a-t16cb`（从 seed 新建，未写共享种子树/旧 B 冻结树/主仓）
- 父任务完整增量核：`63bfcf8..集成候选` 由协调者在三叶齐后执行（本叶不宣称覆盖父范围）

## 2. 文件清单（本叶 diff，seed..head）

| 文件 | 变更 | 说明 |
|---|---|---|
| `app/templates/bags.html` | +6/-6（3 处） | tab 显示名、NVIDIA 车辆列、空结果区文案 |
| `tests/test_task16cb_bag_views.py` | 新增 11 用例 | B 独占新测试文件 |
| `app/web/bags.py` | **未改动** | seed 已满足本叶接线面（data_kind_ctx 消费、detail return_to、三视图参数），无需 B 侧 .py 改动 |

越界申报：**无**。未改共享分类服务（`bag_search_service.py`/`scene_result_query.py`/`api/sources.py`）、未改 `tests/test_task16c_ui_minimal.py`、未改 detail.html（07A/07B 面，仅核入口可达）。

## 3. 行为

1. **tab 显示名对齐 DESIGN §7.3.3**："当前可用切片/原始包/全部历史" → "**切片/原始数据/全部**"（URL 值 `slices|originals|all` 不变，旧书签兼容）；每 tab 加 title 说明语义（切片=AVAILABLE 且当前版本；原始数据=自建/英伟达/切片原始数据三类；全部=含历史/下架切片与全部既有记录）。
2. **NVIDIA 空数据行**：无 PipelineRun 的 NVIDIA 输入记录（NOT_APPLICABLE 角色）车辆列不再误显"待认领"，显"—"（有车辆仍显车辆编号）；采集时间/大小/Topic 面维持 nv fallback 正常空值展示。
3. **不相容筛选组合明确空集**：空结果区文案改为"当前筛选组合无匹配数据（条件均生效，未静默丢弃）"，已选 chip 区保留全部条件（取消任一 chip 其余保留、page 归 1——由 seed 的 `remove_url` 逻辑保证，本侧测试锁定）。
4. **详情/父包追溯/受控获取入口可达**：列表行详情链接 `return_to` 携带全部条件（含 view）；切片详情父包追溯面板（07A 面）与 `access.txt` 取数说明 200 可达；原始包详情场景结果面板跳切片视图入口存在。

## 4. 自测证据（环境：`wt-04a-t16cb`，.venv=主仓 python3.10，SQLite 本地栈，未调用真实模型/未触生产）

| 命令 | 结果 |
|---|---|
| `pytest tests/test_task16cb_bag_views.py -q` | **11 passed**（新用例全绿） |
| `pytest tests/test_web.py tests/test_task07a_visibility.py tests/test_task07b_manual_revision.py tests/test_task16c_ui_minimal.py tests/test_task16cb_bag_views.py -q` | 75 passed，**2 failed（见 §6 越界申报）** |
| `pytest tests/ -q -k "not (devflow or bag_search_page_has_bounded)" --deselect tests/test_web.py::test_bag_list_shows_default_results_and_route_filter` | **1106 passed, 10 skipped, 26 deselected**（96s） |
| `ruff check tests/test_task16cb_bag_views.py` + `ruff format` | 全绿 |

关键断言（新用例）：tab 三链接 `href="/bags"`、`view=originals`、`view=all` 均保留 q/data_kind 且不含 page；取消视图 chip 的 remove_url 保留 `data_kind=nvidia_original`；NVIDIA 无 run 行 `待认领 not in row` 且显 `—`；`dataset_type=nvidia_physicalai&data_kind=scene_slice` → "共 0 条"+空结果文案+双 chip 均保留；双用途包在 scene_original 筛选下单行双徽标（场景原始数据+自建原始数据）；`/bags/{slice_uid}` 200 含父包链接、`access.txt` 200 含 rsync。

## 5. OCR 遗留逐项（本叶面，对照 `reviews/TASK-16C/OCR-LEGACY-20261014.md`）

- **C5**（双用途单值 CASE，owner=A 叶）：本叶**消费侧已验证**——`data_kind_context` 双用途双标一行命中（新用例 `test_dual_purpose_two_badges_one_row`）；SQL 谓词侧修复归 A 叶，不代修。
- **C6**（`data_kind_labels_for` 死代码，owner=A 叶）：归 A 叶；本叶模板消费 `data_kind_context`，未依赖死 helper。
- **C1/C2/C3/C4/C8/C9/16C-c05-0x**（pipelines/pipeline_detail 面）：**归 C 叶**，本叶文件零交集。
- **16C-c03-0x**（cursor/日期面）：**归 A 叶**。
- c06 `bags.html` 原 0 findings、c07 `bags.py` 原 0 findings：本侧 3 处标签/文案改动的复验由协调者增量 OCR 覆盖（新 SHA `e399daf`，旧结论不宣称覆盖）。

## 6. 未测项与共享文件申报（需协调者裁决）

1. **越界申报（共享旧测试文件其他 UI 断言，按入口规定由协调者转 A 单写，本侧未代改）**：
   - `tests/test_web.py:366` `assert "原始包" in page.text`：tab 改名后该断言失败（新标签"原始数据"）。需改为 `"原始数据"`（或两者兼容断言）。
   - `tests/test_task16c_ui_minimal.py`（A 独占）：未断言旧 tab 名，实测 15 passed 全绿，**无需改动**。
2. **seed 既有环境性失败（非本侧引入，seed bd0db1d 上复跑同口径）**：`tests/test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time` 单跑即 `sqlite3.OperationalError: no such table: bag_record`（fixture 隔离问题，seed 与 head 均复现）。
3. **独立浏览器取证**：未执行（归 TESTER 16D，入口明文）；HTTP 200 不替代浏览器验证。
4. **真实 MySQL 面**：本叶零 DDL（仅 SELECT 谓词消费 + 模板文案），隔离 MySQL 演练归 TESTER/16D。
5. 页面烟测用 TestClient 全渲染（Jinja2 真实执行），非仅 HTTP 状态码；静态 JS（bags_filters.js）无 tab 名耦合（grep 实测零命中）。

## 7. 停止条件核

无 schema/状态机/算法变化、无生产写、无未知在途写者、无文件冲突；A 接口未变化（seed 契约消费），B 叶未阻塞。

— 执行者 B，2026-10-14（TASK-16C-B attempt-1，REVIEW_PENDING，等协调者机械核验→串行 OCR→TESTER 独立验证，**未合入**）