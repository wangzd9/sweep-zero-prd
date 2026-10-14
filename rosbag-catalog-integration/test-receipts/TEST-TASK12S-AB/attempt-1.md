# 测试回执：TASK-12S-AB attempt-1 独立验证（12S-A + 12S-B）

- **status：** 12S-A **PASS** ｜ 12S-B **PASS**（B 证据取自冻结 commit 干净隔离树，见 §五 观察项）
- **测试者：** TESTER（cron `167580c0500b`，owner `cron-tester-poll-167580c0500b-20261013-140453-t12sab`）
- **派单：** `inbox/TESTER/TASK-12S-AB/attempt-1-dispatch.md`（协调者 13:5x，用户授权"加速"，与 OCR 并行）
- **ACK：** `inbox/TESTER/TASK-12S-AB/attempt-1-ack.md`
- **交付时间：** 2026-10-13 14:5x +08:00

## 一、固定快照核（rev-parse 实测）

| 任务 | worktree | base | head（实测一致） |
|---|---|---|---|
| 12S-A | `wt-01-t12sa` | `6fb42c4` | `77c395b902f8b8b57276ac509e1c2dcc5ab26e90` |
| 12S-B | `f62a29c211ac846342dd79b2937962f8cb3c172c`（干净隔离树，见 §五） | `6fb42c4` | 同左 |

**派单勘误（不影响 commit 口径）：** 派单写 12S-A worktree `wt-01-t16a`，实测为 `wt-01-t12sa`（A 回执同口径；`wt-01-t16a` 系 16A 历史 worktree）；派单引 `receipts/TASK-12S-A/attempt-1.md` 不存在，实际在 `inbox/1号/TASK-12S-A/attempt-1-receipt.md`。

## 二、12S-A（PASS）

环境：worktree `wt-01-t12sa`（仅 `?? .venv` 软链，零业务改动）；隔离 MySQL 8.4 容器 `tester-t12sab-mysql`（bridge `tester-t12sab-net`，loopback 3387，双库 `t12sab_base`/`t12sab_head`）。

1. **定向**：`pytest tests/test_scene_spray_intake.py -q` → **25 passed RC=0**。
2. **回归五文件**：`test_ingest_config_api/test_ingest_config/test_ingest_frozen_hash/test_scene_config_schemas/test_scene_intake_isolation` → **78 passed RC=0**（旧入口零回归面）。
3. **全仓**：`pytest tests/ -q` → **908 passed, 10 skipped, 4 failed**（RC=1 仅因 4 既有失败）：`test_devflow.py`×3 + `test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time`×1——与 A 回执申报的既有失败集**逐项一致，零新增**。
4. **迁移面（真 MySQL 8.4.11，RC=0×3）**：fresh `upgrade head`→`20261013_01_scene_intake`、`downgrade -1`→`20261012_01_scene_manual`、re-`upgrade head` 往返；`diff 6fb42c4..77c395b -- app/models.py alembic/` **零新增 DDL**（`intake_snapshot_json` 16A 已在 main）→ 本单 MySQL 面=既有单头往返 + API/快照真 MySQL 行为（已覆盖，非仅 SQLite）。
5. **坡道默认零变化（分库 seed 对比）**：base 库（临时 worktree `6fb42c4`）与 head 库各跑 `seed_scene_isolated_profile`，`scene-isolated` 的 profile_id/version/prefix/root/purposes/scenes/params/`_intake_snapshot` **逐字段一致**，快照 sha256 双库同值 `b9a52858…4f1`；base 无 `seed_scene_spray_profile`、head 有（新增面确认）。
6. **spray 行为面（真 MySQL 探针，14 项全 OK）**：能力未接受 `enabled=False`（bootstrap 不崩）→ 注入 spray 能力后翻转 `True`；窄前缀 `spray`；缺 metadata **422 SOURCE_METADATA_REQUIRED**；未知车辆 **422 UNKNOWN_VEHICLE（不自动建）**；未批准 sensor **422 UNKNOWN_SENSOR_PROFILE**；正常创建 **201** + 快照含 `source_metadata` 块 + `source_metadata_hash` 独立 sha256（≠ effective_config_hash，AC-18.2）；同键同 md 回放 **200**、同键异 md **409**；旧入口无 md **201** 且快照零块（逐字节零变化）；旧入口带坏 md **422**。
7. 证据：`scratch/tester_t12sab_p2.log` / `tester_t12sab_p2.json`（CHECK 逐项 OK 在日志）。

## 三、12S-B（PASS）

环境：冻结 commit 干净隔离树（`git worktree add --detach /tmp/… f62a29c`，用毕即毁）；参考图 `/home/wang/work/ros2_slice/images/refs`；1012 小包只读。

1. **定向**：`tests/test_spray_adapter.py` → **54 passed RC=0**（冻结 commit 复现）。
2. **场景域**：`test_scene_capability_contract/test_scene_config_resolution/test_slope_adapter/test_spray_adapter` → **142 passed RC=0**（slope/test-capability 零回归）。
3. **全仓**：`pytest tests/ -q` → **937 passed, 10 skipped, 4 failed**——与 B 回执申报的 base 既有失败集**逐项一致，零新增**。
4. **整数 storage ns（独立探针，6 项全 OK）**：唯一候选精确命中（19 位奇数 ns 原样保留，basis=`bag_storage_ns`）；无候选拒绝（"不能从 ms 文件名冒充源 ns"）；多候选无 file_ms 拒绝；file_ms 1ms 窗内双候选**歧义拒绝**；**亚毫秒偏移保留**（`ms×1e6+333 ≠ ms×1e6`，直接证伪 ms 冒充）；文件名 13 位 ms 提取/无则 None。
5. **分段精度**：`validate_spray_params` 全整数 ns（15s/3s/7s→15e9/3e9/7e9）、坏密度拒绝；`segment_spray_ns` 端到端：140 帧 10Hz、奇数 ns 起点 → 单 spray 段 `start_ns=1700000000000000001`（**奇数保留，无秒 round 丢精度**）、duration 13.9s、publish_target=true。
6. **PCD 解码自洽（stdlib 往返）**：`build_binary_pcd`（x/y/z/intensity）→`parse_binary_pcd_header` 字段/width 正确 →`read_intensity` 10 值精确还原；无 intensity PCD 解析 OK 且 `read_intensity` 抛 `PcdError`（P2_NO_INTENSITY 口径）。
7. **7 参考图（独立 sha256sum/stat/od，非 references.py 自述）**：7/7 sha256、bytes 与冻结清单逐项一致，JPEG magic `ff d8 ff` 7/7；`verify_references()` 实目录运行 RC=0，total_bytes=15190041、ordered_hash=`de01e67b…39e50`。
8. **1012 只读探针**：`/iv_packets_front_mid` **存在**、`/iv_points_front_mid_transformed` 不存在 → packet 路线适用判定与 B 回执一致；1012 目录零写。
9. **NOT_RUN（环境缺依赖，不 mock 当 PASS，与 B 回执同口径）**：真实 decoder 解码（`packet2pointcloud` ldd 缺 libseyond*/librclcpp/librosbag2/libpcl）、Open3D 渲染（numpy/open3d/PIL 缺失）、付费 VLM 双 pass（端点未配置）——留 12S-C/12S-D 处理机口径。
10. 证据：`scratch/tester_t12sab_p3.log`、`tester_t12sab_p4.log`、`tester_t12sab_p4c_probe` 输出、`tester_t12sab_b_clean_*.log`。

## 四、残留与边界

- 自建资源全毁实测：`tester-t12sab-mysql`/`tester-t12sab-net` 已 rm、临时 base worktree 已 remove、干净 B worktree 已 remove、`docker ps -a` 零 t12sab 命中、**夹具 0 残留**。
- 未碰生产/处理机/NAS 生产路径/业务库；1012 与 refs 目录只读；未跑 OCR、未改任何业务实现、未动他人 worktree。

## 五、观察项（交协调者/B 面定性，**非冻结快照缺陷**）

- **`wt-04a-t12sb` 工作区存在未提交改动（B 面 OCR 返修半成品）**：14:35–14:41 本测试进行中，`adapter.py`/`decode.py`/`references.py` 被就地修改（+78/−27，diff 含 S1 `report.valid_frames`、S2 相对 work_dir 守卫前置、S8 auto 缺 topic 归因——对应 12S-B OCR c01 的 S 系列返修）；其中 `adapter.py` import `resolve_decoder_path` 而 `precheck.py` **未定义** → 脏树 `import app.scene.spray` **断**（脏树定向 21 failed/33 passed，非 commit 缺陷）。
- **冻结 commit `f62a29c` 本身完好**：干净隔离树 54/142/937 全复现、§三探针全过；TESTER 未触碰脏树（只读观察），B 面返修归属与完成度请协调者与 B 核对。
- **门禁影响**：若 B 返修最终提交改变 head，本回执 B 段结论按派单 §一口径**失效，需增量复验**；返修未落 commit 前 B 段证据对 `f62a29c` 有效。
- 12S-A 无此问题（`wt-01-t12sa` 全程零未提交改动）。

## 六、结论

- **12S-A：PASS**（功能/回归/迁移/坡道默认零变化/绑定面全部独立证据覆盖）。
- **12S-B：PASS**（对冻结 commit `f62a29c`；真实解码/渲染/VLM 按口径 NOT_RUN，留 12S-D）。
- 交付 **TEST_REPORT_PENDING**，待协调者裁决；本 PASS 不替代 OCR/强审查/合入门禁。