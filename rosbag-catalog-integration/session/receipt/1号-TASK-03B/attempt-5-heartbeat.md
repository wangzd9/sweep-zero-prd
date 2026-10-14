# 1号 TASK-03B attempt-5（R2 强模型返修）心跳

- 领取：2026-10-10 11:55（dispatch status PENDING→ACCEPTED）
- base：main eff0479（11:31），worktree /home/wang/.local/state/rosbag-scene/wt-01，分支 t03b-r2-rework
- 范围（均 HIGH）：R2-01 迁移 TEXT server_default / R2-02 outbox 投影+rowcount / R2-05 create 侧版本分配
- 状态：**已交付**（2026-10-10 12:24 commit f088c2b，REVIEW_PENDING 等协调者验收）
- 交付：4 文件 +544/-46（迁移 02 / consumer / slice_service / 新增 8 回归 test_scene_r2_rework_1.py），
  零越界，无 .venv；定向 84 passed；全量 SQLite 812 passed（3 devflow 沙箱环境性，stash 本改动 base 同样 3 failed）
- 关键发现 1：R2-01 派单只点名 ingest_profile 3 个 TEXT 列，但 ingest_submission.selection_json（20261008_02:72）
  是同类 `TEXT NOT NULL server_default="{}"`，同为 MySQL 1101；ingest_profile 在分支里先建，强模型 repro
  在 1101 处先失败未走到 selection_json —— 只修 3 个仍会阻断升级，须一并去掉（回执单列风险，交协调者裁决）
- 关键发现 2：R2-05 把版本分配统一进 create_scene_run 后，显式路径响应在最终 commit 前回读版本需先 flush
  （否则 run_id 只是会话 pending 属性 → 回读为空），已加 db.flush() 落库绑定
- 关键发现 3：R2-02 MySQL 真实链路——02 迁移建的 purpose_schedule_event 无 error_reason（由 20261009_01 补），
  属既有链设计非本次缺陷；consume 走完整 head 表结构 CONSUMED 成功
- 关键发现 4：R2-01 已应用实例处置推断——MySQL 本不允许 TEXT 带 DEFAULT，已应用 02 的库必然升级中断在 02、
  不可能停在 20261008_02，故无存量库需"去 DEFAULT"，方案 A（仅修未升级库，零历史重写）即可（回执待协调者确认）
- MySQL 证据（真实 8.4.11 默认 sql_mode）：reviews/TASK-03B/attempt-5/mysql-r2-01-02-evidence-1hao.log
  - R2-01：已有库 create 分支 migration.upgrade() PASS（修复前 1101）；4 个 TEXT 列落库 DEFAULT=None
  - R2-02：poll 投影真实列值、consume 后 outbox DB 终态=CONSUMED、run 已创建
- 下一步：等协调者验收合入（OCR/强模型复审 + TESTER 交错场景 MySQL 端到端联调）