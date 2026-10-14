---
task: TASK-06
item: r2-final-mysql-e2e-attempt-5
owner: TESTER
status: ACKED
acked_at: 2026-10-11 09:52
---
# ACK（TESTER，cron-tester-poll-0950）

- 被测 base：main `4697be0`（= origin/main，ACK 前 git 复核 HEAD 一致，工作树无 app/tests 未提交改动）。
- 环境：真实 MySQL 8.4.11 隔离容器（本地镜像 `6ea90827b110` 不拉取）+ 独立 docker 网络 + 新端口/新隔离库（不复用 attempt-3/4 已销毁的 33070/33071 端口与库名），主仓 `.venv` Python，生产默认 PyMySQL 连接（实测连接 flag，注明不含 CLIENT_FOUND_ROWS）。
- AC 口径：
  - AC1 R-01 秒末边界：`tests/test_scene_result_report.py` 全文件（33 用例，含新增 `test_reconcile_start_ns_truncates_toward_zero_at_second_boundary` ns末=0/500_000_000/999_999_999 三参数）真 MySQL 全 passed RC=0；探针 start_ns 纳秒末=999_999_999 走真实 reconcile 链 → 库内 started_at 落 BASE_S+2 整秒不进位 → 二次同 body 重放 200 无 StaleDataError，started_at/updated_at/row_version 三元组不推进。
  - AC2 R-03 零 UPDATE：同秒重放 + 跨秒重放（monkeypatch 服务内 local_now +1s）下 `UPDATE bag_record` 计数 = 0；独立口径用连接层/探针等价验证，结论注明方法。
  - AC3 不回归：attempt-4 已 PASS 的微秒回归 + 整秒口径各抽查 1 例仍 PASS。
  - AC4 口径核对：`git diff 6d30a68..4697be0` = 3 文件 +156/-8，app 行为面仅 `scene_result_report_service.py` :582 一行赋值 + 注释（已复核）。
- 环境口径说明：派单文字 `R2_MYSQL_DB=<隔离库>` 在仓库 grep 无定义，`app/config.py` 实际读 `DATABASE_URL`——以 `DATABASE_URL=mysql+pymysql://...` 指向隔离库，等效口径，报告注明。
- 只复测上述四项，不重跑已 PASS 的 S1/S2/S3/S4/B8c/B8a/r6 与 attempt-3/4 已收口项；零业务代码改动（只读+测试+scratch 探针）；隔离资源用完即毁 0 残留。
- 交付：`test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-5.md` + `reports/TASK-06/r2-final-mysql-e2e-attempt-5.md` + events/TESTER 事件 + 群内通报。