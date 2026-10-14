# TASK-16C-A 查询/API 叶 OCR 合并裁决（协调者，2026-10-14 16:40 +08:00）

## 覆盖身份

- 初 run `7a72eed8`（14:09 起跑）b01 外层 3900s 硬截止 15:14:47：`bag_search_service.py` 15:12:01 review_item_done（2 findings，均 low）；`scene_result_query.py` plan_task context canceled 未完成。该 run 的 scene_result_query 覆盖**作废**。
- 补审 run `0aba25ee`（唯一入口 reuse-run，15:36 起跑，政策 1/1 限额内）：**16:24:11 AWAITING_DECISION**，rc=0，duration 2890.78s，batch_identity_matches=true，coverage 2/2（selected=completed=2，failed=waived=0），remaining_paths 空，manifest `bd0db1d..ff2a005` 精确范围，provider vllm-local / model qwen3.8-27b-fp8，ocr v1.13.0。
- A 叶最终有效 OCR 覆盖 = 初 run 的 `bag_search_service.py` 结果（指纹/文件一致）+ 补审 run 两文件全量结果。两文件全覆盖，`AWAITING_DECISION` 成立（覆盖完成≠通过，本裁决即语义面）。
- 排除：tests/test_task16ca_query_api.py、tests/test_web.py（归 TESTER 16D 独立验证面，排除依据在初 run spec）。

## findings 合并与逐项裁决

初 run 对 `bag_search_service.py` 的 2 条与补审 run 的 2 条为同一文件同一问题面（协调者独立核 wt-01-t16ca 实际代码）：

- **A-OCR-1（F1，low·maintainability，CONFIRMED）— `data_kind_case()` 无调用者的死代码（bag_search_service.py:98-108）**
  - 独立核：全仓 py/html grep 仅 line 98 定义、零调用点；所有筛选调用方已切 `data_kind_pred` 多成员谓词（_apply_filters / scene_result_query.search_scene_bags / web bags.py 197 行 data_kind_context）。
  - 与 OCR C6「归一到共享分类真相或删死 helper，不复制第二分类规则」直接对应：该 CASE 是第二套分类真相，保留即 C6 未真正闭环。seed `bd0db1d` 含旧版 `data_kind_case`（line 38），A 叶重构后残留未删。
  - 裁决：**CONFIRMED，最小返修=删除函数整体**（含 line 98-108），并清理因此变未使用的 import（`case`/`else_` 若他处未用）。
- **A-OCR-2（F2，low·maintainability，CONFIRMED·防御性）— `scene_original` 谓词未排除子包，与兄弟谓词不对称（bag_search_service.py:84-85）**
  - 独立核：`nvidia_original`（line 83）与 `self_built_original`（line 89）均含 `~_scene_slice_pred()`；`scene_original` 仅 `ORIGINAL + _scene_basis_pred()`。Python 标签侧 `data_kind_context`（557-611 行）is_slice 优先，同一包会标 scene_slice 却可被 scene_original 筛出=C6 要消除的筛选/标签分叉形态。
  - 可达性：切片登记 `scene_result_service.py:330` bag_role 固定 SCENE_SLICE，当前无「ORIGINAL 且带 scene_slice 用途且为 derivation 子」的造数路径=实际不可达，故非 CORRECTION 级阻断，但属单源分类口径的防御性缺口。
  - 裁决：**CONFIRMED（防御性），最小返修=补 `~_scene_slice_pred()` 镜像兄弟谓词**，一行改动；TESTER 16D 增加一条该组合夹具断言（筛 scene_original 不返回 derivation 子包）即可。
- 初 run 第 2 条（bag_search_service.py docstring 四舍五入口径不准确）：并入 A-OCR-1 面核对——A 回执 `ff2a005` 后 data_kind_pred docstring 与实现一致（双用途两筛选都命中/UID 一条，DESIGN §7.3.3 明文），**驳回（已在交付中自洽，无残留问题）**。
- 补审 run `scene_result_query.py`：**0 findings**，本文件面无处置项。

## 结论与门禁

- **A 叶接受门禁维持关闭**：两条 CONFIRMED（均 low）回派 A 最小返修（A-OCR-1 删死函数 + A-OCR-2 补一行谓词，同文件同一次 commit）→ 交付冻结 → 协调者机械核验 → **增量 OCR 仅 `bag_search_service.py` 单文件**（head 变化使旧覆盖不自动续用；scene_result_query 未变不重跑）→ 零 CORRECTION 级 + TESTER 16D 增量面（含 A-OCR-2 组合夹具）→ A 叶接受。
- 非本裁决扩需：不新增任务、不动其他文件、不重审 A 叶全量。
- 证据：reviews/TASK-16C-A/ocr-run-20261014-retry1/run/{state.json,b01.log,b01-diagnosis.json}；初 run 15:12:01 findings 见补审 retry_reason 与协调者 14:xx 台账段。

## 裁决冲突统一（协调者，2026-10-14 17:30 +08:00 补段）

- 本目录 16:35 中间记录 `reviews/TASK-16C-A/ocr-run-20261014-retry1/ocr-verdict.md` 将 F2（scene_original 缺子包排除）裁为 REJECTED，理由「bag_role==ORIGINAL 天然排除 slice」。**该理由不成立**：`_scene_slice_pred()` 含 derivation 子（`bag_uid in BagDerivation.child_bag_uid`），16C-c03-04 统一口径正是「SCENE_SLICE 角色**或有效血缘**即子包」，存在 derivation 子而 bag_role=ORIGINAL 的合法组合（历史切片面），F2 维持 **CONFIRMED（防御性）**。本 ruling（16:42，独立核代码）为最终合并裁决，16:35 记录被覆盖，仅留痕。
- A 已按本 ruling 交付返修 `4838ef8`（17:15:40，+3/−15，仅 bag_search_service.py）。协调者 17:2x 机械核验：祖先核 ff2a005→4838ef8 通过、`data_kind_case` 零残留、`~_scene_slice_pred()` 已入 scene_original 分支、ruff 全绿、独立复跑 74 passed + 1 failed（seed 固有 bounded-query，stash 同口径）。
- **新增 A 清理项（来源 B 叶 OCR run `513ab61d` 17:09 收口 1 finding，裁决 `reviews/TASK-16C-B/ocr-run-20261014/ocr-verdict.md`）**：`bag_search_service.py:664` `view_label` 仍为旧名 `{"originals": "原始包", "all": "全部/历史"}`，与 B 叶 tab 新名（切片/原始数据/全部）同屏两套叫法，CONFIRMED UI 一致性低危，修复点在 A 叶文件。已随 `inbox/1号/TASK-16C-A/ocr-r1-rework-2-dispatch-20261014.md` 并入 A 同冻结链（base 续 4838ef8）。
- OCR 口径统一：`4838ef8` 与 view_label 续 commit 同文件小 diff，**A 最终 head 冻结后只做一次单文件增量 OCR**（不逐 commit 两跑）；两份 verdict 中「不烧 OCR/VLM，机械核验即可」的口径作废，以 ocr-and-merge「返修产生新 head，旧审查不自动覆盖新产物」为准。A 叶接受门禁维持关闭至：view_label 续 commit + 机械核验 + 单文件增量 OCR + TESTER 增量面（含 A-OCR-2 组合断言与 view_label 页面断言）。