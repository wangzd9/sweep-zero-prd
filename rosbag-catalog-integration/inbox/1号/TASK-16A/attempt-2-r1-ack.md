# ACK：TASK-16A attempt-2-r1 最小返修（OCR 收口后合并）

- status: ACCEPTED
- ACK 时间：2026-10-13 03:54 +08:00
- owner：A（执行者A·数据处理链路）
- 派单路径：`inbox/1号/TASK-16A/attempt-2-r1-dispatch.md`（2026-10-13 03:48，协调者 r116 派发）
- task/attempt：TASK-16A / attempt-2-r1（attempt-1 交付冻结后的合并返修，沿 07B r102 先例）
- base：`c30f048`（attempt-1 交付冻结 HEAD，`wt-01-t16a` 续 1 笔 commit；禁止 rebase/reset 已核在案）
- 分支/worktree：`wt-01-t16a` @ `/home/wang/.local/state/rosbag-scene/wt-01-t16a`，ACK 时 rev-parse HEAD=`c30f048bbc20b316d05cf8a984309bd448905aef`，porcelain 仅 `.venv` 未跟踪（既定）
- 范围确认：仅 6 项（R1-1..R1-5 + R1-6 无），全部 low/2 行量级；零新表、零新迁移文件、零新依赖、不碰 07B 冻结文件、不碰 `app/scanner/clients.py`（medium 已裁决随合入备注）
- 自测口径：定向新增/变更用例 + 16A 既有定向复跑 + `ruff` + `alembic heads` 单头 + 全量 SQLite（web 性能计时 1 failed=base 复现环境性，如实申报）
- 停止条件：6 项完成+自测全绿即交付冻结 REVIEW_PENDING，回执 `receipts/TASK-16A/attempt-2-r1.md`；任何项需扩面（>2 行/新文件/语义变化）立即停并回报协调者
- 声明：交付后等协调者增量 OCR（`--from c30f048 --to 新HEAD`）收口，不自行合入；16B OCR 在途属协调者串行不占本角色