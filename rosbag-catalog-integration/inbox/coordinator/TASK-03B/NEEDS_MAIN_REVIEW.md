---
task: TASK-03B
item: attempt-5-rework 交付 f088c2b 的机械验收挂起（不抢跑合入）
raised_by: 协调者 cron 机械验收化身（scene-coordinator-heartbeat, 2026-10-10 12:35）
status: NEEDS_MAIN_REVIEW
round: R2 第二轮强模型返修第 1 轮（有界 2 轮）
related:
  - receipts/TASK-03B/attempt-5-rework.md（1号回执，status=REVIEW_PENDING，指纹本轮 monitor 变化事件）
  - inbox/1号/TASK-03B/attempt-5-rework.md（返修派单，status=ACCEPTED）
  - reviews/strongmodel/R2-20261010-verdict.md（11/11 confirmed 裁决，R2-01/02/05-create 回派 1号）
  - reviews/TASK-03B/attempt-5/mysql-r2-01-02-evidence-1hao.log（1号 MySQL 8.4 证据）
  - inbox/coordinator/TASK-03B/NEEDS_MAIN_REVIEW.md.consumed-20261010（同型先例：f11e617 因 OCR 未收口+深度验收超机械范围而挂起）
---

# 挂起：1号 attempt-5-rework（f088c2b）机械验收通过，但合入超机械范围，待主会话裁决

## 事件
本轮唤醒原因：monitor 指纹变化，wt-01 HEAD eff0479 → f088c2b（main 仍 eff0479），
对应 1号 TASK-03B attempt-5-rework 交付（R2-01/02/05-create，R2 强模型 11/11 confirmed 回派）。

## 机械核验结果（化身独立跑，非采信自报，全部 PASS）
- **base 正确**：f088c2b 父链 = eff0479（当时 main，`git merge-base` 确认），`rev-list --count eff0479..f088c2b` = 1（单 commit 增量）。
- **范围一致、零越界**：`git show --name-status f088c2b` = 4 文件（M alembic/versions/20261008_02_ingest_config.py / M app/services/scene_schedule_consumer.py / M app/services/scene_slice_service.py / A tests/test_scene_r2_rework_1.py），+544/-46；无 .venv/__pycache__/环境产物（与派单文件清单一致）。
- **merge-tree 0 冲突**：`git merge-tree --write-tree eff0479 f088c2b` = 干净（rc=0）。
- **定向**：`.venv/bin/python -m pytest tests/test_scene_r2_rework_1.py -q` → **8 passed**（rc=0）。
- **派单定向集**：ingest_config_api + ingest_frozen_hash + scene_slice_scheduling + scene_r2_rework_1 + scene_result_report + nvidia_contract_migration → **84 passed**（rc=0）。
- **全量**（PYTEST_DISABLE_PLUGIN_AUTOLOAD=1）：`pytest tests/ -q` → **812 passed, 3 failed, 10 skipped**；3 failed 全为 test_devflow.py 沙箱环境性（worktree `.git` 是文件非目录，bubblewrap 构造失败），非本次回归。
- **ruff**：`ruff check app tests` → **All checks passed**（rc=0）。
- **OCR 在途**：无（ps 空）；coordinator.lock 本轮空闲。

## 挂起理由（逐条对应 prompt 硬红线，不抢跑合入）
1. **fresh 模块 / 大交付禁机械合入红线（2026-10-10 R2 教训）**：本交付 **4 文件 +544/-46**，超"已审模块增量小修（单 commit ≤3 文件）先合后补跑"的例外上限；且 f088c2b 无 OCR 批次收口记录（`reviews/TASK-03B/` 下 ocr-batches.md 只覆盖 attempt-2 的 14b7a64..a8fac99 旧范围，未含本 R2 返修 commit）。03B 虽有 attempt-2 OCR 闭环，但本轮是 R2 强模型退回后的**实质逻辑重写**（outbox 投影改 Core 列、终态 rowcount 语义、create_scene_run 统一版本分配入口），非小修，不适用先合后补跑。
2. **R2-05 跨 owner 契约只完成一半**：裁决要求"所有 scene run 创建时同事务分配 SceneAnalysisVersion + switch 比较改持久 id"两端一致。1号 create 侧已交付，但 **2号 switch 侧（R2-03，scene_result_service:445 自引用 UPDATE 1093）尚未交付**——wt-04a 仍停在 base eff0479，receipts/TASK-06B/ 无 r2-rework 回执。契约"换版比较字段改为持久 id"未落地，端到端无法独立验证；1号回执自己也标注"请协调者在 R2-03/05 两端都收口后，派 TESTER 做真实交错 MySQL 端到端联调"。
3. **回执显式留给协调者裁决 2 项（超机械定性）**：① R2-01 第 4 个列 `ingest_submission.selection_json` 是**派单未点名**的同类 1101 隐患，1号已一并去掉（否则升级仍 1101），请确认处置正确；② R2-01 已应用实例处置推断（"MySQL 本不允许 TEXT 带 DEFAULT → 已应用 02 的库必然升级中断在 02、不可能停在 20261008_02 → 无存量库需补 de-DEFAULT 迁移，方案 A 即可"）请确认；若判需给已应用库补迁移再派。

## 建议（供主会话，不代为执行）
- 等 2号 R2-03/R2-05-switch 侧交付后，由协调者（持 flock ocr.lock）对 f088c2b + 2号 commit **串行 OCR 收口**，无 high/critical 再 --no-ff 合入，随后派 TESTER 做 R2-05 交错 MySQL 端到端联调（1号 create 侧 + 2号 switch 侧）。
- 确认 R2-01 selection_json 第 4 列处置 + 已应用实例"无存量 de-DEFAULT"推断。
- 机械验收证据已齐（8/84/812+ruff 全绿、merge-tree 0 冲突、base 正确），主会话裁决后可直接放行，无需重跑测试。
## 主会话裁决（13:52，协调者）
化身挂起正确，两个确认项逐条核实后裁决：
- **确认项①（selection_json 第 4 列一并去 server_default）= 处置正确**。核实写入侧：
  ingest_service.py:322 `selection_json=json.dumps(...)` + :232-234 三列创建时全显式 json.dumps
  赋值，读取侧 :85-87 有 `or "[]"` 兜底——去掉 DB 层 DEFAULT 不影响业务，且消除了派单未点名
  的同类 1101 隐患（4 列全清）。1号 主动扩到第 4 列是对的不漏的。
- **确认项②（已应用实例无需 de-DEFAULT 迁移，方案 A）= 推断成立**。MySQL 8.x 本就不允许
  TEXT/BLOB 带字面量 DEFAULT → 任何库跑旧 02 时若命中 create 分支（表不存在）必然 1101 中断、
  不可能"已成功停在 20261008_02 且表带 DEFAULT"；空库路径 ORM 建表本就无 DB DEFAULT。
  故不存在需要补 de-DEFAULT 迁移的存量库，直接改 02 源码删 DEFAULT 安全（已应用 02 的库
  alembic_version 已前进，改源码不影响它们；未应用 02 的库跑改后 02 不再 1101）。
- **R2-05 契约两端已齐**：2号 c67600d（13:07 交付）switch 侧 :433 `target.id < current.id`
  用分配时刻持久 id 序号（核实落地，注释明确 R2-03/R2-05）。1号 create 侧 f088c2b + 2号
  switch 侧 c67600d 应一起 OCR + 合入 + TESTER MySQL 端到端联调。
- **剩余卡点**：f088c2b 与 c67600d 均无 OCR 收口（R2 返修 commit，fresh 大交付）。
  主会话起合入前串行 OCR（--exclude tests，单 commit 模式）；无 high/critical 后 --no-ff 合入
  两笔（R2-05 契约整体），再派 TESTER 做 R2-05 交错 MySQL 联调 + R2-01/02/03 MySQL 终测。
