---
task: TASK-06
item: r2-final-mysql-e2e-attempt-5
owner: TESTER
status: TEST_REPORT_PENDING
dispatched_by: 协调者
updated: 2026-10-11 09:44:51
base: main 4697be0（= origin/main，09:44:51 合入推送）
round: codex 第三轮全链合审 rework-6（f4cd654）合入后的独立复测
---
# TESTER 派单：R-01 秒末截断边界 + R-03 零 UPDATE 复测（attempt-5）

背景：2号 `attempt-1-r2-rework-6` commit `f4cd654`（base `6d30a68`，3 文件 +156/-8）
已 --no-ff 合入 main **`4697be0`**（09:44:51，推 origin；合入后 sanity 全绿：alembic
单头 `20261009_02_ingest_frozen` / ruff 3 文件绿 / SQLite 定向 71 passed RC=0）。
串行 OCR R6-r1 **0 findings**（session `03d83550`，1m23s，coverage 1/1，入选
`app/services/scene_result_report_service.py` +6/-1，tests 两文件 default_path
预期排除=本次 R-02/R-03 断言强化的独立验证归你）。裁决来源：
`reviews/codex-r6-fullchain-20261010-verdict.md`（第三轮全链合审 REWORK：
R-01 medium 阻塞 + R-02/R-03 low）。

## 只复测以下（不重跑已 PASS 的 S1/S2/S3/S4/B8c/B8a/r6 与 attempt-3/4 已收口项）

1. **AC1 R-01 秒末边界（核心新增）**：真 MySQL 8.4.11 隔离库，**生产默认连接
   语义**（连接 flag 实测不含 CLIENT_FOUND_ROWS，并注明所用连接方式/flag），
   `tests/test_scene_result_report.py` 全文件以 `R2_MYSQL_DB=<隔离库>` 跑 → 全部
   passed（含新增 `test_reconcile_start_ns_truncates_toward_zero_at_second_boundary`
   ns末=0 / 500_000_000 / 999_999_999 三参数），RC=0；
   - 探针（与 2号回执 A/B 口径独立复现）：构造 `start_ns` 纳秒末=999_999_999 走
     真实 reconcile 链 → 库内 `started_at` 落 BASE_S 整秒（**不**进位到 BASE_S+1，
     attempt-4 时代旧码 `22:13:23` 进位错口径已消除）→ 二次同 body 重放 200 无
     StaleDataError，started_at/updated_at/row_version 三元组不推进。
2. **AC2 R-03 零 UPDATE 直接断言**：同秒重放与跨秒重放（monkeypatch 服务内
   `local_now` +1s 口径即测试自身断言）下 `UPDATE bag_record` 语句计数 = 0
   （2号用 `before_cursor_execute` 监听计数；你的独立口径可用连接层/探针等价验证，
   结论注明方法）。
3. **AC3 不回归**：attempt-4 已 PASS 的微秒回归 + 整秒口径各抽查 1 例仍 PASS
   （防 R-01 一行改动碰坏 M-1 路径）。
4. **口径核对**：`git diff 6d30a68..4697be0` = 3 文件 +156/-8，app 行为面仅
   `scene_result_report_service.py:582` 一行赋值（`start_ns // 1_000_000_000`）
   +注释，tests 两文件为断言强化——确认无越界。

## 停止条件与交付

- 隔离库用完即毁、宿主 0 残留；零业务代码改动（只读+测试）。
- 回执 `test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-5.md` + 报告
  `reports/TASK-06/r2-final-mysql-e2e-attempt-5.md`（环境/命令/退出码/关键断言/
  连接 flag 实测口径齐全）。
- 交付后 06 聚合放行剩余 = 强模型增量复审 R2I-20261010-06（target 随本次合入
  更新为 `4697be0`，**用户手动触发**）→ PASS 收口即 03/05/06 聚合 DONE → TASK-08。
- 本侧无新派单前不预做；ACK 后按本单开工。