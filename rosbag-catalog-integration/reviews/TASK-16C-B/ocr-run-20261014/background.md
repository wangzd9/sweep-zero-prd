# TASK-16C-B attempt-1 OCR 背景（协调者冻结）

- 任务：TASK-16C-B（Bag 三视图叶，父 TASK-16C）；REQ-16/05、AC-16/05。
- 授权来源：用户 2026-10-14 恢复 v0.4 最小界面闭环（见 inbox/control/V04-UI-RESUME-20261014.md），并要求历史 OCR 未修问题入任务。
- base/head：`bd0db1d2a0fc293cb4562e2079e741739bacb0de`（未接受开发 seed，含已知缺陷）→ `e399dafbabd253691dcdf757df6cf5ea9e695ff6`（分支 `b/task-16c-b-bag-views`，worktree wt-04a-t16cb，HEAD 干净）。
- 本叶文件：`app/templates/bags.html`（+6/-6 三处文案/列调整）、新增 `tests/test_task16cb_bag_views.py`（11 用例）。`app/web/bags.py` 零改动（seed 已满足接线面）。
- 关键不变量：
  - DESIGN §7.3.3 视图语义：tab 显示名「切片/原始数据/全部」，URL 值 `slices|originals|all` 不变，旧书签兼容。
  - 共享分类消费 seed 冻结契约 `data_kind_context`，不自建第二套分类规则；双用途包单行双徽标。
  - Web/API 条件取交集，不静默丢筛选；空结果区文案明确「条件均生效，未静默丢弃」，已选 chip 全部保留（remove_url 逻辑）。
  - NVIDIA 无 PipelineRun 的记录车辆列显「—」，不得误显「待认领」。
  - 详情/父包追溯/受控获取入口 `return_to` 携带全部条件（含 view）。
- 允许行为：仅本叶两文件；不改 A 独占 services/api 文件与 `tests/test_task16c_ui_minimal.py`。
- 测试证据：新增 11 用例全绿；联合 75 passed + 2 failed（其中 1 项=seed 固有环境性 `test_bag_search_page_has_bounded_query_count_and_response_time`，seed 与 head 同复现；1 项=`test_web.py:366` 旧 tab 名断言，属共享旧测试文件其他 UI 断言，按入口规定由协调者转 A 单写，B 未代改）；全仓 1106 passed 排除口径在案；ruff 绿。
- 待核实风险：独立浏览器取证与严格 MySQL 面归 TESTER 16D，本 OCR 不替代。
- OCR 遗留映射（本叶承担面）：c06/c07 原 0 findings，本侧 3 处 bags.html 文案改动复验由本增量覆盖（新 SHA `e399daf`，旧结论不宣称覆盖）；C5/C6 谓词修复归 A 叶，本叶仅消费侧断言。