# TASK-16C 三叶正式集成候选（协调者冻结，17:5x +08:00）

- 固定集成 SHA：`29bd1f4`（wt-coord-intcheck-16c，从 seed `bd0db1d2` 干净重建，三 --no-ff 零冲突）
- 组成（三叶最终 head）：
  - A `1489bc6`（含 OCR 清理：删 `data_kind_case` 死代码 + `view_label` 统一「原始数据/全部」）
  - B `e399daf`（bags.html 三视图 tab）
  - C `ce5921d`（pipeline_detail 血缘兜底 + C8 retry-form guard）
- 集成面回归（协调者实测）：六测试文件 `test_task16ca_query_api`+`test_task16cb_bag_views`+`test_task16cc_scene_detail`+`test_task16c_ui_minimal`+`test_web` 合跑 → **101 passed + 1 failed**；唯一 failed = `test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time`（**seed 固有 no such table 顺序依赖**，TESTER 16D 回执 line 63 在案口径一致，非候选引入）。`ruff check`（bag_search_service/scene_result_query/pipelines）All checks passed。
- 与旧集成候选 `1d7f15ce` 差异：A 面 `ff2a005`→`1489bc6`（补入两处 OCR 清理），其余 B/C 不变；`1d7f15ce` 为临时树作废。
- 性质：**联合验收输入**，非正式集成提交；正式合入待 TESTER 16D 联合验收（固定 SHA `29bd1f4`）PASS + 用户授权。

## 派 TESTER 16D 联合验收（固定 SHA 段，按 V04-UI-RESUME 口径"最终集成 SHA 由协调者提供后再联合验收"）
- 被测：`wt-coord-intcheck-16c` @ `29bd1f4`（detached，树干净）。
- 必做（此前各叶增量 PASS 已覆盖单叶面对，本段只补联合面 + A 清理增量）：
  1. **A 清理面增量确认**：`29bd1f4` 相对 `563a91a`（TESTER 已验的 A head）新增两处 = 删 `data_kind_case`（无行为）+ `view_label` 改「原始数据/全部」（字面量）。确认：`grep -c "def data_kind_case" = 0`；`view_label` 行 = `{"originals":"原始数据","all":"全部"}`；`test_web.py` 三 tab 断言（切片/原始数据/全部）绿；chip 渲染与 tab 同叫法（浏览器 `/bags?view=originals` 已选筛选 chip 显示「视图：原始数据」而非「原始包」）。
  2. **联合验收固定 SHA 段 cursor 矩阵**（此前保留到此，line 92）：在 `29bd1f4` 上对两查询入口（`/bags` + `/api/v1/bags` + `scene_result_query`）执行：连续翻页无漏无重（`test_cursor_chain_no_gap_no_dup` 口径的真实数据复跑）、换筛选 422 不复用旧上下文、旧 cursor（无新键/scene_code None vs 空串）兼容。
  3. **严格 MySQL 8.4.11 日期/分类方言**（复用已建隔离库 `rosbag-t16d-mysql`）：在 `29bd1f4` 上复跑 C7 非法日期 422 + C5 双用途 UID 唯一 + C6 分类真相（21/21 口径），确认 A 清理未改变谓词语义。
  4. **浏览器 Console 零异常**（`29bd1f4` Compose 栈重建）：`/bags`（三 tab + chip）、`/pipelines/{scene}`（血缘兜底 + 终态停刷新）同 target 重载 `errors=[]`。
- 结论口径：联合验收 PASS 才可合入；任一失败回原叶 owner（A/B/C），不代修。
- 夹具自造自清归零、浏览器真实 headless Chrome（非 HTTP200 替代）、不改 seed/其他叶树。