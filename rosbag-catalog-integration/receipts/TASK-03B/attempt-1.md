# TASK-03B attempt-1 回执（3号执行者）

- task_id: TASK-03B
- attempt: 1
- owner: 3号会话（飞书"数据链路监控告警"，hermes default profile）
- status: REVIEW_PENDING
- requirement_version: v0.3.2（2026-10-08）
- interface_version: scene-config-v1（03A 终版 67f9f4c）+ purpose-schedule-event/v1（DESIGN §11.2 协调者冻结 2026-10-08）+ scene-capability/v1（04A 终版 a23c541）
- worktree: /home/wang/.local/state/rosbag-scene/wt-03b
- branch: feature/scene-ingest-api
- base_commit: 8e97ef1（main，含 02=527b033 / 03A 终版=67f9f4c / 04A 终版=a23c541 / 接线 dfd4f0e；2026-10-08 核对干净）
- output_commit: 34d15ac（本 attempt 交付 commit，未推送；e93fbc6/1bd6595/9a33188/a669bde/797dd81 均为被 amend 替代的历史 hash）
- upstream_accepted_commits: 8e97ef1（集成基线）

## 交付范围（与派单允许范围一致，零越界）

新增 6 文件：
- `alembic/versions/20261008_02_ingest_config.py`：三表迁移 + downgrade 破坏性防线
- `app/api/ingest_submissions.py`：三提交接口 + profile 查询（限额/幂等接线）
- `app/services/ingest_service.py`：提交 CRUD、绑定、用途事件生产
- `app/services/scene_capability_read.py`：04A→03A 能力适配（§11.2 单一转换点）
- `tests/test_ingest_config.py`（13）+ `tests/test_ingest_config_api.py`（5，含迁移 2）

修改 7 文件（均为允许范围内的既有接入点）：
- `app/models.py`：追加 IngestProfile/IngestSubmission/PurposeScheduleEvent + Boolean import
- `app/api/__init__.py`：注册 ingest_submissions.router
- `app/scanner/backend.py`：register_source 增 incoming_path 透传
- `app/scanner/runner.py`：marker 持久化 incoming_directory（重启保持快照）
- `app/services/bootstrap.py`：lifespan 幂等种子 default 入口
- `app/services/source_service.py`：register_source 同事务调用绑定钩子（Backend 写边界）
- `tests/test_scanner_stability.py`：适配 register_source 3 参契约（2 处 mock + 断言）

## 关键设计决策

1. **能力事实来源 = 04A CapabilityRegistry（YAML 受版本控制）**，不新建 DB 能力表。`scene_capability_read.RegistryCapabilityRead` 是唯一适配点，把 04A 字段（`parameter_schema`/`TopicRequirement`/`disabled_reason`）转成 03A `CapabilityRead` 协议（`parameter_specs`/`required_inputs`/`unavailable_reason`），以 04A 供给侧字段名为准（§11.2）。03A 的 `StaticCapabilityRegistry` 仅作测试替身，生产路径走本适配器。
2. **两级 config_hash**：事件携带 `effective_config_hash`（03A 整包冻结快照）+ `capability_config_hash`（04A `registry.effective_params` 单能力维度，scene_slice 按场景逐条）。self_built 用途事件**不携带** scene/capability 字段（§11.2），保持既有 Phase0 语义。
3. **P0 自动接收默认关闭**：`SCENE_INGEST_ENABLED=0` 时 `bind_ingest_for_registration` 直接 matched=False，register_source 完全走旧入口行为（不建提交/事件/ingest 键）。旧入口 100% 兼容，测试 `test_bind_switch_off_keeps_legacy_behavior` 固化。
4. **路径抢占**：`path_claim_key = sha256(profile_id|version|relative_path)` 定长唯一占位（relative_path 宽 1024 不入唯一索引，避 MySQL utf8mb4 键长上限，见 HANDOFF 2026-09-28 T-03/T-04 的 1071/1089 坑）；绑定完成释放占位，路径可被后续提交复用。
5. **恢复登记幂等**：`_find_bound_submission(db, bag_uid)` 按 source_id 短路——重启后 Scanner 重放 MOVING/MOVED 标记不得重复出事件（outbox 双保险之一）。
6. **CONFIG_REQUIRED 语义**：显式选未注册场景 → 硬 422（UNKNOWN_SCENE）；仅"入口默认场景不可解析且用户未显式指定"才降级 CONFIG_REQUIRED（登记待处理 BOUND、不出事件、不拒绝提交）。测试分别固化两条路径。
7. **入口匹配两遍法**：非空前缀优先（§3.1 前缀不可重叠），空兜底 default 入口最低优先，避免专用入口被 default 静默吞掉。

## 验证（P0 本地，SQLite 生成数据，不连生产/处理机）

- 新增定向：`pytest tests/test_ingest_config.py tests/test_ingest_config_api.py tests/test_scanner_stability.py -q` → **24 passed**
- 全量：`pytest -q` → **657 passed, 10 skipped, 3 failed**；3 个失败全部为 tests/test_devflow.py 沙箱用例（worktree 的 `.git` 是文件非目录所致，主工作区同文件 24 passed 佐证为环境已知问题，与本任务改动无关）
- 静态：`ruff format --check` + `ruff check app scripts tests` 全过；`compileall` 全过；`git diff --check` 干净
- 迁移：独立库升级/降级往返验证三表建删 + path_claim/事件身份唯一约束行为断言 + PENDING 事件阻断 downgrade

## ocr 审查（第一轮 commit 1bd6595，11 条全部对照 HEAD 核实并修复）

| # | severity | 判定 | 修复 |
|---|---|---|---|
| 1 | medium | 成立 | `_emit_purpose_events` 直调 `registry.effective_params` 绕过适配层、且 `except Exception` 会把非 04A 内部故障（DB flush 等）当"能力不可用"回滚已成功的旧入口登记 → 收口到 `effective_params_by_capability`，只捕获 04A 自身异常 |
| 2 | medium | 成立 | registry 漂移（能力被禁用/移除）不再回滚：保留事件（不带 config_hash），05 侧按契约以 capability_version+scene_code+parameters 重建参数再校验 |
| 3 | medium | 成立 | PATCH 裸 JSON 直接进服务层 → 新增 `IngestSubmissionPatchRequest`（extra=forbid，复用 03A `SceneSelectionSchema`/`IngestPurpose`），FastAPI 自动 422 |
| 4 | medium | 成立 | bind 钩子 `except Exception → matched=False` 把 DB 故障吞成"未匹配"（bag 无声滑回旧链路）→ 去掉 try，DB 故障冒泡回登记事务显式失败 |
| 5 | medium | 成立 | create_submission check-then-act 并发窗口 → `begin_nested` + IntegrityError → 回读 → 409 PATH_CLAIMED |
| 6 | low | 成立 | `effective_params_by_capability` 死代码 → 事件路径已改走它（#1） |
| 7 | low | 成立 | list_profiles 全版本返回 → 按 profile_id 折叠为活动版本（与 _active_profile 同口径） |
| 8 | low | 成立 | 迁移文件末尾缺换行 → 已补 |
| 9 | low | 成立 | 内联 JSONResponse import 提到模块顶部 |
| 10 | low | 成立 | 与 #1 同源，一并修复 |
| 11 | medium→已升级处理 | 成立 | 恢复登记短路恒回 `self_built=False/scheduled_purposes=[]` 与首登不一致 → 新增 `bound_purposes_json` 列（模型+迁移同步），调度时持久化用途集合，恢复登记回显真值；测试断言加固 |

返修过程附带修复（未计上表）：
- amend 时 ruff format 误扫 4 个既有迁移文件（20260911_01 等）混入 commit → 已 `git checkout 8e97ef1 --` 还原，只保留本任务文件（项目门禁范围是 `app scripts tests`，不含 alembic/versions）；
- `header_idempotency_key` 别名因删死代码变未用 import → 已删；
- `_ensure_system_submission` 同窗口风险评估：仅系统默认路径（单 Scanner 串行登记），保持现状不引入 savepoint 复杂度（已在代码注释记录）。

## ocr 审查（第二轮 commit a669bde，2 条全部对照 HEAD 核实并修复）

| # | severity | 判定 | 修复 |
|---|---|---|---|
| 1 | medium | 成立 | `_ensure_system_submission` 默认解析无 SceneConfigError 守卫 → 单个 profile 配置问题把整条登记链路 500 化（Scanner 无限重试同 bag，违反 outbox 目标）→ 降级 CONFIG_REQUIRED（bag 登记待处理）。回归测试红绿验证过（撤修复 FAILED/恢复 PASSED）。注：03A 终版默认路径当前实际走 return None 降级、不抛错，守卫是防 03A 契约演进的兜底 |
| 2 | medium | 成立（建议方案部分误判） | 3 个 async def 路由内做同步 ORM 阻塞事件循环（全仓库唯一 async 路由）→ 改同步 def（ORM 进 threadpool，与仓库一致）；原始 body pre-parse 限额移到 async 依赖 _raw_body（事件循环里读+缓存，实测验证 413 生效）。ocr 建议的 `b"".join(request.stream())` 不可行（async 生成器无法在同步函数里迭代） |

第二轮附注：`WARNING [review_round_failed]`（29 请求中 1 个 deadline exceeded）——全文件核心审查第 2 轮超时，本轮覆盖不完整；第三轮（797dd81）补审返修 diff + 全量，意见核实后补记。

## ocr 审查（第三轮 commit 797dd81，2 条 bug·medium 全部对照 HEAD 核实并修复）

| # | severity | 判定 | 修复 |
|---|---|---|---|
| 1 | bug·medium | 成立 | PATCH 幂等操作 scope 是 `ingest-submission-patch:{id}`（终身）：成功后 row_version 推进，第二次修改复用同客户端 key 会被历史账回放/409 误吞 → operation 加 `:v{row_version}`（期望前置代次入 scope）；补回归测试（同代次重试回放 + 新代次同 key 不冲突） |
| 2 | bug·medium | 成立 | create_submission 的 IntegrityError 处理注释承诺"回读确认是活动占位"但代码没做（第一轮修复时简化过头）：本表有 uq_claim 与 uq_submission_id 两个唯一约束，撞 id/其他完整性失败会被误转 409 PATH_CLAIMED、掩盖真实后端故障 → 补回读（命中活动 PENDING 占位才 409，否则 re-raise）；补双向回归测试（uuid4 撞 id→re-raise IntegrityError；真实路径抢占→409） |

第三轮附注：`WARNING [review_round_failed]`（70 请求中 1 个 deadline exceeded）——7 个文件的全文件核心审查第 2 轮超时，覆盖不完整；第四轮（34d15ac）补审。

## ocr 审查（第四轮 commit 34d15ac，1 条 low 处置 + 7/10 超时补审中）

| # | severity | 判定 | 处置 |
|---|---|---|---|
| 1 | low·maintainability | 成立 | 适配器 import 04A 私有符号 `_version_sort_key` 存在跨模块脆弱耦合（registry.py 重命名/改签名会静默破坏适配器）。**不修，归属 04A**：让 04A 暴露 `version_sort_key` 公有别名属 04A 模块 owner 的范围（DESIGN §11.2 分工，03B 不得擅改 04A 类型）；已把该建议作为共享信息交协调者，若采纳由 04A 波次落公有别名、03B 跟随改 import。模块 docstring 已声明复用意图与原因 |

第四轮附注：`Review partially complete: 1 finding; 7 of 10 selected item(s) failed`（1/53 请求 deadline exceeded）——以下 7 个文件的全文件审查未覆盖（超时失败，非干净通过）：`alembic/versions/20261008_02_ingest_config.py`、`app/api/__init__.py`、`app/api/ingest_submissions.py`、`app/models.py`、`app/services/bootstrap.py`、`app/services/ingest_service.py`、`app/services/source_service.py`。已启动批2 补审（--exclude 已审过的 scanner×2 + scene_capability_read，日志 ocr-34d15ac-batch2.log）。

## ocr 审查（第四轮批2 补审，运行中）

- proc_f235034015d7，7 文件，意见核实后补记。

## 依赖与共享信息

- 消费 03A 终版 67f9f4c 的 `resolve_effective_config`/`CapabilityRead`/`SceneConfigError`/`validate_relative_path`/限额函数（未改 03A 文件）。
- 消费 04A 终版 a23c541 的 `CapabilityRegistry`/`SceneCapability`/`effective_params`/`_version_sort_key`（未改 04A 文件；适配层在 03B）。
- **未动 `app/schemas/__init__.py`**（§11.3：schemas 总导出由协调者合入时更新）。
- **04A 建议（ocr 第四轮 low，归属 04A，不阻塞 03B）**：`app/scene/registry.py` 的 `_version_sort_key` 是 04A 私有符号但被 03B 适配器（`scene_capability_read.py`）跨模块复用（保持版本排序语义两侧一致，见该模块 docstring）。建议 04A 暴露公有别名 `version_sort_key`（或在 `__all__` 登记），使共享契约显式化；若采纳，03B 只需改 import 行跟随。
- 新 env `SCENE_INGEST_ENABLED`（默认 0）：P0 自动接收开关，建议协调者在 compose 模板 / 部署文档登记（不属本任务文件锁范围）。

## 残余风险 / 待确认

- MySQL 8.4 实测未跑（P0 仅 SQLite）。已规避的 MySQL 坑：relative_path 1024 字宽不入
  唯一索引（path_claim_key sha256 摘要）也不入复合索引（删 profile_path 索引，避 1071）。
  建议协调者在隔离 MySQL 库补一次 alembic upgrade 实测，与 T-03/T-04 同口径。
- `purpose_schedule_event` 唯一消费键含可空 `capability_version`/`capability_config_hash`：MySQL 唯一约束对 NULL 不生效，self_built 行靠 `event_id` 唯一 + 05 运行身份幂等兜底（§3.2 双保险），05 消费时需按此实现。
- 新 profile（incoming_prefix 非空）匹配到提交后，Phase0 run 仍由 register_source 既有逻辑创建；scene_slice 任务不在此处创建（归 05 消费事件），self_built 保持既有直建——与派单"不执行推理、事件交 05"一致。

## 下一步

等待协调者验收。建议可解锁：TASK-05（用途事件消费 + 任务创建）、TASK-06A（冻结对账）对 03B 的依赖在本 commit 接受后满足（事件契约 purpose-schedule-event/v1 生产侧就绪）。
---
## attempt-2 返修指令（协调者追加，2026-10-09 00:5x）

协调者代跑了 34d15ac 的 7 文件核心 OCR（你第四轮该批超时 0 覆盖），共 7 条。对照 MySQL 8.4 真实迁移裁决后：

**3 个 critical = 误报（不返修，证据如下）**：
- critical 1/2（TEXT 列 server_default 报 1101）：协调者在 MySQL 8.4 隔离库跑 `alembic upgrade head` 成功落地 20261008_02，general_log 抓取的真实执行 DDL 为 `default_purposes_json TEXT NOT NULL`（**无字面量默认值**）——alembic 迁移上下文渲染丢弃了 TEXT 字面量 server_default，与 OCR 推断的"保留 DEFAULT '[]' 导致 1101"不符。
- critical 3（BIGINT PK 无 autoincrement 报 1048）：真实 DDL 为 `id BIGINT NOT NULL AUTO_INCREMENT`，且功能验证不显式传 id 插入返回 id=1，自增正常。
- 注：OCR 引用的 9273d28 历史事故是"迁移保留 server_default 导致 1101"，本次真实路径未保留，故不复发。但 server_default 写了却不生效属死代码，建议（非阻塞）删除这 4 处 TEXT server_default 并留注释说明 MySQL 8.4 不接受 TEXT 字面量默认值、由 model Python default 供值。

**4 条需 owner 核实返修**（对照代码确认是否属实，属实则修，不属实给反证）：
- [bug · high] ingest_service.py bind 路径：`_find_pending_submission` 复用"任何持占位的 PENDING_INPUT 提交"未按 source 过滤——残留 system-default 行会让新 bag 绑到旧 bag 的 effective_config_hash 出事件，且用户后续显式提交撞 409 PATH_CLAIMED。
- [bug · high] 同流程"建 PENDING system 提交→立即绑定"把 system-default 行永久留在 PENDING_INPUT 且占位未释放（OCR 给了具体 patch：绑定后 `submission.path_claim_key = None`）。
- [other · medium] create_submission 处 `except Exception` 捕获面过宽，把 JSONDecodeError/ValueError/注册表加载失败等服务端故障误报 422（建议收窄 `except SceneConfigError`，与 _ensure_system_submission 写法一致）。
- [other · medium] bind_ingest_for_registration 处同款 except Exception 过宽，同修。

要求：4 条逐条对照代码判定"属实/误报"并记录理由；属实的修 + 加回归测试（至少覆盖 high 1/2 的"残留 system 行不抢绑"场景）；全量测试过；回执本文件补 attempt-2 段，报 REVIEW_PENDING。OCR 由协调者代跑（错峰）。
