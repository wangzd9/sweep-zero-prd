# ACK：TESTER 12S-A/B 独立验证（并行，不等 OCR）

- status: ACK
- ACK 时间：2026-10-13 14:15 +08:00（cron poll `167580c0500b`，prerun 指纹 `9be2537e…`）
- owner：TESTER（独立测试槽，本 ACK 前实测无在途业务进程、无 tester 容器残留）

## 固定快照核（rev-parse 实测）

- 12S-A：worktree `/home/wang/.local/state/rosbag-scene/wt-01-t12sa`，base `6fb42c4` → head **`77c395b902f8b8b57276ac509e1c2dcc5ab26e90`**（实测一致；`git status --porcelain` 仅 `?? .venv` 软链，无业务改动）。
- 12S-B：worktree `/home/wang/.local/state/rosbag-scene/wt-04a-t12sb`，base `6fb42c4` → head **`f62a29c211ac846342dd79b2937962f8cb3c172c`**（实测一致，同上仅 `?? .venv`）。
- **worktree 名勘误申报（不阻塞）**：派单写 12S-A 快照 worktree `wt-01-t16a`，实测 12S-A 交付 worktree 为 `wt-01-t12sa`（A 回执 `inbox/1号/TASK-12S-A/attempt-1-receipt.md` 同口径）；`wt-01-t16a` 为 16A 历史 worktree。base/head commit 与回执完全一致，按 commit 为准。
- 回执核：`inbox/1号/TASK-12S-A/attempt-1-receipt.md`（25 定向 + 78 回归 + 908 passed/10 skipped，4 既有失败申报）与 `receipts/TASK-12S-B/attempt-1.md`（54 定向 + 142 场景域 + 937 passed/4 failed 既有集对照）均在案；派单引用的 `receipts/TASK-12S-A/attempt-1.md` 路径不存在，12S-A 回执实际在 `inbox/1号/` 下（同内容口径，不阻塞）。

## 环境

- 测试库：本地 docker 镜像 `mysql:8.4`（实测在库 6ea90827b110），按 16A 轮口径起 `tester-t12sab-mysql` 隔离容器 + 独立网络 + loopback 3387 映射，用完即毁。
- 12S-A DDL 面预核：`git diff 6fb42c4..77c395b -- app/models.py alembic/` 实测**零新增**（`intake_snapshot_json` 列 16A 已在 main），本单 MySQL 面=既有单头迁移往返 + spray 入口 API/快照在真 MySQL 上的行为验证（迁移面声明以实跑为准）。
- 参考图：`/home/wang/work/ros2_slice/images/refs`（7 jpg 实测在位），sha256/bytes/JPEG magic 与 `references.py` 冻结清单比对。
- 只读探针：`/home/wang/下载/1012/rosbag2_2026_10_12-15_58_23`（57MB 小包，sqlite3 只读）。
- 本机无 numpy/open3d/PIL/decoder 共享库（12S-B 回执同口径）：真实解码/渲染/付费 VLM = NOT_RUN，按派单 §二口径不 mock 当 PASS。

## AC 与验证场景

- 12S-A：定向 `tests/test_scene_spray_intake.py` 复跑 + 全仓 pytest（既有失败集对照）+ 隔离 MySQL 8.4 迁移往返 + `scene-isolated` 坡道默认 base/head 对比 + spray 入口 fail-closed 面 + 旧入口零回归。
- 12S-B：定向 `tests/test_spray_adapter.py` 复跑 + 全仓 pytest + 整数 storage ns 映射（时追证据）+ PCD 解码探针（1012 小包只读）+ 双 pass/异常归一口径 + 7 参考图 hash/顺序比对 + 合成自洽。
- 不碰生产/处理机/NAS 生产路径；不跑 OCR；发现 CORRECTION 级缺陷回执标 BLOCKED + 定位 + 复现命令，不代修。

## 报告路径

- `test-receipts/TEST-TASK12S-AB/attempt-1.md`（PASS/FAIL/BLOCKED 分 A/B 两段）

## 边界确认

- 只读交付快照 + 隔离测试库 + scratch 探针；夹具用毕即毁并申报 0 残留。
- 本 ACK 后按协议：写检查点 → 释放控制租约 → 长验证在途巡检只核查不重启。