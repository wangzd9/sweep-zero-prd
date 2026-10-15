# TESTER TASK-12S-E attempt-2 增量复验 状态：BLOCKED（环境阻塞，未跑完 5 面）

- 生成：2026-10-15 11:20 +08:00；owner 记录=TESTER（cron-tester-poll-167580c0500b-20261015-095657，本轮角色已切协调者，本文件为 TESTER 面交接留证）
- **结论：BLOCKED（验证环境阻塞，非被测代码缺陷）。** 12S-E attempt-2 增量复验 5 面**未实际执行**，E 接受门禁（复验 PASS）**未满足**，不能按「在途/将 PASS」口径推进 E 接受。

## 已完成
- ACK 落 `inbox/TESTER/TASK-12S-E/attempt-2-reverify-ack.md`（10:27）；固定 head 核对一致：worktree `wt-01-t12se` HEAD=`1e9c7de`（base `b39a3ec`），`tests/test_task12se_auto_bind.py` 在位（17 用例，含 E-R1~R8 新增 :616/:660/:732/:812/:871）；`tests/test_pipeline_api.py` E-R6 统计 key 改动面已读。
- 隔离 MySQL 8.4.11 已建（容器 `rosbag-t12se2-attempt2-mysql`，loopback 33791，STRICT_TRANS_TABLES/NO_ZERO_DATE，`mysql_native_password=ON`，专用户 `t12se2`）——**已用完即毁归零**（`docker rm -f`，`docker ps -a` 零 `rosbag-t12se2*` 命中，留证于 TESTER 事件）。

## 阻塞点（证据链）
- **raw pymysql 连接成功**（`SELECT 1` / `VERSION()=8.4.11` 多次稳定 OK，10/10）。
- **但 SQLAlchemy engine（app 测试实际连接路径）在隔离库上 100% 失败**：`OperationalError 1045 Access denied for user 't12se2'@'172.17.0.1'`。已排除凭据（engine 传的 user/pw/db/host/port 与成功的 raw 调用逐参一致）、排除 client_flag（FOUND_ROWS=2 raw 亦成功）、排除密码 URL 解析。属 pymysql/SQLAlchemy 方言在该容器 auth 握手路径的环境级不一致（8.4 caching_sha2/native 在容器 bridge 源 IP 下握手行为），**非被测 attempt-2 代码问题**。
- 结果：`pytest tests/test_task12se_auto_bind.py` 17 ERROR（连接层）、`test_pipeline_api.py` 24 failed/1 passed（同一连接层）——**均为环境阻塞的伪失败，不代表 attempt-2 复验结论**，不得记为代码 FAIL。

## 交接（协调者处置）
- E attempt-2 增量复验**需 TESTER 重跑**，环境建议二选一：① 隔离 MySQL 用 `mysql_native_password` 且 host 映射规避 bridge 源 IP（或容器内跑 pytest）；② 复用前次 attempt-1 PASS 时成功的隔离库配方（00:45 那次 raw+engine 均通，见 `test-receipts/TASK-12S-E/attempt-1.md`①②，其 DSN/连接面与本轮容器差异需比对）。
- 复验未 PASS 前，E 维持「已交付冻结 `1e9c7de` + OCR `a9bf637e` 0 findings 收口 + TESTER attempt-1 PASS 保留（不覆盖真实口径）」，**不转接受**；12S-F 冻结 base 通知（E 接受后）维持暂挂。
- 本 TESTER 面**未跑 OCR、未改业务、未写生产、VLM=0、未碰 1012 大包取消链**；隔离资源已归零。

（本单 attempt-2-reverify 交付回执 `test-receipts/TASK-12S-E/attempt-2-reverify.md` 因环境阻塞未生成正式 PASS/FAIL 结论，以本 BLOCKED 状态记录为准。）