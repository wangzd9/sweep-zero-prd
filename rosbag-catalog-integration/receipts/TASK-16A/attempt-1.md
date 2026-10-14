# 回执：TASK-16A attempt-1 场景接收隔离（v0.4 最小闭环·第一刀）

- status: REVIEW_PENDING
- task/attempt: TASK-16A / attempt-1
- owner: A（执行者A·数据处理链路）
- 派单：`inbox/1号/TASK-16A/attempt-1-dispatch.md`（2026-10-12 22:40，DISPATCHED）
- ACK：`inbox/1号/TASK-16A/attempt-1-ack.md`（22:41，ACCEPTED）
- base: main 本地 `c2018dd`（= origin `502bf8e`+1 纯文档；**未包含 07B 文件**）
- 分支/worktree: `a/task-16a-scene-intake` @ `/home/wang/.local/state/rosbag-scene/wt-01-t16a`
- 交付 commit（冻结）: **`c30f048`**（第二刀，amend 收敛后终值）+ `79f6889`（第一刀基础层）；链 `c2018dd → 79f6889 → c30f048`
- 交付时间: 2026-10-13 01:15 +08:00
- 范围声明: 只接收/调度/扫描域（A 的 03B 连续责任面）；**不碰 07B 冻结文件集**（`scene_manual_revision*`、`detail.html`、`20261012_01_scene_manual` 迁移零出现，`git diff c2018dd..HEAD --name-only` 已核对）；不改生产 compose 实际值（只加契约透传行，空默认=不启用）；不实现 16B 代理/16C 页面；不搬历史文件、不退回复用 raw_rosbags。

## 一、文件清单（base c2018dd → c30f048，16 文件，+1147/-59）
| 文件 | 说明 |
|---|---|
| `app/environment_contract.py` | 新增测试/生产场景三根契约常量（`TEST_SCENE_NAS_*`、`PRODUCTION_SCENE_NAS_*`、`PRODUCTION_SCENE_SLICE_PUBLISH_ROOT`） |
| `app/config.py` | 三个新配置项 + `scene_roots_configured()` + `_validate_scene_roots()`（三根全有或全无、绝对逻辑路径、位于 NAS_STORAGE_ROOT 下、三根互不嵌套+与旧 NAS_* 不重叠、冻结契约值精确匹配）+ `scene_scanner_state_file` |
| `app/scanner/runner.py` | 双根上下文重构（RootContext、`_legacy_context`/`_scene_context`、`_scan_one_root`、`scan_remote` 顶层保持旧口径 + `roots` 字段；一根故障隔离） |
| `app/scanner/paths.py` | `validate_nas_path`/`ready_directory_for` 显式接收根参数（缺省=旧自建，旧行为不变） |
| `app/scanner/clients.py` | `MountedNasClient(scan_root, ready_root)` 双根上下文（缺省=旧自建） |
| `app/scanner/backend.py` | `register_source(..., root_id=)`（仅场景根登记携带） |
| `app/schemas/requests.py` | `SourceRegisterRequest` 契约声明 `incoming_path`/`root_id` |
| `app/services/scene_intake.py`（新增） | 登记身份防线纯路径判定（`validate_register_root`/`derive_root_id_for_ready`） |
| `app/services/ingest_service.py` | `_active_profiles(root_id)` 隔离、`match_profile_for_incoming(root_id, scan_root)`、`seed_scene_isolated_profile`、`_intake_snapshot`（scene-intake/v1）、bind root 分流 |
| `app/services/source_service.py` | register 接线防线 + bind 透传 `effective_root` + 场景未匹配不触发 Phase0 |
| `app/services/bootstrap.py` | 场景三根配置启用时种子 `scene-isolated` 入口 |
| `app/models.py` | `IngestProfile.intake_root_id`、`IngestSubmission.intake_snapshot_json`、索引 |
| `alembic/versions/20261013_01_scene_intake.py`（新增） | 迁移（含 downgrade、逐对象 gate、回填） |
| `compose.yaml` | scanner/backend 三根 + 场景 journal 透传（空默认=不启用） |
| `tests/test_scene_intake_isolation.py`（新增） | 19 用例开发自测 |
| `tests/test_scanner_stability.py` | fixtures 补 scene 字段（行为不变） |

## 二、行为（8 交付面对应）
1. **三配置项**：契约值测试 `/test/scene/{incoming,ready,slices}`、生产 `/public/rosbag_scene_processing/{incoming,ready,slices}`（用户已确认树）；校验 fail-closed；旧 `NAS_*` 校验不替换。
2. **Scanner 双根**：单进程每轮各扫一根；独立 journal（`SCENE_SCANNER_STATE_FILE`）、独立 ScanJob（path=各自 scan root）、独立 incoming→ready（原子 `os.replace`，穿越/符号链接越界由 `MountedNasClient._physical_path` 拒绝）；场景根要求物理挂载（Dsm 口径 fail closed 不扫）；未配置三根时与旧单根行为完全一致。
3. **IngestProfile 扩展**：`intake_root_id` 回填 `self_built`（不改原 ID/version/hash）；`scene-isolated` v1 默认仅 `scene_slice`+`slope`；具体版本 root_id 不可变（create 显式赋值、patch 不接收该字段、新版本继承）。
4. **接收快照**：`intake_snapshot_json`（scene-intake/v1：environment/root_id/逻辑 scan+ready 根/profile ID/version）接受提交时写入（含系统兜底）；与 EffectiveConfig/config_hash 分离，不重算业务 hash。
5. **登记身份防线**：Backend 按受控 ready 根重新推导根身份与上报 root_id 交叉核对（不只信 Scanner）；矛盾 409/未知 400/受控根外声明 409；场景 ready 缺 incoming_path 也不落自建默认；旧客户端缺 root_id 按旧兼容（旧自建 ready 推导 self_built，与既有行为一致）。
6. **用途路由边界（AC-14）**：场景袋默认提交→只建 SCENE_SLICE 事件、**零 Phase0 run**（冒烟实证）；未匹配/开关暂停→停在待处理不触发 Phase0；`SCENE_INGEST_ENABLED=0` 仅暂停场景自动调度。
7. **历史兼容**：已有 submission/run 保留原路径与 hash；不因新根重建运行；启用前清点口径已跑（冒烟栈 `pending_input=0, pending_scene_events=2, bags=2, scan_jobs=2`；生产清点属 TASK-11 部署前）。
8. **staging 契约点声明**：场景 staging 位于 slices 同文件系统（06B `scene_publish_service` 已强制：`publish_root` 绝对受控根 + `os.stat(st_dev)` 同文件系统检查 + `..` 段拒绝）——**由既有 06B 代码承载，本单不动**；16B 代理消费时注入 `SCENE_SLICE_PUBLISH_ROOT`，不信任回报者自选 publish_root。

## 三、验证证据（命令/退出码/环境）
| 项 | 命令 | 结果 |
|---|---|---|
| 全量 pytest（SQLite） | `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest tests/ -q` | **869 passed, 10 skipped**（剔除 3 个 `tests/test_devflow.py` worktree 环境固有问题——`git stash` 后 base 上同 3 失败，非本单引入） |
| 新增自测 | `pytest tests/test_scene_intake_isolation.py -q` | **19 passed**（防线 4xx/矛盾/未知根、入口 root 隔离、bind 分流、seed、双根独立 journal/ScanJob/映射、一根故障隔离、未配置单根兼容、API 伪造 root_id 拒绝） |
| ruff | `ruff check app tests alembic/versions/20261013_01_scene_intake.py` | **All checks passed**（本单 0 新增违规） |
| MySQL 8.4 隔离库迁移往返 | 独立容器（mysql:8.4 + 同 network backend 镜像跑 alembic，凭据编程式） | **upgrade head → DDL/回填核对 → downgrade -1（列消失验证）→ re-upgrade head（`20261013_01_scene_intake`）全部通过**；发现并修复 1 处 MySQL 实坑：`intake_root_id` NOT NULL 在 STRICT 模式需 `server_default`（SQLite 不建模，冒烟探针暴露，已并入 c30f048） |
| 本地 real 栈双根冒烟 | 隔离 compose 栈（独立 mysql/backend/scanner + 临时 NAS 树 + bind mount 本 worktree 代码，不碰主栈） | **全断言通过**：场景袋→`scene-isolated` 入口 SCHEDULED + intake_snapshot（root_id=scene）+ **零 Phase0 run**；旧袋→`default` 入口 + 恰好 1 个 SELF_BUILT_BAG run；两条 journal 各自独立且含 `root_id` 标记；两根 ScanJob 各一条（`/test/incoming`、`/test/scene/incoming`） |

关键断言（冒烟）：
- `SCENE SUBMISSION`：`scene-isolated / SCHEDULED / {"schema_version":"scene-intake/v1","root_id":"scene","scan_root":"/test/scene/incoming","ready_root":"/test/scene/ready",...}`
- `RUNS`（按 bag 归因）：`SELF_BUILT_BAG PHASE0_QUEUE` 仅 legacy-bag；scene-bag 无 run。

## 四、未执行项（如实申报）
- 真 MySQL 8.4 生产口径迁移已在隔离库实证，但**生产库实际 upgrade 属部署阶段**（TASK-11 前置），本单不执行。
- 生产三根实际值部署核验（`/public/rosbag_scene_processing/*` 物理树）属 TASK-11，本单只冻结契约值+测试根可用。
- 显式 self_built/双用途在场景根的"只接受已登记且冻结用途含 self_built 的源"子句：由既有冻结用途机制（`resolve_effective_config` + `SCENE_EMPTY`/`PURPOSE_SCENE_MISMATCH` 守卫）承载，本单未新增代码；`/public` 路径不放白名单由防线 409（受控根外声明）+ 场景 bind 仅按 scene 入口匹配保证。
- TESTER 独立验证（派单第二节口径）未跑——属测试者职责，本单开发自测不替代。

## 五、越界申报
无。07B 冻结文件集零触碰；未改生产 compose 实际值；未部署；未操作生产数据。