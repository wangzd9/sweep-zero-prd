# TASK-16C-A 转派单勘误续单（协调者，2026-10-14 13:22 +08:00）

- 状态：REWORK_DISPATCHED。并入 A 的 TASK-16C-A attempt-1 同一冻结链（不新开 attempt）；同 worktree `wt-01-t16ca`、同 branch `a/task-16c-a-query-api`，base 续 `563a91a8a4ac56031c4ae532c8cbaa4141733d77`。
- 来源：协调者集成契约核验（seed+A`563a91a`+B`e399daf` 干净合并候选，worktree `wt-coord-intcheck-16c`）：`pytest tests/test_web.py -q` → 39 passed + 2 failed；其中 `test_bag_list_shows_default_results_and_route_filter` 失败于 **line 364 `assert "当前可用切片" in page.text`**（B 叶 `e399daf` tab 显示名改「切片」后旧断言失配）。`563a91a` 已修 line 365（原始包→原始数据）即本转派单原口径；line 364/366 失配系原转派单范围漏项（原单只核了 366 一处，A 按「不自行扩面」口径执行无误）。
- 失败证据：协调者候选复跑（13:12 实测，`wt-coord-intcheck-16c`）`tests/test_web.py::test_bag_list_shows_default_results_and_route_filter` FAILED（断言 line 364）；seed 口径该断言原为「当前可用切片/原始包/全部/历史」三行，B 模板现渲染「切片/原始数据/全部」。

## 变更（仅 2 处断言，同一转派单面，DESIGN §7.3.3 新标签口径）

- `tests/test_web.py:364`：`assert "当前可用切片" in page.text` → `assert "切片" in page.text`
- `tests/test_web.py:366`：`assert "全部/历史" in page.text` → `assert "全部" in page.text`
- line 365（原始数据）`563a91a` 已改，不动。
- 同函数内其余断言（`view-tab active` href、demo UID 排除/包含、表格结构）不变；`test_task07a_visibility.py` 与 `test_task16c_ui_minimal.py` 已在候选复跑全绿（52 passed 合跑含两文件），**不需改动**，A 复跑一次留证即可。

## 边界与自测

- 只允许改 `tests/test_web.py` 上述 2 行断言；不碰查询面实现（bag_search_service/scene_result_query/sources.py）、不碰 B/C 域文件。若复跑发现同函数其他断言仍失配，回协调者核，不自行扩面。
- 复跑 `pytest tests/test_web.py tests/test_task16c_ui_minimal.py -q`（seed 固有环境性失败 `test_bag_search_page_has_bounded_query_count_and_response_time` 不计本账，口径在案）。
- 交付=续 commit 冻结 + 回执补本勘误段（新 head/2 行 diff/复跑结果）；状态回 REVIEW_PENDING。

## 协调者核验段（2026-10-14 13:27 +08:00）

- A 勘误续 commit `ff2a005`（13:18:27 落盘）机械核验全绿：`tests/test_web.py` 仅 2 行断言（364 当前可用切片→切片、366 全部/历史→全部）、同 branch/worktree、base 链 `bd0db1d` 祖先核过、零越界。
- 集成候选重建：`wt-coord-intcheck-16c`（seed + A`ff2a005` + B`e399daf` + C 返修`ce5921d`，三 --no-ff 合并 **零冲突**，候选 head `1d7f15c`，协调者临时树，非正式集成）。
- 候选复跑（13:27 实测）：`test_web.py`+`test_task07a_visibility.py`+`test_task16c_ui_minimal.py`+`test_task16ca_query_api.py`+`test_task16cb_bag_views.py`+`test_task16cc_scene_detail.py` 合跑 **108 passed + 1 failed**；唯一失败 `test_bag_search_page_has_bounded_query_count_and_response_time` = seed 固有环境性（口径在案，不计本账）。**原 line 364/366 失配已消除**。
- 全仓复跑（13:32 实测，候选 `1d7f15c`）：**1163 passed + 4 failed**；4 failed = test_devflow×3（seed `bd0db1d` 原树复跑同 3 failed，worktree 环境固有）+ test_web bounded 计时（seed 固有 no such table 顺序依赖）。**零候选回归**。
- 状态：A 叶勘误闭环，待 TESTER 独立验证（MySQL 关键行为）；A 叶 OCR 以 `ff2a005` 为最终冻结 head 排队（**被工具链 v1.13.0 版本门禁阻塞**，裁决在用户面）。