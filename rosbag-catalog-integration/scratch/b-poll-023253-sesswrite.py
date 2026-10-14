sess = '/home/wang/work/doc/prd/rosbag-catalog-integration/sessions/B.md'
line = '- 巡检 2026-10-12 02:34 +08:00（cron poll，真实 checked_at 2026-10-12T02:32:53+08:00 preflight）：**无新派单、无返修，TASK-10 已收口 DONE，P0 停止派发——本侧维持 IDLE_WAITING**——02:28 巡检后零业务变化：inbox/2号 01:20 后零新增（最新 t10-defect3 ACK 已收口，无新派单/返修）；receipts/reports/inbox/coordinator 02:11 后零新增；origin/main 实测 453da0c 双核不变（=TASK-10 收口合入点）；wt-04a-t10d3 HEAD=0943885 冻结干净（仅 .venv 软链）、ps 无本侧 pytest/ocr 在途进程；leases 无 B 在途 owner，本回合 claim/release 正常（owner cron-b-poll-6f7471d8747c-20261012-023253）。维持 **IDLE_WAITING**，不占开发槽。事件 `b-poll-20261012-023253-nochange-task10-done-p0-idle` 落盘。下一步：仅按需巡检与事件接续；TASK-11 生产门禁未放行不自行启动。\n'
old = open(sess).read()
open(sess, 'w').write(line + old)
print('SESSIONS_UPDATED', len(line))
