# 交付回执：t10-defect1-source-ready（TASK-10 缺口 #1 最小返修，03B 域）

- status: REVIEW_PENDING
- 派单：inbox/1号/TASK-03B/t10-defect1-source-ready.md（ack: 同目录 t10-defect1-source-ready-ack.md）
- task / attempt：t10-defect1-source-ready / attempt-1
- owner：cron-a-poll-d5cb80cf2fc5-20261012-001230（1号 A）
- base：main `ca8730d`（= origin/main，2026-10-12 00:12 双核 rev-parse）
- head / commit：`1b92ce6`（分支 `a/t10def1-source-ready`，worktree `wt-01-t10def1`）
- 交付时间：2026-10-12 00:27 +08:00

## 一、行为（修了什么）

正式接收链登记的真实源 `source_status` 初始恒为 `DISCOVERED`（`app/models.py:83` 默认；
`source_service.py` 登记旧值 :215），但 `scene_schedule_consumer.py:208` 与
`scene_slice_service.py:167` 均要求 `source_status == "READY"` 才建/认领 SCENE_SLICE run，
而 app+scripts+alembic 全仓无生产 READY setter → 真实源永远进不了 scene 链（P0 真实闭环断点，
2号 E2E 靠 ORM 手动置 READY 的 harness 前置才驱动到下游）。

修复：`register_source` 在 fingerprint 完整路径（`upsert_bag` 已校验 metadata 引用文件齐备，
缺文件在 catalog_ingest.py:25 抛 ValueError 回滚）把 source_status 由「恒置 DISCOVERED」改为
**只升不降**——仅当当前值 `None`/`DISCOVERED` 时升级到 `READY` 并推进 `updated_at`；已 READY 或
错误态（`mark_source_input_error`:459 另行置 INPUT_UNSTABLE 等）不被重复登记 / Scanner 重扫回退。

## 二、文件清单（零越界，diff 范围 = 登记链 + 测试）

- `app/services/source_service.py`（+14 / -1，仅 register_source fingerprint 块）
- `tests/test_t10def1_source_ready.py`（新增，5 例 SQLite 定向）
- 未动 05 / 06B / 04B / models / alembic / 其他 service（#2 由 2号 `wt-04a-t10d2` 并行）

## 三、自测证据

环境：worktree `wt-01-t10def1`（base ca8730d，.venv 软链主仓，Python 3.10.12）；SQLite 测试库
（`test_execution_mode=mock`，nas 根 `/test`）。

- 定向：`pytest tests/test_t10def1_source_ready.py` → **5 passed**（RC=0）
  - `test_register_real_source_sets_ready_not_discovered`：登记后无 harness 手动置位即 READY
  - `test_register_without_fingerprint_stays_discovered`：无指纹登记保持 DISCOVERED 默认语义
  - `test_outbox_consume_creates_run_no_longer_pending`：登记 scene_slice → `poll_and_consume_purpose_events`
    `pending==0` 且 `created_runs>=1`，产生 SCENE_SLICE run（端到端去掉 harness 1c2 前置口径）
  - `test_recovery_reregister_does_not_revert_ready`：恢复重登记 + 代次推进后仍 READY（不回退）
  - `test_input_error_not_overwritten_by_reregister`：INPUT_UNSTABLE 后重登记不覆盖/不回退错误态
- 反证（load-bearing）：stash 回原 `source_service.py` 跑同一文件 → **4 failed, 1 passed**
  （AC1/AC2/AC3/AC4 全红，仅无指纹边界绿），恢复后 5 passed——证明用例确实覆盖缺陷
- 全量：`pytest tests/ --ignore=tests/test_devflow.py` → **818 passed, 10 skipped**（skipped =
  `test_bag_cleanup_mysql.py` 独占容器验收入口门控），0 failed
- 静态：`ruff check app/services/source_service.py tests/test_t10def1_source_ready.py` → All checks passed

## 四、未执行项 / 阻塞

- **真 MySQL 8.4.11 STRICT 隔离库文件级并发复跑未在本单执行**：本改动仅 `source_status` 字符串
  赋值（无 DDL / 无唯一索引 / 无锁序变化），并发语义由既有 `upsert_bag` old/new 元组 + `updated_at`
  口径承载（t08c-1 已真 MySQL 验证同家族）。按派单四「涉并发语义真 MySQL 复跑」口径，留待协调者
  独立验证 / 合入阶段在隔离库复跑（用完即毁 0 残留）。本单未跑（非阻塞，非 DDL）。
- E2E `scratch/t10_e2e.py` 1c2 harness 前置去掉后的整链路复验，由协调者合入后安排（AC 三，非本单自测范围）。

## 五、越界申报

无。未改 06B / 05 / 04B；未重启共享栈；未动 NAS 业务目录；无跨模块依赖需回派。

## 六、停止条件达成

交付 commit `1b92ce6`（单 commit）+ 自测证据 + 回执落盘 → **REVIEW_PENDING 冻结**，等协调者核验 + 串行 OCR + 合入。