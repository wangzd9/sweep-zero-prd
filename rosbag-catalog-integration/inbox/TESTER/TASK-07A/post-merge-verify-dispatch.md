# 派单：TASK-07A 合入后独立验证（main `caf385b`，07A 收口前最后一环）

- status: ACCEPTED（TESTER 14:29 交付 attempt-1 32/32 PASS；协调者 14:50 裁决 07A DONE，decision inbox/coordinator/TASK-07A/post-merge-verify-acceptance-decision-20261012.md）
- 派单时间：2026-10-12 14:01 +08:00（协调者 coord-poll-20261012-133053）
- owner：TESTER
- 被测快照：**main `caf385bfdb865a4d660b0f0e68fca5969615b38a`**（--no-ff 合入 attempt-1 `f94d006` + attempt-2-r1 `8cc6b80`，origin/main 双核一致）

## 范围（attempt-1 AC 不回归 + attempt-2-r1 两条 finding 行为断言）
1. **view-tabs 筛选保留（finding #1）**：带 `q`（及 scene_code/dataset_type 等任一筛选）访问 `/bags`，切 originals/all tab 链接携带既有筛选且 `page` 恒 1；切回 slices tab=裸 `/bags` 语义；无筛选时三 tab 链接退化为旧裸路径 `/bags`、`/bags?view=originals`、`/bags?view=all`。
2. **col-scene 宽度（finding #2）**：`/bags` 表格 9 列渲染，`.col-scene` 显式 150px、名称列收窄后原列不溢出（innerText/渲染断言即可，不截图）。
3. **attempt-1 面不回归**：三视图行正确（原始/切片/历史标注）、lineage 只读 API 行为、pipelines 场景可见、详情双向跳转（attempt-1 回执与 `reports/TASK-07A/attempt-1.md` 12 段 needle 清单口径）。

## 口径
- 自包含 uvicorn 独立端口 + 临时 SQLite（DEMO_DATA=0），不触碰共享 real 栈/容器/宿主代理/MySQL；结束清残留。
- 本地栈镜像若烤旧代码，以 main `caf385b` 源码直跑为准（本次被测面=模板/css/API 只读，无迁移无镜像依赖变化）。
- 交付：`test-receipts/TEST-TASK07A-post-merge/attempt-1.md`（PASS/FAIL + 逐条证据）。

## 收口
PASS → 协调者写 07A DONE → 派 07B；FAIL → 回派 B 定位（不跨模块）。