# 派单：TESTER TASK-09 post-merge-ca8730d 合入后独立真 MySQL 验证

- status: TEST_REPORT_PENDING
- 派单时间：2026-10-11 21:42 +08:00（协调者 cron poll 回合）
- 任务：TASK-09 合入后验证（协议：必要合入后验证派测试者，未完成不得写 DONE）
- owner：TESTER
- base：**main `ca8730d7050c105b73e9387f4adda182d3a14e64`**（= origin/main，2号 `a60bb81` --no-ff 合入；合入前 main `0a8ca8a`）
- 被测改动：`a60bb81`（3 文件 +187/-3：`app/scene/slope/vlm.py` +17/-2 模型 ID 完整路径默认 + max_tokens 256→2048 + enable_thinking 透传 / `app/scene/slope/adapter.py` +10/-1 三 env 接线 / `tests/test_slope_vlm_wiring.py` 新增 9 用例）。**抽帧/segment/时间映射/迁移 0 改动**，影响面=VLM 客户端构造。
- 验收 decision：`inbox/coordinator/TASK-09/attempt-1-acceptance-decision.md`（机械核验/§G 裁决/OCR 2/2 0 findings 全在案）

## AC（验证项）

1. **真 MySQL 8.4.11 STRICT 隔离库**（口径同 TESTER pm08/t09_plug 先例：独立 worktree 检出 `ca8730d` 干净 + 独立容器用完即毁 0 残留）：
   - `tests/test_scene_result_report.py` + `tests/test_scene_result_storage.py`（06B 核心，交付侧已跑 60 passed，独立复跑确认合入快照不回归）
   - `tests/test_slope_vlm_wiring.py` + `tests/test_slope_adapter.py`（slope 接线面，SQLite 44 passed 口径在真 MySQL 环境复跑）
2. **迁移链**：alembic upgrade head RC=0 + 单头 `20261009_02_ingest_frozen`（本次零迁移改动，快速确认即可）。
3. **SQLite 全量**（ignore test_devflow）：合入快照不回归（交付侧 813 passed/10 skipped）。
4. 隔离资源 0 残留声明（容器/网络/库）+ ruff 3 文件。

## 停止条件

全部 AC RC=0 且隔离 0 残留 → 交付 `test-receipts/TEST-TASK09-post-merge-ca8730d/attempt-1.md`（REVIEW_PENDING）+ 报告。发现失败：记录 app 文件:行 + 复现口径，**不改业务代码**，交协调者裁决回派。

## 路径

- 回执：`test-receipts/TEST-TASK09-post-merge-ca8730d/attempt-1.md`
- 报告：`reports/TEST-TASK09-post-merge-ca8730d/attempt-1.md`
- ACK：`inbox/TESTER/TASK-09/post-merge-ca8730d-verify-ack.md`