# R2-20261010 强模型审查包（第二轮）

## 1. 身份与门禁

| 字段 | 值 |
|---|---|
| review_id | R2-20261010 |
| review_type | PRE_MERGE（§B：R2B 06B 合入前）+ 返修增量复审（§8：R2A/R2C 对第一轮结论的修复验证） |
| scope | 三节按不变链合批：R2A 接收与调度（03B+05 第一轮 #1-#7 全部处置）、R2B 登记与发布（06B 首审）、R2C 识别与切包（04B #2 CDR 对齐修复增量） |
| gate | **R2B 决定 06B 合入门禁（当前暂停，main 停在 3b78736）**；R2A/R2C 代码已合入 main（返修复核，若判 REWORK 则回派修复，不回退已合入范围）；06 聚合与 TASK-08 工程闭环门禁等待 R2B |
| base / target | R2A: b3280c9 → **3b78736**（已合入，main HEAD=origin）；R2B: 3b78736 → **6b21c91**（wt-04a 待合入）；R2C: **eaf632a**（= 第一轮 04B 审查的 target，§8 增量基线）→ **640c5a8**（已合入，含在 R2A target 内；纯 #2 修复增量） |
| integration_candidate | R2A/R2C 适用：main 3b78736 即固定集成候选（多任务已组合并全量验证）；R2B 适用：wt-04a 6b21c91（base=3b78736，组合后 49 定向 + 804 全量已跑，见 §5） |
| contract_version / semantic_hash | purpose-schedule-event/v1（03B 生产→05 消费→06B 消费三层）；scene-run/v1 身份摘要。复算命令：`git show 3b78736:app/services/ingest_service.py \| sed -n '1,220p' \| sha256sum` = 7c5312a6c178b092…（事件生产段）；`git show 3b78736:app/services/scene_schedule_consumer.py \| sha256sum` = 5c9cc29f8c76e35e…（消费端）。R2B 6b21c91 不改这两文件 |
| trigger_decision | **REVIEW_NOW**：① 具体风险事实=第一轮 1 critical+6 high 的修复正确性与存量数据迁移兼容性未经独立复核（尤其 #7 持久身份键改变了 06B 同 source 多 run 的既有行为，验收时已真实暴露 2 个 06B 用例不兼容——跨任务行为改变）；② 待回答问题=§6 待裁决 4 项；③ 受影响不变量=身份唯一性/冻结 hash 不漂移/事件不丢不堵队/发布文件与 DB 一致/换版不倒退；④ 决定的门禁=06B 合入（R2B）+ 06 聚合/TASK-08（全部） |
| package_status | READY_FOR_USER_TRIGGER（R2B 节弱模型 OCR B8 按单 commit 拆批运行中，收口后结论补入 §5，不阻塞送审——OCR 结果不影响本包代码快照） |
| suggested_result_path | /home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/R2-20261010-result.md |

## 2. 目标、不变量与非范围

**必须成立（受审不变量）**：
- I1 配置保持：接受时冻结的能力 hash 全链路不重算、不漂移（03B emit → outbox → 05 消费 → 06B 回报对账，manifest.config_hash == run 快照 capability_config_hash）
- I2 身份唯一：同业务身份（源+代次+用途+冻结能力集合+reanalysis_id）全局只创建一个 scene run（含终态），持久 scene_identity_key 不随终态释放；显式重分析必须带 reanalysis_id
- I3 事件不丢不堵队：outbox 事件 consumed/dropped 均原子离开 PENDING；DROPPED 必带 error_reason；坏事件不得占据 LIMIT 50 头部
- I4 并发正确：PATCH 与 Scanner bind 共享 submission 行锁 + row_version 条件；重复事件幂等回放
- I5 发布一致：文件（非空/可打开/时间证据）与数据库登记均完成才 AVAILABLE；storage_offset_ns 从 manifest 推导不可推导则拒绝发布
- I6 换版保护：新版失败保旧 current 不动；晚到旧版不倒退；NOT_APPLICABLE/FAILED 不换版
- I7 迁移安全：20261009_01 backfill 对存量重复身份去重（规范行持键其余 NULL）；20261009_02 链序单头

**触发本次强审查的风险**：
- 第一轮 #7 修复（持久身份键）改变跨任务行为——已真实命中 06B 两个用例（同 source 建第二个 run 从"新建"变"复用终态 run"），说明行为改变面超出 05 内部
- 06B 是 1960 行全新模块（发布/换版/对账），且第一轮审查时它尚未存在
- 存量数据迁移兼容性（backfill 去重）仅 SQLite 实测，MySQL 8.4 真实 DDL 行为第一轮 #1 已有先例（literal_binds 过读误报）

**非范围**：02/03A/04A/06A（第一轮已审且未变化）、Phase0/A100 执行器内部、NVIDIA 脚本仓库、生产部署与 cutover 清单、TASK-08 联调设计（等工程闭环后另判）。

## 3. 变更地图与调用链

### R2A（b3280c9..3b78736，4259 行 patch：R2A-receive-schedule-full-diff.patch）
- 文件：ingest_service.py（冻结 hash emit + FOR UPDATE）、source_service.py（用途门控 PHASE0 + 双过滤）、scene_schedule_consumer.py（DROPPED 终态 + 冻结 hash 校验）、scene_slice_service.py（持久身份键 + reanalysis_id）、pipeline_service.py（终态不释放 scene_identity_key）、alembic 20261009_01（身份键+outbox error_reason+backfill 去重）/20261009_02（frozen_capability_hashes_json）、orchestrator.py（观测）
- 调用链：Scanner bind（行锁）→ ingest _emit_purpose_events（冻结 hash 落 outbox，FROZEN_HASH_UNAVAILABLE 显式失败）→ orchestrator poll → consumer（校验/建 run/SCENE_UNAVAILABLE 失败留痕/DROPPED）→ pipeline 终态（身份键保留）
### R2B（3b78736..6b21c91，2026 行 patch：R2B-06B-full-diff.patch）
- 文件：scene_result_report_service.py（+553：身份三重校验/av 行回填/完整性门禁/complete-scene/换版/reconcile）、scene_publish_service.py（+245：staging 发布/storage_offset 推导/per-slice manifest）、scene_results.py（+45：3 路由）、scene_result.py schema（+102）、scene_slice_service.py（3 行：error_message None→''）
- 调用链：执行面 /results（lease+源代次+run 类型校验 → manifest 解析 → 冻结 hash 对账 → av 占位行回填登记 → PENDING→AVAILABLE）→ /complete-scene（完整性等值门禁 → 文件校验 → 换版 3 次有界重试 409 重放 → run 终态）→ /reconcile-scene（发布目录 per-slice manifest 补登记，不重复 move）
### R2C（eaf632a..640c5a8，374 行 patch：R2C-cdr-align-full-diff.patch，仅 cdr.py + test_slope_adapter.py）
- 文件：app/scene/slope/cdr.py（_align4 + 解码端全部 32-bit 读点对齐 + 编码端对称 base 语义）、tests 9 个 padding golden
- 调用链：封装头解析 → CDR body（base=封装头后偏移 4 / 裸 CDR base=0）→ 逐字段 align(4) → Image/CompressedImage 解码

## 4. 真实代码材料

关键代码（第一轮问题点当前形态，行号基于 target commit）：

**R2A #1（迁移 TEXT server_default，第一轮判 critical）** —— 20261008_02:47 仍声明 3 个 TEXT server_default，但干净 MySQL 8.4 general_log 实测真实 DDL 为 `TEXT NOT NULL` 无 DEFAULT 子句（§5 证据 E1）；业务路径显式赋值（ingest_service.py:195-201），读取 `or` 兜底。
**R2A #2（CDR 对齐）** —— cdr.py:47-49 `_align4(pos, base)` 只向前、以 CDR body origin 为基准。
**R2A #3（用途门控）** —— source_service.py:240-245 先冻结用途、仅 self_built 在集合内才建 PHASE0 run；恢复登记查询 SELF_BUILT_BAG + source_generation 双过滤（:136-139）。
**R2A #4（冻结 hash）** —— ingest_service.py:160-182 接受时 `effective_params_by_capability` 计算落 frozen_capability_hashes_json，cap is None 时 raise SceneConfigError（FROZEN_HASH_UNAVAILABLE），**不允许 NULL-hash 事件**；05 消费端 registry.get→None 落 SCENE_UNAVAILABLE 失败 run。
**R2A #5（DROPPED）** —— scene_schedule_consumer.py:77-89 mark_event_dropped 原子写终态+reason（WHERE status='PENDING'），poll 只取 PENDING。
**R2A #6（行锁）** —— ingest_service.py:414-421 PATCH 与 bind 共享 `with_for_update()` + status/row_version 条件。
**R2A #7（持久身份键）** —— scene_slice_service.py:183-200 按 scene_identity_key 查重（含终态），终态 run 同身份重放复用；pipeline_service 终态不再清 scene_identity_key（active_identity_key 仍释放）。
**R2A backfill 去重（OCR B6 high 修复）** —— 20261009_01:60-95 按 identity 取 max PK id 规范行持键，其余 NULL + key_check 条件更新。
**R2B 身份三重校验** —— scene_result_report_service.py:56-77 `_require_scene_run`（FOR UPDATE + require_valid_task_lease + pipeline_type + source_generation + check_fence_for_source）。
**R2B 完整性门禁与换版** —— :249-385 `_check_integrity`（expected==registered 等值）/ `complete_scene`（switch_current 3 次有界重试 → 409 重放 / 失败保旧 / 晚到旧版不倒退）。
**R2B storage_offset 推导** —— scene_publish_service.py:57-97（manifest 时间 - 源 bag header 首帧 ns，不可推导返回 None → 拒绝发布）。
**R2B 对账** —— :467-560 `reconcile_scene`（发布目录 per-slice manifest 补登记，_target_matches digest+sha256 校验，不重复 move/不覆盖）。

完整可定位 diff（仓库 /home/wang/work/rosbag-catalog，wt-04a 见 §1 integration_candidate）：
- `git diff b3280c9..3b78736 -- app alembic tests` = review-bundle-20261010/R2A-receive-schedule-full-diff.patch（4259 行）
- `git diff 3b78736..6b21c91 -- app alembic tests`（wt-04a）= R2B-06B-full-diff.patch（2026 行）
- `git diff eaf632a..640c5a8 -- app/scene/slope tests/test_slope_adapter.py` = R2C-cdr-align-full-diff.patch（374 行）

## 5. 验证证据（全部绑定各自 target 快照）

| 证据 | 与 target 关系 | 环境 | 命令/结果 | 关键断言 | 路径 | 未执行项 |
|---|---|---|---|---|---|---|
| E1 #1 误报定论 | 3b78736（02 迁移字节级=当时 main） | 干净 MySQL 8.4 容器（docker.m.daocloud.io） | alembic 完整升级链两遍 RC=0；general_log 抓 CREATE TABLE ingest_profile 三 TEXT 列 = `TEXT NOT NULL` 无 DEFAULT；未触发 1101 | 迁移真实 DDL 合法；强模型第一轮"fresh compile 得 DEFAULT '[]'"为 literal_binds 过读 | reviews/TASK-03B/attempt-2/verify-03b-mysql-text-default.md + inbox/coordinator/TASK-03B/strongmodel-1-critical-ruling.md（21:29 裁决） | 生产 schema（隔离库） |
| E2 F2 并发 | 3b78736（f11e617 在链内） | MySQL 隔离容器 | 真并发 1 成功 + 1 409；pin-事务复证实 409 出自守卫 UPDATE | 乐观锁串行化正确 | reviews/TASK-03B/attempt-2/verify-f11e617-f2.md（16:56 PASS） | — |
| E3 outbox 联调 | 533aa1c（03B+05 返修均在 main；3b78736 与 533aa1c 差异仅 docstring/import 风格 4 commit，不改受审行为） | SQLite | 6/6 PASS：真实 bind emit→消费建 run 身份键非空；冻结 hash 逐字节一致 + registry 漂移重放 reused=1/created=0；漂移建 SCENE_UNAVAILABLE 失败 run 三重留痕；缺 hash→DROPPED+reason 不重捞；50 坏事件两轮清空；self_built 不建 run | I1/I2/I3 端到端 | reviews/TASK-03B/attempt-4/verify-05-03b-outbox-e2e.md | MySQL 真实 outbox DML（SQLite 执行语义等价） |
| E4 R2A target 全量 | 3b78736 | 本地 main | pytest -q = **783 passed / 0 failed**（10 skipped）；ruff 全绿；alembic heads 单头 20261009_02 | 零回归 | 协调者 08:51 运行 | MySQL 8.4 迁移真实 DDL（E1 已覆盖 02；01/03 链 SQLite+隔离库 upgrade 实测于 E2/backfill 测试） |
| E5 backfill 去重 | 3b78736（db4bec7 在链内） | SQLite 真实 alembic 子进程 | upgrade 20261008_02→head + 独立副本反证（不去重版必炸） | I7 | tests/test_scene_slice_scheduling.py（+167 行） | MySQL 8.4 该迁移 DDL |
| E6 R2B target | 6b21c91（wt-04a） | 本地 worktree | 定向 test_scene_result_report+storage = **49 passed**；全量 **804 passed**（3 failed=devflow 沙箱环境性，同基线）；ruff check/format 全绿 | I5/I6 + 与 I2 兼容（reanalysis_id 用例） | 协调者 09:20 独立复跑 | MySQL 8.4；真实 A100 执行面（mock executor） |
| E7 R2B 验收回归事件 | 6b21c91 vs 8bd5618 对照 | 双 worktree | base 8bd5618 上 24 passed；含 I2 的 main 上 2 failed → 定位为 #7 行为改变命中 06B 旧用例 → 6b21c91 修复（reanalysis_id 透传） | 跨任务行为改变的完整因果链 | HANDOFF 08:51 段 | — |
| E8 OCR 全闭环 | 各 commit 绑定 | 本地 Qwen 27B（弱模型） | B4-r1 04B 0 findings（21:35）；B5a f11e617 0（23:53）；B5b 86baad5 3 documentation（00:51，已修）；B6 6ce7b7a complete 2 条（high 已修 b5efba2）；B3 d1f2eba 5 条对照当前 HEAD 4 过时/撤回、2 low 已修（b75c6bf）；B7 db4bec7 0（08:51）；**B8 06B 范围运行中**（r3，10:24 起跑） | 弱模型意见全部处置 | reviews/TASK-05/attempt-1/ocr-batches.md | B8 收口 |
| E9 R2C 定向 | 640c5a8 | 本地 main | 35 passed（含 9 个 1/2/3 字节 padding golden + 真实 Image 封装）；B4-r1 OCR 0 findings | I1 无关；CDR 对齐正确 | 协调者 20:27 验收 | — |

## 6. 弱模型 OCR 与待裁决风险

**已确认并修复**（第一轮 6 high + F2 + OCR high）：#2→34c380d（640c5a8）、#3/#4生产端/#6→86baad5（533aa1c）、#5/#7/#4消费端→6ce7b7a（c764f1b）、F2 并发→f11e617（9506457）、B6 backfill high→db4bec7（b5efba2）；每笔均独立复验（§5）。
**经证据排除的误报**：#1（E1 general_log 铁证，21:29 裁决）；B3 medium#4（审旧 commit，I3 已由 #5 修复）；B3 low#1（代码已移除）；B3 low#3（reviewer 自撤回）。
**未覆盖**：06B 弱模型 OCR 未收口（B8 范围模式 4 连败——range 模式把 6 文件合并成单个 101k input 请求被本地 Qwen canceled；已改按单 commit 拆批：B8a=`-c 6e6bb73 --exclude tests` 在跑，B8b=`-c 6b21c91` 排队；不改变代码快照）；R2B 无 MySQL 8.4 实测（06B 零 DDL，纯 DML，SQLite 即执行环境——判断是否需隔离库补验由你定）；TASK-08 端到端（真实执行器/故障注入）未做，属下一阶段。
**待强模型裁决（聚焦 4 项）**：
1. **Q1（I2 行为改变的边界）**：#7 持久身份键使"同 source 同能力集合、无 reanalysis_id"从"每次新建 run"变为"复用既有 run（含终态）"。06B 已按此适配（E7）。该语义对**03B 事件重放**（同 event_id 重投→复用，符合 I2）无冲突；但请裁决：**用户/系统如何发起"同一 source 同一能力集合的真正新一次分析"**——当前唯一通道是带 reanalysis_id 的显式 API 或 03B 重新 PATCH+bind（代次+1 是否自动改变身份？身份摘要含 source_generation，故会）。是否存在"用户期望新建但拿到复用 run"的歧义入口？
2. **Q2（I5 storage_offset）**：推导依赖"manifest 首段起始时间 - 源 bag 前相机首帧 header 时间"，对多相机 bag 取 camera topic 匹配帧。若源 bag 首帧丢失/时钟偏移 >1s（现有容差），返回 None 拒绝发布——该 fail-closed 是否应改为告警+人工通道，当前 P0 是否可接受拒绝？
3. **Q3（I6 换版 409 重放）**：switch_current 3 次有界重试后返回 409 + 幂等重放语义；并发两个不同新版本同时 complete 时，后到者 409 重放拿到先到者的切换结果（created=false 语义由 store_idempotency 保证）。是否存在"后到者误判自己切换成功"的窗口？
4. **Q4（R2A #1 遗留观察）**：02 迁移 create_table 路径所有 server_default 列真实 DDL 均未渲染 DEFAULT（add_column 路径正常）——业务走 ORM 显式赋值无影响，但**未来若新增依赖列默认值的裸 SQL 路径会踩坑**。裁决：记录为已知方言行为即可，还是要求 02 迁移改为 add_column 写法以消除隐患？

## 7. 强模型输出要求

逐项输出：问题 ID / 严重级别 / 代码位置及证据 / 触发条件 / 错误后果 / 最小修复建议 / 应补充验证 / 是否阻塞及阻塞哪个门禁。
无充分证据标 `待验证`；不得虚构运行结果、修改代码、合并或部署。
总体结论（按节给出）：PASS / PASS_WITH_FOLLOWUPS / REWORK_REQUIRED / INSUFFICIENT_EVIDENCE。
作用范围声明：契约 / 模块合入（R2B）/ 集成（R2A/R2C 返修复核）/ 工程闭环（06 聚合+TASK-08 前提）之一或多个。

## 8. 协调者登记（结果返回后填写）

- result_path / received_at：
- result_snapshot_match：
- target_or_contract_changed_since_review：
- verified_findings / false_positives / unresolved：
- token_and_cost：
- rework_round / incremental_review_scope：
- decision / affected_gate / independent_work_continuing：