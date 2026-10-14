---
task: TASK-06B
item: attempt-1-r2-rework-6
owner: 2号
status: REVIEW_PENDING
dispatch_path: inbox/2号/TASK-06B/attempt-1-r2-rework-6.md
ack_path: inbox/2号/TASK-06B/attempt-1-r2-rework-6-ack.md
base: main 6d30a68
head: f4cd6549e723eac0c2f2e13a0c9883978af67316
branch: scene/task-06b-codex-rework6
worktree: /home/wang/.local/state/rosbag-scene/wt-04a-r6
delivered_at: 2026-10-11T09:29:00+08:00
---
# 2号交付回执：codex 全链合审 REWORK 3 项（R-01 medium 阻塞 / R-02 low / R-03 low）

裁决：`reviews/codex-r6-fullchain-20261010-verdict.md`（codex 第三轮全链合审 74ba3bf..6d30a68 = REWORK，协调者 09:02 独立复现确认）。base `main 6d30a68`（= origin/main）。

## 交单
- 分支 `scene/task-06b-codex-rework6`，单 commit **`f4cd654`**（`f4cd6549e723eac0c2f2e13a0c9883978af67316`），base `6d30a68`，实测 1 ahead（`git log --oneline main..HEAD` 仅 f4cd654，HEAD~1=6d30a68，main 未动）。
- **3 文件 +156/-8 零越界**（.venv 未纳入）：
  - `app/services/scene_result_report_service.py`（+7/-1，R-01 一行级修复+注释）
  - `tests/test_scene_result_report.py`（+121/-4，R-01 边界回归×3 + R-03 同秒/跨秒零 UPDATE 断言 + UPDATE 监听助手）
  - `tests/test_scene_slice_scheduling.py`（+19/-4，R-02 动态 head 断言）

## 行为（逐条对应裁决）
### R-01 [medium，阻塞] :582 秒末截断
- 旧 `datetime.fromtimestamp(der.start_ns / 1e9, tz=utc).replace(tzinfo=None, microsecond=0)`：先转**浮点秒**，纳秒末近秒边界（999_999_999）已**进位**到下一秒，`microsecond=0` 救不回；且 ≥~1ms 向上取整、<1ms 保持的不对称偏移使同一物理时刻按 ns 末不同落库秒不同，M-1 的"读回值对齐" no-op 保护对跨秒偏移失效。
- 改 `datetime.fromtimestamp(der.start_ns // 1_000_000_000, tz=utc).replace(tzinfo=None)`：整数除法先求整秒，构造即整秒，纳秒末一律**向下截断**。
- 回归：新增 `test_reconcile_start_ns_truncates_toward_zero_at_second_boundary`（参数化 ns末=0 / 500_000_000 / 999_999_999），断言**完整 started_at 值** = (BASE_S+2) 整秒（999_999_999 也截到 BASE_S+2 而非 BASE_S+3）+ 各自二次 reconcile 重放**零 UPDATE / 零 StaleDataError**。

### R-02 [low] 迁移 head 断言固定当前 head
- `test_migration_head_revision_id_within_alembic_version_width` 不再把 head 断言钉死成本次 revision 字面量：用 alembic `ScriptDirectory.from_config` 动态取 heads，断言**单 head**（无分叉）+ 单独断言本次 revision `20261009_02_ingest_frozen` 仍在迁移链中 + `alembic current` 落在唯一 head；上方全 ID ≤32 字符宽度断言保留不变。未来加合法后继迁移不再 :1204 误失败。

### R-03 [low] 前轮 low 未补（零 UPDATE 直接断言）
- 新增 `_count_bag_record_updates()`（`event.listen(engine, "before_cursor_execute")`）精确计数目标表 `UPDATE bag_record` 语句次数。
- 同秒重放：M-1 用例与 R-01 边界用例的二次 reconcile 均断言 `updates == 0`。
- 跨秒重放：M-1 用例 monkeypatch 服务模块内 `local_now`（service 是 `from app.clock import now as local_now`，须 patch 绑定名）+1s 重放，同样断言零 UPDATE——证明 no-op 与墙钟同秒无关，非"同秒 updated_at 相同"兜底。

## 验证（命令 / 退出码 / 环境 / 关键断言）
环境：wt-04a-r6，branch `scene/task-06b-codex-rework6`，HEAD `f4cd654`；venv `/home/wang/.local/state/rosbag-scene/wt-04a/.venv`（linked，python 3.10.12 / pytest 8.4.1 / sqlalchemy 2.0.41 / pymysql 1.4.6）。

1. **R-01 纯 Python 边界 A/B**（`_probe_r6/r01_ab.py`，已清理）：rem=0/5e8/999_999_999/1/999_999 下，仅 rem=999_999_999 差异——old `22:13:23`（进位错）/ new `22:13:22`（截断对），其余一致。**负对照**：临时还原旧码跑 `...[ns_remainder_999m]` → **FAILED**（started_at=22:13:23 ≠ 22:13:22）→ 恢复修复后 PASS，证明用例精确捕获 R-01。
2. **真实 MySQL 8.4.11 无 CLIENT_FOUND_ROWS 隔离库 A/B**（`_probe_r6/mysql_r6_ab.py`，compose `rosbag-catalog-local-mysql-1` 172.20.0.6 root 直连，隔离库 `b_r6_verify`，已销毁 0 残留）：
   - `started_at` 列型实测 `datetime`（DATETIME(0)，无 fractional）；
   - **R-01 边界矩阵**（用 service 当前 main 表达式 vs 修复表达式）：rem=0/5e8 一致 `:22`，rem=999_999_999 old `:23`（进位错）/ new `:22`（截断对）；
   - **R-03 两步 reconcile**（reconcile-1 写 + reconcile-2 幂等重放读回比较）：old/new 在 rem=0 与 rem=999_999_999 均 no-op 成立 → **零 UPDATE**（未发出 UPDATE 语句，非 rowcount=0 StaleDataError 触发条件）。
3. **SQLite 定向**：`pytest tests/test_scene_result_report.py tests/test_scene_slice_scheduling.py` → **71 passed**（含 R-01×3 + M-1 强化 + R-02 动态 head）。
4. **SQLite 全量**：`pytest -q` → **825 passed / 3 failed / 10 skipped**（56.34s）。3 failed = `test_devflow.py`（外部沙箱需主仓库 .git，**main 基线同集**，非本次改动；rework-5 同 3 failed/822 passed 口径，本次 825 因新增 3 边界用例 + 强化）。
5. **ruff**：`ruff check <3 文件>` → **All checks passed**（全仓 22 errors 均在本次未触碰文件，pre-existing 基线）。

## 未执行项 / 越界申报
- **未跑 OCR**（派单明确 OCR 不自跑，归协调者串行代跑）。
- **未合入 main、未自标 DONE**（交付 REVIEW_PENDING，等协调者验收 + 增量 OCR → TESTER 无 CLIENT_FOUND_ROWS 隔离库复跑 R-01 边界 + R-03 零 UPDATE → 合入 → 强模型增量复审 R2I-20261010-06 附本裁决+两轮 TESTER MySQL 证据+连接语义边界）。
- **连接语义边界（按裁决 info 条写清，codex 第四轮 11:05 定论）**：真 MySQL A/B 证据为**无 CLIENT_FOUND_ROWS 隔离连接**口径（测试插件自定义 creator 裸调 PyMySQL，默认 client_flag=0，changed-rows 语义）。**生产默认连接不同**：codex 独立无网络探针实测 SQLAlchemy 2.0.41 默认建连 client_flag=2（FOUND_ROWS=True），同值 UPDATE 返回 matched rows=1。故本证据**只证明修复对 changed-rows 连接的 no-op 行为，不能外推为生产默认连接语义验证**（生产默认连接下 no-op 天然不触发 StaleDataError）。此前"匹配 TESTER 生产连接口径"表述有误，已纠。
- 无接口/契约变更；R-01 仅动 1 行赋值+注释，R-02/R-03 仅测试文件。info 观察项（scanner:21 / pipeline:803 / bag_cleanup:495 既有秒精度写入点）不派单、不本次改，记 TODO 观察。

## 下一步
等协调者审核 `f4cd654` + 增量 OCR；交付后 06 聚合放行剩余 = 强模型增量复审 R2I-20261010-06（用户手动触发，附本裁决）。wt-04a-r6 冻结交付，本侧无在途进程。