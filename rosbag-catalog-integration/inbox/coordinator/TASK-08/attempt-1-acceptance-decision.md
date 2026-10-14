# 验收 decision：TASK-08 attempt-1（2号联调报告）

- 状态：**ACCEPT_REPORT + 回派 C1/C2/C3**（TASK-08 本体维持 RUNNING，待 C1C2 t08c-1 与 C3 c3-1 收口后再核 08 DONE 口径）
- 记录时间：2026-10-11 16:46 +08:00（协调者 cron poll 14ae4556629a，checked_at 2026-10-11T16:40:53+08:00，回合 16:46:33 claim）
- 交付物：`receipts/TASK-08/attempt-1.md` + `reports/TASK-08/attempt-1.md`（16:32:51 落盘，REVIEW_PENDING）

## 协调者独立机械核验（非采信自报）

- 交付边界：**业务代码 0 改动**——`wt-04a-t08` HEAD=`62a85bf`=派单固定 base，`git status` 仅未跟踪 `.venv` 软链（`/home/wang/work/rosbag-catalog/.venv`）；符合派单"不改业务代码，失败记录回派"口径。
- main/origin 双核一致 `f9bafb0`（16:45 rev-parse 复核），交付 base 为 `62a85bf`（ACK 时 origin/main，派单口径允许；I-1 合入 `f9bafb0` 在 ACK 后 14 分钟，按 ACK 口径由 I-1 回归验证项动态核对，2号已执行）。
- **55 PASS/10 FAIL 文件级汇总核实**：`scratch/t08-e2e/fkoff/allfiles_summary.txt`（16:26:37，与交付同批）逐行计数 PASS=55/FAIL=10/SKIP=3，红文件清单与报告 §B 表逐文件一致（含用例数 3/1/4/1/2/1/2/1/10errors/3 全吻合）。
- **场景核心文件真 MySQL 独立复核**（`allfiles/af_60` 35 passed / `af_61` 25 passed / `af_63` 3 failed+33 passed）——报告 §A"35/35、25/25"成立；16:01 的 `fkoff_0/fkoff_2` 单文件日志（errors）属早期 FK-on 口径，交付口径为 16:26 allfiles 独立新库批，协调者以 allfiles 批为准核验（报告证据节所指即此批）。
- **I-1 回归验证项独立复核**：`fkoff/i1_scheduling.log`（`6823f2d` @ wt-01-i1 真 MySQL）**36 passed RC=0**——I-1 合入 `f9bafb0` 后该文件红消失，回归项按 ACK 口径完成。
- **根因证据独立抽查**：
  - C2：`isol2_2_test_bag_cleanup_worker.py.log` 实测 `StaleDataError: UPDATE statement on table 'bag_cleanup_operation' expected to update 1 row(s); 0 were matched.`（5/6 红文件均命中该异常）；app 帧定位 `bag_cleanup_service.py:618/:624/:935`、`source_service.py:205` 与日志 traceback 一致。
  - C1：`isol2_8_test_lineage_lifecycle.py.log` 实测 `assert '2026-10-11T16:15:53.438020' == '2026-10-11T16:15:53'`（`test_lineage_lifecycle.py:51`，微秒 vs 整秒读回）；`isol2_6_test_web.py.log` 实测 `test_bag_time_filter_supports_second_precision` 秒边界过滤误含（bag 时间 10:42:44 落 02:42:46 起查——DATETIME(0) 截断边界语义偏移）。
  - C3：`isol2_7_test_scene_slice_lineage.py.log` 实测 `(1406, "Data too long for column 'bag_uid'")` setup 10 errors；`tests/test_scene_slice_lineage.py:74-75` 源码核对 `BAG_PREFIX + hex[...]+"PARENT"/"CHILD"` = 27 字符越 VARCHAR(26)，I-1 派单范围（仅 scheduling 文件 T05 族）不含此文件，属**新同型**定性成立。
  - SQLite 对照：`sqlite_*.log` 同批文件全绿（11/3/36 passed 等），"SQLite 遮坑"定性成立。
- **证据缺口（记录，不阻断本 decision）**：① `scratch/t08-e2e/migrate-up.log`/`migrate-down1.log`/`migrate-up2.log` 三文件 0 字节（15:37-15:38 早期批，stdout 重定向缓冲未 flush——OCR 长批教训同型），迁移 RC=0 主张以 16:26 allfiles 批中 `test_migration_lineage_rollback.py`/`test_china_standard_time_migration.py` PASS + heads 单头 `20261009_02_ingest_frozen`（`heads.log` 33B 在案）+ 06 聚合 S1 三路径强复审 V-3 已验为间接支撑，**C1C2 t08c-1 验收时须以 allfiles 口径重核迁移链**（2号复现脚本在案可复跑）；② 05 消费链空跑探针输出目录未见独立落盘文件（报告 §A 主张全零无副作用），间接支撑=TESTER attempt-1 outbox e2e PASS 6/6（证据不失效，2号报告引用同口径）——t08c-1 交付时若涉 pipeline 时间列改动，协调者将抽跑消费链空跑复证。
- 隔离库清理：2号自报 t08* 全 drop + t08 用户 drop（after=[] user=0）；协调者 `docker ps` 复核本地栈仅 8 既有容器 healthy，无 t08/r2i6 残留容器。

## 裁决与回派

1. **C3-lineage → 1号 `c3-1`**（已落 `inbox/1号/TASK-05/c3-lineage-fixture-uid-dispatch.md`，base `f9bafb0`，最小夹具单：lineage:74-75 uid ≤26 + assert，零 app 变更，真 MySQL 文件级全绿为停止条件）。纯测试交付，预期 OCR 0 入选（R8/R9/i1-1 先例），验收=机械核验+真 MySQL 日志独立复跑。
2. **C1+C2 → 2号 `t08c-1`**（已落 `inbox/2号/TASK-08/c1c2-second-precision-dispatch.md`，base `f9bafb0`，秒精度时间戳专项：同根因家族合并单，app 修复点逐处定性+真 MySQL A/B 证据，9 红文件文件级全绿+06B 回归项 35/25 不破坏为停止条件）。**app 行为面**，交付走 机械核验 → 串行 OCR 增量（C1C2 涉 app 文件，OCR 实际入选）→ 合入；同根因（缺陷3家族）第二轮性质，若再失败即按"同根因两轮返修"升级。
3. 两单**并行**（A/B 两开发槽，文件集无冲突：c3-1 仅 `test_scene_slice_lineage.py`，t08c-1 不碰该文件；均 base `f9bafb0`）。C 槽保持空闲待命。
4. **TASK-08 本体口径**：attempt-1 联调执行已按派单完成（全链路 PASS+I-1 回归项完成+失败发现记录回派，边界零越界），联调面收口条件=C1C2 t08c-1 合入 + C3 c3-1 合入 + 协调者核 t08c-1 交付中 9 红文件全绿证据（含迁移链重核）后 08 转 DONE；届时 TASK-10 候选重算（TASK-09 仍 BLOCKED 等真实样本授权，生产门禁不变）。
5. 强审查：本批为 TASK-08 联调回派修复（C1C2 涉 app 行为），按 strong-review 口径**C1C2 t08c-1 合入后评估**是否并入既有强复审包（R2I-20261010-06 已 PASS 收口不重开；新包仅当 C1C2 定性为"app 行为修复且涉并发/迁移面"时准备，交用户手动触发）——当前记 NOT_REQUIRED，随 t08c-1 交付事实再评。

- 门禁不变：生产启用/真实样本（TASK-09/10/11）维持未放行。
