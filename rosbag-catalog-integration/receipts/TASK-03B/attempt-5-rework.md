---
task: TASK-03B
attempt: 5-rework
owner: 1号
status: REVIEW_PENDING
base: eff0479
output_commit: f088c2b
worktree: /home/wang/.local/state/rosbag-scene/wt-01
branch: t03b-r2-rework
updated: 2026-10-10 12:26
round: R2 第二轮强模型返修第 1 轮（有界 2 轮）
---
# TASK-03B attempt-5-rework 交付（1号接收/调度侧：R2-01 / R2-02 / R2-05-create）

R2 裁决（reviews/strongmodel/R2-20261010-verdict.md，11/11 confirmed）中我负责 3 条 HIGH，
全部已有独立 MySQL 8.4 复现证据。核心教训：**SQLite 全绿 ≠ MySQL 放行**（双引号=标识符
fallback、允许自引用 UPDATE、无 TEXT-DEFAULT 限制，系统性遮坑）。

## 交付内容（4 文件，+544/-46，零越界，无 .venv/环境产物）

### R2-01：已有库增量迁移 1101（阻断生产升级）
- `alembic/versions/20261008_02_ingest_config.py`：create 分支去掉 4 个 TEXT 列的字面量
  server_default，列保持 NOT NULL：`ingest_profile` 的 default_purposes_json /
  default_scenes_json / default_scene_parameters_json，**以及 `ingest_submission.selection_json`**。
- 写入侧不变：IngestProfile 模型三个 JSON 列带 Python `default=`，create_profile（ingest_service.py:232）
  亦显式传值；selection_json 各写入点（:322/:494/:623）均显式赋值。DB 层默认值本就不被依赖，
  去掉不影响业务路径。
- **风险（派单未点名，须协调者裁决）**：R2-01 派单只列了 ingest_profile 的 3 个 TEXT 列。
  但 `ingest_submission.selection_json`（20261008_02:72）是同类 `sa.Text(), nullable=False,
  server_default="{}"`，同样触发 MySQL 1101。strongmodel repro 在 ingest_profile（分支内先建）
  的 1101 处先失败，**没走到 selection_json**——只修派单点名的 3 个，升级会在建 ingest_submission
  时照样 1101。我已一并去掉（4 个全修），MySQL 实测见下；请协调者确认此处置。
- **已应用实例处置（按派单"方案写进回执，最终裁决归协调者"）**：
  - 方案 A（推荐，**零历史重写**）：02 的 TEXT DEFAULT 去掉后，**从未升级过的已有库**（卡在
    20261008_01 或之前）→ upgrade head 现在能成功（无 1101）。这是生产最常见的"待升级"场景，
    方案 A 直接解。
  - **已经应用过 02 的库**（若存在）：02 建出的 TEXT 列当时 MySQL 会 1101 → 该库实际不可能停在
    20261008_02（升级在 02 就中断了）。因此不存在"已成功带 DEFAULT 建出这些列"的库 → **无需**
    最小重写 02 或补"去 DEFAULT"的 ALTER 迁移（MySQL 本来就不允许给 TEXT 设 DEFAULT，也不存在
    需要去 DEFAULT 的存量列）。唯一理论例外：某库曾用 SQLite/其他方言成功建出这些列再迁 MySQL——
    本仓未发生。故 R2-01 对生产是纯"修复未升级库"，无存量数据迁移负担。请协调者确认此推断。
- 回归：`test_r2_01_ingest_create_tables_have_no_text_server_default`（已有库 20261008_01 状态
  → stamp → upgrade 02，断言 4 个 TEXT 列 NOT NULL 且 server_default=None）。

### R2-02：outbox 投影 MySQL 方言 bug（阻断调度）
- `app/services/scene_schedule_consumer.py`：
  - `poll_outbox_events`：去掉手工 `f'"{c}"'` 拼接，改用 `select(*[PurposeScheduleEvent.__table__.c[c]
    for c in _EVENT_FIELDS])`——Core 列对象按方言渲染标识符（MySQL 反引号/裸名、SQLite 裸名），
    不再是方言无关的裸双引号字面量（旧写法在默认 sql_mode 下投影的是字段名当字符串）。
  - `mark_event_consumed` / `mark_event_dropped`：返回**真实 rowcount 是否 >0**（0 行=真实异常，
    不得静默当成功）。outbox 表不存在（fixture 事件）时返回 True（事件本就不在 outbox，无需标记）。
- 回归：`test_r2_02_poll_projects_real_columns_not_literal_names`（真实 PENDING 行 poll 出真实值，
  非字段名）；`test_r2_02_poll_select_compiles_per_dialect_with_real_identifier_quoting`（MySQL/SQLite
  编译产物都限定到真实表列，且 MySQL 无 `"col"` 字面量形态）；`test_r2_02_terminal_update_checks_real_rowcount`
  （命中→True+status 翻正，不命中→False）；`test_r2_02_real_event_consumed_to_consumed_status`
  （poll→consume 后 outbox DB 终态=CONSUMED，PENDING 头部不再占位）。

### R2-05（create 侧）：创建时即分配版本行（跨 owner 契约，与 2号 switch 侧两端一致）
- `app/services/scene_slice_service.py`：把版本分配统一进 `create_scene_run` 的创建分支——
  自动事件路径与显式 API 路径**创建 run 同一事务内**按 entries 顺序 `allocate_analysis_version`
  + 回填 run_id/capability_version/config_hash，随后 `db.flush()` 落库。原先只有显式路径
  （create_scene_analysis_runs）分配、自动路径首回报才分配。
- 显式路径 `create_scene_analysis_runs`：不再重复 allocate（原 created 分支再调
  allocate_analysis_version 会重复建行/版本漂移），改用新增 `_analysis_versions_for_run` 按
  (parent, scene, run_id) 回读 version 标签用于响应。幂等复用（created=False）路径也走回读。
- 契约效果：换版比较用版本行**提交时点顺序（持久 id 序号）**，不用回报时点——晚到旧任务
  （自动路径，创建早→av id 小）不再按回报先后覆盖用户显式新分析（创建晚→av id 大）的 current。
  回归 `test_r2_05_late_old_auto_run_does_not_override_newer_current`：自动旧 run（av1，id 小）
  + 显式新分析（av2，id 大）→ 新分析 switch 成 current、晚到旧 run switch 被 switch_current
  拒（409 不倒退）。**2号 R2-03 把 switch_current 比较字段改为持久 id（去掉 created_at 自引用
  子查询 1093）后，本 create 侧的 id 顺序即最终比较依据——两端一致。**
- 回归：`test_r2_05_auto_event_path_allocates_version_at_creation`（自动路径建 run 即有 av1/current=False）；
  `test_r2_05_two_auto_events_get_distinct_versions_in_creation_order`（av1.id < av2.id 提交顺序）；
  `test_r2_05_late_old_auto_run_does_not_override_newer_current`（晚到旧 run 不覆盖新 current）。

## 验证（真实命令 + 退出码，wt-01 借主仓 venv）
- 新增定向 **8 passed**（tests/test_scene_r2_rework_1.py）
  - 命令：`.venv/bin/python -m pytest tests/test_scene_r2_rework_1.py -q` → 8 passed（rc=0）
- 派单定向 + 相邻回归 **84 passed**
  - `.venv/bin/python -m pytest tests/test_ingest_config_api.py tests/test_ingest_frozen_hash.py \
    tests/test_scene_slice_scheduling.py tests/test_scene_r2_rework_1.py tests/test_scene_result_report.py \
    tests/test_nvidia_contract_migration.py -q` → **84 passed**（rc=0）
- 全量 SQLite **812 passed, 3 failed, 10 skipped**
  - `.venv/bin/python -m pytest tests/ -q` → 812 passed, 10 skipped（test_bag_cleanup_mysql 独占容器口）
  - 3 failed 全为 `tests/test_devflow.py` 沙箱环境性（worktree `.git` 是文件非目录，bubblewrap 构造失败）：
    **已 stash 本改动在 base eff0479 单跑 test_devflow.py 同样 3 failed**，确认非本次回归。
- **真实 MySQL 8.4 证据（R2-01/R2-02 门禁必交项，本地隔离容器 rosbag-catalog-local-mysql-1，
  随机库+随机用户，跑完自动 DROP，不输出凭据）**：
  - 证据文件：`reviews/TASK-03B/attempt-5/mysql-r2-01-02-evidence-1hao.log`（脚本
    `/home/wang/.hermes/cache/scratch/r2_mysql_evidence.py`，可复跑）
  - version/sql_mode = 8.4.11 / `ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,...`（**默认，无 ANSI_QUOTES**）
  - **R2-01**：构造已有库（create_all 后删 3 张 ingest/outbox 表 = 20261008_01 状态），
    in-process 调真实 `20261008_02.upgrade()`（同 strongmodel repro 法，跑真迁移代码+真方言渲染）→
    **upgrade PASS（修复前 1101）**；续跑 20261009_01/02 到 head 全 PASS。落库核对 4 个 TEXT 列
    `default=None, nullable=False`（ingest_profile 三列 + ingest_submission.selection_json）。
  - **R2-02**：默认 sql_mode 下 poll 投影真实列值 `{purpose: scene_slice, scene_code: slope,
    source_id: R2FIXBAG, capability_config_hash: cap-r2fix}`（非字段名）；consume 后
    outbox 查 DB 终态 = **CONSUMED**（非永久 PENDING），run 已创建，stats consumed=1/created=1。
- ruff：`.venv/bin/python -m ruff format <4 文件>` + `ruff check app tests` → **All checks passed**

## 待协调者验收的要点 / 契约选择说明
1. **R2-01 第 4 个列（selection_json）是派单未点名的**——已一并修（否则升级仍 1101），MySQL 实测 4 列
   DEFAULT=None。请确认此处置正确。
2. **R2-01 已应用实例处置推断**：MySQL 本就不允许 TEXT 带 DEFAULT → 已应用 02 的库必然升级中断在 02、
   不可能停在 20261008_02，故**无存量库需"去 DEFAULT"**，方案 A（仅修未升级库，零历史重写）即可，
   不需要补"去 DEFAULT 的 ALTER"迁移或重写 02。请协调者确认；若判定需要给已应用库补迁移再派。
3. **R2-05 与 2号 R2-03 的契约衔接**：我让两路径都在创建时按提交顺序分配 av 行（持久 id 递增），
   2号把 switch_current 比较字段从 created_at 改为 av 行持久 id 后即闭环。当前 switch_current 仍用
   `(created_at, id)` 比较（R2-03 未修，1093 自引用子查询）——我的 R2-05 回归 `..._does_not_override_newer_current`
   用 `switch_current` 现有比较验证不倒退语义成立（因创建时分配使 created_at/id 顺序=提交顺序）；
   2号 R2-03 改成持久 id 后语义不变、更稳（去 1093）。请协调者在 R2-03/05 两端都收口后，
   派 TESTER 做真实"自动旧→显式新 / 两次自动 / 显式旧→自动新"交错 MySQL 端到端联调（覆盖我 create 侧）。
4. **R2-02 rowcount 返回 bool**：`mark_event_consumed/dropped` 签名由 None→bool，`_mark`/`_consume_one`
   未改（只增不破坏）；无现有调用依赖返回 None。fixture 事件（outbox 不存在）返回 True 避免误报。
5. 未自跑 OCR / 强模型复审（按派单：协调者交付后串行）。