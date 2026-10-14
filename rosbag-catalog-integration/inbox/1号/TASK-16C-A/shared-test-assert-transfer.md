# TASK-16C-A 共享旧测试断言转派（协调者，2026-10-14）

- 状态：DISPATCHED（并入 A 的 TASK-16C-A attempt-1 同一冻结链，不新开 attempt；若 A 叶已冻结，作为最小追加单在同一 worktree 续 commit 后重新交付冻结）。
- 来源：执行者 B 交付回执 `receipts/TASK-16C-B/attempt-1.md` §6.1 越界申报。按 [当前入口](../../control/V04-UI-RESUME-20261014.md)「共享旧测试文件其他 UI 断言由 B/C 提出，协调者转 A 单写，禁止多人并改」转派本单。
- 变更（仅 1 处断言，B 实测证据在案）：
  - `tests/test_web.py:366`：`assert "原始包" in page.text` → 改为 `"原始数据"`（B 叶 tab 改名「切片/原始数据/全部」，URL 值不变；新标签为 DESIGN §7.3.3 口径）。
  - `tests/test_task16c_ui_minimal.py`：B 实测未断言旧 tab 名，15 passed 全绿，**无需改动**（B 已核，A 交付前复跑一次即可）。
- 范围边界：只允许改上述断言面；不得动 bag_search_service.py/scene_result_query.py/sources.py 的查询面实现（那是 A 叶正题）；若复跑发现 test_web.py 其他断言因 tab 改名连带失败，先回协调者核是否同样转 A，不自行扩面。
- 验收：A 叶冻结时 `tests/test_web.py` 相关断言全绿（seed 固有环境性失败 `test_bag_search_page_has_bounded_query_count_and_response_time` 除外，seed/head 同口径复现在案，不计 A 账）。
- 协调者核账：C 叶 OCR（run `e7a5580cdf9f4eed8b448aad1c61f53b`）在途持锁，B 叶 OCR 排队；A 交付冻结后串行提交。B 叶本单交付后机械核验+OCR+TESTER 独立验证通过即接受，不等 A。

## 追加（协调者，2026-10-14 12:41）：A 12:39 交付 `a1e416a` 未含本转派单，需续 commit

- **事实**：A attempt-1 已冻结 `a1e416a`（12:39:51 事件 `a-t16ca-attempt1-delivery-20261014T123951`），回执未提本转派单；`tests/test_web.py:366` 在 A 冻结树仍为旧断言 `原始包`（seed 口径，本叶独立验证面不受影响）。
- **要求（本单原口径不变）**：同一 worktree `wt-01-t16ca` 续 1 个最小 commit——`tests/test_web.py:366` 断言 `原始包` → `原始数据`（若复跑发现 tab 改名连带其他断言失败，先回协调者核，不自行扩面）；复跑 `tests/test_task16c_ui_minimal.py` 一次并在回执补记；重新冻结交付（新 head），回执追加 attempt-1 续单段。
- **对 OCR 的影响**：A 叶 OCR 快照以**续 commit 后的最终冻结 head** 为准，协调者暂不对 `a1e416a` 起 OCR（避免审查身份重开）；B/C 叶不受影响。
- **门禁不变**：A 叶最终接受仍需 OCR 裁决 + TESTER 独立验证（MySQL 关键行为交 TESTER 已申报在案）。