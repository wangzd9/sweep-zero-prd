---
task: TASK-06B
item: attempt-1-r2-rework-5
> **连接语义纠错（2026-10-11 13:55 协调者，据 codex 第七轮 B-01）**：本文件所称
> "PyMySQL 生产默认连接/生产默认语义"均指**无 CLIENT_FOUND_ROWS 隔离连接**（裸 pymysql.connect 无 client_flag，changed-rows 语义）；生产实际默认建连
> （SQLAlchemy 2.0.41 + PyMySQL 1.1.1）默认 client_flag=2 带 FOUND_ROWS，同值 UPDATE 返回
> matched rows=1。本文件证据只验证 changed-rows 连接下的修复行为，**不外推生产默认连接**。
> 详见 reviews/codex-r10-finalstate-20261011-verdict.md。

owner: 2号
status: REVIEW_PENDING
commit: 5c854ea（单 commit）
base: main 5f0124b
branch: scene/task-06b-codex-rework5（wt-04a-r5）
delivered: 2026-10-10 22:42 +08:00
---
# 回执：codex 独立审查 3 项返修（M-1 微秒精度 / M-2 迁移边界 docstring / M-3 测试注释）

裁决来源：`reviews/codex-r2final-20261010-verdict.md`（codex CLI 0.162.1
read-only 快照审查 74ba3bf..5f0124b，11.9 万 token，结论 REWORK 2 medium + 1 low）。

## 文件清单（3 文件，零越界，单 commit 5c854ea）

- `app/services/scene_result_report_service.py`（M-1，+6/-1，app 代码面）
- `alembic/versions/20261009_02_ingest_frozen.py`（M-2，docstring 边界记录，+8/-3）
- `tests/test_scene_result_report.py`（M-3 注释纠偏 + M-1 新增回归用例，+57/-2）
- 未改任何既有测试断言、未删用例、未动 complete 路径、未动其他任务文件。

## 各项处置

### M-1 [medium] started_at 微秒使 no-op 检测失效（真 bug，必修）

根因：`bag_record.started_at` 为 MySQL **DATETIME(0) 秒精度**（`SHOW COLUMNS` 实测
`datetime` 无 fractional）。旧码 `_mark_children_available` 在 `:577` 由纳秒
`der.start_ns` 直接 `fromtimestamp(...).replace(tzinfo=None)` **保留微秒**。二次
reconcile 从库读回整秒 → old 元组（含 started_at）判"变化" → 写微秒值被截断回
同整秒 + updated_at 同秒 → **无 CLIENT_FOUND_ROWS 连接 rowcount=0** →
`StaleDataError` 复发（与缺陷3 同根因，缺陷3 修复只对齐了 updated_at、漏了
started_at 这一列的比较口径）。

修复：`:582` 赋值统一 `.replace(tzinfo=None, microsecond=0)`（写入精度与持久化
精度对齐，比较口径随之正确），与裁决选定的"写入侧对齐"方向一致。

### M-2 [medium→边界记录] 改短 revision 适用边界

协调者已驳回"需版本映射"（22:23 全量核实 5 类存活库无旧 33 字符 ID、TESTER 隔离库
已销毁，codex 反例前提不成立）。按裁决在 `alembic/versions/20261009_02_ingest_frozen.py`
的改短注释把"零兼容风险"改为**记录适用边界**：核实范围（开发机 3 个 SQLite +
本地栈 MySQL 20260928_02 + 处理机生产库基线 20260928_02 + TESTER 隔离库已销毁）
+ 未来若出现存旧 ID 库的人工升级语句。不改 `revision=`/`down_revision=`，零功能改动。

### M-3 [low] 注释纠偏

`tests/test_scene_result_report.py:119` "SQLite 静默截断曾掩盖该约束" 改为
"SQLite 未校验列宽（VARCHAR(26) 写 28 字符读回仍 28），掩盖超长问题"（codex
探针实证：SQLite 不校验列宽，非截断）。纯注释。

## 命令 / 退出码 / 环境 / 关键断言 / 证据

环境：wt-04a-r5（`/home/wang/.local/state/rosbag-scene/wt-04a-r5`），branch
`scene/task-06b-codex-rework5`，HEAD `5c854ea`，base `5f0124b`；venv
`/home/wang/work/rosbag-catalog/.venv`（sqlalchemy 2.0.41 / pymysql 1.4.6 /
pytest 8.4.1 / python 3.10.12）。真实 MySQL 8.4.11 = 本机 docker
`rosbag-catalog-local-mysql-1`（172.20.0.6，隔离库 `b_m1_verify`，root 直连）。

1. **M-1 回归锚（SQLite，已入 commit）**——新增
   `test_reconcile_fractional_second_start_ns_starts_at_truncated_to_second`：
   带 0.5s 小数秒的 `start_ns` 走真实 reconcile 链（`_stage_and_publish` +
   `/reconcile-scene`），断言落库 `child.started_at.microsecond == 0` + 幂等二次
   no-op（registered=True）。**A/B 反证**：临时还原旧码（保留微秒）该用例
   **FAILED**（microsecond=500000 未对齐）→ 恢复修复后 **PASS**，证明该用例
   精确捕获 M-1 条件（旧回归/探针均整秒数据，恰好漏掉微秒条件）。
2. **真实 MySQL 8.4.11 A/B（M-1 语义证据）**——脚本
   `/home/wang/.hermes/cache/scratch/b_m1_ab.py`（PyMySQL 默认连接，**不含
   CLIENT_FOUND_ROWS**，匹配 TESTER/生产连接语义；隔离库 `b_m1_verify`）：
   - 列精度实测 `started_at`/`updated_at` = `datetime`（无 fractional）；
   - **旧微秒分支**：reconcile-1 写 `.500000` → 库读回整秒 `:23`（DATETIME(0)
     截断）→ reconcile-2 old 元组判变化 → 多列 UPDATE **rowcount=0**（即
     StaleDataError 触发条件）；
   - **修复整秒分支**：reconcile-1 写整秒 → 库读回同整秒 → old 元组相等 →
     **no-op 零 UPDATE**（正确收敛）。
   两分支对照直接证明 M-1 修复闭环。
3. **SQLite 定向**：`pytest tests/test_scene_result_report.py -q` → **32 passed**
   （含新增 M-1 回归，基线 31 +1）。
4. **全量**：`pytest -q` → **822 passed**，3 failed（`test_devflow.py`
   沙箱环境性 = main 基线同集），10 skipped。
5. **ruff**：`ruff check <3 文件>` → **All checks passed**。
6. 隔离库 `b_m1_verify` 已销毁，宿主机 0 残留（`SHOW DATABASES LIKE 'b_m1%'` 空）。

## 未执行项 / 边界申报

- 未跑 OCR（派单明确 OCR 不自跑，归协调者串行代跑）。
- 未合入 main、未自标 DONE（交付 REVIEW_PENDING，等协调者验收 + 增量 OCR +
  TESTER 生产默认连接语义复跑）。
- M-2/M-3 为纯 docstring/注释，无行为改动；M-1 仅动 1 行赋值，无接口/契约变更。
- rework-4（夹具 uid 收敛）已被 `6ee858b` 覆盖交付合入，该单关单，本侧无动作
  （派单"另"项已确认）。

## 交单

- 分支 `scene/task-06b-codex-rework5`，HEAD `5c854ea`（单 commit，base `5f0124b`）。
- 群内通报见 events/B；等协调者增量 OCR → TESTER 生产默认连接语义复跑 M-1 →
  合入 → 强模型增量复审（06 聚合放行链路继续）。