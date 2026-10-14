---
review_id: codex-r6-fullchain-20261010
item: codex-review-verdict
owner: 协调者裁决
status: DECIDED
updated: 2026-10-10 09:02
result_path: ~/.hermes/cache/scratch/codex-review-r6.log（9156 行，结论段 9050-9110）
---
# codex 全链合审裁决（74ba3bf..6d30a68，REWORK：1 medium 阻塞 + 2 low + info）

codex 第三轮（完整链首次合审，13.1 万 token，只读快照+ORM 实测）。逐条对照 main 6d30a68 核实：

## R-01 [medium] 秒末截断错误 —— **confirmed，协调者独立复现，回派 2号（阻塞项）**
`scene_result_report_service.py:582` `datetime.fromtimestamp(der.start_ns / 1e9, tz=utc).replace(tzinfo=None, microsecond=0)`
——先转**浮点秒**再构造 datetime，纳秒精度在浮点阶段已丢。协调者 09:02 独立边界矩阵复现：
- `ns末=999999999`：当前码 = **22:13:23（进位！）**，整数除法 = 22:13:22（正确向下截断）
- `ns末=0/5e8`：两者一致；`ns末=1`：当前码=23（向上取整），整数除法=23
**危害比 codex 说的还多一层**：当前码行为**不对称**——纳秒末 ≥~1ms 向上取整到下一秒、
<1ms 保持，同一物理时刻按 ns 偏移不同落库值不同；M-1 的"读回值对齐"no-op 保护对
这种跨秒偏移**失效**（读回 23 与内存 23 一致，但值本身就是错的秒）。
**最小修复**：`datetime.fromtimestamp(der.start_ns // 1_000_000_000, tz=utc).replace(tzinfo=None)`
（先整数除法求秒，构造即整秒，无需再 replace microsecond）。

## R-02 [low] 迁移宽度断言固定当前 head —— **confirmed，同单**
`test_scene_slice_scheduling.py:1197` 断言 head == 本次 revision：未来加合法后继迁移会在 :1204 误失败。
修：动态取唯一 head（ScriptDirectory heads）断言单 head + 单独断言本次 revision 仍在链中 +
全 ID ≤32 宽度断言保留。

## R-03 [low] 前轮 low 未补（:963 无零 UPDATE 断言）—— **维持，同单**
补强：同秒+跨秒重放中监听 UPDATE（事件计数或 SQL 捕获），明确断言目标行 UPDATE 零次。

## info（不阻塞，记入强模型增量复审包）
- **连接语义**：codex 实测 SQLAlchemy 2.0.41+PyMySQL 1.1.1 默认建连带 CLIENT_FOUND_ROWS
  （URL 指定 client_flag=0 方言仍补）→ TESTER 无 flag 连接的 rowcount=0 证据只证明修复对
  changed-rows 连接的耐受性，**不能证明生产默认连接会/不会 StaleDataError**。仓库 conftest/
  MySQL factory 未关 flag（codex 核实）→ 全仓 MySQL 测试 rowcount 断言无系统性失真。
  **强模型增量复审须附此边界**，避免误判"生产默认连接下 no-op 修复无效"。
- **既有秒精度写入点**（scanner:21/pipeline:803/bag_cleanup:495）：同类隐患存在于本批之外，
  默认生产连接 FOUND_ROWS 语义兜底，不开新单，记 TODO 观察项。

## codex 通过维度（已独立抽查）
迁移链 17 revision 单 head 最大 30 字符 ✓ / 夹具全调用点 ≤26 无 tag 碰撞 ✓ / 六列 no-op 全覆盖
（ORM 实测六列分别变化均正确写回、同秒重放零 UPDATE）✓ / 4 commit 零越界无新异常吞掉 ✓。

## 回派
2号 attempt-1-r2-rework-6（R-01 修复+秒末边界回归 / R-02 动态 head 断言 / R-03 零 UPDATE 断言，同单 3 项）。
解除条件（R-01）：补秒末（999999999）及下一秒边界用例断言完整 started_at 值 + 重放仍零 UPDATE。
交付后：OCR 增量 → codex 第四轮复审（可选，R-01 一行级修复可直接走 OCR+TESTER 复测）→
强模型增量复审（附两轮 TESTER MySQL 证据+codex 三轮报告+本裁决+连接语义边界）。