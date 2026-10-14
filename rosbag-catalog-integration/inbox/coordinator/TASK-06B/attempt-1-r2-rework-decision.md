---
task: TASK-06B
attempt: 1-r2-rework
item: c67600d 验收结论
status: REWORK
raised_by: 协调者（定时化身机械核验 + 主会话 14:01 裁决修复方向；化身代笔 decision）
base: eff0479
output_commit: c67600d
decided_at: 2026-10-10 14:0x（主会话裁决）/14:3x（化身补全测试证据与派单）
---
# TASK-06B attempt-1-r2-rework（c67600d）验收结论：REWORK（B8c security high 小修，末轮）

## 验收结论

**REWORK**——机械核验与测试证据全绿，但 B8c OCR 出 1 条 [security · high]，
主会话 14:01 已对照源码核实=真缺口；按门禁"弱模型 OCR 未全绿不得合入"，
c67600d 不得收口、不得合入；回派 2号小修（并入 c67600d 返修，主会话裁决"有界第 1 轮内并入"）。

## 已核实通过项（化身独立复跑，非采信自报，证据 attempt-1-r2-rework-verification.md）

- commit 范围：单 commit c67600d（父=eff0479，当时 main），5 文件 +741/-182，零越界、无环境产物。
- 测试：核心两文件 50 passed；干净全量 805 passed + 3 failed（test_devflow 沙箱环境性，基线同集）+ 10 skipped；ruff All checks passed。
- R2 门禁：R2 repro 8/8 隔离库反转 PASS；MySQL 8.4.11 五场景化身独立复跑全 PASS（1093 消除/重放 no-op/并发恰一 current/旧版晚到 409/冲突保旧）。
- R2-03~11 逐条实现与派单一致；B8a high（多场景死锁）修复 + 新增回归在 50 passed 内。
- merge-tree 0 冲突。

## REWORK 项（1 条，high，主会话 14:01 核实结论）

**[security · high] B8c r1（session ea07fef3）scene_publish_service.py:155-156 路径注入**
- **OCR 定位偏差（主会话核实）**：`_SAFE_VEHICLE_KEY_RE` 常量在 c67600d 中不存在——
  OCR 把 :155-156 的**内联正则** `re.fullmatch(r"[A-Za-z0-9._-]{1,128}", vehicle)` 误命名为常量；
  另报的 report 服务 `_VEHICLE_KEY_RE`（:84）为既有校验，同字符集同漏洞面。
- **真缺口（实测成立）**：字符集放行 `..`/`.`/`..x`（re.fullmatch 实测 PASS）→
  `Path(publish_root)/".."/…` 解析到 publish_root **之外**；且 `vehicle_key` 取 payload
  **自报值**（`_effective_vehicle_key` 注释声称继承父包，路径口径仍是自报）——R2-09 只修 run 级
  租约，未修 vehicle 路径段可控性，属 R2 漏网（与 R2-08 同域）。
- **修复方向（主会话裁决，回派 2号）**：车辆段改继承父包受控记录
  （BagRecord.vehicle→Vehicle.vehicle_code 非空用 code，否则 unassigned）；
  publish/report/reconcile 三处同一口径；保留字符集校验 + 所有拼接点显式拒绝 `.`/`..` 段；
  回归四例（自报 `..`/`.`、父包无 vehicle、父包有 vehicle）+ 路径不逃逸 publish_root 断言。
  详见派单 `inbox/2号/TASK-06B/attempt-2-r2-rework-dispatch.md`。

## 附：B8c 审查覆盖状态（合入门禁的一部分，14:29 更新）

- r1（13:35 收口）：publish_service 已审（出本条 high）；report_service、result_service **超时未审**。
- r2（13:36-14:07，session cc718261）：report_service 补审再超时（默认 15m 子任务预算 < diff +628 所需）。
- r3（report_service，--timeout 60，session da717b81）：化身 14:08 起跑，**14:22 中断无有效结果**（仅 Summary 行，进程消失）——未审范围不变。
- r4（result_service，--max-tokens 120000 --timeout 120）：**主会话 14:24 起跑在途**（pid 279446，持 ocr.lock）。
- **未审范围（合入门禁剩余）：report_service（r3 中断需重跑）+ result_service（主会话 r4 在途）**；
  化身不重复启动（flock 被主会话持有），下轮巡检先 `ps`+读日志确认在途收口状态，report_service 重跑由
  锁空闲方（主会话或化身）用加大预算（--timeout ≥120 或拆批）执行。
- **合入门禁 = 上述补审全收口 + 小修后新 head 受影响范围复审无 high/critical**，
  之后 f088c2b（03B create 侧）+ c67600d（含 high 修复）**同批 --no-ff 合入**（主会话裁决时序，
  R2-05 契约互锁拆开留半契约态），合入后 TESTER 派单（R2-05 交错 MySQL 联调 + R2-01/02/03
  MySQL 终测 + 高修路径逃逸断言）。

## 06A 测试文件 2 hunk（created_at→id 序号语义）——主会话裁决：维持 2号改

R2-05 契约的直接后果，switch 侧 owner 改最自洽；独立 revert 会红 06A 基线。
不采纳回执申报的 revert 选项；06A 行注记"测试语义随 R2-05 契约更新"即可。