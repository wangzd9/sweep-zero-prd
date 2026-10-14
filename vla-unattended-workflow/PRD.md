# VLA 数据集无人化工作流与 Agent 监督平台 PRD

**版本**：v1.0  
**状态**：方案设计稿  
**日期**：2026-09-09  
**关联项目**：`vla_dataset_builder`、`proj_dataset_builder`、`proj_nvidiadata_builder`、`rosbag-catalog`  
**详细流程参考**：`/home/wang/work/dataset_build/dataset_processing_analysis.md`

当前实施优先级：`vla_self_dataset_pipeline_v1_prd.md` 与 `vla_nvidia_dataset_pipeline_v1_prd.md` 是单台 A100 场景下的 V1 实施基线，定义实际队列、Worker、资源租约、路径和验收边界；本文保留为后续无人化和 Agent 能力的长期设计。三份文档冲突时，以两份路线 V1 PRD 为准。

> **当前状态校准（2026-09-21）**：本文描述的是目标态，不应视为当前已完整实现的“无人值守”能力。当前已落地的是自建路线的 NAS 扫描、处理机宿主机 Phase0、A100 Phase1/Phase3、质量基础校验、DatasetFrame 导入、manifest、重试边界、NAS final 发布和页面追踪；业务质量门禁的动态相机/NPY shape/覆盖率规则、完整质量报告与发布阻断、在途故障恢复演练、主动告警、完整血缘图以及 NVIDIA 全链路仍有缺口或处于暂停状态。当前事实以 `rosbag-catalog/HANDOFF.md`、`docs/project-status.md` 和自建 V1 PRD 为准。

## 1. 文档目的

本文定义一套从数据发现、备份、处理、语义标注、质量校验到数据集发布的无人化工作流。

系统需要同时支持：

1. 自建 ROS 2 rosbag 数据集；
2. NVIDIA PhysicalAI 开源数据集；
3. 数据管理平台所在内网机器执行 Phase0；
4. A100 执行 Phase1、Phase3、模型推理和语义标注；
5. 后续可由平台机上的 Agent/Skill 监督任务、分析失败并决定安全重试；
6. 数据库记录原始数据、处理任务、产物、数据血缘、版本和发布状态；
7. 正常数据从进入约定目录到最终发布全程不需要人工点击或执行命令。

“无人化”不是允许大模型任意执行命令。确定性编排器负责状态推进，大模型只在受控工具和明确权限范围内诊断、重试、调参和生成报告；无法证明安全的异常进入隔离队列，不污染正式数据集。

## 2. 背景与现状

### 2.1 当前实际链路

自建数据：

```text
车端采集 ROS 2 bag
  -> 同一块硬盘复制到 NAS 原始区
  -> 平台机 Scanner 发现 NAS 新增稳定数据
  -> 平台机自动复制并执行 Phase0
  -> Phase0 结果上传 A100
  -> A100 执行 Phase1
  -> A100 执行导航、场景描述、模型处理
  -> 最终结果备份 NAS，并在 A100 供训练使用
```

NVIDIA 数据：

```text
HuggingFace PhysicalAI
  -> A100 下载和解压
  -> Phase1 严格时间同步、图片和轨迹生成
  -> 规则导航、VLM 复核、导航文本和场景描述
  -> 教师推理、CoT/logits 和训练数据集
```

### 2.2 已有能力

- 自建 `run_phase0.sh`、`run_phase1.sh` 已有 wrapper、done 文件和 resume；
- `upload_and_run_phase1.sh` 已有校验、上传、远端锁和结果检查；
- 自建 Phase3 已有导航和场景描述脚本，CoT 仍是 TODO；
- NVIDIA 路线已有下载、解压、严格索引、规则导航、VLM 复核和场景描述；
- `rosbag-catalog` 已有 FastAPI、Jinja2、SQLAlchemy、MySQL、NAS scanner、Bag/车辆/标签检索；
- `rosbag-catalog` 前后端已具备 Docker Compose 镜像化基础。

### 2.3 当前问题

- 不同机器依赖人工复制、运行脚本和检查日志；
- 没有统一任务 ID，NAS、平台机、A100 上的副本关联不稳定；
- done 文件只表示脚本步骤，不能代表数据质量合格；
- 重试依赖人判断，容易重复计算或覆盖正确结果；
- CPU、GPU、网络和 VLM 任务没有统一资源调度；
- 导航和场景描述已生成，但不一定进入训练 loader；
- 代码版本、配置和模型版本没有完整进入数据血缘；
- 多人并发可能处理同一个 bag 或写同一个结果目录。

## 3. 产品目标

### 3.1 核心目标

1. 新增自建 bag 满足稳定性条件后，自动完成登记、NAS 关联、Phase0、上传、Phase1、Phase3、校验和发布；
2. NVIDIA 新 chunk 自动完成下载后续处理和发布；
3. 正常任务零人工介入，失败任务由规则引擎优先处理、Agent 辅助诊断和重试；
4. 任意最终样本可追溯到原始数据、处理步骤、代码、配置、模型、主机、日志和所有产物；
5. Phase0 与 A100 后续流程由平台机统一 Worker 调度，后续可扩展更多执行机；
6. 重复扫描、重复 API 请求、进程退出和机器断电不会制造重复记录或破坏正确结果；
7. 正式数据只能由通过质量门禁的不可变版本发布。

### 3.2 量化指标

| 指标 | MVP 目标 | 稳定期目标 |
|---|---:|---:|
| 正常自建数据零人工完成率 | >= 90% | >= 98% |
| 可重试故障自动恢复率 | >= 80% | >= 95% |
| 重复任务/重复产物率 | 0 | 0 |
| 数据血缘完整率 | 100% | 100% |
| 正式发布结果引用文件存在率 | 100% | 100% |
| 任务状态可恢复时间 | <= 10 分钟 | <= 2 分钟 |
| Agent 非白名单操作次数 | 0 | 0 |

## 4. 非目标

一期不做：

- 重写 Phase0/Phase1 核心算法；
- Kubernetes 或复杂大数据平台；
- NAS 全量历史数据重新治理；
- 将 DB3、图片或 NPY 正文存入数据库；
- 允许大模型获得任意 Shell、数据库写权限或删除权限；
- 自动修改算法代码并直接上线生产；
- 在未定义训练 schema 前宣称导航、描述和 CoT 已进入训练；
- 因追求零人工而无限重试无效数据。

## 5. 用户与使用场景

### 5.1 角色

- 数据采集人员：只负责结束采集并把硬盘内容复制到约定入口；
- 数据工程师：维护流水线版本、配置和质量规则；
- 算法工程师：使用已发布数据集，查看导航、描述和轨迹质量；
- 平台运维：维护控制面、数据库、NAS、平台机 Phase0 Worker、A100 Worker 和凭据；
- Agent Supervisor：后续运行在平台机或受控服务中，使用 Skills 观察任务、诊断异常并执行允许的恢复动作。

### 5.2 理想操作体验

采集人员只需要将原始 rosbag 复制到 NAS raw 入口。Scanner 自动发现完整 bag，平台机完成后续流程。用户可以在数据管理界面看到：

```text
原始数据已备份 NAS
平台机 Phase0 已完成
A100 Phase1 已完成
导航/描述已完成
质量门禁通过
NAS/A100 已发布
```

失败时界面显示失败原因、Agent 诊断、已尝试动作和下一次重试时间，不要求用户登录机器翻日志。

## 6. 总体架构

```text
                         Control Plane
                +-----------------------------+
                | rosbag-catalog Backend/API  |
                | Scheduler + Policy Engine   |
                | MySQL + Web UI              |
                +----------+------------------+
                           |
              lease/API/event/heartbeat
                 +---------+---------+
                 |                   |
        +--------v---------+   +-----v------------+
        | Platform Worker  |   | A100 Worker      |
        | NAS Scanner      |   | Phase1/Phase3    |
        | Phase0 Runner    |   | VLM/Inference    |
        | Transfer Agent   |   | Publisher        |
        | Agent Supervisor |   | Validator        |
        +-----+------------+         |
              |                      |
      local Phase0 work disk     A100 result area
              |                         |
              +---------> NAS raw/final+
```

### 6.1 控制面

基于 `rosbag-catalog` 扩展：

- FastAPI 提供任务、Worker、产物和 Agent 决策接口；
- SQLAlchemy 维护数据模型；
- 一期继续使用现有 MySQL，避免先做数据库迁移；
- 使用数据库任务表和租约锁实现队列，无需一期引入 Redis；
- Web 页面提供数据血缘、任务时间线、质量报告和异常队列；
- 前后端和数据库可由 Docker Compose 管理；
- 控制面不在 HTTP 请求线程执行长任务；Phase0 Worker 和 Orchestrator 负责异步处理与传输。

### 6.2 平台机 Phase0 Worker

运行在数据管理平台所在内网机器，负责：

- 领取 NAS Scanner 创建的 `PHASE0_QUEUE` 任务；
- 将 NAS raw bag 复制到本地任务目录并校验；
- 调用现有 `run_phase0.sh`；
- 校验 Phase0 结果、生成 manifest 并上传 A100 staging；
- 通过 Backend 回写状态、指标和产物；
- 使用独立工作目录和资源租约，支持断点恢复。

### 6.3 A100 Worker

运行在 A100 现有处理环境，职责：

- 领取 Phase1/Phase3/NVIDIA 任务；
- 调用现有 builder 脚本；
- 调用 Qwen vLLM 服务；
- 执行结果校验和数据集打包；
- 将正式结果发布到 A100 使用区和 NAS final；
- 上报日志摘要、指标和产物 manifest。

### 6.4 文件系统与数据库边界

| 位置 | 保存内容 |
|---|---|
| NAS raw | 原始 rosbag/NVIDIA 原始归档，不修改 |
| 平台机工作盘 | 当前任务原始副本、Phase0、中间结果和日志 |
| A100 incoming | 尚未校验的 Phase0/任务输入 |
| A100 work | Phase1/Phase3 中间结果 |
| A100 published | 训练/推理使用的不可变版本 |
| NAS final | 最终数据集版本备份 |
| MySQL | ID、路径、状态、指标、血缘、manifest 摘要，不存大文件正文 |

## 7. 端到端工作流

### 7.1 自建数据无人化流程

```text
1. NAS Scanner 发现 metadata.yaml + db3
2. 连续两次确认文件数和大小稳定
3. 生成 fast_fingerprint、source_manifest 并由 Backend 创建 source_id
4. Backend 幂等创建 Phase0 job
5. 平台机 Phase0 Worker 领取租约
6. 从 NAS 断点复制到平台机本地工作目录并校验
7. 执行 run_phase0.sh
8. 校验 6 路 MP4、FPS、JSON 和 done 文件
9. 上传 Phase0 到 A100 .incoming
10. A100 执行 Phase1、导航、描述和最终校验
11. 生成 dataset_version 和 output_manifest
12. 发布 A100 immutable 目录
13. 复制最终版本到 NAS final
14. 批量导入逐帧索引
15. 校验成功后标记 PUBLISHED
16. 按保留策略清理平台机/A100 work 中间文件
```

### 7.2 NVIDIA 数据无人化流程

```text
1. 控制面登记待处理 chunk
2. A100 Worker 执行 download_physicalai.py
3. 校验下载文件清单
4. 执行 unzip_data_files.py，禁止自动删除 ZIP
5. 执行 infer_data_gen.py
6. 校验 inference_index_strict.csv 和引用
7. 执行 navi_gen_rule.py
8. 执行 navi_gen_llm.py
9. 执行 navi_gen_route.py / nav_gen_final.py
10. 执行 clip_llm_comprehension.py
11. 生成版本、质量报告和 manifest
12. 将 A100 原始下载数据备份到 NAS，校验后再发布 NVIDIA 任务
```

### 7.3 训练数据发布

正式发布目录必须版本化：

```text
<dataset_type>/<source_id>/<pipeline_version>/<dataset_version>/
├── dataset_manifest.json
├── quality_report.json
├── checksums.sha256
└── data/
```

正式目录只读，不允许就地覆盖。重跑产生新的 `dataset_version`。数据管理界面可切换当前推荐版本，但保留旧版本血缘。

## 8. ID、指纹与数据血缘

### 8.1 ID 定义

| ID | 粒度 | 生成规则 |
|---|---|---|
| `source_id` | 原始 bag/clip | UUID；首次登记生成 |
| `source_fingerprint` | 原始内容 | metadata 规范化内容 + 文件名/大小等哈希 |
| `clip_id` | 切片 | 原始 clip 名或 NVIDIA UUID |
| `sample_id` | 帧样本 | dataset_type/source_id/clip_id/frame_id |
| `pipeline_run_id` | 一次全链执行 | UUID |
| `step_run_id` | 一次步骤执行 | UUID |
| `artifact_id` | 一个产物 | UUID |
| `dataset_version_id` | 一次正式发布 | UUID/语义版本 |

### 8.2 快速指纹

自建 bag 默认不对整个 DB3 每次做全量 SHA256，使用：

```text
SHA256(
  metadata.yaml 规范化内容
  + DB3 相对路径排序
  + 每个 DB3 文件大小
  + 起始时间、持续时间、消息数
)
```

发生候选冲突时由后台低优先级任务计算分块或完整 SHA256，并缓存结果。

### 8.3 血缘边

数据库必须能表达：

```text
source -> phase0 artifact -> phase1 artifact
       -> navigation artifact
       -> description artifact
       -> dataset version
       -> training/inference run
```

任何产物必须记录父产物、生成步骤、代码版本、配置哈希和模型版本。

## 9. 状态机

### 9.1 Source 状态

```text
DISCOVERED -> WAITING_STABLE -> VALIDATING -> READY
READY -> PHASE0_QUEUE -> COPYING_TO_PLATFORM -> PHASE0_RUNNING
PHASE0_RUNNING -> PHASE0_DONE -> A100_PROCESSING
READY -> BACKING_UP -> NAS_READY
任何状态 -> QUARANTINED / INVALID
```

### 9.2 Job 状态

```text
PENDING -> LEASED -> RUNNING -> VALIDATING -> SUCCEEDED
                    |              |
                    v              v
              RETRY_WAIT <---- FAILED_RETRYABLE
                    |
                    v
              FAILED_FINAL / QUARANTINED
```

### 9.3 数据集版本状态

```text
DRAFT -> QUALITY_CHECKING -> READY_TO_PUBLISH
-> PUBLISHING -> PUBLISHED
-> DEPRECATED
```

`PUBLISHED` 后不可修改文件。纠错必须产生新版本并将旧版本标记 `DEPRECATED`。

## 10. 数据库设计

一期复用 MySQL 8 和 SQLAlchemy。后续如数据规模或查询需求显著增长，再单独评估 PostgreSQL；数据库选择不应阻塞自动化 MVP。

### 10.1 `data_sources`

```text
id, source_id, dataset_type, source_name
fast_fingerprint, strong_checksum, checksum_status
vehicle_id, collected_at, discovered_at
local_path, nas_raw_path, a100_source_path
file_count, total_bytes, metadata_json
status, created_at, updated_at
```

唯一约束：`dataset_type + fast_fingerprint`。强校验确认内容不同时允许创建冲突版本。

### 10.2 `source_copies`

记录同一原始数据在不同位置的副本：

```text
id, source_id, storage_type, host_id, path
manifest_hash, verification_level, status
last_verified_at, created_at
```

`storage_type`：`NAS_RAW`、`PLATFORM_LOCAL_RAW`、`A100_INCOMING`、`A100_INFER`、`NAS_FINAL`、`NVIDIA_ORIGIN_NAS`。

### 10.3 `pipeline_definitions`

```text
id, name, dataset_type, version
dag_json, default_config_json
git_repository, git_commit
active, created_at
```

### 10.4 `pipeline_runs`

```text
id, pipeline_run_id, source_id, pipeline_definition_id
requested_by, trigger_type, priority
status, current_step, config_json, config_hash
started_at, finished_at, last_error
```

`trigger_type`：`AUTO_DISCOVERY`、`SCHEDULED`、`API`、`RETRY`、`AGENT_RECOVERY`。

### 10.5 `step_runs`

```text
id, step_run_id, pipeline_run_id, step_name
required_capability, assigned_worker_id
status, attempt, max_attempts
lease_token, lease_until, heartbeat_at
command_template_id, input_manifest_hash
output_manifest_hash, exit_code
log_uri, metrics_json, error_class, error_summary
started_at, finished_at
```

唯一约束建议：

```text
pipeline_run_id + step_name + attempt
```

### 10.6 `workers`

```text
id, worker_id, worker_type, host_name
capabilities_json, environment_fingerprint
cpu_count, memory_bytes, disk_free_bytes
gpu_json, status, current_load
agent_enabled, last_heartbeat_at
```

能力示例：

```text
self.phase0.nvdecode
self.phase1
self.phase3.nav
vlm.qwen
nvidia.preprocess
nas.transfer
```

### 10.7 `artifacts`

```text
id, artifact_id, source_id, pipeline_run_id, step_run_id
artifact_type, storage_type, host_id, path
parent_artifact_id, file_count, total_bytes
manifest_hash, checksum_uri, schema_version
status, created_at
```

### 10.8 `dataset_versions`

```text
id, dataset_version_id, dataset_type, source_id
pipeline_run_id, version, status
sample_count, clip_count
quality_score, quality_report_uri
a100_path, nas_final_path
published_at, deprecated_at
```

### 10.9 `agent_decisions`

```text
id, decision_id, step_run_id, agent_id
model_name, model_version, prompt_template_version
evidence_json, diagnosis, proposed_action
skill_name, skill_args_json
risk_level, policy_result, execution_status
result_summary, created_at
```

该表用于审计：大模型看到了什么、为什么判断、调用了哪个 Skill、是否执行成功。

### 10.10 `quality_checks`

```text
id, artifact_id, check_name, check_version
status, observed_value, threshold
details_json, checked_at
```

## 11. 任务领取与并发控制

### 11.1 数据库租约队列

Worker 通过 API 领取符合自身 capability 的任务：

1. 控制面在事务中选择一条 `PENDING/RETRY_WAIT` 任务；
2. 设置 `LEASED`、`assigned_worker_id`、随机 `lease_token` 和 `lease_until`；
3. Worker 每 30 秒 heartbeat；
4. 租约过期且无 heartbeat 时回收任务；
5. 完成/失败接口必须携带 `lease_token`，防止旧 Worker 覆盖新结果。

### 11.2 幂等键

步骤幂等键：

```text
source_id + pipeline_version + config_hash + step_name
```

存在已校验成功产物时直接复用。强制重跑必须创建新的 `pipeline_run_id` 或版本，不能覆盖旧产物。

### 11.3 目录锁

数据库租约之外，本机仍需使用文件锁：

```text
<work_dir>/.pipeline.lock
```

数据库防止多机重复领取，文件锁防止同机两个进程写同一目录。

## 12. 平台机 Agent Supervisor 与 Skill 设计

### 12.1 定位

Agent 不是主调度器。主调度器根据 DAG 和状态机推进任务；Agent 只在以下事件触发：

- 步骤失败且规则库无法唯一决定恢复动作；
- 输出校验出现异常但未达到直接隔离条件；
- 性能明显低于同类任务基线；
- VLM 响应格式异常；
- 重试前需要从日志和环境中综合判断；
- 每个 pipeline run 完成后生成质量总结。

### 12.2 Skill 原则

每个 Skill 是一个固定输入输出、最小权限的工具，不向模型暴露通用 Shell。Skill 必须声明：

```text
name, version, purpose
allowed_paths, allowed_commands
input_schema, output_schema
timeout, resource_limit
risk_level, requires_policy
```

### 12.3 MVP Skills

| Skill | 只读/写入 | 作用 |
|---|---|---|
| `inspect_job_status` | 只读 | 查询数据库状态、attempt、租约和依赖 |
| `read_step_log` | 只读 | 读取当前步骤受限行数的日志 |
| `inspect_environment` | 只读 | GPU、磁盘、ffmpeg、Python、网络检查 |
| `validate_rosbag` | 只读 | 检查 metadata、DB3 清单和 topic |
| `validate_phase0` | 只读 | 检查 6 路 MP4、FPS、JSON、done |
| `validate_phase1` | 只读 | 检查索引、图片和 NPY 引用 |
| `validate_vlm_output` | 只读 | 检查 content、JSON 和 range 格式 |
| `classify_failure` | 只读 | 用规则提取 OOM、超时、缺文件等错误 |
| `retry_step` | 受控写 | 仅将允许的步骤放回 RETRY_WAIT |
| `adjust_runtime_config` | 受控写 | 只允许降低并发、延长超时、换空闲 GPU |
| `restart_local_worker` | 受控写 | 只重启本机 Worker 服务 |
| `quarantine_job` | 受控写 | 隔离任务，禁止发布 |
| `generate_incident_report` | 写报告 | 生成结构化故障报告 |

### 12.4 禁止 Skills

一期禁止提供：

- 任意 Shell；
- `rm`、覆盖正式目录、修改原始数据；
- 直接执行 SQL；
- 修改代码、Git push、部署生产；
- 获取/输出明文密码；
- 任意 SSH 到服务器；
- 绕过控制面直接标记任务成功。

### 12.5 Agent 决策输出协议

Agent 必须返回结构化 JSON：

```json
{
  "diagnosis": "GPU OOM during camera extraction",
  "confidence": 0.94,
  "evidence": ["log line ...", "free memory ..."],
  "action": "adjust_runtime_config",
  "arguments": {"max_bag_workers": 1, "gpu": 1},
  "risk": "LOW",
  "retry_after_seconds": 60,
  "expected_result": "phase0 resumes from incomplete camera step"
}
```

Policy Engine 校验 action、参数范围、attempt 数和目录后才执行。模型文本不能直接成为命令。

### 12.6 Agent 重试策略

| 故障 | 自动动作 | 最大次数 | 超限动作 |
|---|---|---:|---|
| 网络/rsync 中断 | 断点续传 | 5 | 延迟队列 |
| VLM 超时/连接拒绝 | 健康检查后重试 | 3 | 隔离语义步骤 |
| GPU OOM | 降并发/换 GPU | 2 | 隔离 |
| 磁盘空间不足 | 清理允许的缓存或换工作盘 | 1 | 隔离 |
| Worker 掉线 | 租约过期后换 Worker | 3 | 告警 |
| 缺相机/topic | 不重试 | 0 | INVALID |
| 地图缺失 | 不使用默认地图 | 0 | QUARANTINED |
| 索引引用缺失 | 尝试从上一阶段重建 | 1 | QUARANTINED |
| CoT TODO | 不执行伪完成 | 0 | SKIPPED_UNIMPLEMENTED |

### 12.7 Agent 记忆与知识来源

Agent 可读取：

- 当前任务日志和 manifest；
- 已批准的故障知识库；
- `dataset_processing_analysis.md`；
- 当前 pipeline/version 的运行手册；
- 同类型历史任务的聚合指标。

Agent 不把自然语言会话当作唯一记忆。所有有效经验必须转成版本化规则、Skill 或知识条目后才影响生产。

## 13. 确定性校验与质量门禁

### 13.1 Source 门禁

- `metadata.yaml` 可解析；
- 一个或多个 `.db3` 非空；
- 文件数和大小稳定；
- 必需 topic/消息类型存在；
- 指纹与数据库无冲突；
- NAS raw 副本校验完成。

### 13.2 Phase0 门禁

- 预期 done 文件状态为完成；
- 每个 clip 有规定的 6 路相机；
- MP4 非空且可 ffprobe；
- 实际平均 FPS 达到配置阈值；
- 视频解码帧数与输入帧清单一致；
- `ins.json`、`sample.json`、Planning 状态符合策略。

### 13.3 Phase1 门禁

- `dataset_index.csv`/`inference_index_strict.csv` 可解析且非空；
- 每行所有模型必需图像存在；
- history/future NPY 存在，shape 和 dtype 合规；
- 相机与 ego 同步误差达标；
- Planning 可用率、无效帧率在阈值内；
- reduce 前后样本数和删除文件数可解释。

### 13.4 Phase3 门禁

- 自建导航必须有明确地图版本；
- navigation 覆盖率达到数据类型阈值；
- VLM `content` 非空，JSON/文本格式正确；
- range 的 frame ID 位于索引范围内；
- NVIDIA `final_navi` 不为空且与主索引 frame_id 对齐；
- CoT 未实现时明确标记，不伪造完成。

### 13.5 发布门禁

- 所有必选步骤成功；
- `quality_report.json` 无阻断错误；
- manifest 和 checksum 完整；
- A100/NAS 路径处于 incoming，未覆盖正式目录；
- 发布后抽样重新打开图片、CSV 和 NPY；
- 数据库状态与文件系统状态一致。

## 14. API 设计

### 14.1 Source

```text
POST /api/v1/sources/discover
GET  /api/v1/sources/{source_id}
POST /api/v1/sources/{source_id}/copies
POST /api/v1/sources/{source_id}/verify
```

### 14.2 Pipeline

```text
POST /api/v1/pipeline-runs
GET  /api/v1/pipeline-runs/{run_id}
GET  /api/v1/pipeline-runs/{run_id}/timeline
POST /api/v1/pipeline-runs/{run_id}/cancel
POST /api/v1/pipeline-runs/{run_id}/retry
```

### 14.3 Worker

```text
POST /api/v1/workers/register
POST /api/v1/workers/{worker_id}/heartbeat
POST /api/v1/jobs/lease
POST /api/v1/jobs/{step_run_id}/start
POST /api/v1/jobs/{step_run_id}/heartbeat
POST /api/v1/jobs/{step_run_id}/complete
POST /api/v1/jobs/{step_run_id}/fail
```

### 14.4 Artifact/Quality

```text
POST /api/v1/artifacts/register
POST /api/v1/artifacts/{artifact_id}/quality-checks
GET  /api/v1/artifacts/{artifact_id}/lineage
POST /api/v1/dataset-versions/{id}/publish
```

### 14.5 Agent

```text
POST /api/v1/agent/incidents
POST /api/v1/agent/decisions
GET  /api/v1/agent/decisions/{id}
POST /api/v1/agent/decisions/{id}/execute
```

所有写接口使用幂等键。文件上传不经过 API，只上传 manifest、路径和摘要。

## 15. 数据管理界面

### 15.1 数据源列表

显示：来源类型、车辆、采集时间、标签、NAS 状态、最新流水线状态、当前版本和质量分数。

### 15.2 数据源详情

两级视图：

1. bag/chunk/批次级；
2. clip、原始文件和逐帧索引级。

同时展示 NAS、平台机本地、A100 副本和 source 指纹状态，并展示逐帧索引统计与检索入口。

### 15.3 任务时间线

```text
发现 -> 稳定 -> NAS -> 平台机复制 -> Phase0 -> 上传 -> Phase1
-> 导航 -> 描述 -> 校验 -> 发布
```

每个节点可查看耗时、Worker、attempt、日志、输入输出和 Agent 决策。

### 15.4 异常队列

显示：错误分类、影响数据、Agent 诊断、重试次数、隔离原因。正常运营不要求人工逐条处理；隔离数据不会阻塞其他任务。

## 16. 配置与版本管理

以下配置必须版本化并计算 `config_hash`：

- 相机配置；
- Phase0 FPS、GPU 和删除策略；
- Phase1 同步阈值、采样和 reduce；
- 地图版本和导航文本表；
- VLM endpoint 逻辑名、模型版本、prompt 模板；
- Agent 模型、Skill 版本和策略；
- 质量门禁阈值。

密码和 token 不进入配置 JSON、manifest、日志或 PRD，使用环境文件或 Secret Store 注入。

## 17. 日志、指标和告警

### 17.1 日志

每个 `step_run_id` 单独记录：

```text
stdout.log
stderr.log
runner.jsonl
agent_decisions.jsonl
```

日志进入本地文件和控制面摘要。大日志不直接存数据库。

### 17.2 指标

- 各阶段耗时和吞吐；
- 每 GB/每 clip 处理时间；
- GPU 利用率、显存峰值、CPU、内存和磁盘 IO；
- 过滤帧数和原因；
- Planning/navigation/description 覆盖率；
- VLM 调用耗时、重试率和格式失败率；
- Worker 在线率和租约回收次数；
- Agent 诊断准确率和恢复成功率。

### 17.3 告警

仅对系统性问题告警：控制面不可用、NAS 不可用、A100 全部 Worker 离线、队列持续增长、连续多任务同类失败、正式产物 checksum 不一致。单个坏 bag 进入隔离，不应叫醒运维。

## 18. 安全和权限

- 平台机 Phase0 Worker、A100 Worker 使用独立身份和短期 token；
- NAS raw 账号只读，发布账号只写 incoming/final 指定根目录；
- A100 Worker 不向平台机 Phase0 Worker 暴露通用远程 Shell；
- Agent Skill 使用 allowlist、参数 schema、超时和目录沙箱；
- 正式目录禁止覆盖和删除；
- API、Agent、发布动作记录审计日志；
- 数据库不保存服务器明文密码；
- 日志自动脱敏密码、token、SSH 命令参数；
- 破坏性清理只由固定 retention job 执行，不提供给 Agent。

## 19. 部署方案

### 19.1 控制面 Docker Compose

```text
frontend
backend
mysql
scheduler
```

一期可让 scheduler 与 backend 共用代码镜像、使用不同启动命令。数据库必须使用持久化卷和定期一致性备份。

### 19.2 平台机 Phase0 Worker

以 Compose 独立服务或 systemd 服务运行：

```text
vla-phase0-worker.service
vla-agent-supervisor.service
```

处理算法继续使用平台机宿主机 Conda/CUDA 环境。Worker 本身可以打包为 Python wheel 或轻量容器，但不得隔离掉所需 ROS/`xlbp_parse` 运行环境。

### 19.3 A100 Worker

以独立服务运行，使用 A100 已验证环境和固定代码版本。一个 Worker 可以声明多个 capability，但同一 GPU 同时允许的任务数由资源策略控制。

## 20. 实施阶段

### 20.1 第一阶段：确定性无人化 MVP

交付：

- 数据库新增 source/run/step/worker/artifact/quality 表；
- NAS Scanner、平台机 Phase0 Worker 注册、租约和 heartbeat；
- 自建 Phase0 wrapper 接入；
- A100 Phase1/Phase3 Worker 接入；
- manifest、幂等、质量校验和版本化发布；
- NAS/A100 双端发布；
- 基础任务时间线页面。

验收必须用一份真实新 bag 完成零点击端到端发布。

### 20.2 第二阶段：Agent 监督与自动恢复

交付：

- 只读诊断 Skills；
- 低风险重试和调参 Skills；
- Policy Engine；
- Agent 决策审计；
- OOM、网络、VLM、磁盘等故障演练；
- 自动故障报告。

### 20.3 第三阶段：NVIDIA 路线和训练协议

交付：

- NVIDIA chunk DAG；
- 两条路线统一 sample schema；
- navigation/description 显式接入 loader；
- 教师推理和 CoT/logits 产物血缘；
- 数据集版本选择和训练消费记录。

### 20.4 第四阶段：闭环优化

交付：

- 基于历史指标自动选择并发和 Worker；
- 自动质量抽样；
- 标签模型版本对比；
- 训练结果反馈到数据筛选；
- 经过评审后将稳定 Agent 决策固化为确定性规则。

## 21. MVP 验收标准

### 21.1 自建路线

1. 将一个新 bag 复制到 NAS raw 入口后，无需人工运行命令；
2. 自动确认稳定并生成同一 `source_id`；
3. NAS raw 自动复制到平台机本地工作目录；
4. 平台机 Phase0 自动执行并通过 6 路相机/FPS 门禁；
5. A100 Phase1 自动执行；
6. 主索引的图片和 NPY 引用 100% 存在；
7. 导航和描述按配置完成；
8. A100/NAS 发布内容和 manifest 一致；
9. 数据库可展示完整血缘和时间线；
10. 断网、Worker 重启后可从最后成功步骤恢复。

### 21.2 Agent

1. 模拟网络中断后自动断点续传；
2. 模拟 VLM 超时后按策略重试并记录证据；
3. 模拟 GPU OOM 后降低并发或换 GPU；
4. 缺相机时不盲目重试，直接隔离；
5. Agent 不能执行任意 Shell、删除文件或覆盖正式目录；
6. 每次 Agent 动作可以从数据库完整审计；
7. Agent 不得绕过质量门禁标记成功。

### 21.3 并发与一致性

1. Scanner 重复发现同一 bag 只产生一个有效 source；
2. 同一步骤同一版本同一时刻只有一个有效租约；
3. 旧 Worker 的延迟回报不能覆盖新 Worker；
4. 重复 API 请求不产生重复 run/artifact；
5. 发布失败不出现半成品正式目录。

## 22. 测试策略

- 单元测试：指纹、状态机、策略、Skill 参数校验；
- 集成测试：数据库租约、Worker heartbeat、任务回收；
- 样例测试：使用 `/home/wang/work/dataset_build` 两条路线样例；
- 故障注入：断网、磁盘满、进程退出、OOM、VLM 无响应、CSV 损坏；
- 恢复测试：控制面重启、Worker 重启、A100 暂时不可用；
- 安全测试：路径穿越、命令注入、过期 token、Agent 越权；
- 端到端测试：真实 bag 从发现到双端发布。

## 23. 关键产品决策

1. 一期继续使用现有 MySQL，不把数据库切换作为前置条件；
2. 任务队列先使用数据库租约，不引入 Redis/Kafka；
3. Phase0 在数据管理平台所在内网机器，Phase1 及之后在 A100；
4. NAS 保存原始数据和最终结果，不保存普通中间结果；
5. 确定性编排器拥有状态推进权，Agent 只通过 Skills 提议和执行受控恢复；
6. 正常路径零人工，异常路径自动隔离，绝不为追求“无人”而发布可疑数据；
7. 所有正式结果不可变，重跑生成新版本；
8. 导航、描述和 CoT 只有被统一 schema 和 loader 消费后，才算真正进入训练链路。

## 24. 待确认事项

1. 控制面正式部署主机、MySQL 地址和高可用要求；
2. 平台机 CUDA/驱动和 `xlbp_parse` 授权方式；
3. NAS 到平台机、平台机到 A100 的实际带宽及开放协议；
4. A100 incoming/work/published 的正式根路径和配额；
5. Qwen vLLM 服务由哪台服务器提供、并发上限和 SLA；
6. 自建地图名如何从采集数据可靠获得，是否新增采集侧字段；
7. Phase1 是否全部固定在 A100；当前 V1 固定由 A100 执行；
8. 最终训练统一 schema 的负责人和首个消费模型；
9. 平台机/A100 中间文件保留天数和自动清理容量阈值；
10. Agent 所用模型部署位置、上下文窗口和推理资源预算。
