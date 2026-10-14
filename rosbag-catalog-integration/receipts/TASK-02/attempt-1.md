# TASK-02 回执 attempt-1

- task_id: TASK-02
- attempt: 1
- owner: 会话1号（飞书「数据处理链路开发」）
- status: REVIEW_PENDING
- requirement_version: v0.3.2
- interface_version: DESIGN §4/§8.1/§9/§11.3
- worktree: /home/wang/work/rosbag-catalog（主工作区，多会话并行，提交只含本任务文件）
- base_commit: dfd4f0e（协调者合并 TASK-03A/04A 后的 HEAD；我领取时 054b753，开发期间协调者推进了基线）
- upstream_accepted_commits: bc6263b（TASK-04A 合并）、dfd4f0e（03A/04A 共享入口合并）

## 允许范围（TASK-02 卡 + DESIGN §11.3）
- app/models.py：新表 + BagRecord 角色/可用性扩展 ✅
- alembic/versions/：独占迁移链 ✅
- app/services/bag_cleanup_service.py：派生防线四阶段阻断 ✅
- app/services/source_service.py：指纹归并防子包改写 ✅
- app/services/scene_lineage.py（新增）：血缘查询/守卫 ✅
- tests/test_scene_slice_lineage.py（新增）✅
- 未改：算法（ros2_slice）、API 路由/调度、03B 接收入口、bag_cleanup_plan.py（纯函数计划器无需改）

## 实际输出
- commit: 527b033（主提交）+ e10cab4（OCR 7 条修复）+ a317e48（复审暴露的 server_default 漂移 +
  evidence 级联修复），均已推 GitLab origin/main；GitHub 镜像 remote 推送失败：`git@github.com: Permission denied (publickey)`，id_ed25519_github 当前被拒，需人工检查 GitHub SSH key）
- 6 文件：app/models.py(+204)、alembic/versions/20261008_01_scene_slice_model.py(新增,324)、
  app/services/scene_lineage.py(新增,57)、app/services/bag_cleanup_service.py(+19)、
  app/services/source_service.py(+17)、tests/test_scene_slice_lineage.py(新增,11 测试)

## 实现行为
1. **BagRecord 扩展**：`bag_role`(ORIGINAL/SCENE_SLICE/NOT_APPLICABLE, server_default ORIGINAL) +
   `availability`(PENDING/AVAILABLE/WITHDRAWN, NULL=非切片) + 组合索引
   (bag_role, availability, started_at, bag_uid)（DESIGN §8.1 必要索引）。
2. **新表（BIGINT 主键，DESIGN §8.1）**：
   - `scene_capability`：能力不可变版本（scene_code+capability_version 唯一，参数 schema/defaults、
     输出/发布标签窄 JSON、config_hash）；
   - `scene_analysis_version`：父包+场景分析版本，current 指针（uq parent+scene+version，
     idx parent+scene+current）；
   - `scene_segment`：纳秒 BIGINT 闭区间，label/publish_target/slice_key/边界证据引用，
     idx (analysis_version_id, start_ns, id)；
   - `bag_derivation`：父子血缘，child_bag_uid 唯一，父子 FK 均 RESTRICT（bag_record.bag_uid），
     run_id+slice_key 唯一，idx (parent_bag_uid, scene_code, run_id, child_bag_uid)；
   - `bag_scene_label_evidence`：标签来源 MODEL/MANUAL/LEGACY_MANUAL + 原始判定引用 +
     修订者/原因（P1 审计字段预留）；
   - `bag_purpose`：用途关联（purpose, bag_id 复合主键 + lookup 索引）。
3. **历史回填**：迁移内 `UPDATE bag_record SET bag_role='NOT_APPLICABLE' WHERE dataset_type != 'self_built'`
   （当前 dataset_type 仅 self_built/nvidia_physicalai 两种取值，无第三类可猜，符合 DESIGN §9"不猜测"）。
4. **downgrade 防线**：bag_derivation 非空或 scene_analysis_version.current=true 时拒绝回滚
   （MySQL DDL 隐式提交前检查）；MySQL 中 FK 列显式索引不能先于 drop table（error 1553），
   已改为按 FK 依赖逆序直接 drop table。
5. **清理四阶段派生阻断（DESIGN §9，"未经适配的旧清理必须在服务端阻断"）**：
   - preview：`start_preview` 在身份检查后 `assert_no_derivation` → 409 HAS_DERIVATION；
   - inspection（preview 与 worker claim-INSPECT 共同路径）：`run_inspection` 派生包判
     BLOCKED（error_category=HAS_DERIVATION），不留可确认计划；
   - confirm：身份复核后二次 `assert_no_derivation`（防 preview 后新建血缘）→ 409；
   - finalize：`_finalize_deletion_guard` 首道 `assert_no_derivation`（FK RESTRICT 前的可读阻断）。
6. **register 防归并（DESIGN §3.2/§4.1，"父子同指纹不被归并或改写父路径"）**：
   `register_source` 指纹命中"任一" SCENE_SLICE 行即 409（父子可共享指纹，不能只看 id 序第一行）；
   子包走专用派生登记（TASK-06B 范围），本任务只建防线。

## 验证命令与结果
| 命令 | 结果 |
|---|---|
| `ruff format --check` + `ruff check`（本任务 6 文件） | 全过 |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/test_scene_slice_lineage.py` | 11 passed |
| `pytest -q`（全量，未设 DATABASE_URL） | 626 passed, 10 skipped（MySQL 专属 skip） |
| `local_stack.sh test` | 本地模拟全链路通过（platform revision 3a87027 时） |
| SQLite 迁移：upgrade head / downgrade -1 / 重入 upgrade | 通过；派生数据时 downgrade 被拒 |
| **MySQL 8.4 隔离库**（独占容器 task02-mysql-check，回环 3399，用完即删） | upgrade 到 head；
  新列/5 张 BIGINT 主键/索引/FK RESTRICT 落地核实；nvidia 历史行回填 NOT_APPLICABLE；
  派生数据时 downgrade 被拒；清理后 downgrade 放行且列/表/索引全回滚；重入 upgrade 成功。容器已删除 |
| `local_quality_gate.sh` | Ruff 全过、pytest 全过、Compose 解析过；**Ruff format 步骤被 03A/04A owner 的在途未提交文件（app/domain/scene_config.py、tests/test_scene_config_resolution.py）挡住，非本任务文件，未代改** |
## OCR 审查结果（commit 527b033；Qwen 队列与其他会话争用，拆 4 批）
**5 个代码文件经 OCR 审完**（migration×3 次 / models×1 / bag_cleanup_service / scene_lineage / source_service，
后三者 0 意见）；**测试文件 tests/test_scene_slice_lineage.py 未审**——ocr 二进制 `default_path`
硬编码排除 tests/，`--rule` 多种键名（default_path/user_exclude/excludes/include_tests）均无法覆盖，
尝试 session d0843521 被判 skipped(0 文件)。测试代码以 642 passed 全量回归为准，但严格说 OCR 覆盖
不含该文件，如实标注（用户/协调者如要求测试文件也过 OCR，需升级 ocr 或人工审查）。
共 7 条意见（models/迁移 6 条 + migration 复现 1 条，无一条来自测试文件），全部对照 HEAD 核实并修复（e10cab4，已推 origin/main）：
1. [bug · medium] 回填谓词 NULL 缺口：`dataset_type != 'self_built'` 对 NULL 行求值为 NULL，
   历史 NULL 行被误保留 ORIGINAL。修复：`WHERE dataset_type IS NULL OR dataset_type != 'self_built'`。
   谓词语义已用 SQLite 临时表独立验证（NULL→NOT_APPLICABLE，旧谓词漏判证实）。
2. [maintainability · low] bag_purpose 复合主键 (purpose, bag_id) 与 ix_bag_purpose_lookup 冗余。
   修复：model + 迁移两处同删（migration 第二次复现同一意见）。
3. [performance · low] ix_scene_segment_analysis_version_id 是复合索引最左前缀，冗余。修复：两处同删。
4. [maintainability · low] ix_bag_derivation_parent_bag_uid 是复合索引最左前缀且 model 未声明，漂移。修复：迁移删除。
5. [maintainability · low] child_bag_uid 唯一约束命名 model(uq_ 前缀)/迁移(ix_ 前缀) 不一致，MySQL autogenerate 会误报。
   修复：迁移改列级 unique=True 与 model 对齐。
修复后验证：ruff 双过、11 血缘测试过、全量 642 passed、SQLite 迁移 upgrade/索引核对/downgrade/重入全过、
谓词 NULL 分支独立验证过。

## OCR 修复复审中暴露的两处额外真实缺陷（commit a317e48，已推 origin/main）
MySQL 8.4 隔离库按"迁移自身 DDL 路径"复验 e10cab4 时发现：
1. **bag_role server_default 漂移**：迁移 add_column 带 `server_default='ORIGINAL'`，而 model 只有
   Python 侧 `default`——create_all 路径（测试/新库）与迁移路径 DDL 不一致，`alembic check`
   会对生产库误报。修复：model 补 `server_default="ORIGINAL"` 对齐（防御性，两条路径 DDL 一致）。
2. **bag_scene_label_evidence FK 挡清理链（真实缺陷）**：本任务把 `bag_scene.bag_id` FK 从
   RESTRICT 改 CASCADE（允许清理删 bag），但 evidence 表的 `bag_uid`/`scene_id` 仍是 RESTRICT——
   带场景标签证据的 bag 走清理删除时会留孤儿或 FK 500。修复：model 与迁移同步改 CASCADE
   （证据层语义跟随 bag_scene 级联，P1 人工纠错审计由 analysis_version/segment 的 SET NULL +
   保留 withdrawn 字段承载，不受影响）。
复验证据：迁移自身 create_table DDL 在 MySQL 产出 `ibfk_1/ibfk_2 = CASCADE`；回填
nvidia/self_built/NULL 三行角色正确；删除带 bag_scene 的 HSB 无残留；派生数据 downgrade 被拒、
清理后复放通；全量 642 passed。

## 旧 ID/FK 风险盘点（TASK-02 要求，DESIGN §8.1）
现状（MySQL 8.4，21 张既有表）：
- **BIGINT 主键仅 1 张**：`dataset_frame`（已有 with_variant Integer/sqlite 模式，本次新表沿用）。
- **INTEGER 主键的高增长表**：`bag_record`、`bag_file`、`bag_topic`、`source_copy`、`artifact`、
  `pipeline_run`、`step_run`、`pipeline_event`、`api_idempotency`、`bag_cleanup_operation`。
  MySQL 下 INTEGER=INT，上限 21.47 亿行。当前本地测试库各表行数 < 千级；处理机生产库行数未在本次
  只读范围实测（需用户授权查看处理机时补 `SELECT COUNT(*)`，TODO 标记）。
- **FK 引用 INTEGER 主键的下游**：bag_file.bag_id、bag_topic.bag_id、bag_scene.bag_id、
  bag_purpose.bag_id(新)、resource_lease.resource_request_id、resource_request.step_run_id/lease_id。
- **扩容成本判定**：bag_record.id 若改 BIGINT，需同步改上述 4 个 FK 列（bag_file/bag_topic/bag_scene/
  bag_purpose），MySQL 下 INT→BIGINT 是 INSTANT/INPLACE 兼容扩容（不重写数据），但 bag_scene 是
  复合主键（bag_id, scene_id），改主键列类型走 COPY 重建（长锁风险）。**结论：不属于"低成本兼容
  同批可做"，按 DESIGN §8.1 判定列 TASK-15（后置），触发条件=bag_record 行数达 ~10 亿或
  实际 INSERT 报 1486 越界；本次 P0 新表全部 BIGINT，不依赖旧表扩容。** 已在回执明确，不标"已完成扩容"。
- 对外 bag_uid 26 位字符串不变；PipelineRun 等以字符串 ID 为主键语义，无容量风险。

## 未执行项
- 处理机生产库 ID 行数盘点（只读 SELECT COUNT）：未执行，原因=需用户授权查看处理机状态（新会话规则默认只查本地）。
- GitHub 镜像 push：失败（publickey），需人工检查 `~/.ssh/id_ed25519_github` 是否仍绑定账户。
- OCR 审查：运行中，结果补充在本回执。

## 契约影响与文档修订建议
- 新表名/列/索引/唯一约束为下游 03B/05/06A/06B 的正式数据契约（DESIGN §4.1 目标字段已落地）；
  其中 `scene_capability` 与 TASK-04A 的**内存注册表**（app/domain/scene_config.py 的
  SceneCapability dataclass）是两层：04A 是代码内不可变描述+契约测试，本表是数据库持久登记
  （DESIGN §2.1"Backend 校验并登记不可变版本"）。**建议协调者确认**：04A 合并的 YAML 注册表是否
  需要在 03B/05 接入时同步登记到 scene_capability 表，还是 P0 以代码注册表为准、本表留作
  审计/版本指针——两者字段口径一致（scene_code/capability_version/parameter schema），不冲突。
- bag_purpose 是复合主键表 + 独立映射类 BagPurpose（与 bag_scene 模式对齐），用途读写
  （bag.purposes）归 03B 配置绑定使用。
- 建议 DESIGN §4.1 补一句：availability 列原始包为 NULL（非空=切片），避免 06A 误设默认值。

## 建议可解锁任务
按 TODO §6.2，TASK-02 接受后候选：TASK-03B、TASK-05、TASK-06A（需 03A/04A 已接受——
协调者已合并 03A/04A，若 02 验收通过则三者依赖齐备）。