# TASK-07B DONE 裁决（协调者 r136，2026-10-13 08:4x）

## 裁决

**07B（人工纠错/下架）整链收口 DONE，合入 main `4b9f30a`。**

## 收口条件核对（全链证据，逐条）

1. **开发交付**：`5fa0942`→`f4bfcf2`→R2 `68b5188`→R3 `4baf79f`→R4 `62620a3`（5 commit，base `502bf8e` 祖先核 ANCESTOR_OK，13 文件面：迁移+api+models+service+模板/css+web/bags.py+3 测试）。
2. **机械核验**：R4 交付独立核全绿（定向 12 passed 复跑 / ruff 绿 / alembic 单头 `20261012_01_scene_manual` / diff 逐行零越界 / 越界申报独立探针成立）。
3. **OCR 弱审**：attempt-1 10/10 + R2 增量 5/5 + R3 增量 6/6 + R4 增量 1/1 全收口；CONFIRMED CORRECTION 全部闭环（R2-1~10 / R3-1~4 / R4-1~2），剩余 findings 均 LOW/documentation 非阻塞（账 `reviews/TASK-07B/*/ocr-batches.md`）。
4. **强审查**：R2 REVIEW_NOW（call `50c665e4…` REWORK_REQUIRED 4C+1GAP→R3 修复）+ R3/R4 增量复审（call `a8febf1a…` REWORK_REQUIRED 唯一 R4-01 medium→**契约负责人裁决非原 AC 违例不返修**，`r4-01-adjudication-20261013.md`，独立探针证合成态不可由 partial-upgrade 产生）。冻结原 AC 全程未放宽。
5. **独立验证**：TESTER 07B-post-r **08:21 交付 PASS 4/4**（`test-receipts/TEST-TASK07B-post-r/attempt-1.md`）：SR-05 真 MySQL 8.4.11 独占容器双连接同版本并发恰 200/409（守卫拒绝语义非 500，row_version 只+1，审计恰 1 条）/ R4 迁移面真 MySQL+SQLite 双库 upgrade-downgrade-upgrade 三往返 RC=0 + 表缺失态 downgrade 不抛异常 / 定向 12 passed / 页面真实 HTTP 6 项口径；环境用完即毁 0 残留，被测 worktree 零业务改动。
6. **合入后 sanity（协调者独立复跑 main `4b9f30a`）**：alembic heads 单头 `20261012_01_scene_manual` + ruff（service/api/models 3 文件）All checks passed + 07B 定向 3 测试文件 12 passed RC=0。

## 合入记录

- merge commit：`4b9f30af1802f5748c92bd5dbe01741d332509a0`（--no-ff，parents `c2018dd`+`62620a3`，merge-tree 预核零冲突）
- 双推：origin `502bf8e..4b9f30a`、github `c2018dd..4b9f30a`（本地 main 文档 commit `c2018dd`/`30e55a3` 随链一并推送，零 app 面）
- changelog：F-040 `scene-manual-revision-withdraw` pending 候选随收口生成（commit `3d2a075` 双推），**待用户批准，不自行 approved**

## 遗留与边界

- 07C 预览增强：DEFERRED，不自动激活（v0.4 规划口径，非本轮前置）。
- R4-01 合成态 evidence 列 drop=既定接受语义（docstring 已文档化），TESTER post-r 按裁决出单未执行，维持。
- TASK-11 生产门禁维持 PRODUCTION BLOCKED 待用户授权，本轮无生产动作。
- 07B 审计/修订页面面为 16C 保留契约（16C 不得回退），已写入 16C 派单。