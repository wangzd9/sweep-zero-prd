---
task: TASK-03B
attempt: 5-rework-2
owner: 1号
status: REVIEW_PENDING
base: f088c2b（attempt-5-rework 交付之上续做，不重置）
output_commit: c285e2e
worktree: /home/wang/.local/state/rosbag-scene/wt-01
branch: t03b-r2-rework
updated: 2026-10-10 16:41
round: 同返修单小修（不占新轮次）
---
# TASK-03B attempt-5-rework-2 交付（f088c2b OCR 2 findings 小修）

派单：`inbox/1号/TASK-03B/attempt-5-rework-2.md`（协调者 16:26 派发；ACK 见
`inbox/1号/TASK-03B/attempt-5-rework-2-ack.md`）。f088c2b OCR 收口（88c0f2c2，15m19s）
出 2 条，均为小修，全部完成：

## 文件清单（2 文件，+118/-21 量级，零越界）
- `app/services/scene_schedule_consumer.py`
- `tests/test_scene_r2_rework_1.py`（+1 新增回归，改 1 既有回归注释/断言口径）

## 修复 1 [medium/bug]：R2-02 rowcount 契约生产链路接线
- `_mark` 原先丢弃 `mark_event_consumed/mark_event_dropped` 的 bool 返回值：0 行命中
  时依旧 `stats[bucket] += 1` 静默计成功——R2-02 "0 行不得静默" 在真实 consume 路径上
  不成立（隔离测试验了 bool，集成面没接线）。
- 处置：`_mark` 检查返回值。**0 行时不得计 consumed/dropped**：
  - **生产 poll 路径**（`poll_and_consume_purpose_events` 投影行打标 `from_outbox=True`，
    由 `poll_outbox_events` 经 `_poll_events_with_marker` 打标；`from_outbox` 是内部字段，
    不属 purpose-schedule-event/v1 契约集）：0 行=outbox 行必然存在却查无=真实异常，
    计入 `stats["errors"]`（`OUTBOX_MARK_MISSED`）+ 记 `logger.warning`，事件留在 PENDING 下轮重放。
  - **fixture 驱动路径**（DESIGN §11.2 "消费者测试可构造事件，不必等待 Scanner"）：行本就不
    在 outbox，0 行是预期形态，保持既有计数语义（不新增 error、不破坏 6 个既有 fixture 回归）。
    事件来源判别放在 `_mark` 调用方（from_outbox 标记），`mark_event_*` 本体不猜来源。
- 定向回归：`test_r2_02_mark_checks_rowcount_in_consume_path`（构造 poll 口径 0 行命中
  → 断言 consumed=0 + errors 含 OUTBOX_MARK_MISSED + caplog 捕获 warning；真实 PENDING 行
  对照组 → consumed=1 不误伤）。
- 既有回归 `test_r2_02_terminal_update_checks_real_rowcount` 断言口径同步为
  "bool 返回值 + _mark 按 from_outbox 接线"（mark_event_* 签名保持 bool 未变）。

## 修复 2 [low/style]：终态 UPDATE 改 Core 表达
- `mark_event_consumed`：`text(f"UPDATE {OUTBOX_TABLE} ...")` →
  `update(PurposeScheduleEvent).where(event_id==...).values(status="CONSUMED")`。
- `mark_event_dropped`：同上 → `.where(event_id==..., status=="PENDING").values(
  status="DROPPED", error_reason=reason[:255])`（原 WHERE status='PENDING' 语义保留）。
- 与 poll 投影改造同风格（按方言渲染标识符）；`text` import 移除，`update` 引入。
- 行为等价：rowcount 仍取真实命中行数（R2-02 回归继续覆盖）。

## 验证（真实命令 + 退出码，wt-01 借主仓 venv）
- 定向（本单 2 文件相关回归）：**44 passed**（tests/test_scene_r2_rework_1.py
  10 passed + tests/test_scene_slice_scheduling.py 35 passed）
  - `.venv/bin/python -m pytest tests/test_scene_r2_rework_1.py tests/test_scene_slice_scheduling.py -q` → rc=0
- 全量 SQLite：**813 passed, 3 failed, 10 skipped**
  - `.venv/bin/python -m pytest tests/ -q`
  - 3 failed 全为 `tests/test_devflow.py` 沙箱环境性：**stash 本改动在 base f088c2b 单跑
    test_devflow.py 同样 3 failed**，确认非本次回归（813 = 上轮 812 + 本单新增 1）。
- ruff：`ruff format` 2 文件 + `ruff check` → **All checks passed**
- 未跑 MySQL 隔离库：本次小修无 DDL/方言行为变更（Core update 与旧 text UPDATE 同语义，
  rowcount 接线为纯 Python 层）；R2-02 的 MySQL 真实链路证据沿用 attempt-5 交付段
  （`reviews/TASK-03B/attempt-5/mysql-r2-01-02-evidence-1hao.log`）。

## 未执行项
- 未自跑 OCR / 强模型复审（按派单：协调者增量串行审）。
- 未合入：合入门禁（五笔同批 --no-ff + OCR）在协调者侧，本单 commit 为
  `f088c2b → c285e2e` 增量。

## 越界申报
- 无。仅动派单点名的 `scene_schedule_consumer.py` 与其回归文件；
  `from_outbox` 为内部打标字段，未改动契约字段集 `_EVENT_FIELDS` 与 API 响应。