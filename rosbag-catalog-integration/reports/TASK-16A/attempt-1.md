# 报告：TASK-16A attempt-1 场景接收隔离（开发证据）

- owner: A（执行者A·数据处理链路）
- 时间: 2026-10-13 01:18 +08:00
- 交付: `c2018dd → 79f6889 → c30f048`（分支 `a/task-16a-scene-intake`，worktree `wt-01-t16a`）
- 回执: `receipts/TASK-16A/attempt-1.md`（REVIEW_PENDING）

## 一、迁移往返证据（真 MySQL 8.4 隔离库，T03/T04 口径）

方法：独立 docker network 起 `mysql:8.4` 容器（编程式凭据，不落盘），backend 本地镜像 + worktree bind mount 在同 network 跑 alembic（绕开 host PyMySQL caching_sha2 桥接坑）。

1. `alembic upgrade head` → **OK**（空库 big-bang create_all 按当前 model 建全表，逐对象 gate 重入安全）
2. DDL 核对（`SHOW CREATE TABLE ingest_profile`）：
   - `` `intake_root_id` varchar(16) NOT NULL DEFAULT 'self_built' ``（MySQL 8.4 实测渲染 DEFAULT；STRING 类型 server_default 合法，不同于 TEXT 1101 坑）
   - `` KEY `ix_ingest_profile_root_enabled` (`intake_root_id`,`enabled`) ``
   - `ingest_submission.intake_snapshot_json` TEXT NULL（无默认值，避开 1101）
3. 回填探针：INSERT 一行不带 `intake_root_id` → SELECT 得 `self_built`（server_default 生效）；`SELECT COUNT(*) WHERE intake_root_id IS NULL` = 0
4. `alembic downgrade -1` → **OK**；`SHOW COLUMNS LIKE 'intake_%'` 两列均消失（回滚干净）
5. `alembic upgrade head` → **OK**；`alembic_version` = `20261013_01_scene_intake`

**期间发现并修复 1 处真实 MySQL 坑**：初版迁移 `intake_root_id` 仅 Python `default`，MySQL STRICT 下不带该列的 INSERT 报 1364（SQLite 不建模、本地全绿遮不住）——model 加 `server_default="self_built"` 后隔离库复跑全绿（c30f048 已含）。

down_revision 指向 `20261009_02_ingest_frozen`（base c2018dd 单头）。**07B（20261012_01_scene_manual）未合入**：若其先合入，本迁移需 rebase 到其链后（revision 命名独立不冲突，链位置由协调者 BASELINE 裁决）。

## 二、双根冒烟证据（本地 real 栈口径，隔离 compose 栈）

栈构成：独立 `t16asmoke-<tag>` 项目（mysql:8.4 + backend + scanner，均用 worktree 代码 bind mount），临时 NAS 树 `/home/wang/.local/state/rosbag-scene/smoke/nas`，`SCENE_INGEST_ENABLED=1`、三根=测试契约值、scanner user=1000 对齐。**主本地栈（rosbag-catalog-local-*，含一个 RUNNING mock run）全程未触碰**，结束后 `down -v` + 镜像 tag 清理。

输入：`/test/incoming/legacy-bag-<tag>` 与 `/test/scene/incoming/scene-bag-<tag>` 各一个 fixture 袋（metadata.yaml + part.db3 + .done，内容不同）。

实测结果（全部断言通过）：
- 两条 journal 独立：`/data/scanner-state.json` 只含 legacy 袋、`/data/scanner-state-scene.json` 只含 scene 袋，各自带 `root_id`（`self_built`/`scene`）与 `ready_directory` 映射
- 两根 ScanJob 各一条：`/test/incoming` SUCCESS `{...,"root_id":"self_built"}`、`/test/scene/incoming` SUCCESS `{...,"root_id":"scene"}`
- **场景袋**：登记 → 绑 `scene-isolated` 入口 → `ingest_submission.status=SCHEDULED`，`intake_snapshot_json={"environment":"test","profile_id":"scene-isolated","profile_version":1,"ready_root":"/test/scene/ready","root_id":"scene","scan_root":"/test/scene/incoming","schema_version":"scene-intake/v1"}`；**pipeline_run 零行（不建 Phase0）**
- **旧袋**：登记 → 绑 `default` 入口 SCHEDULED；恰好 1 个 `SELF_BUILT_BAG / PHASE0_QUEUE` run（旧行为不变）
- 一根故障隔离：单测 `test_scene_root_fault_does_not_block_legacy_root` 实证（scene 客户端 login 抛错 → 旧根 created=1、`roots.scene.state=FAILED` 带错误信息）
- 未配置三根单根口径：单测 `test_single_root_when_scene_unconfigured` 实证（roots 仅 self_built，顶层统计=旧口径）

## 三、历史清点（派单 AC7 口径，启用前）

冒烟栈（全新库+启用场景三根前）：`pending_input=0, pending_scene_events=2, bags=2, scan_jobs=2`（后两袋为本轮冒烟输入）。

主本地栈（rosbag-catalog-local-mysql-1）现状核对：`ingest_profile` 迁移前无 `intake_root_id` 列（旧代码在跑）；存量 `ingest_submission` PENDING_INPUT=0。生产库清单属 TASK-11 部署前动作，本单不执行。

## 四、与 16B/16C 的契约交接点
- 16B 消费：`IngestProfile.intake_root_id`、`intake_snapshot_json`（scene-intake/v1）、register 请求 `root_id` 字段、`SCENE_NAS_READY_ROOT`（源路径=ready 根+bag relative_path）、`SCENE_SLICE_PUBLISH_ROOT`（受控发布根注入）。
- 16C 消费：`intake_snapshot_json` 只读回显字段。
- 06B 已承载发布侧受控核对（`publish_root` 绝对 + st_dev 同文件系统 + `..` 拒绝），本单未动。

## 五、风险与待核对
- 07B 合入顺序影响本迁移链位置（见上）。
- `tests/test_devflow.py` 3 个 worktree 固有问题（`.git` 文件 vs 目录），base 同样失败，非本单。
- 生产三根物理树存在性未核验（TASK-11 前置）。