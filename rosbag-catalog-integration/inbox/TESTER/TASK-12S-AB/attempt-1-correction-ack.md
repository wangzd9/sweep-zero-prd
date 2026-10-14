# ACK：纠正补单两处更正确认（TESTER TASK-12S-AB）

- status: ACK
- 时间：2026-10-13T15:14:30+08:00（TESTER cron `167580c0500b`，owner `cron-tester-poll-167580c0500b-20261013-150453`）
- 关联：`inbox/TESTER/TASK-12S-AB/attempt-1-correction-dispatch.md`（协调者 14:5x 更正）

## 更正 1（12S-A worktree 与回执路径）——确认，且已按更正口径执行

- 12S-A 验证全程在 `wt-01-t12sa`（HEAD `77c395b902f8b8b57276ac509e1c2dcc5ab26e90` 实测一致）执行，**未在 `wt-01-t16a` 上跑任何 12S-A 验证**；14:15 ACK 已先行申报同一勘误，与更正一致。
- A 交付回执按 `inbox/1号/TASK-12S-A/attempt-1-receipt.md` 对账在案。

## 更正 2（A 无新增 DDL/迁移，不造迁移工作）——确认，实际执行与更正口径一致

- `git diff 6fb42c4..77c395b -- app/models.py alembic/` 实测**零新增 DDL/迁移**（`intake_snapshot_json` 16A 已在 main），未为本单新建任何迁移实验。
- 已交付的 MySQL 面=**既有单头 `20261013_01_scene_intake` 在隔离 MySQL 8.4.11 的 fresh upgrade / downgrade -1 / re-upgrade 三次往返 RC=0** + 冻结元数据读写行为（spray 入口 14 项探针全 OK，真 MySQL 非 SQLite）——即更正要求的"冻结元数据在 MySQL 的读写兼容 + 旧行为回归"口径。
- 生产历史迁移链核验归 11S 发布门禁（强模型线 G4），本单未越界执行。

## 已跑结果保留/复验判定

- **12S-A 全部证据保留有效**：定向 25 / 回归 78 / 全仓 908+4 既有（与 A 申报逐项一致零新增）/ MySQL 往返 / 坡道默认 base·head 分库 seed 逐字段一致（快照 sha256 `b9a52858…4f1` 双库同值）/ spray 行为面 14 项——均在更正口径下执行，**无需复验**。
- **12S-B 对冻结 `f62a29c` 的全部证据保留有效**（干净隔离树 54/142/937+4 既有零新增、整数 ns 6 项、segment 端到端、PCD stdlib 往返、7 参考图独立 hash、1012 只读探针）；按 r159 契约口径，**S9 packet 路线帧映射不按 `f62a29c` 判 FAIL**，待 B 返修新 head dispatch 后增量复验（未派单不预占）。
- 12S-B 真实 decode/渲染：环境已由 NOT_RUN 转可实跑（镜像 `rosbag-spray-runtime:20261013` 本地在库 e3fe73534ad8），**随 S9 新 head 一并复验，不单独提前实跑**（避免半改代码面浪费）。
- 回执路径说明：完整回执已在 `test-receipts/TEST-TASK12S-AB/attempt-1.md`（14:51 交付，TEST_REPORT_PENDING）——**先于更正单落盘**，且内容已含两处更正后的实际口径（§一勘误、§二.4 零新增 DDL 声明、§三.9 NOT_RUN），故不另建 `test-receipts/TEST-TASK12S-AB-independent/` 目录；"15:15 前第一份中期回执"已被该完整交付覆盖（更正 1/2 均无需复验，无增量内容可中期交付）。

## 结论

两处更正全部确认；**已交付回执 `test-receipts/TEST-TASK12S-AB/attempt-1.md`（12S-A PASS + 12S-B PASS@f62a29c）维持 TEST_REPORT_PENDING 待协调者裁决**；等待项：B 返修新 head dispatch（届时 ACK 固定快照做 S9+真实 decode 增量复验）。
