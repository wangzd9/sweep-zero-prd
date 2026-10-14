# 回执：TASK-07A attempt-2-r1 最小返修（REVIEW_PENDING）

- 状态：**REVIEW_PENDING（交付冻结）**
- 时间：2026-10-12 13:35 +08:00
- owner：B（前端功能开发群，`wt-04a-t07a` @ `scene/task-07a-visibility-lineage`）
- 派单：`inbox/2号/TASK-07A/attempt-2-r1-dispatch.md`（13:15，协调者 r79 收口轮）
- base：`f94d006`（attempt-1 冻结 commit，双核一致）
- **交付 commit：`8cc6b80`（单 commit，base `f94d006` 之上，3 文件 +51/−5，零越界）**

## 一、实际 diff 范围

1. `app/templates/bags.html`（view-tabs 三链接，+9/−3）：
   - 原静态 `href="/bags"` / `/bags?view=originals` / `/bags?view=all` → 改走与分页同型的 `filters.remove_url('view')` 保留逻辑：`_tab_base = filters.remove_url('view')`（剔除 view、page 归 1、其余 active filter 原样携带），originals/all 在 base 上追加 `&view=…`（base 无 query 时 `?`）。
   - finding #1 修复：带 q/scene_code/dataset_type/vehicle/时间/用途等筛选切 tab 不再丢参数；page 恒归 1；slices tab 无 view 参数（裸 `/bags` 语义）。
   - 无筛选时 `_tab_base`=`/bags`，三链接逐字符退化为旧裸路径（旧书签不回归）。
   - 未动 `app/web/bags.py`（`remove_url` 语义与派单口径一致，无冲突，未触发 §五申报条件）。
2. `app/static/bag-search.css`（+4/−1）：
   - finding #2 修复：新增显式 `.bag-table .col-scene { width: 150px; }`，`.col-name` 26%→18%。
   - 宽度取值依据：9 列合计 18%+150+110+170+130+120+130+80+40，在 `min-width:1000px` 表格宽 1000–1200px 区间均闭合（1000px→180px 名+930px 固定=1110px 由表格 min-width 与 wrapper 滚动共同兜底，场景列恒 150px 确定性成立）；场景列 150px 同时容纳 `.bag-scene-cell` min-width 120px（徽标+标签+历史+父包链接纵向排布），原列不被挤压变形。
3. `tests/test_task07a_visibility.py`（+43/−1）：
   - 新增 `test_bags_view_tabs_preserve_filters_and_reset_page`：带 `q`+`scene_code`+`page=2` 进入 all 视图→三个 tab 均保留 q/scene_code、`page=2/page=1` 均不出现、originals/all 各显式 1 次；无筛选默认视图→三链接退化为旧裸路径。
   - 未删/未弱化任何既有断言；attempt-1 定向 6 用例原样保留。

## 二、自测证据（worktree `wt-04a-t07a`，venv 软链主仓 `.venv`，提交前已删）

| 命令 | 结果 |
|---|---|
| `pytest tests/test_task07a_visibility.py` | **7 passed**（6 原用例+1 新用例），RC=0 |
| `pytest tests -k "scene or web or bags or pipeline"` | **329 passed, 534 deselected**，RC=0（attempt-1 口径 328+1 新增） |
| `ruff check tests/test_task07a_visibility.py` | **All checks passed**，RC=0 |
| 页面实测（自包含 uvicorn 127.0.0.1:18761 + 临时 SQLite `/tmp/t07a_a2r1_smoke.db`，DEMO_DATA=0，不触共享 real 栈/容器/宿主代理/MySQL） | **5/5 PASS**，详见 `reports/TASK-07A/attempt-2-r1.md` |

- 隔离资源 0 残留：临时 SQLite 已删、uvicorn 进程已 terminate、夹具 `_purge`（同定向测试口径）。
- 未执行项：未跑全量 `pytest tests -q`（改动面=1 模板+1 css+1 测试文件，过滤组 329 已全绿覆盖，与 attempt-1 口径一致）；未跑真 MySQL（0 数据库语义/迁移改动，本单纯渲染层）。

## 三、越界申报

- 无。3 文件均在派单 §二允许范围内（bags.html tab 处 + bag-search.css col-scene + 1 条定向断言）；未动 attempt-1 其他 9 文件、未动服务层/状态机、未新增迁移、未改契约；bag_role 下拉按协调者裁决未加。

## 四、等待

- 协调者机械核验→增量 OCR（仅 `bags.html`+`bag-search.css`）→--no-ff 合入 main（核 base 漂移）→TESTER 页面+API 独立验证→07A DONE。
- 交付冻结后不自行合入/推送、不跑 OCR、不扩需求；收到返修（问题 ID 单）按 attempt 续 `scene/task-07a-visibility-lineage`。