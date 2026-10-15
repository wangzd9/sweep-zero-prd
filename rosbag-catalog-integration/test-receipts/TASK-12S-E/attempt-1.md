# TESTER TASK-12S-E attempt-1 独立验证报告（TEST_REPORT_PENDING）

- 生成时间：2026-10-15 00:45 +08:00
- **结论：PASS**（冻结 SHA `b39a3ec` 在真实 MySQL 8.4.11 隔离库下五面独立验证全过；零越界核实；隔离资源已自毁归零）
- 被测：`b39a3ecc76da1f578d32f4e3c88a6ce989cf749d`（分支 `a/task-12s-e-auto-bind`，worktree `wt-01-t12se`，base `16a154fff6f23e20b15498d1285a783713859647`）
- 派单：`inbox/TESTER/TASK-12S-E/attempt-1-independent-verify-dispatch.md`（协调者 2026-10-14 23:44）
- 环境：TESTER 自建 MySQL 8.4.11 隔离容器 `rosbag-t12se-d3ced1d1-mysql`（loopback 33751，STRICT_TRANS_TABLES/NO_ZERO_DATE 实测，`alembic upgrade head` → `20261013_01_scene_intake` 单头，fresh 路径实测；该交付零迁移变更，existing 库路径=同一 head 不变）；wt-01-t12se `.venv`（Python 3.10.12）；mock 执行模式，零模型调用、零生产触碰、零 1012 三包重放（复用 REPORT.md binding-repair 既有证据，派单边界明确）。

## ① MySQL 隔离库固定 SHA 重放（A 机械用例 SQLite 口径 → 真 MySQL 方言）

命令（DATABASE_URL=隔离库 DSN，wt-01-t12se 内执行）：

| 命令 | 退出码 | 结果 |
|---|---|---|
| `.venv/bin/python -m pytest tests/test_task12se_auto_bind.py -q` | 0 | **12 passed**（首轮 clean 库 1.60s） |
| 同上 + `test_pipeline_api test_source_register_purpose test_ingest_config test_scene_slice_scheduling test_t10def1_source_ready test_scene_intake_isolation test_scene_spray_intake`（A 自报 154 口径） | 0 | **154 passed**（首轮 12.80s；整库 drop 重建后复跑 12.81s 同口径） |
| `.venv/bin/alembic upgrade head`（fresh 库） | 0 | head=`20261013_01_scene_intake`，单头 |
| `.venv/bin/ruff check` 4 变更文件 | 0 | All checks passed |

覆盖断言（A 用例，真 MySQL 下执行）：先提交/先登记两先后、commit 丢失窗口下一轮收敛、重复对账幂等（run/attempt/事件零增长）、父子同快指纹重登记 200 归并同一 UID、无原包身份+切片指纹 409、歧义 409 AMBIGUOUS_SOURCE、跨根 ROOT_MISMATCH、车辆冲突 ERROR:*、代次漂移 GENERATION_DRIFT、开关 0 旧行为、零活动返回体逐键相等。

## ② TESTER 独立探针（A 套件之外的真 MySQL 语义面，全程同一隔离库）

脚本 `scratch/t12se_probe_v2.py`，日志 `scratch/t12se_probe_v2_mysql.log`，**8/8 PASS**（另 CLEANUP 精确复核 0 残留，见⑤）：

- **P1a**：pymysql 直连 `SHOW CREATE TABLE pipeline_run` → `UNIQUE KEY uq_pipeline_run_scene_identity_key (scene_identity_key)` 真实 DDL 在位（幂等载体的 MySQL 方言实证，SQLite 同构不能替代）。
- **P1a2**：`ingest_submission` DDL 含 `uq_ingest_submission_claim` 唯一约束（path_claim 并发 409 的 MySQL 载体）。
- **P1b**：同 `scene_identity_key` 两次 ORM 插入 → 第二次 `IntegrityError 1062 Duplicate entry` 真实拒绝（真 MySQL，P0 已核 app.engine 绑定=隔离库，防 import 顺序回退）。
- **P2 交错并发**：8 线程 Barrier 同时 `consume`（内含 reconcile）同一 PENDING 提交 → **runs=1、提交 SCHEDULED、零泄漏异常**（真 MySQL 锁/唯一键下无重复 run）。
- **P3 重复提交**：正式提交活动 PENDING 期间同路径第二笔 POST → **409 PATH_CLAIMED**（真 MySQL 唯一约束语义）；对账绑定释放 claim 后同身份再建第二笔 → 消费 `created=0/reused=1`，**runs=1**（scene_identity_key 复用，不烧模型桩计数不增）。
- **P5 单条隔离（独立复现）**：车辆冲突条 `skipped={'ERROR:HTTPException': 1}` 保持 PENDING_INPUT，同批正常条 bound=SCHEDULED/runs=1（单条故障不拖垮整批，下轮可重试）。
- **P4 开关 0（独立 API 面复跑）**：`PENDING_BINDING_RECONCILE=0` 零 PENDING 时 `POST /api/v1/orchestrator/purpose-events/consume` 返回体 `stats` 与旧口径**逐键相等**（无 `pending_reconciled` 键），rc 200。

## ③ 回归面（154 口径含关键项）

`test_pipeline_api`（12S-C incoming→ready 归并既有语义）、`test_scene_slice_scheduling`（含零活动旧返回体严格断言+迁移 head 宽度用例）、`test_t10def1_source_ready`、`test_scene_intake_isolation`、`test_scene_spray_intake` 全 PASS（真 MySQL）。旧自建/NVIDIA 入口回归：`test_source_register_purpose`+`test_ingest_config` PASS；P2/P5 探针中 self_built 源零触碰断言通过。

## ④ 零越界核

`git diff --stat 16a154f..b39a3ec` = 仅 4 文件 +911/−19（`app/services/pending_binding.py` 新增 220 行 / `scene_schedule_consumer.py` +28− / `source_service.py` +75− / `tests/test_task12se_auto_bind.py` 新增 607 行）；对 `app/api/ingest_submissions.py`、`app/models.py`、`alembic/`、`app/web/`、`scripts/`、`config/` 的 diff --name-only = **空**（零越界）；worktree 状态仅 `?? .venv`（未跟踪软链，派单边界已声明）。

## ⑤ 资源与残留

- 探针/测试夹具全部按唯一 tag 前缀自清：`scratch/t12se_cleanup_verify.py` 精确回读 bag_record/ingest_submission/ingest_profile/vehicle/pipeline_run/bag_file/bag_topic/purpose_schedule_event **全部 0 残留**（step_run 0；scan_job 1 行为 pytest bootstrap 固定种子，随容器同毁）。
- 隔离资源自毁：`docker rm -f rosbag-t12se-d3ced1d1-mysql` + `docker network rm rosbag-t12se-d3ced1d1-net` 已执行，`docker ps -a` 零 `rosbag-t12se-*` 命中（脚本 `scratch/t12se_destroy.sh` 带自有容器前缀护栏）。
- 被测 worktree 全程只读（零 commit/零改动，HEAD 仍 `b39a3ec`）。

## 未执行项（如实申报）

- 真实已接受结果复用单独取证：派单边界明确不重烧历史生产三包，复用既有 REPORT.md binding-repair 证据；真实 VLM 链路不在本交付变更面（零模型代码触达）。
- 交错并发仅到 8 线程 in-process Barrier 口径（真 MySQL 锁语义已验证）；未做跨进程多实例压测（派单未要求）。
- 生产处理机/1012 在途批次零触碰（派单边界）。

## 交付状态

**TEST_REPORT_PENDING**（PASS 面）：交协调者裁决。E 接受门禁 TESTER 侧=本回执 PASS；另一侧=协调者 OCR run `617b9375` 零 CORRECTION 级裁决（在途，TESTER 不代跑不代裁）。若协调者需要，②④段脚本均可按固定 SHA 复跑（隔离库重建约 2 分钟）。