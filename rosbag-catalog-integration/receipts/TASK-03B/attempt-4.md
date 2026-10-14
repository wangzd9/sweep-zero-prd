---
task: TASK-03B
attempt: 4
owner: 3号
status: REVIEW_PENDING
base: c764f1b
output_commit: 86baad5
worktree: /home/wang/.local/state/rosbag-scene/wt-03b
updated: 2026-10-10 00:59
---
# TASK-03B attempt-4 交付（强模型审查 3 条 high 返修，生产端）

## 交付内容（7 文件，+943/-31，零越界，无 .venv/环境产物）

### #3 high：用途配置控制 Phase0 创建（source_service.py）
- `register_source` 重构：先 `bind_ingest_for_registration` 冻结用途，**仅当 self_built 在冻结用途集合内**才查找/创建 `PHASE0_QUEUE` run；仅选 `scene_slice` 的包不再启动 self-built 链（DESIGN §4 用途替换规则，REF-DESIGN line58）。
- 既有 run 查询加 **`pipeline_type=SELF_BUILT_BAG` + `source_generation` 双过滤**（`_find_self_built_run`），NULL 代次兜底历史行；场景 run（SCENE_SLICE）不再被当 self_built run 返回——**跨类型误配回归测试已覆盖**。
- 恢复登记（同一 bag 重放 MOVING/MOVED）在 **bind 之前**判定（`pre_bound` 查询），不重复建 run、只回显既有 self_built run。此处是首版实现的坑：bind 同事务会把该 bag 提交置 BOUND/SCHEDULED，若判定放 bind 之后则首登误判为恢复→首登不建 run（测试捕获后已修正）。
- CONFIG_REQUIRED 提交（选择未解析成功）读 `selection_json` 原始 purposes 回显，含 self_built 时仍建 Phase0 run，避免用户补配置后用途与 run 不一致。
- `PipelineRun.source_generation` ORM 映射 + 迁移补列（该列**不在**既有链上，是 #3 登记代次冻结新增；`20260928_01/02` 的同名列建在 `bag_cleanup_operation`/`source_operation_fence`，无关）；`SourceRegisterResponse.pipeline_run_id` 允许 None（纯 scene_slice 首登无 self_built run）。Scanner `runner.py`/`metadata.py` 已容忍该值（SOURCE_CLEANED 路径本就返回 None），无连锁影响。

### #4 生产端（协调者裁决"接受时冻结"，两端同一策略）能力 hash 冻结
- `IngestSubmission` 新增 `frozen_capability_hashes_json`（Text，`{scene_code: {capability_version, capability_config_hash}}`）。
- **接受时刻**（`create_submission` / `patch_submission` 成功 / `_ensure_system_submission` 系统兜底）按当时 registry 计算 04A 单能力 hash 并持久化（`_frozen_capability_hashes`）。
- `bind`（`_emit_purpose_events`）**只读冻结值，不再从当前 registry 重算**；registry 此后漂移（能力禁用/移除）→ 事件仍带接受时刻 hash → 05 消费端 `registry.get` 返回 None → SCENE_UNAVAILABLE 失败运行留痕（不是丢弃）。
- CONFIG_REQUIRED（接受时能力未解析）→ 冻结值恒 `{}`，bind 停 BOUND 不出 scene 事件。
- 冻结缺失或与有效配置版本不一致（存量行/数据异常）→ bind **显式失败**（CapabilityError），**绝不发 NULL-hash 违约事件**流出本服务。05 的 CONTRACT_VIOLATION 保留为真正的不变式违约兜底，我们自己的生产端永远不该触发它。

### #6 high：PATCH 与 Scanner bind 共享行锁
- `patch_submission` 读 submission 的 SELECT 加 `with_for_update()`；`_find_pending_submission`（bind 路径）同加 `with_for_update()`——两路径锁同一稳定行，消除"bind 读旧快照→PATCH 并发成功→bind 按旧代次覆盖→用户收'修改成功'但运行用旧配置"的窗口。
- `patch_submission` 读 profile 行也 `with_for_update()`。
- 保留既有守卫 UPDATE 条件 `status='PENDING_INPUT' AND row_version=:expected`（F2 成果，乐观锁+行锁双保险）。

### 迁移 20261009_02_ingest_frozen_columns（接 20261009_01 后）
- `pipeline_run.source_generation`（add_column + index，gate）
- `ingest_submission.frozen_capability_hashes_json`（add_column，gate）+ 存量行回填 `'{}'`
- **逐对象 gate**（`_pipeline_run_cols`/`_submission_cols`/`_pipeline_run_indexes` 先 inspect 再操作）：链起点 `20260911_01` 从空库 upgrade 时按**当前 model** `create_all(checkfirst=True)`，新列已在空库落库 → 无 gate 的 `add_column` 报 "duplicate column name"（隔离库 `upgrade head` 实测触发）。部署中的真实 DB 无此列 → gate 放行。与 `20261009_01`（05）处理 `scene_identity_key` 完全同模式。

## 验证（真实命令 + 退出码）
- 新增定向测试 **17 passed**（`tests/test_ingest_frozen_hash.py` 9 + `tests/test_source_register_purpose.py` 8），覆盖：接受冻结、bind 用冻结值不重算（registry 漂移注入）、CONFIG_REQUIRED 不出事件、self_built 冻结空合法、PATCH 重新冻结、冻结缺失显式失败不发 NULL 事件、系统兜底冻结、PATCH/bind 的 with_for_update 证据、纯 scene_slice 首登无 run、恢复不重复建 run、跨类型误配回归、代次推进重建、开关关闭旧行为不变、input_error 仍命中 Phase0 run。
  - 命令：`.venv/bin/python -m pytest tests/test_ingest_frozen_hash.py tests/test_source_register_purpose.py -q` → **17 passed**（rc=0）
- 全量回归：`.venv/bin/python -m pytest tests/ -q` → **777 passed, 3 failed, 10 skipped**（rc 因 3 failed 非 0）。
  - 3 failed 全为 `tests/test_devflow.py`（`主仓库缺少 .git，无法构造沙箱`）：worktree 的 `.git` 是文件非目录，bubblewrap 沙箱构造失败——**环境性，与主仓一致，非本任务回归**（我在主工作区 `git stash` 验证 devflow 24 passed，与本改动无关）。
  - 10 skipped 为 `test_bag_cleanup_mysql.py`（独占容器验收口，需协调者/测试者跑）。
- **迁移往返**：空库 `alembic upgrade head`→rc0（落 20261009_02，两列均在）→`downgrade 20261009_01`→rc0（两列移除）→`upgrade head`→rc0（两列恢复）。`tests/test_nvidia_contract_migration.py`（跑全链到 head）**1 passed**（修复前因 duplicate column 失败）。
- ruff：`.venv/bin/python -m ruff format app/ tests/` + `ruff check app/ tests/` → 我改的文件 **0 error**（迁移文件 E402/I001 与既有 `20261009_01` 完全同款模式，属 alembic 链起点 import 惯例，不额外处理以免与 05 迁移风格漂移）。

## 待协调者验收的要点 / 契约选择说明
1. **`pipeline_run.source_generation` 是全新列**（#3 登记代次冻结需要）。它**不在**既有迁移链上——全链空库 `upgrade head` 到 `20261008_02`（main 模型）后 `pipeline_run` **无** `source_generation`（已实测），`20260928_01/02` 的 `source_generation` 建在 `bag_cleanup_operation`/`source_operation_fence`，与 `pipeline_run` 无关。之所以空库 SQLite 上会"已存在"，是链起点 `20260911_01` 的 `Base.metadata.create_all(checkfirst=True)` 按**当前 model** 建表所致（我补了 model 映射后空库建表就带上了）→ 无 gate 的 `add_column` 在空库重放报 "duplicate column name"。**迁移 20261009_02 对该列加了 gate**：空库（create_all 已建）→ 跳过 add；真实部署 DB（该列本不存在）→ 补建。与 `20261009_01`（05）处理 `scene_identity_key` 完全同模式。**请核实：生产 DB 的 `pipeline_run` 无 `source_generation` 列**（gate 会安全补建，nullable 不破坏既有行）。
2. **恢复登记判定放 bind 之前**（`pre_bound` 查询）是本任务一个非显然的顺序约束：bind 同事务改变提交状态，判定必须在改变前。已在代码注释 + 回归测试固化。
3. **CONFIG_REQUIRED 的 self_built 回显**读 `selection_json.purposes`：若未来 selection 结构变更需同步此解析（当前是 `{purposes, scenes}` 规范化 payload，`_idempotent_payload` 固定）。
4. **#4 与 05 联调**：本次只改生产端，事件契约字段集未变（capability_version/capability_config_hash 位置不变），05 消费端 `_consume_one` 的 SCENE_UNAVAILABLE 失败留痕路径无需改。合入顺序仍按 BASELINE：**03B 收口（含 #1 终测 PASS）→ 05 rebase 到最终 03B 做真实 outbox 联调**。
5. 未执行项：MySQL 8.4 隔离库 `with_for_update` 行锁并发实证（SQLite 编译省略 FOR UPDATE，隔离库为权威）——留协调者/测试者代跑，我已在测试中用 `db.scalar` 包裹捕获 `_for_update_arg` 证明语句携带行锁标志。

---

## OCR B5b 返修交付段（attempt-4-ocr-rework，2026-10-10 00:58 领取）

- **output_commit（本段）**：`6f1a9ad`，分支 `feature/scene-03b-ocr-rework`，base = main `b5efba2`（86baad5 已在 main 祖先链，本段为 main 之上的纯文档级增量，2 文件 +17/-7）。
- **处置 3 条（全 documentation 级，核心逻辑零改动）**：
  1. **medium（必修）** `ingest_service.py:_emit_purpose_events` docstring——旧文写"registry 漂移时事件以 capability_config_hash=None 落 outbox 不抛错"，与 #4 返修后的显式失败实现直接冲突。已替换为协调者核实的文本：事件只携带接受时刻持久化冻结 hash、不重算 registry；漂移由 05 消费端 registry.get→None 落 SCENE_UNAVAILABLE；冻结缺失/版本不一致显式 raise CapabilityError 回滚事务，绝不发 NULL-hash 事件。
  2. **low** `20261009_02` 迁移 docstring——补 ⚠️ downgrade→upgrade 往返风险（backfill 未门控，生产库往返会把真实冻结 hash 静默覆写为 '{}' → 后续 bind 命中"冻结缺失" raise → 登记 500 + Scanner 重试）+ 运维处置（对受影响 PENDING_INPUT 重新 PATCH 恢复冻结值）。仅文档化，不改列结构（与 20261009_01 drop-数据列口径一致）。
  3. **low** `20261009_02` import 位置——4 个 E402 消除，import 移到文件顶部（与 20261008_02 组织方式一致）。
- **验证（真实命令 + 退出码，wt-03b 借主仓 venv）**：
  - 定向 `.venv/bin/python -m pytest tests/test_ingest_frozen_hash.py tests/test_source_register_purpose.py -q` → **17 passed**（rc=0）
  - 相邻 `.venv/bin/python -m pytest tests/test_ingest_config.py -q` → **21 passed**（docstring 改动无行为回归）
  - `.venv/bin/python -m ruff check alembic/versions/20261009_02_ingest_frozen_columns.py` → **All checks passed**（E402 清零）
  - `.venv/bin/python -m ruff check app/services/ingest_service.py` → **All checks passed**
  - `.venv/bin/python -m py_compile <迁移>` ok；`.venv/bin/alembic heads` → 单 head `20261009_02_ingest_frozen_columns`（import 重排未破坏迁移链）
- **范围**：`git diff b5efba2 6f1a9ad --name-only` = 2 文件（ingest_service.py、20261009_02 迁移），零越界，无 .venv/环境产物。
- **OCR 不自跑**，等协调者对 6f1a9ad 复审（本单为 OCR 返修第 1 轮，有界 2 轮）。
- status：REVIEW_PENDING（等协调者验收合入）。