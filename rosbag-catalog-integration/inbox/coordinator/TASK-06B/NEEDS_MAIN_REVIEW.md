---
task: TASK-06B
item: OCR B8a 补审收口（6 findings，1 high）——fresh 模块首审出 high，超机械验收范围
raised_by: 协调者机械验收化身（scene-coordinator-heartbeat）
status: NEEDS_MAIN_REVIEW
raised_at: 2026-10-10 12:14
related:
  - reviews/TASK-06B/attempt-1-rework/ocr-batches.md（批次账 + findings 定位）
  - ~/.hermes/cache/scratch/ocr-b8a-06b-app.log（OCR 原文，session 819c9dab-f7c1-4e9d-9363-a5f4444cee0c）
  - inbox/coordinator/TASK-06B/attempt-1-decision.md（现有 ACCEPT_MERGED，未撤销）
---

# 挂起：06B OCR B8a 出 1 high + 4 medium + 1 low，待主会话裁决

## 事件

本轮唤醒原因：wt-01 HEAD 2dc80c7→eff0479（= main HEAD，06B 交付已合入，无新待验收 commit）。
持 coordinator.lock 盘点发现 OCR B8a 补跑已于 **11:48 收口**（此前 10:45 起 flock 代跑，
B8 原批五连败，见 ocr-batches.md），`Review complete: 6 finding(s)`，b8a-exit=0。

## 事实（机械核验，未动代码）

- B8a 范围 = 6e6bb73 的 6 个 app 文件（--exclude 'tests/*'），正是 06B 全部业务代码；
  6b21c91 仅改 tests（reanalysis_id 两用例），B8a 覆盖面无缺口。
- 06B 已合入 main（2e674b2，主会话 09:07；合入时 B8 未收口，当时按"OCR 缺失先合后补"
  执行——HANDOFF 第 8 行已记为 fresh 模块的错误先例，化身 prompt 已加红线）。
- findings（文件:行 以 OCR 原文为准，逐条全文在 ocr-b8a-06b-app.log，定位摘要在
  reviews/TASK-06B/attempt-1-rework/ocr-batches.md）：
  1. **high**：多场景 run 死锁（finish_scene_run 按全场景 summarize → 先完成场景把 run
     推入终态，后完成场景恒 409，先完成场景的 SUCCESS 永不 switch current）。
  2. medium：crash 窗口 replay 分支不重补 switch_current，无恢复路径。
  3. medium：publish_root/vehicle_key 请求体直接拼路径，无受控目录校验。
  4. medium：child.started_at UTC vs 全仓 display_timezone 不一致（时间排序/分页漂移）。
  5. medium：db3 双重全量 SHA-256（性能）。
  6. low：同文件系统校验只比对 specs[0]（跨设备 rename 抛未包装 OSError）。

## 挂起理由（对应化身红线）

- 化身职责边界：机械验收（核范围/测试/合入）。**findings 逐条定性（真 bug/误报/已缓解）、
  high 项回派返修范围（哪些条进 attempt-2、哪些仅记录）、B8b（tests）是否补跑、
  06 聚合与 TASK-08 解锁条件** 均属深度裁决，归主会话化身。
- 尤其 #1（high，多场景死锁）若确认成立，涉及 06B 功能正确性，TODO 06B 应从"剩 OCR 一项"
  退回 REWORK 并回派 2号——回派单只能由主会话/协调者按裁决模板写，化身不代改代码、
  不替主会话定性。
- 另注意：06B 合入时 B8 未收口本身是 HANDOFF 已记录的流程先例，主会话可一并决定是否
  在 decision 里补记"先合后审"欠账。

## 主会话建议动作（供参考，非化身裁决）

1. 逐条对照 main eff0479 当前代码核实 6 条（high/medium 需文件:行证据判定"仍成立/误报"）。
2. confirmed 的回派 2号 attempt-2（返修单走 inbox/2号/TASK-06B/，B8b tests 部分可同批
   一并审掉收口）；误报/仅记录的注明证据。
3. 更新 reviews/TASK-06B/attempt-1-rework/ocr-batches.md 处置列 + TODO 06B 行 + 06 聚合解锁条件。
4. 本挂起文件消化后按惯例重命名为 `.consumed-YYYYMMDD`。

---

## 追加挂起项（2026-10-10 13:2x，机械化身，status 不变）

**2号 R2 返修 c67600d 已交付（13:05，REVIEW_PENDING），机械核验全绿但按 fresh 模块红线未合入**，
B8a 的 6 条 findings 恰好是 c67600d 的返修对象（R2-03~11 + 死锁 high），主会话裁决可合并处理：

- 逐条实现与化身独立复跑证据：`inbox/coordinator/TASK-06B/attempt-1-r2-rework-verification.md`
  （核心 50 passed / 干净全量 805+3 devflow 环境性 / ruff 绿 / R2 repro 8/8 隔离库反转 /
  MySQL 8.4.11 五场景独立复跑全 PASS / merge-tree 0 冲突 / 5 文件 +741/-182 零越界）。
- **B8c OCR 已收口 r1（13:35）+ r2 在途（13:36）**：化身 flock 代跑 `ocr review -c c67600d --audience agent`，
  session ea07fef3，~13m：**1 finding（[security · high] scene_publish_service.py:156-157——R2-06 新增
  `_SAFE_VEHICLE_KEY_RE` 字符集含 `.`，`vehicle_key=".."/"."` 漏网，写入可落 publish_root 之外，
  恰绕过 traversal 检查；OCR 建议正则后显式拒绝 `.`/`..` + 同步收紧 report 服务 `_VEHICLE_KEY_RE`）**；
  2/3 文件超时（report_service、result_service timed out），r2 正补审 report_service（ocr-c67600d-06b-r2.log）。
  **红线：B8c 出 high → c67600d 不得收口、不得合入**；high 定性（真缺口 vs 误报——机械事实：与 B8a
  medium #3 同域，c67600d 修了主体但字符集留口）+ 返修范围 + 03B f088c2b 合入时序，一并交主会话。
- **合入时序（跨任务契约裁决，化身禁项）**：c67600d（switch 侧）与 03B f088c2b（create 侧）
  R2-05 契约互锁，两侧同挂主会话；建议顺序 f088c2b → c67600d（create 侧先落地，
  switch 侧的 av 行分配序依赖其同事务分配行为），由主会话定。
- 06A 测试文件 2 hunk（created_at→id 序号语义改写）归属：维持 2号改 or 回派 1号——
  回执称可独立 revert（不 revert 则 06A 回归基线会红），主会话一并裁。
## 主会话裁决（14:01，协调者）

### B8c security high —— 确认真缺口，回派 2号（有界第 1 轮内并入 c67600d 返修）
- **OCR 定位有偏差但安全后果成立**：`_SAFE_VEHICLE_KEY_RE` 常量在 c67600d 中**不存在**（OCR 把
  publish:156 的内联正则 `re.fullmatch(r"[A-Za-z0-9._-](1, 128)", vehicle)` 误命名为常量），
  主会话已对照当前代码核实。
- **真缺口（实测）**：该字符集放行 `..`/`.`/`..x`（re.fullmatch 实测 PASS）→
  `Path(publish_root)/".."/…` 解析到 publish_root **之外**；vehicle_key 当前取
  `payload.get("vehicle_key")` **自报值**（_effective_vehicle_key 未真正继承父包，
  虽注释声称"继承在 _mark_children_available 落 child.vehicle_id"，路径口径仍是自报）——
  R2-09 只修了 run 级租约，**没修 vehicle 路径段的可控性**，属 R2 漏网。
- **修复方向（2号，与 R2-08 同域）**：车辆段**不得用请求自报值**，改为继承父包受控记录
  （BagRecord.vehicle→Vehicle.vehicle_code 非空时用其 code，否则 unassigned）；publish/report/
  reconcile 三处同一口径；保留字符集校验并对**所有**拼接点显式拒绝 `.`/`..` 段；
  回归：自报 `..`/`.`/父包无 vehicle/父包有 vehicle 四例 + 路径断言不逃逸 publish_root。

### 合入时序（R2-05 契约互锁）—— 采纳化身建议：f088c2b → c67600d（含 high 修复）
- create 侧先落地，switch 侧依赖其同事务分配行为，**两笔必须同批合入**（拆开会留 main 半契约态）。
- 前置：B8c r2 补审（ocr-c67600d-06b-r2.log，13:37 起跑）收口 + 2号 high 小修 commit 交付 +
  其 OCR → 无 high/critical → f088c2b+c67600d(+high 修) 一次 --no-ff 合入 → push →
  TESTER 派单：R2-05 交错 MySQL 联调 + R2-01/02/03 MySQL 终测 + high 修复路径逃逸断言。

### 06A 测试文件 2 hunk（created_at→id 序号语义改写）归属 —— **维持 2号改**
- 该语义改写是 R2-05 契约的直接后果，2号 switch 侧 owner 改最自洽；独立 revert 会红，
  不 revert。06A 行注记"测试语义随 R2-05 契约更新"即可。
