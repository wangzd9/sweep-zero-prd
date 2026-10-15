# TESTER TASK-16D 最终联合验收派单：固定集成 SHA `44b6c07`（协调者，2026-10-14 19:41 +08:00）

- status: **TESTER_FINAL_INTEGRATION_DISPATCHED**；owner=TESTER（并入 TASK-16D attempt-1 同一验证链，不新开 attempt）。
- 前置已齐：三叶全部叶接受（B 18:10 / C 14:24 / **A 19:40** `leaf-acceptance-decision-20261014.md`），A 叶 R1-3 双证齐（OCR f7899cfc 0 findings + TESTER F1 增量 34/34 PASS 19:26）。旧集成 `29bd1f4` 含 F1 未修不可合入，**本单测新候选 `44b6c07`**。
- 被测树：`/home/wang/.local/state/rosbag-scene/wt-coord-intcheck-16c` @ `44b6c07`（detached 干净，仅 .venv 软链 untracked；坐标者已从 seed `bd0db1d2` 三 --no-ff 重建：`496a3e4`(A `8958291`) → `f24653c`(B `e399daf`) → `44b6c07`(C `ce5921d`)；祖先链 8958291/e399daf/ce5921d 均已在内，协调者核 OK）。
- 相对旧候选 `29bd1f4` 的**唯一 diff** = `app/services/bag_search_service.py` +18/−10（F1 两谓词 NVIDIA 排除 + F3 docstring + F2 注释），已由 F1 增量段严格 MySQL 面验证；本单做联合确认，不重复 F1 已覆盖的增量断言。
- 验收清单（联合面，口径同 29bd1f4 段、版本换 `44b6c07`）：
  1. **集成面确认**：`grep -c "def data_kind_case" app/services/bag_search_service.py = 0`；F1 谓词在位（`dataset_type != "nvidia_physicalai"` 两分支）；`view_label` 新名口径；`git diff --stat 29bd1f4..44b6c07` = 仅 1 文件 +18/−10（零意外文件）。
  2. **cursor 矩阵**（两查询入口，严格 MySQL 8.4.11 隔离库 `rosbag-t16d-mysql` 复用）：连续翻页无漏无重 / 换筛选 422 / 旧 cursor 兼容 / scene_code None 与空串归一（20 项口径复跑）。
  3. **严格 MySQL 8.4.11 方言**（21/21 口径复跑）：C7 非法日期 422 + C5 双用途双标 UID 唯一 + C6 分类真相 + 幂等。
  4. **浏览器 Console 零异常**：Compose 栈以 `44b6c07` 重建，`/bags`（三 tab+chip「视图：原始数据」）与 `/pipelines/{scene}`（血缘兜底+终态停刷新）同 target 重载 `errors=[]` 且钩子存活；页面 header 版本核 `44b6c07`。
- 口径：夹具自造自清归零实证；真实 headless Chrome 非 HTTP200 替代；不改 seed/各叶树/业务实现；**联合验收 PASS = 16D 最终联合验收完成**，解除合入 HOLD 的 TESTER 面（合入/推送/测试环境更新执行归协调者，按 18:22 用户授权，不含生产）；任一失败回原叶 owner（A/B/C）最小返修，不代修。
- 回执追加到 `test-receipts/TEST-TASK16D/attempt-1.md`（新段：最终联合验收固定 SHA `44b6c07`），给完整命令/退出码/DB 值/Console 证据。
- 背景：F1 返修链（A 交付→机械核验→OCR→TESTER F1 增量）全部收口，本单是 18:22 授权「PASS 后可直接合入」前最后一道联合验证门。