# TESTER 回执：TASK-10 / e2e-reverify / attempt-2（复跑 v2，#3 合入后全链取证）

- 总判定：PASS（AC 全绿；TASK-10 满足收口条件，待协调者判 DONE）
- 时间：2026-10-12 02:01 +08:00
- 被测快照：main HEAD `453da0c1d88f2a94f5d990ea35a6471cee024a0e` = origin/main fetch 双核一致（#1 `277e40f` + #2 `d4719f6` + #3 `453da0c` 三笔返修均入 main）
- 驱动：`scratch/t10_e2e_reverify.py`（协调者 01:51 固化，step4 已补 `SlicePublishSpec(actual_start_ns/actual_end_ns)`，:336-342 独立核）；执行面=主仓 `453da0c` 代码起独立 app 实例（fresh SQLite + create_all + TestClient 正式 API）+ 真实 VLM `192.168.2.45:8002/v1/chat/completions`（非旧镜像冒充）
- 运行：`scratch/t10-driver-v2.out` RC=0；日志 `scratch/t10/t10-run.log`；证据 `scratch/t10/t10-e2e.json`
- VLM 袋数：v2 单袋（row19），累计 v1+v2=2 袋，未超派单上限

## 逐项 AC

### AC-1 全链登记→切片→发布→/results→/complete-scene 200 可置 AVAILABLE — PASS
- 1a submission 冻结 `config_hash=0845b402…` OK
- 1b register `source_id=3723682575DE4F949438A1B87E` matched=True
- 1d run `scene-8f45c0ae421e432f8935d2e8119f` 冻结同 hash
- 3_analyze 真实 VLM **SUCCESS**（01:57:50→01:59:13，约 83s，1 段可发布）
- 4_offset `derive_storage_offset = 100381744`（**非 None**，≈100.38ms，#2 修复真链生效）
- 4_publish 1 切片原子发布成功
- 4_report `/results` **200**（availability=PENDING，registered_segments=1，derived_children=1）
- 4_complete `/complete-scene` **200**：outcome=SUCCESS / run_status=SCENE_DONE / run_finalized=True / **switch={switched:True, current:True}（#3 修复点：真包 offset≠0 存储域区间复核通过，不再 409，可置 AVAILABLE）**
- manifest `slice_manifest.json` 落 actual 边界：`actual_start_ns=1787021470786469238` / `actual_end_ns=1787021479647655120`（字符串口径，#3 落位确认）

### AC-2 step5 正式 API 获取：非空可打开 + 原包独立复核 ALL_UNCHANGED — PASS
- `GET /bags/T10S22c76051fd384d17` **200**：status=READY，message_count=6668，total_size=141910016B，files 含 rosbag2_0.db3
- 子包 rosbag2_0.db3 独立可打开：sqlite `PRAGMA integrity_check=ok`，messages 表 6668 行、20 topics，与 API 上报一致
- 原包 ALL_UNCHANGED：驱动 before 口径（<60MB 全文件 sha256、≥60MB head1MB）**独立复测 7/7 文件全部 match**（含 239MB .db3 head1MB + 5 个 mp4 全文件 + metadata.yaml）→ **ALL_UNCHANGED=True**
- 说明：驱动 `5_source_unchanged=SOURCE_MODIFIED` 为**驱动自身 after 段口径不一致伪报**（after 段统一 head1MB，对 <60MB 文件与 before 全文件口径不同），非真实变更；TESTER 用 before 同口径独立复测已证伪，源袋真实只读未变（mtime 全部停留 2026-08-19 11:04）
- 未执行项：`GET /bags/{child}/lineage` 404——app 无该路由（`app/api/` 全目录 grep 无 lineage 路由），驱动沿袭 attempt-1 固化步骤；父子血缘改由 `/complete-scene` body（switched/current）+ `/results` derived_children=1 + 子包 manifest 覆盖取证，不影响 AC 成立，**如实申报非阻塞**

### AC-3 offset 非 None + 全链 SUCCESS + 原包 ALL_UNCHANGED → PASS
- 三项齐备：offset=100381744 / 3_analyze SUCCESS + 4_complete SUCCESS / ALL_UNCHANGED=True（独立复测）
- 零业务代码改动（TESTER 只跑驱动+只读取证+独立 sqlite/hash 复核）

## 隔离资源
- fresh SQLite：`scratch/t10/t10-e2e.db`（驱动内建，收口后留存作证据）
- v1 attempt-1 证据已归档 `scratch/t10/v1-attempt-1/`（db/json/log/out/work/publish）
- 无 TESTER docker 容器/worktree 创建（独立 app 进程实例已退出），0 残留

## 交付
- 派单 status→TEST_REPORT_PENDING（本回执出具时改回，见下）
- 结论：三笔返修（#1 DISCOVERED→READY / #2 storage offset / #3 存储域 actual 边界）协同闭环，端到端正式链全绿，**满足 TASK-10 DONE 收口条件**，交协调者裁决（DONE→P0 收口，不自动转 TASK-11）