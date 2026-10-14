---
task: TASK-03B
attempt: 2
owner: 3号
status: ACCEPTED
type: rework-minor
updated: 2026-10-09 14:1x
base: a8fac99
worktree: /home/wang/.local/state/rosbag-scene/wt-03b
---
# 03B 小返修：F2 隔离库并发实测发现（1 条 medium，~5 行改动）

协调者按验收标准（不接受"SQLite 单会话无法实证"为终态）在 MySQL 8.4 隔离库
（docker network + python:3.10-slim + pymysql 1.1.1）对 patch_submission 做了
**双独立会话同代次并发竞争**实测，证据：`reviews/TASK-03B/attempt-2/f2-isolation-evidence.log`。

## 事实
- 守卫**生效**：竞争双方恰好 1 个成功（row_version 1→2），另 1 个的 UPDATE 影响 0 行——
  数据一致性无破口（不会出现双 200 静默覆盖）。
- 但失败方**抛 `StaleDataError`（500）而非 409 `ROW_VERSION_CONFLICT`**：
  `result.rowcount == 0` 的 409 分支（ingest_service.py ~440 行）不可达——
  失败会话内该 UPDATE 在到达 rowcount 判定前就抛了 StaleDataError，
  全库无 StaleDataError 处理（grep 确认），API 面表现为 500。
- 与 DESIGN/回执承诺（"rowcount=0 → 409 + 回滚本事务内容写"）不符。

## 要求
1. 让 409 路径在真并发下可达：`sa_update(...).execution_options(synchronize_session=...)`
   取不抛 StaleDataError 的策略（fetch/evaluate 择一实测），或捕获 StaleDataError 转
   HTTPException(409, "ROW_VERSION_CONFLICT...") 同口径回滚——哪种都行，但必须**用隔离库
   双会话竞争复测**证明：1 OK + 1 HTTP 409、row_version=2、内容不被覆盖。
2. 回归测试：单会话无法模拟（同库连接串行会掩盖），用 monkeypatch 在 flush/execute 层
   模拟 0 行匹配，断言 409 而非 500/异常。
3. attempt-2 回执追加"协调者隔离库复测"段（命令+结果），status 保持
   REWORK_DONE_PENDING_OCR；增量 commit 后报 output_commit。
4. 这是验收补证发现，不算新一轮 OCR 意见；你的 F1/F2/F3 修复方向正确，改动面很小。

协调者 OCR B1-r2（14b7a64..a8fac99 增量）仍在跑，收口后连同本条一起裁决。