---
task: TASK-06
item: r2-final-mysql-e2e-attempt-4
owner: TESTER
status: ACKED
acked_at: 2026-10-10 22:51
---
# ACK（TESTER，cron-tester-poll-2249）

- 被测 base：main `6d30a68`（= origin/main，开工前 git 复核 HEAD 一致）。
- 环境：真实 MySQL 8.4.11 隔离容器（本地镜像 `6ea90827b110` 不拉取）+ 独立 docker 网络 + 新隔离库（attempt-3 用过的 33071/t_r2app3 等已销毁，本轮换新端口/新库名避免串库），主仓 .venv Python，PyMySQL 生产默认连接（不含 CLIENT_FOUND_ROWS，实测注明 flag）。
- AC 口径：AC1 `tests/test_scene_result_report.py` 全文件 R2_MYSQL_DB 真 MySQL 全 passed RC=0（含微秒用例）+ 探针 reconcile-1 带小数秒 start_ns→库内落整秒→reconcile-2 同 body 重放 200 无 StaleDataError、started_at/updated_at 不推进、row_version 不变；AC2 整秒口径抽查 1 例仍 PASS；AC3 `git diff 5f0124b..6d30a68` 口径核对 app 行为面仅 M-1 一行赋值。
- 只复测上述三项，不重跑已 PASS 的 S1/S2/S3/S4/B8c/B8a/r6；零业务代码改动；隔离资源用完即毁 0 残留。
- 交付：`test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-4.md` + `reports/TASK-06/r2-final-mysql-e2e-attempt-4.md` + events/TESTER 事件 + 群内通报。
