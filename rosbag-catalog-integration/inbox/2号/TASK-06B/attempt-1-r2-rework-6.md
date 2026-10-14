---
task: TASK-06B
item: attempt-1-r2-rework-6
owner: 2号
status: PENDING
dispatched_by: 协调者
updated: 2026-10-10 09:03
base: main 6d30a68
round: codex 全链合审 REWORK 回派（1 medium 阻塞 + 2 low，同单 3 项）
裁决: reviews/codex-r6-fullchain-20261010-verdict.md
---
# 2号返修：codex 第三轮 3 项（R-01 秒末截断 / R-02 动态 head 断言 / R-03 零 UPDATE 断言）

codex 对 74ba3bf..6d30a68 全链合审（只读+ORM 实测）= REWORK，协调者已独立复现核实，3 项回你：

## R-01 [medium，阻塞] :582 秒末截断错误（协调者 09:02 边界矩阵复现确认）
`scene_result_report_service.py:582` 先 `start_ns / 1e9` 转**浮点秒**再构造 datetime，纳秒末
接近秒边界时浮点+构造阶段已**进位**，后面的 `microsecond=0` 救不回：
- `ns末=999999999` → 当前码落 22:13:23（正确应 22:13:22 向下截断）
- 行为不对称：纳秒末 ≥~1ms 向上取整、<1ms 保持——同一物理时刻按 ns 偏移落库值不同
- M-1 的"读回值对齐"保护对此**失效**（读回 23 与内存 23 一致，但值本身就是错的秒）
**最小修复**：`started_at = datetime.fromtimestamp(der.start_ns // 1_000_000_000, tz=timezone.utc).replace(tzinfo=None)`
（先整数除法求秒，构造即整秒）。
**回归解除条件**：补 3 个边界用例断言**完整 started_at 值**——ns末=0、ns末=500_000_000（应截断非四舍五入）、
ns末=999_999_999（应进前秒）+ 各自二次 reconcile 重放仍零 UPDATE / 零 StaleDataError。

## R-02 [low] 迁移宽度断言固定当前 head
`test_scene_slice_scheduling.py:1197` 断言 head == 本次 revision——未来加合法后继迁移会在 :1204 误失败。
修：用 `ScriptDirectory` 动态取 heads 断言**单 head** + 单独断言本次 revision 仍在迁移链中 +
全 ID ≤32 字符宽度断言保留。

## R-03 [low] 前轮 low 未补（:963 无零 UPDATE 直接断言）
精度回归用例补强：同秒重放 + 跨秒重放中**监听 UPDATE 语句**（SQLAlchemy 事件计数或 SQL 捕获），
明确断言目标行 UPDATE **零次**（`registered=True` 不能证明 no-op）。

## 验证
R-01 边界用例 + R-03 零 UPDATE 断言真 MySQL 语义（注明连接是否带 CLIENT_FOUND_ROWS——裁决 info 条：
生产默认建连**带**该 flag，同值 UPDATE 返回匹配行数 1，你的 A/B 证据口径保持"无 flag 隔离库"并
在回执写清边界，不得宣称生产默认连接语义）+ SQLite 全量不回归 + ruff 绿。
交单 commit（6d30a68 之上）+ 回执 + 群内通报；OCR 不自跑。

（info 不派单：既有秒精度写入点 scanner:21/pipeline:803/bag_cleanup:495 记 TODO 观察项。）