# 派单：TASK-03B / attempt-5-r2-final-s1（R2-01 迁移链 1406 最小修复）

- status: PENDING（先独立 ACK 后执行，ACK 同目录 -ack.md，只改 status）
- 下达：协调者 2026-10-10 18:24
- 依据：TESTER 终测报告 `test-receipts/TEST-TASK06-r2-final-mysql-e2e/attempt-1.md` §S1 FAIL（缺陷1，高）——S1 R2-01 为 06 聚合放行业务门禁，唯一 FAIL 场景。

## 基线

- base：**main 74ba3bf**（你的 wt-01 仍在 c285e2e，开工前 pull/merge 到 main 74ba3bf）
- worktree：`/home/wang/.local/state/rosbag-scene/wt-01`

## 问题与根因（测试者实测，非推测）

- `alembic_version.version_num` 由 alembic 默认建为 **VARCHAR(32)**；当前 head revision ID `20261009_02_ingest_frozen_columns` 长度 **33** → 任何 MySQL 库（全新/已有/本地栈/生产）从 `20261009_01` upgrade 到 head **必然 1406 Data too long 中断**（卡死在写 `20261009_02` 版本行）。
- 最小复现：`~/.hermes/cache/scratch/tester_r2_r1_repro.py`（干净 MySQL 8.4.11，全新库 upgrade head RC=1；已有库增量路径同因）。
- 注：R2-01 原目标（去 4 个 TEXT 列 server_default 防 1101）**本身成立**（测试者 SHOW CREATE 双库核实 4 列均 `text NOT NULL` 无 DEFAULT），败在链尾 revision ID 越宽，不要回退/修改已有迁移。

## 修复范围（最小，单一 commit）

1. **新增**一个 alembic 迁移（down_revision = `20261009_02_ingest_frozen_columns`，revision ID 自定义但**长度 ≤32 字符**，避免自己再踩同一坑）：upgrade 首段幂等加宽 `alembic_version.version_num` → `VARCHAR(255) NOT NULL`（先 inspect 当前列宽，已 ≥255 则跳过）；downgrade 留 no-op + 文档说明（不缩回，缩回会重新卡 33 字符 ID）。
2. **禁止**：改 revision ID `20261009_02_ingest_frozen_columns`（已有库兼容差）；改 20261009_02 或其他既有迁移内容；改 app 代码（本缺陷纯迁移链问题）。
3. 加一条定向迁移测试（隔离 SQLite 跑 alembic 链不回归即可；MySQL 证据由测试者复测补）。

## 验收（AC）

- AC1：干净 MySQL 8.4 `alembic upgrade head` RC=0、`alembic current` = 新 revision（测试者 S1 新 attempt 复测）。
- AC2：已有库增量路径：先 `upgrade 20261009_01` 再 `upgrade head`，无 1406 走到底（同上复测）。
- AC3：幂等：库中 `version_num` 已为 VARCHAR(255)（运维临时加宽过）时新迁移 upgrade 不报错。
- AC4：本侧自测：迁移链相关既有测试 + 定向新测 PASS；全量 SQLite 不回归；ruff 绿。
- AC5：新 revision ID 长度 ≤32（commit 说明里给出长度核对）。

## 停止条件与交付

- 单 commit 交付 + 回执 `receipts/TASK-03B/attempt-5-r2-final-s1.md`（REVIEW_PENDING，含 diff/命令/RC/AC 对照）；**不跑 OCR、不合入 main**，OCR 与合入由协调者串行。
- 交付后 TESTER 将以新 attempt 复测 S1（含 AC3 幂等场景）；S1 转 PASS 后 06 聚合门禁才解除。