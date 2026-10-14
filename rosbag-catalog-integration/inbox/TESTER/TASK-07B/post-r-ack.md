# ACK：TASK-07B 07B-post-r 合入后独立验证（attempt-1）

- status: ACKED
- ACK 时间：2026-10-13 08:02 +08:00（测试者 poll cron 167580c0500b，会话 cron-tester-poll-167580c0500b-20261013-075953）
- 派单：`inbox/TESTER/TASK-07B/post-r-dispatch.md`（r133 派发）
- 被测 target：`62620a3ddc5cfa614c5e72681c852c96d60507b3`（`scene/task-07b-manual-revision-withdraw` @ `/home/wang/.local/state/rosbag-scene/wt-04a-t07b`，R4 交付冻结 HEAD，base `4baf79f`）
- 整链 origin base：`502bf8e`（未合入）
- 快照核对：实测 `git rev-parse HEAD` = `62620a3ddc5cfa614c5e72681c852c96d60507b3`，工作树仅 `.venv`/`scratch` untracked（非代码改动）；07B 三个测试文件在案；镜像 `docker.m.daocloud.io/mysql:8.4` 本地已缓存（6ea90827b110，8.4.11 待容器内 SELECT VERSION() 实测）
- 环境口径：独占 MySQL 容器 + 独立 docker 网络（无宿主端口映射）、用完即毁 0 残留；自包含 uvicorn 独立端口 + 临时 SQLite 夹具（DEMO_DATA=0）；不触碰共享 real 栈/容器/宿主代理/生产
- AC 范围：SR-05 真 MySQL 双连接同版本无关联并发 200/409（版本 +1、审计行/MANUAL evidence 各一行）；R4 迁移面正常态 fresh upgrade→downgrade -1→upgrade 往返 RC=0 + SHOW COLUMNS 双表 corrected_label + 容器 0 残留；表缺失态 SQLite 内存 + 真 MySQL 双库 DROP `scene_manual_revision` 后 downgrade 不抛异常；07B 定向 pytest 三文件全绿；页面实测不回归
- 合成态（审计表缺失+evidence 列存在）按 r133 裁决 `r4-01-adjudication-20261013.md` 不属本单验收项
- 交付：`test-receipts/TEST-TASK07B-post-r/attempt-1.md`
- 停止条件：全项 PASS/FAIL 取证完毕交付 TEST_REPORT_PENDING；不扩 07B 需求面
