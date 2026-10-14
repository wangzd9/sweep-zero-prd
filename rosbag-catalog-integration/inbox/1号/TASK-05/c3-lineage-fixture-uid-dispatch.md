# 派单：C3-lineage 夹具 bag_uid 越宽最小修复（TASK-08 联调发现回派）

- task/attempt：C3-lineage / c3-1（TASK-08 attempt-1 联调发现 §C3 新同型，2号报告 §F.1 建议 1号连续）
- 角色：1号（A）
- 固定 base：main `f9bafb0`（= origin/main，已含 i1-1 `6823f2d`；ACK 前若 main 前移以合入时 origin/main 复核，不重跑已完成证据）
- 范围（最小，仅测试夹具，零 app 变更）：
  - `tests/test_scene_slice_lineage.py:74-75` 父/子 uid 构造：`BAG_PREFIX "T02" + hex[:24]`（含 "PARENT"/"CHILD" 后缀拼接）= 27 字符，越 `bag_record.bag_uid` VARCHAR(26)，真 MySQL 8.4.11 strict 下 setup 1406（10 errors 全因它，SQLite 遮坑）
  - 修口径与 i1-1 `6823f2d` 完全一致：hex 段缩短使最长 uid ≤26 字符 + 构造处加 `assert len(uid) <= 26` 防回归
  - 仅改该文件 uid 生成点；`_purge`/断言/业务逻辑不动；同文件其余 24 hex 用法逐处核对是否同族越宽（`child_uid` 同处生成），一并收敛
- AC：真 MySQL 8.4.11 STRICT 隔离库（本地栈 `rosbag-catalog-local-mysql-1`，对齐 2号 t08 口径：独立新库+会话 FK off+create_all，用完即毁 0 残留）下 `tests/test_scene_slice_lineage.py` 文件级全绿；SQLite 定向同文件不回归；ruff 绿
- 停止条件：上述文件级全绿 + 隔离库 0 残留 + 回执 REVIEW_PENDING；发现 app 面问题只记录不修（回派口径同 TASK-08 边界）
- 路径：新建任务分支（如 `scene/task-08-c3-lineage-fixture`）+ 独立 worktree（如 `wt-01-c3`）；不动在冻 worktree（`wt-01`/`wt-01-i1` 冻结不删）
- 交付：回执 `receipts/TASK-08/c3-lineage-c3-1.md` + 报告 `reports/TASK-08/c3-lineage-c3-1.md`（环境口径、命令/退出码、真 MySQL 文件级日志路径、隔离库清理证据）
- 证据定位（2号 scratch，可复用复现）：`~/.hermes/cache/scratch/t08-e2e/fkoff/isol2_7_test_scene_slice_lineage.py.log`（10 errors 1406）、`allfiles/af_62_test_scene_slice_lineage.py`
- 越界申报：零 app 变更；不处理 C1/C2（2号专项单已派）
