# ACK：TASK-11 残留最小清理

- status: ACCEPTED
- 派单: `inbox/1号/TASK-11/t11-cleanup-residual-20261012.md`
- task: TASK-11（生产门禁项）/ attempt: 0（观察与清理链接续，不占开发槽）
- owner: A（执行者A，cron poll d5cb80cf2fc5）
- base: main `453da0c`（本单零 app 代码面）
- 实际 worktree: 不适用（仅本地测试栈 DB 与 NAS 测试根文件清理）
- ACK 时间: 2026-10-12 08:47 +08:00
- 前核: `bag_record` 当前 total=18，uid `021F73162DAE4E3188B10BE7FE` 行 id=26（status READY/source_status READY，updated 08:30:51），关联 bag_file=1 / bag_topic=22 / bag_purpose=0；两袋目录实测在位（slope 229M / flat 287M），ready/ 其余 6 袋既有数据保留。