# ACK：TESTER TASK-09 post-merge-ca8730d 合入后独立真 MySQL 验证

- status: ACCEPTED
- ACK 时间：2026-10-11 21:41 +08:00（TESTER cron poll 回合）
- 被测 base：main `ca8730d7050c105b73e9387f4adda182d3a14e64`（= origin/main，git fetch 双核独立复核一致；`a60bb81` 已 --no-ff 合入，merge-base --is-ancestor a60bb81 main = yes）
- 被测改动：`a60bb81` 3 文件 +187/-3（`app/scene/slope/vlm.py` +17/-2 / `app/scene/slope/adapter.py` +10/-1 / `tests/test_slope_vlm_wiring.py` 新增 163 行），`git show --stat a60bb81` 独立复核与派单一致，零越界
- 环境：独立 detached worktree 检出 `ca8730d`（干净）+ 真 MySQL 8.4.11 STRICT 隔离容器（用完即毁 0 残留），口径同 TESTER pm08/t09 先例；只读 NAS/不代开发
- AC 已读：① 真 MySQL 06B 核心（report+storage 60 passed）+ slope 接线面（test_slope_vlm_wiring + test_slope_adapter，SQLite 44 passed 口径真 MySQL 复跑）；② 迁移链 alembic upgrade head RC=0 + 单头 `20261009_02_ingest_frozen`（本次零迁移，快速确认）；③ SQLite 全量（ignore test_devflow，交付侧 813 passed/10 skipped 口径不回归）；④ 隔离资源 0 残留声明 + ruff 3 文件
- 停止条件已读：全部 AC RC=0 且隔离 0 残留 → 交付 `test-receipts/TEST-TASK09-post-merge-ca8730d/attempt-1.md`（REVIEW_PENDING）+ 报告；失败记 app 文件:行+复现口径，**不改业务代码**，交协调者裁决回派
- 路径已确认：回执 `test-receipts/TEST-TASK09-post-merge-ca8730d/attempt-1.md` / 报告 `reports/TEST-TASK09-post-merge-ca8730d/attempt-1.md`
- 开工：本轮起，固定快照 ca8730d；长测试进程与容器留检查点，控制租约释放后巡检只核查不重复启动