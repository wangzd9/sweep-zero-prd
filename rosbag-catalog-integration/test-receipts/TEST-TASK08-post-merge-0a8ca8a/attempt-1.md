# test-receipt：TEST-TASK08-post-merge-0a8ca8a / attempt-1

- status: TEST_REPORT_PENDING
- 角色：TESTER，交付 2026-10-11 19:44 +08:00
- 被测：main `0a8ca8a`（= origin/main 独立复核一致）
- 环境：真 MySQL 8.4.11 STRICT 隔离容器（tester-pm08-mysql @172.22.0.2，镜像 6ea90827b110，tester_pm08 用户，逐文件 t_pm08_0..13 FK off + create_all，生产默认 PyMySQL），detached worktree wt-tester-pm08
- 命令（每文件同型）：`.venv/bin/python3 -m pytest tests/<file> -p pm08_plug -p no:cacheprovider -o addopts= -q --tb=short`
- 结果：14/14 PASS RC=0（24/11/19/2/8/25/3/41/36 + 35/25 + 2/2 + 10 passed 1 skipped）
- 证据：`~/.hermes/cache/scratch/t08-tester-pm08/results.json`（all_pass=true, elapsed 79.6s）+ `logs/pm08_00..13_*.log`
- 清理：容器/网络/逐文件库/worktree 0 残留（docker ps -a 核实）
- 报告：`reports/TASK-08/post-merge-0a8ca8a-red-files.md`；回执：`receipts/TASK-08/post-merge-0a8ca8a-red-files.md`