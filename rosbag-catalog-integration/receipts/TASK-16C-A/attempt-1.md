# TASK-16C-A attempt-1 回执（执行者 A）

status: REVIEW_PENDING（冻结交付，**未合入**，待协调者审查/OCR 与 TESTER 独立验证）
- task/attempt: TASK-16C-A / attempt-1（父 TASK-16C；REQ-16/05、AC-16/05）
- owner: 执行者 A（chat `oc_a2b2bc6b8a261371ff713d1b2a2aff6c`）
- base: `bd0db1d2a0fc293cb4562e2079e741739bacb0de`（派单固定 seed，未接受、带已知缺陷）
- head: `a1e416a`（branch `a/task-16c-a-query-api`，worktree `/home/wang/.local/state/rosbag-scene/wt-01-t16ca`）
- 交付时间: 2026-10-14 12:39 +08:00（commit 落盘后冻结）

## 文件清单（3 文件，+595/−86）

- `app/services/bag_search_service.py`（修改）
- `app/services/scene_result_query.py`（修改）
- `tests/test_task16ca_query_api.py`（新增，19 用例）
- `app/api/sources.py`：未改动（派单文件清单内，核读确认 seed 接线已满足"有界 GET 集合路由"，无需增量）
- `tests/test_task16c_ui_minimal.py`：冻结，未动（仅 A 单写，本单以新文件承载断言）

## 行为变化（最小增量，无接口名/返回形状变化）

- C5：`data_kind_pred(kind)` 多成员 SQL 谓词为 Web 与 API 共用筛选真相；双用途原包（scene_slice+self_built 用途）在 `scene_original` 与 `self_built_original` 两个 `data_kind` 筛选都命中，每视图 UID 唯一。`data_kind_case()` 保留为单值展示/兼容口径，与谓词同优先级。
- C6：`data_kind_context()` 分类真相与 SQL 谓词同一优先级，删除 seed 中第二套 Python 分叉规则（原 `data_kind_labels_for` 语义并入 context）；NOT_APPLICABLE 且非 NVIDIA 不猜类型（标签 `[]`、API 行内 `data_kind=None`，模板渲染"未分类"）。
- C7：`_parse_time(value, end=…)` 单入口，Web（400）与 API（422）共用：非法字符串不再直入 DateTime 触发 DB 层 500；`Z`/aware 任意时区统一换算到 `settings.display_timezone`（业务 naive，与 `app.clock.now()` 写入口径同源）；`YYYY-MM-DD` 的 end 边界全天截止（23:59:59.999999）；`end<start` 422。
- 16C-c03-02：cursor payload 覆盖全部实际筛选字段（view/scene_code/data_kind/purpose/dataset_type/started_from/started_to/role/vehicle_id/keyword/parent_bag_uid/include_history）；换筛选条件复用 cursor → 422（不误翻页）。
- 16C-c03-03：历史 cursor 缺新键时仅校验其实际携带字段（兼容旧合法值）；`scene_code` None 与空串归一同义；bool 字段（`include_history`）比较不做 `v or ""` 归一（防 False→"" 误拒）。
- 16C-c03-04：子包识别 = `bag_role=SCENE_SLICE` 或存在有效 derivation（任一即可，含合法无血缘历史切片），SQL 谓词与 Python 标签同口径。
- B 消费接口：函数名/返回形状/标签字段全部保持 seed 口径（`search_scene_bags`、`data_kind_context`、`data_kind_case`、items 行 `data_kind` 单值取首个命中），**无需协调**。

## 自测证据（环境：worktree venv py3.10；测试库=pytest 共享 scratch SQLite；未跑 MySQL）

- 命令：`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest tests/test_task16ca_query_api.py tests/test_task16c_ui_minimal.py tests/test_scene_result_storage.py -q`
- 结果：**59 passed**（本单 19 + 冻结 15 + 场景存储 25），rc=0
- 全量（排除 `tests/test_devflow.py` worktree 环境已知失败、`test_bag_cleanup_mysql.py`/`test_bag_cleanup_concurrency.py` 隔离 MySQL 专属）：`pytest tests/ -q` → **1115 passed, 1 failed**；失败项 `tests/test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time` 为**seed 既有失败**（stash 本单改动后在 seed 与主仓复跑同失败，单跑 `no such table` 顺序依赖），非本单回归。
- `ruff check`（三个改动文件）：**All checks passed**（line-length=120；seed 文件已 ruff format，本单未跑 format 全文件重写，仅 check 口径）。
- 关键断言摘录：双用途两筛选命中+UID唯一（API/Web）；`scene_original` 不含纯 self_built 父包；NOT_APPLICABLE 非 NVIDIA API `data_kind=None` 与 Web `[]`；非法日期 API 422/Web 400；end 全天截止含 23:59:59 行、次日 00:00:00 行排除；aware UTC+10 换算=业务 naive；cursor 换 started_from/data_kind/dataset_type 均 422、同条件续页 200；旧 cursor（剔除新键）续页=新 cursor 同结果；篡改 cursor 422。

## 未执行项（如实申报）

- **MySQL 关键行为未验证**：隔离 MySQL 库/容器未跑（派单自测口径"使用隔离库或明确交 TESTER 验证"）——`started_at` 边界在 MySQL DATETIME(0) 的秒精度行为、`data_kind_pred` 的 IN 子查询在 MySQL 方言下性能/正确性，**交 TESTER 独立验证**；SQLite 绿不宣 MySQL 通过。
- `./scripts/local_quality_gate.sh` 未跑（其含 browser gate）：`scripts/run_bag_search_browser_test.py` 在 seed 与主仓均失败（"测试数据未生成可点击的下一页"，seed 既有环境失败，非本单引入；stash 对照证据在 sessions/A.md），pytest 面已全量覆盖。
- 未跑 OCR/强审查（协调者唯一入口）；未合入、未部署、未改生产。
- `tests/test_task16ca_query_api.py` 夹具 UID 前缀 `T16CA`，按前缀自清；日期窗 2026-12-01 用于 cursor 类隔离（共享 SQLite 中其他 test 文件日期 1–4 月，demo 行 2026-07-20，均窗外）。

## 越界申报

- 无：未改 `app/api/sources.py`、模板、B/C 域文件、TODO/HANDOFF/DESIGN/decision；分支内只动派单允许的三个查询面文件。

---

## attempt-1 续单段：共享旧测试断言转派（`shared-test-assert-transfer.md`，协调者 2026-10-14 12:41）

- 状态：**续 commit 已冻结交付，REVIEW_PENDING**（未合入；门禁不变——最终接受仍待协调者 OCR + TESTER 独立验证）
- 新 head: `563a91a`（续 `a1e416a`，同 branch `a/task-16c-a-query-api`、同 worktree `wt-01-t16ca`，base 仍 `bd0db1d2…`）
- 变更（仅 1 处断言，按转派单原口径，未扩面）：
  - `tests/test_web.py:366`（`test_bag_list_shows_default_results_and_route_filter`）：`assert "原始包" in page.text` → `assert "原始数据" in page.text`（B 叶 `e399daf` tab 改名「切片/原始数据/全部」连带，DESIGN §7.3.3 口径，URL 值不变）。
- 复跑证据（worktree `wt-01-t16ca`，venv=主仓 py3.10，SQLite 本地栈，2026-10-14 12:46–12:47 +08:00 实测）：
  - `pytest tests/test_web.py tests/test_task16c_ui_minimal.py tests/test_task16ca_query_api.py -q` → **74 passed, 1 failed**（rc 口径见下）。
  - 唯一失败 `test_bag_search_page_has_bounded_query_count_and_response_time` 单跑复现 `sqlite3.OperationalError: no such table: bag_record`（fixture 顺序依赖），与 seed/主仓固有失败同口径（本 attempt-1 正文已申报 stash 对照），**不计本续单账**。
  - `tests/test_task16c_ui_minimal.py` 复跑 15 passed 全绿（转派单要求复跑一次，已在上述合跑中覆盖，单独 `16 passed` 亦实测：目标用例 1 + 15）。
  - 连带断言核：`tests/test_web.py` 全文 grep `原始包` 已零命中（含 B 改名涉及的其他断言面），无其他 tab 改名连带失败，**未回协调者扩面**（前提不成立）。
  - 范围核：续 commit 仅 1 文件 1 行（`tests/test_web.py`）；未动 `bag_search_service.py`/`scene_result_query.py`/`sources.py` 查询面实现。
- 对 OCR 的影响（转派单在案口径）：A 叶 OCR 快照以续 commit 后最终冻结 head `563a91a` 为准。
- 时间：发生（commit 落盘）2026-10-14 12:46 +08:00（`563a91a` committer date 12:46:39 实测）；测试实测窗口 12:46–12:47 +08:00；本段补录 12:47 +08:00。

---

## attempt-1 勘误续单段：共享旧测试断言转派勘误（`shared-test-assert-transfer-correction-20261014.md`，协调者 2026-10-14 13:1x）

- 状态：**续 commit 已冻结交付，REVIEW_PENDING**（未合入；门禁不变——最终接受仍待协调者 OCR + TESTER 独立验证；OCR 提交当前被协调者工具链版本门禁阻塞，身份策略同 attempt 链不变）
- 新 head: `ff2a005`（`ff2a0055c75655f2f91f273a80af99633c9fbebf`，续 `563a91a`，同 branch `a/task-16c-a-query-api`、同 worktree `wt-01-t16ca`，base 仍 `bd0db1d2…`）
- 变更（仅 2 行断言，同一转派单面，未扩面）：
  - `tests/test_web.py:364`（`test_bag_list_shows_default_results_and_route_filter`）：`assert "当前可用切片" in page.text` → `assert "切片" in page.text`
  - `tests/test_web.py:366`：`assert "全部/历史" in page.text` → `assert "全部" in page.text`
  - line 365（原始数据）`563a91a` 已改，未动；同函数其余断言未动；查询面实现（bag_search_service/scene_result_query/sources.py）未动。
- 复跑证据（worktree `wt-01-t16ca`，venv=主仓 py3.10 软链，SQLite 本地栈，2026-10-14 13:17–13:18 +08:00 实测）：
  - `pytest tests/test_web.py tests/test_task16c_ui_minimal.py tests/test_task16ca_query_api.py -q` → **74 passed, 1 failed**。
  - 唯一失败 `test_bag_search_page_has_bounded_query_count_and_response_time` 单跑复现 `sqlite3.OperationalError: no such table: bag_record`（fixture 顺序依赖），与 seed/主仓固有失败同口径（前两段已申报 stash 对照），**不计本勘误账**。
  - `tests/test_task16c_ui_minimal.py` 复跑全绿（合跑覆盖 15 passed）。
  - 同函数其余断言（view-tab active href、demo UID 排除/包含、表格结构）实测无失配，**未回协调者扩面**（前提不成立）。
  - 环境注记：worktree `.venv` 软链本轮发现缺失已重建（`ln -s /home/wang/work/rosbag-catalog/.venv`），仅 untracked 不入 diff，不影响冻结口径。
- 对下游的影响（按派单在案口径）：A 叶 OCR 快照仍以本勘误续 commit 后最终冻结 head `ff2a005` 为准；协调者集成候选 `wt-coord-intcheck-16c` 待 A 本 commit 后重建；16D 最终固定 SHA 以三叶最终 head 为准。
- 时间：发生（commit 落盘）2026-10-14 13:18 +08:00（`ff2a005` committer date 13:18:27 实测）；测试实测窗口 13:17–13:18 +08:00；本段补录 13:20 +08:00。

---

## attempt-1 OCR 最小返修段：A 叶 OCR 合并裁决返修（`ocr-r1-rework-dispatch-20261014.md`，协调者 2026-10-14 16:42）

- 状态：**续 commit 已冻结交付，REVIEW_PENDING**（未合入；并入 attempt-1 同一冻结链，不新开 attempt；同 branch `a/task-16c-a-query-api`、同 worktree `wt-01-t16ca`，base 续 `ff2a0055c75655f2f91f273a80af99633c9fbebf`）
- 新 head: `4838ef8c3f9e11c3f7e5332882a9b2627085696a`（续 `ff2a005`，committer date 2026-10-14 17:15:40 +08:00 实测）
- 来源：A 叶 OCR 合并裁决 `ocr-merge-ruling-20261014.md`（初 run `7a72eed8` + 唯一入口补审 `0aba25ee` 16:24 收口全覆盖）。两条 CONFIRMED（均 low），只改一个文件 `app/services/bag_search_service.py`。
- 变更（仅 1 文件，+3/−15）：
  - **A-OCR-1**：删除 `data_kind_case()` 函数整体（原 line 98–108 的 SQL CASE 定义，第二套分类真相）。全仓 py/html 零调用点独立核实（`grep -rn data_kind_case` 仅定义行命中）；`case` import 他处仍用（line 365/448 的 `case(` 调用）故**保留**，无 `else_` 裸名 import 需清理（`else_` 全程仅以 `else_=` 关键字参数出现），**import 行未动**（ruff 全绿确认无 unused import）。
  - **A-OCR-2**：`data_kind_pred` 的 `scene_original` 分支补 `~_scene_slice_pred()`，镜像兄弟谓词 → `return and_(BagRecord.bag_role == "ORIGINAL", ~_scene_slice_pred(), _scene_basis_pred())`（子包优先，堵 ORIGINAL+derivation 子包这一当前不可达组合，非 CORRECTION 级阻断）；同步 `data_kind_pred` docstring 分类规则第 3 条口径（"且非子包（子包优先，与 data_kind_context 一致）"），避免第二套口径描述漂移。
- 双用途行为核对：A-OCR-2 不改变双用途原包行为（双用途原包 `bag_role=ORIGINAL` 且无 derivation 子包关系，`~_scene_slice_pred()` 恒真，仍在 `scene_original` 与 `self_built_original` 两筛选都命中、UID 一条）；仅新增排除"ORIGINAL 且带 scene_slice 用途且为 derivation 子"的当前不可达组合。
- 复跑证据（worktree `wt-01-t16ca`，venv=主仓 py3.10 软链，SQLite 本地栈，本轮 commit 前实测，commit 落盘 17:15 +08:00）：
  - `ruff check app/services/bag_search_service.py` → **All checks passed**。
  - `pytest tests/test_task16ca_query_api.py tests/test_task16c_ui_minimal.py tests/test_web.py -q` → **74 passed, 1 failed**。
  - 唯一失败 `test_bag_search_page_has_bounded_query_count_and_response_time`（N+1 bounded-query 断言 11>8）为 **seed 固有失败**：`git stash` 本返修后在 base `ff2a005` 单跑同口径复现失败（`1 failed`），**本返修零新增失败**，不计本账。
  - 派单复跑清单中 `tests/test_task16cb_bag_views.py` 为 **B 叶测试文件**，不在 A 专属 worktree（A 自 seed 仅承载 A 范围文件），本单零越界、未代跑 B 面，由协调者集成候选/B 侧覆盖。
- 后续门禁（按裁决/返修单口径，不代判）：协调者机械核验 → **增量 OCR 仅 `bag_search_service.py` 单文件**（head 变化使旧覆盖不自动续用；`scene_result_query.py` 未变不重跑）→ 零 CORRECTION 级 + TESTER 16D 增量面（含"筛 scene_original 不返回 derivation 子包"组合断言，TESTER 自加，A 不写）→ A 叶接受。
- 时间：发生（commit 落盘）2026-10-14 17:15 +08:00（`4838ef8` committer date 17:15:40 实测）；ruff+pytest 实测为本轮 commit 前执行；本段补录 17:17 +08:00。

---

## attempt-1 OCR 清理续单 R1-2 段：已选筛选 chip 视图名对齐（`ocr-r1-rework-2-dispatch-20261014.md`，协调者 2026-10-14 17:30）

- 状态：**续 commit 已冻结交付，REVIEW_PENDING（A 叶最终冻结 head）**（未合入；并入 attempt-1 同一冻结链，同 branch `a/task-16c-a-query-api`、同 worktree `wt-01-t16ca`，base 续 R1 已交付 `4838ef8c3f9e11c3f7e5332882a9b2627085696a`）
- 新 head: `1489bc6b58a20a57650831969c53e6af39d57f75`（续 `4838ef8`，committer date 2026-10-14 17:40:26 +08:00 实测）——**协调者口径：本 commit 为 A 叶最终冻结 head**
- 来源：B 叶 OCR run `513ab61d`（17:09 收口，rc=0）唯一 finding，协调者裁决 CONFIRMED（`reviews/TASK-16C-B/ocr-run-20261014/ocr-verdict.md`）。B 叶 tab 已改「切片/原始数据/全部」，同屏「已选筛选条件」chip 的 `view_label` 仍渲染旧名「视图：原始包 / 视图：全部/历史」，同页两套叫法（UI 一致性低危）。修复点在 A 叶独占文件，超出 B 授权，由 A 处置。
- 变更（仅 1 文件 1 行，`app/services/bag_search_service.py` `build_active_filters` line 664）：
  - `view_label = {"originals": "原始包", "all": "全部/历史"}.get(...)` → `{"originals": "原始数据", "all": "全部"}.get(...)`，与 B 叶 tab 名及 `test_web.py` 已改断言（切片/原始数据/全部）一致。
  - **`slices` 键不加**：外层 `if state.view != "slices"` 已使 slices 视图不渲染 chip，加 `"slices": "切片"` 为死代码（会被 OCR 判定），保持最小改动；三种视图中仅 originals/all 两 chip 实际渲染，均已对齐新名。
  - 不动谓词面（R1 的 A-OCR-1/A-OCR-2 已交付，不重做）；不改其他文件。
- 复跑证据（worktree `wt-01-t16ca`，venv=主仓 py3.10 软链，SQLite 本地栈，本轮 commit 前实测，commit 落盘 17:40 +08:00）：
  - `ruff check app/services/bag_search_service.py` → **All checks passed**。
  - `pytest tests/test_task16ca_query_api.py tests/test_task16c_ui_minimal.py tests/test_web.py -q` → **74 passed, 1 failed**。
  - 唯一失败 `test_bag_search_page_has_bounded_query_count_and_response_time` 为 **seed 固有失败**（N+1 bounded-query，与 R1 段 stash 基线 ff2a005 同口径），本 R1-2 仅改 chip 展示字符串不动 SQL，**零新增失败**，不计本账。
- 后续门禁（按 R1-2 单口径，不代判）：协调者机械核验 → **单文件增量 OCR 一次**（覆盖 R1+R1-2 同文件小 diff，`scene_result_query.py` 未变不重跑，不逐 commit 重复烧 OCR）→ 零 CORRECTION 级 + TESTER 增量面 → A 叶接受。
- 时间：发生（commit 落盘）2026-10-14 17:40 +08:00（`1489bc6` committer date 17:40:26 实测）；ruff+pytest 实测为本轮 commit 前执行；本段补录 17:43 +08:00。