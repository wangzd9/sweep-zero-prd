# 验收 decision：TASK-10 e2e-reverify-v2（复跑 v2，#3 合入后全链取证）

- 时间：2026-10-12 02:0x +08:00（协调者 cron poll 14ae4556629a，checked_at 2026-10-12T02:00:53+08:00）
- 交付方：TESTER，回执 `test-receipts/TEST-TASK10-e2e-reverify/attempt-2.md`（02:01 交付，总判定 **PASS**）
- 被测快照：main HEAD `453da0c1d88f2a94f5d990ea35a6471cee024a0e` = origin/main（rev-parse 双核一致；#1 `277e40f` + #2 `d4719f6` + #3 `453da0c` 三笔均入 main）

## 协调者独立机械核验（本轮实测）

1. **全链 200 复核**：`scratch/t10/t10-run.log` 01:57:50→01:59:14 独立复读=analyze SUCCESS 83s/1 段、`derive_storage_offset=100381744`（非 None，#2 真链生效）、publish 1 slice、`/results` 200、`/complete-scene` **200** SCENE_DONE run_finalized=True switch switched/current=True（#3 修复点=真包 offset≠0 存储域区间复核通过，v1 的 409 消除）。
2. **manifest actual 边界落位**：`slice_manifest.json` slice 段 `actual_start_ns=1787021470786469238`/`actual_end_ns=1787021479647655120`（存储域，与 v1 核验的已发布 db3 消息 max 一致=偏移 97.191ms≈offset 内，#3 口径正确）。
3. **子包独立可打开**：`rosbag2_0.db3` 只读 sqlite `PRAGMA integrity_check=ok`、messages 6668 行、topics 21 行，与 API `/bags/T10S22c76051fd384d17` 上报（6668 消息/21 topic 清单）及 manifest topics=21 **三方一致**；db3 sha256 `ee66f144…` 与 manifest `db3_sha256` **逐字节匹配**。
4. **原包 ALL_UNCHANGED 独立证伪驱动伪报**：驱动 verdict `5_source_unchanged=SOURCE_MODIFIED` 系 **驱动 after 段 hash 口径 bug**（after 统一 head1MB vs before <60MB 全文件 sha256）——协调者独立用 before 同口径复测 **7/7 文件全部 match**（含 239MB db3 head1MB + 5 mp4 全文件 + metadata.yaml 全文件 sha256 实测 `a2c60bdd…` 一致），且源袋 7 文件 mtime 全部停留 2026-08-19 11:04（只读未变）。TESTER 回执对同源伪报的申报与独立复测**属实**。
5. **lineage 404 申报核实**：`app/` 全目录 grep 无 `/lineage` 路由（`scene_result_query.lineage` 是服务函数未挂 API）——驱动 step5 沿袭 attempt-1 固化步骤，404=**harness 步骤与 app 现状不符，非 AC 失败**；父子血缘已由 `/complete-scene` switch + `/results` derived_children=1 + 子包 manifest（source_id/source_generation）覆盖取证。记入 TASK-11 前置事实（lineage API 若为 REQ-13 面则届时按契约补，**本轮不扩需求不返修**）。
6. **隔离与预算**：无 TESTER docker/worktree 残留（ps 无 t10 进程，驱动进程已退出）；fresh SQLite `scratch/t10/t10-e2e.db` 留存作证据；VLM 累计 v1+v2=2 袋=派单上限内。

## 裁决

- **ACCEPT_TEST_REPORT（PASS）**：AC-1/2/3 全绿独立核验通过，三笔返修（#1 DISCOVERED→READY / #2 storage offset / #3 存储域 actual 边界）端到端协同闭环成立。
- **TASK-10 → DONE**：满足收口条件（两笔前置返修合入 + E2E 复跑 v2 全绿）。
- **强审查 NOT_REQUIRED**：本轮零新 app commit（复跑纯验证单），无新增行为面。
- **P0 收口**：按派单 §四/TODO 口径 **停止派发，不自动转 TASK-11**；TASK-11 生产门禁维持未放行（独立授权）；TASK-07/12/13/14/15 维持 DEFERRED。
- 遗留事实记录（非阻塞）：①驱动 after 段 hash 口径 bug（harness 面，供后续 E2E 复用前修复）；②`/bags/{uid}/lineage` 路由缺失 vs 驱动固化步骤（TASK-11 前置事实）。