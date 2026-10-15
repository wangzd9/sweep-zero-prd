# TASK-12S-E attempt-1 OCR 背景（协调者冻结，2026-10-14 23:44 +08:00）

## 任务与版本

- 任务：TASK-12S-E 接收/登记/绑定自动闭环（父 TASK-12S），REQ-20 / AC-20.1 / AC-20.2，细化 REQ-01/02/06/08/14/18。
- 仓库：/home/wang/work/rosbag-catalog；冻结 worktree `/home/wang/.local/state/rosbag-scene/wt-01-t12se`，分支 `a/task-12s-e-auto-bind`。
- base：`16a154fff6f23e20b15498d1285a783713859647`（main，v0.4 三叶 16C 已合入）。
- head：`b39a3ecc76da1f578d32f4e3c88a6ce989cf749d`（交付冻结，2026-10-14 23:33:56 +08:00）。
- 授权来源：`/home/wang/work/doc/prd/rosbag-catalog-integration/inbox/control/V04-UI-RESUME-20261014.md`（用户恢复决定，P0 本地实现授权沿用既有授权；生产/真实样本单独门禁）。

## 变更文件（4，全部在派单独占范围内）

1. `app/services/pending_binding.py`（新增，207 行）：有界后台对账，单次 limit=50、单条独立事务；开关 `PENDING_BINDING_RECONCILE`（默认 1，显式 0 回旧行为）。
2. `app/services/scene_schedule_consumer.py`（+28/-x）：`poll_and_consume_purpose_events` 消费前接入对账；零活动返回体与旧口径逐键一致。
3. `app/services/source_service.py`（+75/-19）：快指纹登记三档身份判定替换旧「id 序第一行无条件重绑」。
4. `tests/test_task12se_auto_bind.py`（新增，607 行）：12 个机械用例。

## 关键契约（必须保持，来自派单）

1. 时序收敛：先提交/先登记/并发/登记后崩溃窗口，PENDING_INPUT 提交在既有 orchestrator 每轮 consume 入口被对账绑定，收敛到「单份用途事件/运行 + 已有结果复用」；对账不查模型负载、不等模型槽。
2. 准确定位：后提交按冻结 intake_snapshot（root_id/scan_root/ready_root/profile_id/profile_version）+ 相对 ready 映射定位原包行；命中行必须落在冻结 ready 根物理相对段下（跨根同包名 → ROOT_MISMATCH 不绑）；非 basename/快指纹匹配。
3. 快指纹仅候选索引：三档判定——精确原包身份重登记放行（生产 1012 批首登恢复被拒的根因修复）；incoming→ready 移动恢复归并既有 UID（12S-C 既有语义保留）；同指纹多原包/多 incoming 行 → 409 AMBIGUOUS_SOURCE；无准确身份且同指纹切片存在 → 保留 TASK-02 409（子包走专用派生登记）。绝不能把子包当原包、覆盖父路径、归并 UID 或移除派生围栏。
4. 幂等身份：对账按本条提交自身冻结身份出事件（不按 bag 短路）；消费端 `scene_identity_key` 持久唯一键复用既有 run——不新建 run、不烧模型、不增 attempt、不新增分析版本；车辆冲突 → 既有 409 fail-closed ERROR:* 隔离；代次漂移 → GENERATION_DRIFT 隔离；资料不齐留痕待补，不制造成功绑定。
5. 有界对账：单条独立事务，故障只回滚本条下轮重试；时限沿用既有扫描/消费节奏。

## 允许行为与范围

- 仅上述 4 文件；未触 `app/api/ingest_submissions.py`（接线复用既有 consume 入口）；不碰场景算法/代理/UI/ros2_slice/models/迁移/部署。
- 无 schema/状态机/算法变化；零生产写入。

## 测试证据（交付自测，协调者已独立复跑 12/154 与 ruff 全绿）

- `tests/test_task12se_auto_bind.py` 12 passed；8 个相关文件合跑 154 passed；全量 1186 passed/10 skipped/4 failed（4 失败 test_devflow×3、test_web×1 为 base 16a154f 既有失败，A 已临时 worktree 复现）；ruff 4 文件 clean。
- 关键断言不只看 HTTP 200：重复 consume 后 run/attempt/事件行数零增长；父子同指纹重登记 200 且归并同一 UID；跨根/车辆冲突/代次漂移均不绑定；开关 0 时返回体与旧口径逐键相等。

## 待核实风险（OCR 关注点）

- 对账与登记三档判定在并发/崩溃窗口下是否真幂等（唯一键依赖 scene_identity_key 持久约束，SQLite 与 MySQL 同构性）。
- source_service 三档判定对 12S-C 既有 incoming→ready 归并语义与 TASK-02 409 是否有回归。
- 零活动路径返回体与旧口径逐键一致的声称。
- TESTER 独立验证面（MySQL 隔离库重放）与本 OCR 并行，tests 文件行为断言以 TESTER 为准，OCR 不替代独立测试。