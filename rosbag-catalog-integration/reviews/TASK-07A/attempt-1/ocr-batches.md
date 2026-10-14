# OCR 批次账：TASK-07A attempt-1（f94d006）

base `453da0c` / head `f94d0062acb7b5431e386d9cfd99ed8d9c3a85ba`，wt-04a-t07a，单 commit 11 文件 +905/-30。
协调者串行触发（ocr.lock 持有，ocr v1.12.13，provider vllm-local Qwen3.8-27b）。
排除依据：tests/*（default_path，独立验证挂 TESTER）；app/static/bag-search.css（生成式样式，finding #2 由协调者裁决覆盖，不静默漏审）。
入选 app 文件 8 个：sources.py / bag_search_service.py / scene_result_query.py / web/bags.py / bags.html / detail.html / pipelines.html（全量 wc -l 均 <1400 行）。

cron 回合 420s terminal 硬上限实测（2026-10-12 11:32-13:0x）：多文件合批触发 context compaction 后单轮必超 420s 被 reap（7 文件整批 5m43s、2 文件 g2 组 3 次 resume 均未收口）；单文件（或 10 行+17 行小组）248-318s 可收口。**本轮采用单文件逐审短路径**，reap 后一律 --resume 断点续审（session 实时落盘，已完成组不重跑）。

| batch_id | 输入 | 运行 | 结果 |
|---|---|---|---|
| T07A-r1（整批 7 文件） | 8 入选-1(css) | session eed6889b，5m43s，7/7 item cancelled | **FAILED 不算通过**（cron 会话 reap，context canceled），作废改单文件 |
| T07A-r1f-pipelines（单） | pipelines.html | session 8d88be20→c894b135，420s reap | 未完成，并入 g1 |
| T07A-r1f-g1（2 文件） | sources.py + pipelines.html | session ef0780e9，151s | **0 findings** |
| T07A-r1f-g2（2 文件） | detail.html + web/bags.py | session 6db74bf9→6a35662c→eead83dc，3 次 resume 均 420s reap | **拆单文件重试** |
| T07A-r1f-bagspy（单） | web/bags.py | session 2829e0d0，248s | **0 findings** |
| T07A-r1f-dethtml（单） | detail.html | session 1fc9cfa4→41eb7ad4(2 次 llm_error)→21be1698，291s | **0 findings** |
| T07A-r1f-bagshtml（单） | bags.html | session c03c3551(420s reap)→cc864786 resume | **2 findings（medium）见下** |
| T07A-r1f-scenres（单） | scene_result_query.py | session a6744857，254s | **0 findings** |
| T07A-r1f-bagsvc（单） | bag_search_service.py | session 462e2cb5→a8a5a535(均 reap 无 manifest 不可 resume)→b3f4fb5a，318s | **0 findings** |

**覆盖结论**：8/8 入选 app 文件全部取得有效 OCR 结果；唯一 findings 在 bags.html。css 排除已裁决（见下 #2）。tests/* 排除=先例口径（独立验证挂 TESTER）。

## findings（bags.html，均 severity=medium，category=maintainability）

1. **view-tabs 静态 href 丢失既有筛选**：三个视图 tab 用静态 `/bags`、`/bags?view=originals`、`/bags?view=all`，用户带筛选（q/dataset_type/status/vehicle/时间/scene_code/purpose/page）切 tab 时全部丢失。分页已用 `state.url(...)` 保留参数，tabs 应同口径（只换 view、page 归 1）。**裁决=CORRECTION，违反派单 2.3「既有车辆/时间/关键词筛选不回归」**，回派 B 最小返修 attempt-2-r1。
2. **colgroup 第 9 列 col-scene 无宽度声明**：`.bag-table { table-layout: fixed }` 只声明了原 8 列宽度，新场景列吸收剩余 ~57px，宽度不确定（`.bag-scene-cell` min-width 120px 在 auto 列下偏紧）。**裁决=CORRECTION（渲染确定性）**，随 finding #1 一并最小返修（bag-search.css 补 `.col-scene` 宽度并相应收窄 `.col-name`）。css 文件的 OCR 排除因此不成立为"漏审"——该文件的实质风险点已由本 finding 覆盖。

## 裁决记录（协调者，2026-10-12 13:1x）

- **bag_role 独立下拉**（B 回执 §三 待核对项）：裁决**接受现状**——三视图 tab 覆盖 原始/切片 维度，all 视图 + 既有数据类型下拉覆盖 自建 维度，角色三值均可见可选，不构成 AC 缺口；不进返修范围、不扩需求。
- 合入门禁：attempt-1 `f94d006` **暂不合入**，等 attempt-2-r1（bags.html+bag-search.css 最小返修）交付→增量 OCR（`-c` 新 commit，仅返修文件）无 high/critical→再合入→TESTER 页面+API 独立验证（含 findings 两条行为断言）。
- 强审查：无用户有效授权，维持人工触发；07A 为 P1 UI+新只读 API，NOT_REQUIRED 预判（合入后按 strong-review 口径冻结 AC 复核，不阻塞）。