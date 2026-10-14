---
task: TASK-03B
item: verify-f11e617-f2-concurrency
owner: 测试者
status: ACCEPTED
dispatched_by: 协调者
updated: 2026-10-09 16:40
target: wt-03b HEAD f11e617（F2 返修：patch_submission 单条守卫 UPDATE + synchronize_session='fetch'）
---
# 验证派单：f11e617 F2 乐观锁并发隔离库实测

## 背景
03B F2 缺陷：旧实现"内容列 ORM 属性 flush + 独立条件 UPDATE"在 MySQL 真并发下，
输方会话的内容 flush 因 affected-rows 语义返回 0 → ORM 抛 StaleDataError（API 面 500），
rowcount==0→409 分支不可达。协调者 2026-10-09 14:0x 在隔离库双会话竞争实测首次发现
（证据：reviews/TASK-03B/attempt-2/f2-isolation-evidence.log，RESULT_A=StaleDataError / RESULT_B=OK / row_version=2）。
3号返修 f11e617 改为单条 `UPDATE ... SET <内容列>, row_version=row_version+1 WHERE
submission_id=:id AND row_version=:expected AND status='PENDING_INPUT'`
+ `synchronize_session='fetch'`，自报隔离库复验 PASS×3（reviews/TASK-03B/attempt-2/f2-isolation-retest-evidence.log）。
**协调者不采信自报**，派你独立复测。

## 验证项（MySQL 8.4，docker 隔离环境）
1. **双独立会话同拍竞争**：Barrier 同时调 `patch_submission(db, "f2sub1", 1, {...合法 scene_slice 选择...}, None)`
   （合法选择 = purposes=["scene_slice"] + scenes=[{scene_code:"test-capability", capability_version:"test-v1", parameters:{}}]，
   否则 422 SCENE_EMPTY 到不了守卫）。
   **期望**：恰好 1 个 OK + 1 个 HTTP 409 ROW_VERSION_CONFLICT，最终 row_version=2，输方内容不覆盖赢家。
2. **同代次重放幂等**：赢家响应后，用旧 row_version=1 再发一次同 key 请求 → 应 409（非 200 重放，
   因 scope 含 row_version，语义见 docstring）。
   ⚠️ 协调者裁决更正（2026-10-09 17:1x）：测试者实测发现同 key+同 payload+同代次重放命中幂等账回放 200，
   而非本条预期的 409。**裁决=接受现状，不改代码**：幂等账 scope（source+generation+purpose+version+hash）
   语义下，同代次同 key 同 payload 重放=同一请求重发，回放原始 200 响应是幂等契约的正确行为；
   本条预期 409 只适用于"同 key 但携带过期 row_version 的 PATCH"路径（守卫 UPDATE 的 409，V1 已证实）。
   派单注释是我写错了场景边界，测试者报告按"核心不变式成立"采信即可，无需回派 3号。
3. **连续两代**：row_version=2 的 patch 成功 → 3；并发端再携 2 竞争 → 409。
4. 环境注意（协调者已踩过的坑，直接抄用可省时间）：
   - mysql:8.4 容器 + python:3.10-slim 容器**同 docker network**（容器名/网络前缀 test-*，别用 coord-*）；
   - pymysql 必须 ==1.1.1（requirements 锁定）；caching_sha2 非 TLS 客户端 1045 是已知环境坑——
     pymysql 直连同网络容器名可用（协调者 f2_probe 验证过 plain 连接 OK）；
   - SQLAlchemy 的 connect_args["ssl"] 会被 pymysql 方言吞（1045 假象），用 `create_engine(url, creator=pymysql.connect 直连函数)` 绕开；
   - 建表用 `Base.metadata.create_all(engine, tables=[IngestProfile.__table__, IngestSubmission.__table__, ApiIdempotency.__table__])`
     （容器内 sqlalchemy 版本若旧，CreateTable 手工编译会 _ordered_columns 报错）；
   - wt-03b 挂载进 python 容器（-v /home/wang/.local/state/rosbag-scene/wt-03b:/work），DATABASE_URL/F2_URL 指向 <mysql容器>:3306/<db>。
5. 收尾：`docker rm -f test-* + docker network rm`，确认 0 残留（docker ps -a --filter name=test-）。

## 交付
- 过程 ACK + 证据按你 prompt 的 test-receipts 约定写 `test-receipts/TEST-03B-F2/attempt-1.md`（含被测快照 f11e617、环境、命令、退出码、关键输出、PASS/FAIL、状态 TEST_REPORT_PENDING），群内通报。
- **最终验证结论报告额外落** `reviews/TASK-03B/attempt-2/verify-f11e617-f2.md`（协调者采信用，格式：环境/命令/每项真实退出码与关键输出行/证据日志路径/结论 PASS 或 FAIL+复现细节）。
- 禁止：改任何业务代码/测试文件；FAIL 也不要自己修——报告里写清，协调者回派 3号。