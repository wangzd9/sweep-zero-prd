---
task: TASK-06
item: r2-final-mysql-e2e-attempt-4
owner: TESTER
status: TEST_REPORT_PENDING
dispatched_by: 协调者
updated: 2026-10-10 23:02
base: main 6d30a68（= origin/main，22:46 推送）
round: codex 审查 M-1 返修（5c854ea）合入后的生产默认连接语义独立复测
---
# TESTER 派单：M-1 微秒回归 + 生产默认连接语义复测（attempt-4）

背景：2号 codex 裁决 3 项返修 `5c854ea` 已合入 main `6d30a68`（OCR R5-r1 0 findings，
session `94bdf176`）。M-1=缺陷3 同根因第二列：`scene_result_report_service.py:582`
started_at 赋值统一 `.replace(tzinfo=None, microsecond=0)`（bag_record.started_at 为
MySQL DATETIME(0) 秒精度；保留微秒→二次 reconcile 读回整秒判变化→UPDATE 截断回同秒
rowcount=0→StaleDataError 复发）。2号自测含真 MySQL A/B（隔离库 b_m1_verify，PyMySQL
默认连接**不含 CLIENT_FOUND_ROWS**）与 SQLite 回归用例
`test_reconcile_fractional_second_start_ns_starts_at_truncated_to_second`，但独立验证归你。

## 只复测以下（不重跑已 PASS 的 S1/S2/S3/S4/B8c/B8a/r6）

1. **AC1 M-1 微秒回归（核心新增）**：真 MySQL 8.4.11 隔离库，**生产默认连接语义**
   （连接 flag 不含 CLIENT_FOUND_ROWS，并注明所用连接方式/flag 实测），构造带小数秒的
   `start_ns`（纳秒，非整秒）走真实 reconcile 链：
   - `tests/test_scene_result_report.py` 全文件以 `R2_MYSQL_DB=<隔离库>` 跑 → 全部
     passed（含新增微秒用例），RC=0；
   - 探针：reconcile-1 写带小数秒 started_at → `SHOW COLUMNS`/SELECT 确认库内落整秒 →
     reconcile-2 同 body 重放 → 200 无 StaleDataError，二次后子包行 started_at/updated_at
     均未推进、row_version 不变（与 attempt-3 探针口径对齐，扩展断言 started_at 列）。
2. **AC2 不回归**：attempt-3 已 PASS 的缺陷3 幂等口径（整秒数据）在 6d30a68 下抽查 1 例
   仍 PASS（防 M-1 改动碰坏整秒路径）。
3. **口径核对**：6d30a68 vs 5f0124b 仅 `scene_result_report_service.py`（+6/-1）、
   `20261009_02_ingest_frozen.py`（docstring）、tests（用例+注释）变更——确认无 app
   行为面越出 M-1 一行赋值（git diff 5f0124b..6d30a68）。

## 停止条件与交付

- 隔离库用完即毁、宿主 0 残留；零业务代码改动（只读+测试）。
- 回执 `test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-4.md` + 报告
  `reports/TASK-06/r2-final-mysql-e2e-attempt-4.md` + 事件 `events/TESTER/`；
  群内通报 PASS/FAIL 与证据。
- FAIL 不自行修代码：定性（M-1 修复缺口/环境/夹具）+ 最小证据，交协调者回派。
- 强模型增量复审（R2I-20261010-06，target 已更新 6d30a68）仍由用户手动触发，你不代跑。