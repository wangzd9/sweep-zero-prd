# TASK-16D 联合验收派单：固定集成 SHA `29bd1f4`（17:5x，协调者）

- status: DISPATCH；owner=TESTER
- 三叶增量面你已各自 PASS（A `563a91a`/B `e399daf`/C `522bb3f`+`ce5921d` 返修面），本单=**联合验收固定 SHA 段**，按 V04-UI-RESUME 口径"最终集成 SHA 由协调者提供后再联合验收"执行。
- 被测树：`/home/wang/.local/state/rosbag-scene/wt-coord-intcheck-16c` @ `29bd1f4`（detached，树干净；从 seed `bd0db1d2` 三 --no-ff 重建，A 面已含 OCR 清理 `1489bc6`）。
- 验收清单（只做联合面+A 清理增量，不重复各叶已 PASS 的增量面）：
  1. **A 清理面增量确认**：`grep -c "def data_kind_case" app/services/bag_search_service.py = 0`；`:664 view_label = {"originals":"原始数据","all":"全部"}`；浏览器 `/bags?view=originals` 已选筛选 chip 渲染「视图：原始数据」（与 tab 同叫法，不再是「原始包」）；`test_web.py` 三 tab 断言绿。
  2. **cursor 矩阵（此前保留到固定 SHA 段，attempt-1.md line 92）**：两查询入口连续翻页无漏无重 / 换筛选 422 不复用旧上下文 / 旧 cursor（无新键、scene_code None vs 空串）兼容。
  3. **严格 MySQL 8.4.11 方言（复用已建 `rosbag-t16d-mysql` 隔离库）**：C7 非法日期 422（非 500）+ C5 双用途双标 UID 唯一 + C6 分类真相（21/21 口径），确认 A 清理未改变谓词语义。
  4. **浏览器 Console 零异常**：`29bd1f4` Compose 栈重建，`/bags`（三 tab+chip）与 `/pipelines/{scene}`（血缘兜底+终态停刷新）同 target 重载 `errors=[]` 且钩子存活。
- 口径：夹具自造自清归零；真实 headless Chrome 非 HTTP200 替代；不改 seed/其他叶树；**联合验收 PASS 才允许合入**，任一失败回原叶 owner（A/B/C）不代修。
- 回执追加到 `test-receipts/TEST-TASK16D/attempt-1.md`（新段：联合验收固定 SHA `29bd1f4`），给完整命令/退出码/DB 值/Console 证据。
- 背景：用户 17:5x 群内指令"直接推进"——16C 三叶开发+OCR+返修+各叶 TESTER 增量全闭环，本单是合入前最后一道联合验证门；验收绿后协调者提请用户授权合入。