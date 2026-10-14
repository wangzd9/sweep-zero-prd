# ACK：TASK-08 合入后 9 红文件全绿复核（post-merge-0a8ca8a）

- status: ACK
- 角色：TESTER（独立真 MySQL 取证）
- ACK 时间：2026-10-11 19:22 +08:00（preflight checked_at 2026-10-11T19:19:53+08:00 control=ACTIVE、legacy_busy 空）
- 被测快照：main `0a8ca8a`（独立复核 = origin/main，fetch 后双核一致，--no-ff parents `98f6c88`+`bf48a45`，19:17 合入）
- 环境：真 MySQL 8.4.11 STRICT 隔离库（镜像 `docker.m.daocloud.io/mysql:8.4` 6ea90827b110，新容器/新库 t_tester_pm<N>，FK off + create_all，生产默认 PyMySQL，用完即毁 0 残留）；独立干净检出 main `0a8ca8a`（新建 TESTER 专属 worktree，不动开发槽）
- 范围：9 红文件 + 06B 回归 2 文件 + 迁移链 2 文件 + `test_scene_slice_lineage` 1 文件，文件级真 MySQL 全绿 RC=0，隔离库/用户 0 残留
- 报告路径：`reports/TASK-08/post-merge-0a8ca8a-red-files.md` + 回执 `receipts/TASK-08/post-merge-0a8ca8a-red-files.md`（TEST_REPORT_PENDING）
- 停止条件：全绿交付；任一 FAIL → 定位 app 文件:行 + 最小复现，不改业务代码
- 执行方式：长测试留实际进程+固定快照检查点后释放控制租约，后续巡检只核查不重复启动