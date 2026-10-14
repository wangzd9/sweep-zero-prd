---
task: TASK-05
attempt: 2
owner: 1号
status: REVIEW_PENDING
base: 9506457（origin/main 合入后最新，含 03B F2 返修）
output_commit: b75c6bf（worktree HEAD，增量：6ce7b7a 基线 + db4bec7 OCR 返修 + 641aacd 风格小单 E402 + b75c6bf 风格小单 B3 low，前两者已合入 main b5efba2）
worktree: /home/wang/.local/state/rosbag-scene/wt-01
branch: scene/task-05-e402-styles（本轮风格小单分支；历史：scene/task-05-rework / hotfix/task-05-ocr-backfill）
updated: 2026-10-10 01:24
---
# TASK-05 attempt-2 交付（强模型返修 #5/#7/#4消费端）

## 交付内容（文件清单 + 语义）
纯 05 scope，6 文件，无越界、无环境产物（.venv 为软链不入库）：

1. `app/models.py`
   - `PipelineRun.scene_identity_key`（String(64) nullable）+ 唯一约束
     `uq_pipeline_run_scene_identity_key`——持久业务身份键，终态不释放。
   - `PurposeScheduleEvent.error_reason`（String(255) nullable）——DROPPED 终态原因；
     status 注释补 DROPPED 取值。
2. `alembic/versions/20261009_01_scene_identity_key.py`（新增）
   - `down_revision = "20261008_02"`（03B 迁移）。
   - upgrade：`add_column` scene_identity_key（gate 部分应用重入安全）→
     从 `scene_run/v1` 快照确定性回填历史场景 run 身份键（幂等，重跑不变）→
     建唯一索引 → `add_column` outbox error_reason。
   - downgrade 反向，SQLite 隐式 sqlite_autoindex 的 drop_column 兜底。
   - **迁移链顺序待协调者裁决**（见下方契约选择说明 #2）。
3. `app/services/scene_slice_service.py`
   - `scene_run_identity_key(..., reanalysis_id=None)`：reanalysis_id=None 时摘要体
     与历史算法**逐字节一致**（保活既有 run 身份 + 迁移回填一致）；非 None 时
     加入身份维度 → 显式重分析走新 run。
   - `create_scene_run`：查重从 `active_identity_key` 改为**持久 `scene_identity_key`
     （含终态 run）** → 终态后同身份新 event_id 重放复用不重建（#7 核心修复）；
     并发 IntegrityError 兜底回查也改按持久键；新建时同时写
     `source_identity`/`active_identity_key`/`scene_identity_key`。
   - `SceneRunCreate` 增加 `reanalysis_id`；`create_scene_analysis_runs` 从
     payload 透传；snapshot 与 GET detail 回显 reanalysis_id。
4. `app/schemas/requests.py`
   - `SceneAnalysisRunRequest.reanalysis_id`（optional, min/max 64）——显式重分析维度。
5. `app/services/scene_schedule_consumer.py`
   - 新增 `mark_event_dropped`：原子 `UPDATE ... SET status='DROPPED',
     error_reason=... WHERE event_id=:eid AND status='PENDING'`（#5 核心修复）。
   - `_mark(..., reason="")`：dropped 桶落 outbox 终态，不再只改内存 stats。
   - 永久错误路径全部落 DROPPED+原因：未知用途、源已删/角色不符/代次失效、
     缺 capability_version/hash（#4 契约违约）、缺 scene_code。
     瞬时错误（源未 READY）保持 PENDING 不变。
   - 模块 docstring 更新幂等/终态语义。
6. `tests/test_scene_slice_scheduling.py`（基线 25 → 32）
   - `_purge` 增加清理 outbox 行；新增 outbox 直插替身 + `_event_from_outbox` 投影。
   - 新回归：DROPPED 原子离开 PENDING+原因、源未 READY 保持 PENDING、
     终态 run 新 event_id 重放复用不重建、reanalysis_id 显式重分析走新 run/
     首次重放复用/分析版本递增 av2、cancel 后第二次显式分析带 reanalysis_id。

## 验证（命令 + 真实退出码）
```
$ ruff check app tests                    → All checks passed!
$ ruff format（改动 5 文件）→ 3 files reformatted（顺带解 E501 长行）
$ alembic heads                            → 20261009_01_scene_identity_key (head)（单头，无分叉）
$ alembic upgrade head @ 空 SQLite 库      → 成功；scene_identity_key/uq 索引/outbox error_reason 均落库
$ alembic downgrade 20261008_02            → 成功（SQLite drop_column 兜底）；再 upgrade head 成功
$ PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/test_scene_slice_scheduling.py tests/test_nvidia_contract_migration.py -q
  → 33 passed, 1 warning, 退出码 0
$ PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q   @ 6ce7b7a（rebase 到 9506457 后）
  → 757 passed, 10 skipped, 3 failed；3 failed 全为 tests/test_devflow.py 沙箱环境性
     （在 base 9506457 无我改动时同样复现：3 failed 21 passed，与本改动无关）
```
- 迁移链往返（upgrade→downgrade→upgrade）已实测；SQLite 链起点 `20260911_01`
  用 `create_all` 建表，故新列可能已随 create_all 落库 → 本迁移逐对象 gate，
  部分应用重入安全。MySQL 生产路径 `DROP COLUMN` 无 SQLite 隐式索引限制，
  兜底分支仅在 SQLite 空库回退触发。

## 待协调者验收的要点 / 契约选择说明
1. **#7 修复选型**：用独立持久列 `scene_identity_key`（区别于活动租约
   `active_identity_key`），而非复用 source_identity。理由：活动租约语义是
   "终态/取消释放以便重试回队恢复"，与"业务身份只创建一次"是两个正交需求；
   `source_identity` 是 512 宽非唯一索引，不能加唯一约束。reanalysis_id 维度
   仅在显式重分析传入时进入摘要，事件消费恒 None，历史摘要体逐字节不变，
   既有 run 身份 + 迁移回填一致。
2. **迁移链顺序（需你裁决）**：outbox 表（purpose_schedule_event）是 03B 的
   （20261008_02）。我把字段变更放在**自己新迁移 20261009_01**，down_revision
   挂 20261008_02 之后。但 03B attempt-4 strongmodel 返修（#3/#4生产端/#6）
   在途未合，若 3号 也新增迁移，可能与我这条抢同一段链序。**建议**：03B
   attempt-4 收口后，我把 20261009_01 的 down_revision 改接到 03B 最终迁移头
   再联调（返修单既定顺序：先 03B 返修收口 → 05 rebase 到最终 03B 联调）。
   当前已 rebase 到含 03B F2（9506457）的 main，outbox 结构以 20261008_02 为准；
   待 attempt-4 合入后按最终 03B 复核 error_reason 列是否与 3号 迁移冲突。
3. **#4 消费端**：漂移（registry.get→None）建失败运行留痕的既有路径
   （`create_scene_run`+`_fail_scene_run`→SCENE_FAILED）已确认保留；缺 hash
   的 CONTRACT_VIOLATION 现在与 #5 联动落 outbox DROPPED 终态。#4 与 3号
   生产端真实 outbox 联调，待 03B attempt-4 收口后进行（本次仅 fixture/直插
   替身覆盖消费侧契约）。
4. **未跑 OCR**（协议：协调者代跑 flock）。核心 3 文件
   （scene_slice_service / scene_schedule_consumer / models）请代跑
   `ocr review -c 6ce7b7a --audience agent`；合入以 OCR + 你的代码核实 +
   #4 真实 outbox 联调三者都过为准。
5. **MySQL 8.4 落库**：本迁移仅本地 SQLite 实测（DDL 往返 + 回填）。
   scene_identity_key 唯一约束含 NULL（多场景/非场景 run 恒 NULL），MySQL
   对 NULL 唯一约束放行多值，与 outbox 既有 uq 同语义；建议测试者隔离库
   补验 upgrade 落库 + 历史回填 SQL 在 MySQL 下的执行（尤其 executemany
   UPDATE 与 512 宽 source_id 摘要）。
## OCR 返修交付段（B6 批次，1 high + 1 low，2026-10-10 00:00）
- **修复 commit**：db4bec7（worktree wt-01，分支 hotfix/task-05-ocr-backfill，base=main 533aa1c）
- **high（backfill 未按身份去重）**：`_backfill_scene_identity` 改为按身份只给规范行（max int PK id）写键，其余保持 NULL 后再建唯一索引。SELECT 增加取 `id` 列；UPDATE 参数由元组改为显式命名 dict（顺带修 SQLAlchemy 2.x 批量执行下 `:key` 复用重名 bind param 报 "A value is required for bind parameter 'key'" 的隐患，改名 `:key`/`:key_check` 分离 SET 与 WHERE 两侧同值参数）。
- **low（W292）**：迁移文件末尾补换行。
- **backfill 去重回归测试**：`tests/test_scene_slice_scheduling.py::test_migration_backfill_dedupes_duplicate_identity_runs`。实现方式=**真实度最高的 alembic CLI 子进程路径**（与 test_nvidia_contract_migration 同款）：临时独立 SQLite 库 → `alembic upgrade 20261008_02` 建表 → 直插同业务身份两条 SCENE_SLICE run（R1 id=1 已 SCENE_DONE、R2 id=2 新 run，快照逐字节相同）→ `alembic upgrade head` 触发真实 backfill + 唯一索引 → 断言索引建成、R2 持键、R1 NULL → 独立库副本反证（给 R1 也写同键必抛 IntegrityError，证明测试覆盖该缺陷）→ downgrade 20261008_02 + 再 upgrade head 断言幂等结果不变。
- **验证（真实退出码）**：
  ```
  $ 定向回归（新测试单跑）→ 1 passed
  $ pytest tests/test_scene_slice_scheduling.py tests/test_nvidia_contract_migration.py -q → 34 passed（05 调度回归 32 基线 + 本轮新增 backfill 去重回归，nvidia 迁移链测试并入同批执行，全绿）
  $ 全量 pytest -q @ db4bec7 → 778 passed, 10 skipped, 3 failed
    3 failed 全为 tests/test_devflow.py 沙箱环境性（stash 我的改动后同样 3 failed 21 passed，与本改动无关）
  $ ruff check app tests → All checks passed
  $ ruff format（改动 2 文件）→ 2 files reformatted
  ```
- **OCR 自跑**：无（协议：协调者代跑 flock）。请代跑 `ocr review -c db4bec7 --audience agent`。
- **MySQL 说明**：backfill 为纯 SELECT+executemany UPDATE+create_index，去重逻辑方言无关；MySQL 8.4 落库由测试者隔离库终测覆盖（dispatch 风险评估节）。
- status 维持 **REVIEW_PENDING**，output_commit 更新为 **db4bec7**（原 6ce7b7a 的 OCR 返修增量）。
## 风格小单交付段（attempt-2-ocr-rework-2，4 个 E402 import 位置，2026-10-10 01:07）
- **修复 commit**：641aacd（worktree wt-01，分支 scene/task-05-e402-styles，base=main b5efba2）
- **改法**：`alembic/versions/20261009_01_scene_identity_key.py` 的 4 个 import
  （hashlib/json/sqlalchemy/alembic）从 revision/down_revision 属性之后移到模块
  docstring 之后顶部，消除 E402，与既有 20261008_02（03B）风格统一；
  `ruff check --fix` 顺带按 isort 规则把 import 块与 revision 属性间的空行收敛为
  ruff 规范（1 空行块内分组不变）。
- **验证（真实退出码）**：
  ```
  $ ruff check alembic/versions/20261009_01_scene_identity_key.py → All checks passed（无 E402）
  $ ruff format --check 同文件 → 1 file already formatted
  $ PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/test_scene_slice_scheduling.py -q
    → 33 passed（含真实 alembic CLI 子进程 upgrade 20261008_02→head 的 backfill 去重回归，
      即改后的迁移文件本身在 upgrade 路径被执行过）
  ```
- 语义零变更：仅 import 位置移动，迁移逻辑/属性/函数体逐行未动。
- **待验收**：请核 641aacd 单文件 diff（5 增 5 删纯 import 移位）；OCR 该文件已无 E402，
  是否需代跑 `ocr review -c 641aacd` 由你定（纯风格移位，建议 ruff 证据即可合入）。
## 风格小单 B3 low 交付段（attempt-2-ocr-rework-2 后半，orchestrator 观测，2026-10-10 01:24）
- **修复 commit**：b75c6bf（worktree wt-01，分支 scene/task-05-e402-styles，base=641aacd，纯任务 scope 2 文件）
- **改法（app/orchestrator.py `_consume_purpose_events`）**：
  1. errors 未 log → stats['errors'] 非空时该行追加 `/ N errors, first: <event_id> <message>`（单事件失败保持 PENDING 每轮重放，原先消费端/backend 两侧都无日志痕迹）；
  2. 空轮次无限打 0 行 → 仅当任一计数（consumed/dropped/pending/created_runs/reused_runs）非 0 或 errors 非空时才 print（outbox 合入前每 10s 刷全 0 行，现静默）。
  纯 print 逻辑调整，业务路径（_post 调用、异常捕获）未动，写边界（不 import 数据库会话）不变。
- **验证（真实退出码）**：
  ```
  $ ruff check app tests → All checks passed
  $ ruff format --check app/orchestrator.py tests/test_scene_slice_scheduling.py → 2 files already formatted
  $ PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/test_scene_slice_scheduling.py -q → 35 passed（33 基线 + 2 新：errors 必打含首条 event_id、全零静默）
  $ PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q @ b75c6bf → 780 passed, 10 skipped, 3 failed
    3 failed 全为 tests/test_devflow.py 沙箱环境性（与 db4bec7/641aacd 基线一致，与本改动无关）
  ```
- **交付汇总**：本单两半合计 2 commit——641aacd（E402 迁移 import 移位，单文件 5+/5-）+ b75c6bf（B3 low 观测，2 文件）。请核两个 commit 的 diff；OCR 是否代跑由你定（均纯风格/观测移位，建议 ruff+测试证据合入）。
