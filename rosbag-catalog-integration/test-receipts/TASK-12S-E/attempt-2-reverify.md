# TESTER TASK-12S-E attempt-2 增量复验报告（TEST_REPORT_PENDING）

- 生成时间：2026-10-15 12:0x +08:00（11:5x 重建环境，12:0x 完成全部 5 面）
- **结论：PASS**（冻结 head `1e9c7de` 在真实 MySQL 8.4.11 隔离库下 attempt-2 增量 5 面独立复跑全过；attempt-1 PASS 面按派单口径复用不重跑；隔离资源已归零留证）
- 被测固定快照：base `b39a3ecc76da1f578d32f4e3c88a6ce989cf749d` → head `1e9c7deff16b532ad7430c5b3639f2e55bb62ec3`（worktree `wt-01-t12se` 分支 `a/task-12s-e-auto-bind`，HEAD 实测一致）
- 派单：`inbox/TESTER/TASK-12S-E/attempt-2-reverify-dispatch.md`（协调者 10:26）
- 上一轮 BLOCKED（11:20 记录）根因复核：**mysql:8.4 官方镜像只为 `MYSQL_USER` 建 `@'localhost'` 条目，容器 bridge 源 IP（172.17.0.1/172.22.0.1）不匹配 → 1045**。与 client_flag/URL 解析无关（11:20 已排除项维持）；本轮补授 `GRANT ... 'user'@'%'` 后 raw pymysql 与 SQLAlchemy engine（app 实际连接路径）**双通**，复验得以执行。

## 环境（TESTER 自建，用完即毁）

- 容器 `rosbag-t12se2b-165cc806-mysql`（mysql:8.4，8.4.11 实测），loopback 127.0.0.1:39261 发布，专用户 `t12se2b`（默认 `@'localhost'` + 本轮补授 `@'%'`）
- sql_mode 实测 `ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION`（留证 `scratch/t12se2b_165cc806_sql_mode.txt`）
- `alembic upgrade head` rc=0，单头 `20261013_01_scene_intake`（fresh 路径实测；本交付零迁移变更，existing 路径=同 head 不变）
- wt-01-t12se `.venv`（Python 3.10.12），`TEST_EXECUTION_MODE` 走测试夹具口径，VLM 调用=0

## 5 面逐条结论

### ① E-R7 真实口径夹具 → PASS
`tests/test_task12se_auto_bind.py` 全文件 17 用例在真 MySQL 8.4.11 下 **-q 17 passed（5.76s，rc=0，-v 逐条 PASSED）**。其中真实口径面 `test_reconcile_bound_paths_real_physical_caliber_and_purposes`（:616）+ `test_reconcile_fifo_selection_when_over_limit`（:660）= E-R7 新增夹具独立复跑通过：源行经 upsert_bag 登记后 `relative_path` 落 storage 相对段，incoming 侧检测在真实口径下命中（b39a3ec 旧口径恒 False 的缺陷不复现）。

### ② E-R1~R3 字段断言 → PASS
同上 17 用例集内 `bound_ready_path`（storage_root/relative_path 真实物理口径、非 ready_root 拼接）、`bound_incoming_path`（含 `profile.incoming_prefix` 段）、`bound_purposes_json` 持久化且同一 bag 两次登记用途回显一致不变式——由 :616/:660 用例断言覆盖，真 MySQL 下全 PASSED。

### ③ E-R8 两路 → PASS
- 豁免路 `test_register_move_recovery_with_slice_sibling_exempts_409`（:812）PASSED：incoming 侧恰 1 原包行+本次注册落受控 ready 根+同指纹切片兄弟行 → 不 409 走移动恢复。
- 非豁免路 `test_register_slice_fingerprint_still_409_without_move_recovery`（:871）PASSED：同指纹切片兄弟但 incoming 侧 0 行/多行 → 仍 409。
- 切片兄弟行血缘不动由两用例断言核实；无需"断点+材料"登记（真 MySQL 夹具可完整构造）。

### ④ E-R4 防御面 → PASS
`test_reconcile_defensive_root_not_configured_fails_closed`（:732）PASSED：ready 根不在 storage 根下且根身份不可推导 → `ROOT_MISMATCH` 不绑（夹具模拟，未构造生产配置异常，符合派单口径）。

### ⑤ 回归抽查 → PASS
attempt-1 154 口径扩展复跑：`test_task12se_auto_bind` + `test_pipeline_api` + `test_source_register_purpose` + `test_ingest_config` + `test_scene_slice_scheduling` + `test_t10def1_source_ready` + `test_scene_intake_isolation` + `test_scene_spray_intake` = **159 passed（13.12s，rc=0，真 MySQL 8.4.11）**。零失败；E-R6 统计 key 面（`test_pipeline_api` 改动+`test_consume_endpoint_no_pending_returns_legacy_shape` :594）核 `pending_reconciled` 条件键与旧口径兼容（outbox 空时统计集合不意外缩小）通过。attempt-1 五面（12 机械口径/独立探针/回归/零越界/自清）按派单"只补增量面"复用既有 PASS 证据，不重跑。

## 零越界与环境边界

- 被测 worktree 全程只读：HEAD 保持 `1e9c7de`、`git status` 仅 `?? .venv`（派单边界既有软链），零 commit/零改动。
- VLM 调用=0；未写生产库/NAS/A100；未碰 1012 大包取消链与 12S-F 开发树。
- 隔离资源归零证据：`docker rm -f rosbag-t12se2b-165cc806-mysql` + `docker network rm rosbag-t12se2b-165cc806-net` 已执行，`docker ps -a --filter name=rosbag-t12se2b` 输出空（12:0x 实测）。
- 上轮 11:20 已归零的 `rosbag-t12se2*` 容器无残留（本轮容器名前缀 `t12se2b` 独立）。

## 命令与退出码汇总

| 命令 | 退出码 | 结果 |
|---|---|---|
| `alembic upgrade head`（fresh 隔离库） | 0 | head=`20261013_01_scene_intake` 单头 |
| SQLAlchemy engine `SELECT VERSION()` 探针 | 0 | 8.4.11（engine 路径双通，11:20 BLOCKED 点解除） |
| `pytest tests/test_task12se_auto_bind.py -q`（DATABASE_URL=隔离库） | 0 | 17 passed |
| 同上 `-v` 逐条 | 0 | 17/17 PASSED（E-R1~R8 点位 :616/:660/:732/:812/:871 全在） |
| 8 文件回归集（154 口径扩展） | 0 | 159 passed |
| `docker rm -f` + `network rm` + `ps -a` 复核 | 0 | 零 `rosbag-t12se2b*` 残留 |

## 交付状态

**TEST_REPORT_PENDING（PASS 面）**：交协调者裁决。按派单后续链：E 接受（head `1e9c7de`）→ 通知 B 12S-F 冻结 base rebase。本回执与 11:20 BLOCKED 记录并存，以本 PASS 为准（BLOCKED 为环境阻塞历史，非代码缺陷）。