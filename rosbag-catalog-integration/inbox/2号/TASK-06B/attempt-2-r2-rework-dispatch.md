---
task: TASK-06B
item: attempt-2-r2-rework
owner: 2号
status: ACCEPTED
dispatched_by: 协调者（主会话 14:01 裁决；定时化身本轮代笔派单，v2 协议）
updated: 2026-10-10 14:3x
base: main eff0479（在你当前分支 scene/task-06b-r2-rework 上增量，新 head）
round: B8c security high 小修（并入 c67600d 返修，主会话裁决"有界第 1 轮内并入"）
---
# 2号返修：B8c security high——车辆段路径注入（主会话 14:01 裁决方向，小修）

> 本派单修复要求**以主会话 14:01 裁决为准**（NEEDS_MAIN_REVIEW.md「主会话裁决」节）；
> 化身 14:3x 初稿的"点号分量黑名单"口径已被主会话裁决的更严方向**覆盖**，作废。

## 背景

c67600d（attempt-1-r2-rework）机械核验与测试全绿（核心 50/干净全量 805+3 环境性/ruff 绿/
R2 repro 8/8/MySQL 8.4.11 五场景协调者复跑全 PASS/merge-tree 0 冲突），但协调者串行 B8c
OCR（r1 session ea07fef3，13:35 收口）出 1 条 [security · high]，主会话已对照源码核实=真缺口。
decision 见 `inbox/coordinator/TASK-06B/attempt-1-r2-rework-decision.md`。

## 缺陷（主会话 14:01 核实结论）

- OCR 定位有偏差但后果成立：`_SAFE_VEHICLE_KEY_RE` 常量在 c67600d 中不存在（OCR 把
  `scene_publish_service.py:155-156` 的**内联正则** `re.fullmatch(r"[A-Za-z0-9._-]{1,128}", vehicle)`
  误命名为常量）；该字符集放行 `..`/`.`/`..x`。
- **真缺口**：`vehicle_key` 当前取 `payload.get("vehicle_key")` **自报值**（`_effective_vehicle_key`
  注释声称继承父包，但路径口径仍是自报）；`Path(publish_root)/".."/…` 解析到 publish_root 之外。
  R2-09 只修了 run 级租约，没修 vehicle 路径段可控性，属 R2 漏网（与 R2-08 同域）。

## 修复要求（主会话裁决方向，≤3 文件 + 回归，不改其他 R2 已修项）

1. **车辆段不得用请求自报值**：改为继承父包受控记录——`BagRecord.vehicle → Vehicle.vehicle_code`
   非空时用其 code，否则 `unassigned`。
2. **publish / report / reconcile 三处同一口径**（`_effective_vehicle_key` 真正继承 +
   `publish_scene_slices` 的 vehicle 段来源改为受控值，不再信 payload 自报）。
3. 保留字符集校验，并对**所有拼接点**显式拒绝 `.`/`..` 段（兜底，防受控值本身异常）。
4. 回归（四例 + 路径断言）：
   - 自报 `vehicle_key=".."` → 不生效、不逃逸（继承父包值或 unassigned）；
   - 自报 `vehicle_key="."` → 同上；
   - 父包无 vehicle → 车辆段 = `unassigned`，路径正确；
   - 父包有 vehicle → 车辆段 = `Vehicle.vehicle_code`，路径正确；
   - 各例断言最终路径**不逃逸 publish_root**（`target.resolve().is_relative_to(publish_root)`）。

## 门禁与交付

- worktree：/home/wang/.local/state/rosbag-scene/wt-04a（现有分支上增量 commit，不进 .venv/本地 repro 文件）。
- 自测：定向（scene_publish + scene_result_report 相关用例）+ 全量 SQLite + ruff，真实退出码写入回执。
- 交付：新 commit + `receipts/TASK-06B/attempt-2-r2-rework.md`（status REVIEW_PENDING）+ 群内一行通报。
- OCR/强模型复审**不自跑**（协调者串行；小修范围小时只对新 head 差异复审）。
- 合入时序（主会话裁决）：f088c2b（03B create 侧）→ c67600d（含本 high 修复）**同批 --no-ff 合入**，
  前置 = B8c 全文件补审收口（r3 report 在途/r4 result 排队）+ 本修复 commit 的 OCR 无 high/critical；
  合入后 TESTER 派单（R2-05 交错 MySQL 联调 + R2-01/02/03 MySQL 终测 + 高修路径逃逸断言）。
- 06A 测试 2 hunk：维持 2号改（R2-05 契约直接后果，不 revert）。

## 领取

只改 status 行为 ACCEPTED，正文不改；开工后在自己 worktree 增量提交。