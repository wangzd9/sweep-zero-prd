# Decision：TASK-07A attempt-1 收口裁决（机械核验+OCR 全链完成，2 处 medium findings 回派最小返修）

- 时间：2026-10-12 13:15 +08:00（协调者 cron poll 14ae4556629a r79）
- 交付身份：B `wt-04a-t07a` @ `scene/task-07a-visibility-lineage`，单 commit `f94d0062acb7b5431e386d9cfd99ed8d9c3a85ba`（11 文件 +905/-30，base `453da0c` 双核一致，`merge-base --is-ancestor` 实测）
- 裁决：**ACCEPT_REPORT_WITH_REWORK**（不合入 attempt-1 快照；回派 attempt-2-r1 最小返修 2 条）

## 独立机械核验（协调者本轮实测，非复述回执）

1. 快照：`git rev-parse HEAD=f94d006`、`merge-base --is-ancestor 453da0c HEAD`=yes、worktree 洁净（status 空，.venv 已删申报属实）。
2. 越界：`git show --name-only f94d006` 零 alembic/迁移文件、零状态机/发布逻辑文件；11 文件=回执清单一致。
3. 定向复跑：`pytest tests/test_task07a_visibility.py`=**6 passed**（协调者主仓 venv 独立跑，RC=0）；`.pytest_cache/lastfailed` 仅 3 例 test_devflow 沙箱环境性失败（与 attempt-1 申报一致，非业务红）。
4. 页面实测证据：`reports/TASK-07A/attempt-1.md` 12 段 needle 清单与自包含 uvicorn 口径核读一致（独立端口 18642/临时 SQLite/不触共享栈=越界申报合规，共享 real 栈 1 RUNNING+3 NVIDIA_DONE 在途，local_stack up 会 restart 宿主代理，口径接受）。

## OCR 门禁（串行，8/8 入选 app 文件有效覆盖）

账：`reviews/TASK-07A/attempt-1/ocr-batches.md`（session uuid/时长/排除依据全记录）。
唯一 findings=**bags.html 2 处 medium**：
- #1 view-tabs 静态 href 丢既有筛选 → **CORRECTION**（违反派单 §2.3 旧筛选不回归），回派 attempt-2-r1。
- #2 fixed 布局下 col-scene 无宽度声明 → **CORRECTION**（渲染确定性），随 #1 一并回派。
css 排除裁决：实质风险点已由 #2 覆盖，非静默漏审。tests/* 排除=先例口径（TESTER 独立验证）。

## 待核对项裁决

- **bag_role 独立下拉**（B 回执 §三）：**接受现状**——三视图 tab 覆盖 原始/切片，all+数据类型下拉覆盖 自建；角色三值均可见可选，非 AC 缺口，不进返修范围、不扩需求。
- **强审查**：无用户有效授权→NOT_REQUIRED 预判（P1 UI+只读 API，零迁移零状态机改动），维持人工触发口径；不阻塞合入链，合入后冻结 AC 复核。

## 合入门禁

- attempt-1 `f94d006` **暂不合入**；链路=attempt-2-r1 交付→机械核验→增量 OCR（仅 bags.html+bag-search.css，cron 单文件短路径）→无 high/critical 即 --no-ff 合入 main（核 base 漂移）→TESTER 页面+API 独立验证（含 finding #1/#2 行为断言）→07A DONE→派 07B。
- 07B/07C 维持串行待前置；TASK-11 生产维持 PRODUCTION BLOCKED。