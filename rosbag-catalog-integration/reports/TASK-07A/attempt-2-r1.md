# 报告：TASK-07A attempt-2-r1 页面实测证据（自包含 uvicorn 独立端口 + 临时 SQLite）

- 时间：2026-10-12 13:3x +08:00
- 口径：沿用 attempt-1 自包含实例——`127.0.0.1:18761` 独立端口、临时 SQLite `/tmp/t07a_a2r1_smoke.db`（DEMO_DATA=0）、不触碰共享 real 栈（:18080/:8181）/容器/宿主代理/MySQL；对同一份 worktree 代码（`8cc6b80`）做真实 HTTP 渲染断言。
- 夹具：1 原始包父袋 + 2 AVAILABLE 切片（`a2r1-abc012345` / `a2r1-xyz012345`）+ 1 场景 run（`slope_a2r1`），经定向测试同型 `_mk_bag/_mk_der` 构建。
- 脚本：`/home/wang/.hermes/cache/scratch/t07a_a2r1_smoke.py`（真实 HTTP `urllib` 断言，非 TestClient）。

## 结果 5/5 PASS

1. `tab_preserve_q_reset_page` PASS：`/bags?q={s1}&page=2` 渲染的三个 view-tab 链接均携带 `q={s1}`；导航内 **`page=2` 与 `page=1` 均不出现**（page 归 1 即省略）；`view=originals`/`view=all` 各显式 1 次；slices tab href 无 `view=` 参数（裸 `/bags` 语义）。
2. `tab_preserve_in_originals` PASS：`/bags?q={s1}&view=originals` 渲染的三 tab 同样全部保留 `q`（跨视图切换不丢筛选）。
3. `nine_cols_col_scene_150` PASS：`/static/bag-search.css` 含 `.bag-table .col-scene { width: 150px; }` 显式声明；`/bags` 渲染 colgroup 实测 **9 个 `<col>`**（含 `col-scene`），`table-layout:fixed` 下场景列宽度确定性成立（不再吸收剩余 ~57px）。
4. `q_filter_rows_correct` PASS：slices 视图带 q 行集合=仅 s1（s2 不出现）；all 视图带 q 同口径正确。
5. `scene_code_preserve` PASS：`/bags?q={s1}&scene_code=slope_a2r1&view=slices` 三 tab 均保留 `scene_code`（3/3）。

## 清理

- uvicorn terminate 后退出确认；夹具 `_purge`（der/segment/version/parent+s1+s2）；临时 SQLite 文件删除；隔离资源 0 残留。