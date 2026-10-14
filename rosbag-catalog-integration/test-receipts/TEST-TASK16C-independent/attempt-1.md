# 报告：TASK-16C 独立验证（t16c-independent-verify，attempt-1）

- status: TEST_REPORT_PENDING
- task/attempt: TASK-16C / t16c-independent-verify
- 角色: TESTER（测试者）
- 交付时间: 2026-10-13 11:0x +08:00
- 派单: `inbox/TESTER/TASK-16C/t16c-independent-verify-dispatch.md`（协调者 r142）
- 交付回执: `receipts/TASK-16C/attempt-1.md`（B）
- **总体结论: PASS（9 项场景全部取证通过；0 新增失败；0 残留）**

## 一、被测快照（独立核实）
- worktree `/home/wang/.local/state/rosbag-scene/wt-04a-t16c`，分支 `b/task-16c-scene-ui-minimal`，HEAD **`5c80857`**
- `git merge-base --is-ancestor 6fb42c4 5c80857` → 确认 `5c80857` 为 main `6fb42c4` 子节点单 commit
- `git diff 6fb42c4..5c80857` sha256 与 `git diff 4b9f30a..ad37ae1` 逐字节一致（`8f0f0437…310`）
- **未合入 main，全程以该 worktree 只读取证，未切 main、未改业务实现**

## 二、环境（自包含，未依赖既有栈）
- 独立临时 SQLite（scratch，`DATABASE_URL=sqlite:///<tmp>`）+ `DEMO_DATA=1`，`Base.metadata.create_all` 自建
- 本地 uvicorn `127.0.0.1:18795`（API 探针）+ `127.0.0.1:18796`（浏览器走查），结束后端口已释放
- 浏览器：browser_exec 真实 HTTP（`/bags`、`/pipelines/*`）走查，非 TestClient 复跑
- **未触碰 16B worktree `wt-03b-t16b` 与 `inbox/ocr.lock`**；`wt-04a-t16c` 只读
- **MySQL 面口径（派单明示）**：本单无 DDL/迁移变更，仅 SELECT 谓词；SQLite 取证，不要求真 MySQL 独立验证（如实标注，不降标也不谎称已验 MySQL）

## 三、逐项 1-9 证据（探针 `probe.py` 独立夹具，前缀 V16C，不复跑 B 的 15 用例）

### 1. 三类原始行（originals 视图 + 双标/未分类）— PASS
- 自建 ORIGINAL（无场景用途）→ originals 视图可见 ✓（`1_originals_selfbuilt`）
- NVIDIA 输入记录 `bag_role=NOT_APPLICABLE`+`dataset_type=nvidia_physicalai` → originals 可见 ✓（`1_originals_nvidia_notapplicable`）；页面 badge=「英伟达原始数据」✓
- 场景源 ORIGINAL（scene_slice 用途）→ 可见 ✓（`1_originals_scene`）；切片被排除 ✓（`1_originals_excludes_slice`）
- `data_kind_context`：NVIDIA NA → `['nvidia_original']`；双用途 → `{'scene_original','self_built_original'}`；未知历史（NOT_APPLICABLE+self_built）→ `[]` 不猜 ✓（`1_unknown_not_guessed`/`1_nvidia_ctx`/`3_dual_ctx_both`）
- 浏览器 `/bags?view=all`：未知行 badge=「未分类」(title=未知历史：all 视图保留但不猜测类型) ✓

### 2. 切片视图（当前/历史/下架）— PASS
- 默认 `view=slices`：当前 AVAILABLE 切片在；PENDING 切片**不进可用检索**；WITHDRAWN 切片**退出默认检索** ✓（`5_default_slices_*`）
- `include_history=true`：历史切片可见，行内 `current` 字段 cur=True / hist=False ✓（`2_history_slice_visible`/`2_current_flag_marks`）
- `view=all`：WITHDRAWN 切片仍可见（模型原结果保留）✓（`2_withdrawn_in_all`）

### 3. 双用途原包（双标并置 + 单值 CASE）— PASS
- 行级多标签 badge：浏览器实测 `vbag-03`/`vbag-05` 的「数据来源」td 内**两个独立 `<span class=badge>`**（场景原始数据 + 自建原始数据）✓
- 筛选走单值 CASE（scene_original 优先）：双用途行命中 `data_kind=scene_original`、**不**命中 `data_kind=self_built_original` ✓（`3_dual_in_scene_original`/`3_dual_NOT_in_selfbuilt_filter`）

### 4. data_kind 四类 × 视图/来源组合 — PASS
- 不相容组合 `dataset_type=self_built & data_kind=nvidia_original` → **HTTP 200 `items=[]`**（非 500、非静默丢条件）✓（`4_incompat_200_empty` + 浏览器页面 0 行）
- 相容交集 `dataset_type=nvidia_physicalai & data_kind=nvidia_original` → 命中 ✓（`4_compat_intersection`）
- 非法 `data_kind=bogus` / `view=zzz` → **422** ✓（`4_invalid_kind_422`/`4_invalid_view_422`）

### 5. `GET /api/v1/bags` 集合路由 — PASS
- 路由存在且返回 `{items,limit,has_more,next_cursor}` ✓（`5_route_collection_200`）
- **路由顺序**：字面量 `/api/v1/bags` 不被 `/api/v1/bags/{bag_uid}` 吞并（按 uid 查仍 200，集合查独立）✓（`5_route_byuid_still_works`）
- view=slices/originals/all 三视图、data_kind/dataset_type/purpose/时间边界过滤 ✓
- cursor 翻页：`limit=1` has_more=true 带 next_cursor；**`limit=99999` 收敛到 200**（非 422）✓（`5_clamp_200`）；正确上下文续页 200 ✓（`5_cursor_nextpage_ok`）
- **cursor 上下文不一致 → 422**（originals 的 cursor 用在 slices 视图）✓（`5_cursor_mismatch_422`）
- **历史 cursor 兼容**：无 data_kind/purpose 键的旧口径 cursor 在匹配视图 → 200 ✓（`5_legacy_cursor_compat`）

### 6. 场景八步详情 — PASS
- SUCCESS run：八步中文名全出现（输入检查/解码抽帧/模型识别/区间生成/切包/产物校验/NAS发布/登记完成）✓（`6_success_8zh` + 浏览器 stepMissing=[]）
- **部分完成不伪标**：run 终态 SUCCESS 但只 2 步 DONE → 阶段总览表**已完成行=2、未开始行=6**（未启动后继不回填完成）✓（`6_partial_done_count_2`/`6_partial_unstarted_count_6`）
- **NO_MATCH**：区间生成及之后「已跳过（无需）」；运行级结果展示 **NO_MATCH（非 SUCCESS）** ✓（`6_nomatch_*` + 浏览器 结果：NO_MATCH）
- **FAILED**：真实错误文本 `model timeout: connection refused` 原样透出；场景正常重试通路（非强制）✓（`6_fail_real_error`/`6_fail_retry_path`）
- **终态页无 10s 自动刷新**（SCENE_DONE/SCENE_FAILED 均无 `location.reload()`）；**非终态（RUNNING）仍保留自动刷新**（行为不变）✓（`6_success_no_reload`/`6_nonterminal_keeps_reload`）

### 7. 场景运行环境区 — PASS
- 模型端点（`http://127.0.0.1:8002/v1`）/处理机输入/场景 NAS 路径展示 ✓（`7_model_endpoint_shown` + 浏览器 hasSceneEnv=true）
- **无 A100 面**：场景页无「A100 Phase1/Phase3 结果」面板、无自建强制重试 ✓（`7_no_a100_on_scene`/`6_success_no_forced_retry`）
- **血缘降级**：run 的 source bag 行缺失（uid 99 不存在）→ 页面 **200 不 500** ✓（`7_lineage_downgrade_no_500`）

### 8. 旧界面兼容回归 — PASS
- bags 列表页 200，原有数据分类筛选下拉四类齐全 ✓（`8_bags_page_200`/`8_bags_page_has_dkind_filter` + 浏览器 dataKindFilter 四类）
- `dataset_type` 旧书签可用（200）✓（`8_dataset_type_bookmark`）
- 原有分页保留（`?page=1` 200）✓（`8_bags_pagination`）
- **pipeline 详情非场景面板**：SELF_BUILT_BAG run → 无「场景运行环境」面板、有 A100/自建 Phase 面板、badge=自建数据集 ✓（`8_nonscene_no_scene_panel`/`8_nonscene_self_phases` + 浏览器）

### 9. SQLite 全仓回归 — PASS
- `pytest tests/ -q`（wt-04a-t16c，PYTEST_DISABLE_PLUGIN_AUTOLOAD=1）→ **898 passed, 4 failed, 10 skipped**
- 4 failed **全部为 base 既有**（与 B 回执 stash 复跑同口径，独立复跑核实非本变更引入）：
  - `tests/test_devflow.py`×3（worktree `.git` 为文件非目录的沙箱环境问题，主仓应全绿）
  - `tests/test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time`（共享库缺表/时序顺序污染族；**单独 `pytest tests/test_web.py -q` 复跑仍 1 failed**，与本单零关联）
- **0 新增失败**；本单相关用例在全量顺序跑中全绿

## 四、资源残留核对（0 残留）
- uvicorn `18795`/`18796`：已 terminate，`ss -tln` 两端口均无监听 ✓
- 临时 SQLite：6 个 scratch 库（探针×5 + 浏览器×1）全部删除，`glob` 复核 0 残留 ✓
- 浏览器 worktree / 被测 worktree：只读取证，未产生 commit/未改文件 ✓
- 未创建任何 cron、未跑 OCR、未触碰生产/16B/ocr.lock ✓

## 五、未执行项与口径
- **真 MySQL 独立验证未做**：派单明示本单无 DDL/迁移仅 SELECT 谓词，SQLite 取证即可；此口径如实申报（SELECT 谓词跨方言风险低，非降低验证环境）。
- 探针断言为**独立夹具**（前缀 V16C），非复跑 B 的 15 用例；两者口径一致（同 DESIGN §7.3.3/§8.4），交叉印证。
- 普通测试 PASS ≠ OCR/强审查/生产门禁通过；OCR/强审查/合入门禁维持协调者调度，本单不触发。

## 六、结论
- **9 项场景全部 PASS，0 新增失败，0 资源残留。** 建议协调者推进 16C 串行 OCR 裁决与合入门禁核对（合入仍受既有门禁约束，本验证不替代 OCR/强审查）。