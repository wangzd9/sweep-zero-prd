# 派单：TASK-07A attempt-2-r1 最小返修（bags.html 视图切换保留筛选 + col-scene 列宽确定性）

- status: ACKED
- 派单时间：2026-10-12 13:15 +08:00（协调者 cron poll 14ae4556629a，r79 收口轮）
- 任务：TASK-07A 最小返修 attempt-2-r1（不新增范围，不重做 attempt-1 其他文件）
- owner：B（前端功能开发群，wt-04a-t07a，attempt-1 原 owner）
- base：`f94d006`（attempt-1 冻结 commit，`wt-04a-t07a` 分支 `scene/task-07a-visibility-lineage` 上继续）
- 下游：本单收口→协调者增量 OCR（`-c` 新 commit，仅返修文件）→合入 main→TESTER 页面+API 独立验证→07A DONE→派 07B。

## 一、返修依据（OCR T07A-r1 串行逐文件 8/8 覆盖，唯一 findings 文件 bags.html，均 medium）

1. **view-tabs 静态 href 丢既有筛选（finding #1，违反派单 attempt-1 §2.3「既有车辆/时间/关键词筛选不回归」）**：
   `app/templates/bags.html` L16-19 三个视图 tab 用静态 `/bags`、`/bags?view=originals`、`/bags?view=all`。用户带筛选（q/dataset_type/status/vehicle/start_from/start_to/scene_code/purpose/page）点击 tab 切换时全部丢失。
   修法口径（与分页一致）：tab 链接走 `state.url(...)` 同型参数保留逻辑——只替换 `view` 参数（slices=省略 view 保持裸 `/bags`、originals/all 显式）、`page` 归 1，其余 active filter 原样携带。
2. **colgroup 第 9 列 col-scene 宽度不确定（finding #2，table-layout:fixed 下吸收剩余 ~57px）**：
   `app/static/bag-search.css`：`.bag-table` fixed 布局只声明原 8 列宽度。补显式 `.bag-table .col-scene { width: ... }` 并相应收窄 `.col-name`（现 26%），使场景列宽度确定性成立（`.bag-scene-cell` min-width 120px 不再与 auto 列冲突）。宽度取值由 B 按 9 列布局自行定，保证现有列不被挤压变形。

## 二、范围与禁止

- 只改 `app/templates/bags.html`（tab 链接处）+ `app/static/bag-search.css`（col-scene 宽度）；允许为 finding #1 补 1-2 条定向断言（tests/test_task07a_visibility.py：带筛选切 tab 后 query string 保留 q/scene_code 且 page 重置、切回 slices 恢复裸路径语义）。
- 不动 attempt-1 其他 9 文件、不动服务层/状态机、不新增迁移、不改契约（lineage envelope/三视图语义不变）、不做 07B/07C。
- bag_role 独立下拉：协调者已裁决**接受现状**（三视图 tab+数据类型下拉覆盖角色三值），**不要加**，本单范围不含。
- 页面实测口径沿用 attempt-1（自包含 uvicorn 独立端口+临时 SQLite，不触碰共享 real 栈/容器/宿主代理），补充两条：①带 q 筛选在 slices↔originals↔all 间切 tab，筛选保留、page 归 1、目标视图行正确；②9 列布局下场景列宽度稳定（innerText/渲染断言即可，不截图）。

## 三、AC（冻结，attempt-1 AC 不回归 + 两条返修断言）

1. finding #1 修复：`/bags?view=originals&q=abc` 渲染的 tab 链接携带 q；slices tab=裸 `/bags`（view 省略，既有语义）；page 恒 1；scene_code/purpose/dataset_type/vehicle/时间筛选同样保留。
2. finding #2 修复：`.col-scene` 有显式宽度声明，fixed 布局下 9 列总宽闭合（无剩余吸收），`.col-name` 相应调整后原列不溢出。
3. attempt-1 定向 6 用例 + 过滤组 328 全绿不回归；ruff 绿。
4. 页面实测补充两条 OK（自包含实例）。

## 四、交付物

- 新 commit（base `f94d006` 之上，单 commit）+ 回执 `receipts/TASK-07A/attempt-2-r1.md`（REVIEW_PENDING，列实际 diff 范围+自测证据）+ 页面实测证据追加 `reports/TASK-07A/attempt-2-r1.md`。
- 交付后：协调者机械核验→增量 OCR（仅返修文件，cron 单文件短路径）→无 high/critical 即 --no-ff 合入 main（核 base 漂移零冲突）→TESTER 页面+API 独立验证→07A DONE→派 07B。

## 五、停止条件

- 交付冻结后不自行合入/推送、不跑 OCR、不扩需求；返修只限本单两条 finding。
- 若 finding #1 修法与既有 `state.url` 工具冲突需要动 web/bags.py：先 ACK 申报口径，不擅自扩大 diff。