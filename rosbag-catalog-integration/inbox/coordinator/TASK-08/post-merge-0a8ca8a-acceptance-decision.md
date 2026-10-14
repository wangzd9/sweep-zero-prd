# Decision：TASK-08 合入后 9 红文件全绿复核验收 + TASK-08 收口

- status: ACCEPT + TASK-08 DONE
- 裁决时间：2026-10-11 19:46 +08:00（cron poll 14ae4556629a，真实 checked_at 2026-10-11T19:45:53+08:00）
- task/attempt：TASK-08 / post-merge-0a8ca8a-red-files（合入后独立验证）
- owner：TESTER（独立真 MySQL 取证，不复用 2号容器/库/日志）
- 被测快照：main `0a8ca8a`（= origin/main，协调者本轮 rev-parse 双核一致；--no-ff parents `98f6c88`+`bf48a45`，19:17 合入）

## 协调者独立机械核验（本轮实测，非仅采信回执）
- **快照核对**：`git rev-parse HEAD`=`bf48a45`（wt-04a-t08c 侧）→ origin/main=`0a8ca8a`，`git log -1 origin/main` = Merge 08 t08c-1；main 未再前移。
- **机器证据逐条核**：`~/.hermes/cache/scratch/t08-tester-pm08/results.json` `all_pass: true`，14 文件逐条 `rc=0` + `dropped=true`（api/concurrency/worker/clone/source_register/pipeline/lineage/web/scheduling/report/storage/migration_rollback/cst/scene_slice_lineage）。
- **日志 spot-check**（非采信 summary 行）：`pm08_00` 24 passed / `pm08_07` 41 passed / `pm08_08` 36 passed / `pm08_13` 10 passed 1 skipped，与回执报告表格一致。
- **残留核**：`docker ps -a` 无 pm08/t08/tester 容器残留；`/home/wang/.local/state/rosbag-scene/` 无 tester worktree 残留（回执"测毕 worktree remove + 隔离库 0 残留"成立）。
- **AC 全命中**：9 红文件（0–8）全 RC=0 全绿 ✓ / 06B 回归 report 35 + storage 25 不破坏 ✓ / 迁移链 2 文件 RC=0 零迁移改动链未破坏 ✓ / scene_slice_lineage 10+1 skipped（skip=SQLite 方言守卫，c3-1 既有口径非本单引入）✓。

## 裁决
- **ACCEPT**：合入产物 main `0a8ca8a` 经 TESTER 独立真 MySQL 8.4.11 STRICT 取证**无回归**，9 红文件全绿成立。
- **TASK-08 收口**：收口条件 2/2 满足——c3-1→`98f6c88`（17:02）+ t08c-1→`0a8ca8a`（19:17）均已 --no-ff 合入 main，合入后 9 红文件全绿复核 PASS（本轮 19:46）。**TASK-08 转 DONE**。
- 强复审 R2I-20261010-06 已 PASS 收口（15:18，无新增门禁）；生产启用/真实样本门禁（TASK-09/10/11）维持未放行，不因 08 DONE 自动放行。

## 下一步候选重算
- TASK-08 DONE 释放联调线；TASK-10（目录→坡道切片→数据库→API 真实工程闭环）前置依赖 TASK-08+TASK-09。TASK-09 仍 BLOCKED（需用户授权真实坡道样本/VLM 服务），**TASK-10 维持 WAITING**，不因 08 DONE 单独派发（依赖 09 未解除）。
- 无其他本期已授权、依赖已接受、无冲突的候选 → **本轮无新派单**，A/B/C/TESTER 空闲不扩需求。

- 裁决人：协调者 cron（单写租约持有，控制动作即时释放）