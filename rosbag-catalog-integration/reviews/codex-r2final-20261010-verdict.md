---
review_id: codex-r2final-20261010
item: codex-review-verdict
owner: 协调者裁决
status: DECIDED
updated: 2026-10-10 22:24
result_path: ~/.hermes/cache/scratch/codex-review-r2final.log（5386 行，结论段 5331-5384）
---
# codex 独立审查裁决（范围 74ba3bf..5f0124b，结论 REWORK 2 medium + 1 low）

codex CLI 0.162.1 read-only 快照审查（11.9 万 token），独立探针验证（迁移图解析、SQLite 列宽探针、ORM UPDATE 行为探针）。逐条对照 main 5f0124b 核实：

## M-1 [medium] started_at 微秒使 no-op 检测失效 —— **confirmed，回派 2号**
代码核实成立：`scene_result_report_service.py:577` `datetime.fromtimestamp(der.start_ns/1e9, tz=utc).replace(tzinfo=None)` 保留微秒；
`started_at` 列 = `DateTime`（MySQL DATETIME(0) 秒精度，models.py:266）。缺陷3 的 no-op 检测 old 元组（:566-573）含 started_at——
二次 reconcile 从库读回**整秒**值，赋微秒值 → 元组判"变化" → 写 started_at（截断回同整秒）+ updated_at（同秒）→ 无 CLIENT_FOUND_ROWS
连接 rowcount=0 → StaleDataError **复发**。现有回归/TESTER 探针均整秒数据，恰好漏掉微秒条件。
**修复裁决**：started_at 赋值统一 `replace(microsecond=0)`（与持久化精度对齐，写入=比较同一口径）；
补 1 条 MySQL 回归：纳秒 start_ns 带小数秒 → 两次 reconcile 零 StaleDataError + 同秒重放 no-op。
（备选"读回时对齐比较"不采纳——写入侧对齐更简单且保证落库值确定性。）

## M-2 [medium] 改短 revision "无库存旧 ID" 前提反例 —— **核实后驳回"需映射"，改为记录适用边界**
codex 声称"TESTER 报告:40 记载加宽 version_num 后续跑旧迁移"——**该反例不成立**：TESTER 报告原文
"临时绕法 ALTER...可续跑（本单其余场景即用此后跑完成），但属运维动作非代码修复"，且 §清理 明确
**全部隔离库（t_r2mig/t_r2mig2/t_r2app2/t_r2app4/t_r2app5）随容器销毁、宿主机 0 残留**——加宽后写入旧 ID 的库
已不存在。协调者 22:23 全量核实存活库：
- `rosbag-catalog/app.db`：旧 ID 0 命中
- `rosbag-catalog/rosbag_catalog.db`：旧 ID 0 命中
- `wt-03b/rosbag_catalog.db`：旧 ID 0 命中
- 本地栈 MySQL rosbag_catalog 库：`alembic_version=20260928_02`（场景系列迁移未开始，无 20261009_02）
- 处理机生产库：从未部署过 20261009_02（该迁移 10-10 当天才产生，生产基线 20260928_02）
**结论**：无任何存活库持有旧 33 字符 ID，codex 反例前提不成立；但 codex 的验证方法（逐库核实而非推导）是对的。
**处置**：不迁移映射（无对象）；在迁移文件 :40 docstring 把"零兼容风险"改为**记录适用边界**（"核实范围=开发机 3 个 SQLite +
本地栈 MySQL + 处理机生产库（22:23 核实）全无旧 ID；若未来出现存旧 ID 的库，升级前需 `UPDATE alembic_version SET
version_num='20261009_02_ingest_frozen' WHERE version_num='20261009_02_ingest_frozen_columns'`"）。归入 M-3 同单。

## M-3 [low] SQLite "静默截断"注释不准确 —— **confirmed**
codex 探针：SQLite 写 28 字符到 VARCHAR(26) 读回仍 28——SQLite 不校验列宽，"截断"说法错误。
`test_scene_result_report.py:119` 注释改"SQLite 未校验列宽，掩盖超长问题"。同单 2号。

## codex 其余维度（已检查无发现）
迁移链 17 revision 单 base/head 全 ID ≤32 ✓ / UID 全调用点 ≤26 无碰撞 ✓ / 六字段覆盖该函数全部业务列 ✓ /
无异常吞掉、提交边界回归 ✓。**codex 观察项（不派单，记入强模型增量复审包）**：TESTER 自定义连接无
CLIENT_FOUND_ROWS + 全局关 FK 检查，与生产 SQLAlchemy/PyMySQL 默认语义不同——本轮 MySQL 证据的适用边界
需强模型增量复审时确认（特别是 no-op 修复 M-1 后，生产默认连接下 rowcount 语义不同，回归要以生产语义为准）。

## 回派
- 2号 attempt-1-r2-rework-5：M-1 修复（started_at 微秒对齐+MySQL 回归）+ M-2 边界 docstring + M-3 注释（同单 3 项）。
- attempt-1-r2-rework-4（夹具 uid 收敛）状态 PENDING 但**已被 6ee858b 覆盖交付并合入**——关单（回执补记）。
- 交付后：OCR 增量审 → TESTER 以**生产默认连接语义**（带 CLIENT_FOUND_ROWS）复跑缺陷3场景+微秒回归 →
  强模型增量复审（附 codex 报告+本裁决+TESTER 两轮 MySQL 证据）。