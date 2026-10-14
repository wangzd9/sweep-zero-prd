# 派单：TASK-05 / I-1 夹具 uid 越宽最小修复（attempt i1-1）

- task/attempt：TASK-05 / i1-1（来源=强复审 R2I-20261010-06 VERIFICATION_GAP I-1，result §2）
- 角色：1号（A）
- 固定 base：main `62a85bfb6b3791ebfa706cce0125bb217635126f`
- 范围（最小边界，零 app 变更）：
  - 仅改 `tests/test_scene_slice_scheduling.py` 中 `T05` 前缀夹具 `bag_uid` 生成点（如 `T05noscene-*`/`T05api-dis-*`/`T05cancel1-*` 等 28 字符 uid，`bag_record.bag_uid` 为 VARCHAR(26)，真 MySQL strict 下 setup 1406 拒插）
  - 口径=同 `6ee858b` 的 hex 缩短（前缀 + 随机段收敛使总长 ≤26），并在 uid 构造处加长度 assert（>26 直接测试失败，防止回归）
  - 不改 app/、不迁移、不改其他测试文件、不处理 T06 等其他前缀族
- AC：
  1. 本地 SQLite 定向 `pytest tests/test_scene_slice_scheduling.py` 全绿 + ruff 绿
  2. 真 MySQL 8.4 隔离库（自建容器、用完即毁 0 残留）跑 `tests/test_scene_slice_scheduling.py` **文件级全绿**（I-1 停止条件）
- 交付：单 commit，回执 `receipts/TASK-05/i1-1.md`（REVIEW_PENDING），附 1/2 两项原始日志路径
- 停止条件：交付回执即停；不扩范围（其他夹具族/观察项一律不碰）
- 路径：新建任务分支 `scene/task-05-i1-fixture-uid` + 独立 worktree（如 `wt-01-i1`），不动在冻 worktree
