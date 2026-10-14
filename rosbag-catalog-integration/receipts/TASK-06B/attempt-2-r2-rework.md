---
task: TASK-06B
attempt: 2-r2-rework
item: B8c security high 小修（车辆段路径注入）
owner: 2号（执行者 B）
status: REVIEW_PENDING
base: main eff0479 / 分支 scene/task-06b-r2-rework（增量自 c67600d）
output_commit: a07c181
worktree: /home/wang/.local/state/rosbag-scene/wt-04a
received: 2026-10-10 14:01（派单 attempt-1-r2-rework.md B8c 高回派段，主会话裁决时间）
delivered: 2026-10-10 15:02（git commit 时间）
---

# TASK-06B attempt-2-r2-rework 回执（B8c security high 小修）

## 交付行为

主会话 14:01 裁决方向落地：车辆段路径段改**受控口径**（继承父包
`BagRecord.vehicle → Vehicle.vehicle_code`，非空用其 code 否则 `unassigned`），
请求自报 `vehicle_key`（含 `..`/`.`）不再进入路径；publish / complete-scene /
reconcile-scene 三处同一口径；保留字符集校验并在所有拼接点**显式拒绝 `.`/`..` 段**
兜底（防受控值本身异常）。

## 根因

B8c OCR r1（session ea07fef3）1 [security · high]：`_effective_vehicle_key` 取
payload 自报值，旧字符集 `[A-Za-z0-9._-]` 放行 `..`/`.`，`Path(publish_root)/".."/…`
解析到发布根之外。R2-09 只修 run 级租约，未覆盖 vehicle 路径段可控性（与 R2-08 同域漏网）。

## 文件清单（3 文件，≤3 约束内，零越界）

- `app/services/scene_publish_service.py`（+26/-2）：新增 `SAFE_PATH_SEGMENT_RE` +
  `safe_path_segment()`（拒绝空段/.//../非法字符）；`publish_scene_slices` 车辆段与
  `scene_code` 段共用本校验（原内联正则替换）。
- `app/services/scene_result_report_service.py`（+41/-26）：`_safe_vehicle_key` 与
  `_effective_vehicle_key` 改从父包受控记录取车辆 code（不再读 payload 自报值）；
  兜底 fail-closed（受控值异常 → 409）；移除本文件重复 `_VEHICLE_KEY_RE`（校验统一到发布层）。
- `tests/test_scene_result_report.py`（+170/-2）：`_stage_and_publish` 改用服务同受控口径
  取车辆段落盘（与回报/对账读取路径天然一致，旧测试恒 vehicle_key="" 无回归）；
  `_purge` 补父包关联 Vehicle 记录清理；新增 B8c 4 例回归 + 路径不逃逸断言。

未执行项：无（自测/全量/ruff 全做）。

## 验证（真实退出码，环境 worktree a07c181，SQLite 隔离库）

- 定向 scene 4 文件：`pytest tests/test_scene_result_report.py test_scene_result_storage.py
  test_scene_slice_scheduling.py test_scene_slice_lineage.py` → **100 passed**（含 B8c 4 新增）。
- B8c 4 例单跑：`pytest -k b8c` → **4 passed**
  （自报 `..`/`.` 不逃逸落 unassigned；父包无 vehicle→unassigned；父包有 vehicle→
  继承 `CAR-B8C` 且自报 `..` 不覆盖；各例断言
  `target.resolve().is_relative_to(publish_root)`）。
- 全量 SQLite：`pytest tests/` → **810 passed / 3 failed / 7 errors / 10 skipped**
  - 3 failed = `test_devflow.py` 沙箱环境性（主仓库 .git 结构/`/usr/bin/bwrap`，与 main
    基线同集，非本次变更）；
  - 7 errors = `test_r2_repro.py` 需 `/tmp/r2-review-*` 隔离库（其 client fixture 硬门禁，
    由协调者/测试者按隔离库入口另跑，本单不代跑）。
- ruff：`ruff check` 3 文件 → **All checks passed**。
- 提交范围：`git diff --cached --stat` = 3 文件 +235/-28；`.venv`、`tests/test_r2_repro.py`
  均未纳入（worktree 原有未跟踪文件，未动）。

## 越界申报

无。3 文件全在派单允许范围（publish/report 服务 + 本任务测试）。

## 下一步

等协调者：对新 head a07c181 受影响范围（scene_publish/report_service 差异）做 B8c 复审
无 high/critical → 按主会话裁决时序与 f088c2b（03B create 侧）+ c67600d（含本 high 修复）
同批 --no-ff 合入 → 合入后 TESTER 派单（高修路径逃逸断言 + R2-05 交错 MySQL 联调 +
R2-01/02/03 MySQL 终测）。OCR/强模型复审不自跑。