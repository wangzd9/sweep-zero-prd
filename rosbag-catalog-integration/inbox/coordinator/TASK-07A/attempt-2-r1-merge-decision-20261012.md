# Decision：TASK-07A attempt-2-r1 收口（机械核验+增量 OCR 全绿，--no-ff 合入 main `caf385b`）

- 时间：2026-10-12 14:01 +08:00（协调者 cron poll 14ae4556629a，coord-poll-20261012-133053）
- 交付身份：B `wt-04a-t07a` @ `scene/task-07a-visibility-lineage`，单 commit `8cc6b80`（3 文件 +51/−5，base `f94d006`）
- 裁决：**ACCEPT_MERGED**（合入 main，待 TESTER 独立验证后 07A 才可写 DONE）

## 独立机械核验（协调者本轮实测）
1. 快照：`HEAD=8cc6b80`、`merge-base --is-ancestor f94d006 8cc6b80`=yes、worktree 洁净、单 commit 3 文件与回执一致。
2. 越界：零 alembic/迁移/服务层文件；`app/web/bags.py` 未动（finding #1 用既有 `filters.remove_url` 实现，无 §五 申报情形）。
3. 语义核（逐行 diff）：
   - finding #1：三视图 tab 走 `_tab_base = filters.remove_url('view')`（与分页同型，剔除 view、page 归 1、其余筛选原样携带）；无筛选时 `_tab_base`=`/bags` 且三链接逐字符退化为旧裸路径（旧书签不回归）；originals/all 追加 `&view=…` 分隔符判断正确。
   - finding #2：`.col-scene { width: 150px }` 显式声明 + `.col-name` 26%→18%，fixed 布局 9 列闭合，`.bag-scene-cell` min-width 120px 不再与 auto 列冲突。
4. 独立复跑：`pytest tests/test_task07a_visibility.py`=**7 passed**（主仓 venv，RC=0）；`ruff check` 测试文件 **All checks passed**。

## OCR 门禁（串行，2/2 入选文件有效覆盖）
账：`reviews/TASK-07A/attempt-2-r1/ocr-batches.md`。bags.html 0 findings（session 8055d30e）、bag-search.css 0 findings（session b105894b；v1 420s reap 作废已记）；tests 排除=default_path 先例。

## 合入
- `git merge --no-ff 8cc6b80` → main `caf385b`，push origin 双核一致（453da0c..caf385b）。
- 合入后 sanity：定向 7 passed RC=0。

## 后续链
- TESTER 独立验证（派单 `inbox/TESTER/TASK-07A/post-merge-verify-dispatch.md`：三视图 tab 筛选保留/page 归 1/退化裸路径 + col-scene 150px 渲染 + lineage API 行为断言，自包含口径）。
- PASS → 07A DONE → 派 07B；FAIL → 按定位回派 B。
- 强审查：无用户有效授权维持人工触发，NOT_REQUIRED 预判（P1 UI+只读 API 零迁移）不变。