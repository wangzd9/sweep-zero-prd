# 回执：TASK-08 合入后 9 红文件全绿复核（post-merge-0a8ca8a）

- status: TEST_REPORT_PENDING
- 角色：TESTER
- 交付时间：2026-10-11 19:44 +08:00
- 被测快照：main `0a8ca8a`（独立复核 = origin/main，fetch 双核一致）
- 环境：真 MySQL 8.4.11 STRICT（容器 `tester-pm08-mysql` 172.22.0.2，utf8mb4，FK off + create_all，生产默认 PyMySQL），TESTER 专属 detached worktree @ `0a8ca8a`
- 结果：**14/14 文件 PASS RC=0**——9 红文件（api 24 / concurrency 11 / worker 19 / clone 2 / source_register 8 / pipeline 25 / lineage 3 / web 41 / scheduling 36）+ 06B 回归（report 35 / storage 25）+ 迁移链（lineage_rollback 2 / china_standard_time 2，RC=0 零迁移改动链未破坏）+ `test_scene_slice_lineage`（10 passed 1 skipped）
- 清理证据：13 逐文件库跑毕即毁（results.json 逐条 dropped=true），容器/网络/用户/worktree 全部移除，`docker ps -a` 0 残留；零业务代码改动
- 报告：`reports/TASK-08/post-merge-0a8ca8a-red-files.md`
- 机器证据：`~/.hermes/cache/scratch/t08-tester-pm08/`（`results.json` all_pass=true + `logs/pm08_00..13_*.log` 逐文件 pytest 输出）
- AC 核对：9 红文件全绿 ✓ / 06B 35/25 不破坏 ✓ / 迁移链 RC=0 ✓ / scene_slice_lineage 10+1 skipped ✓ / 隔离库 0 残留 ✓ → **全 AC 命中，建议 ACCEPT**
- 边界：普通测试 PASS，非 OCR/强审查/生产门禁；待协调者裁决