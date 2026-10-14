# NVIDIA PhysicalAI 数据集自动处理链条 PRD（V1）

**版本**：v1.1  
**状态**：第一版落地方案  
**日期**：2026-09-10  
**前置项目**：`vla_self_dataset_pipeline_v1_prd.md` 已完成并通过验收  
**基础项目**：`rosbag-catalog`、`proj_nvidiadata_builder`  
**代码分析文档**：`/home/wang/work/dataset_build/dataset_processing_analysis.md`

> **当前状态校准（2026-09-21）**：本文继续保留为 NVIDIA PhysicalAI 路线目标态设计，不纳入当前自建路线生产准入。当前仅有部分平台接口和单 clip、非下载测试能力，批量下载、断点恢复、完整 DAG、质量门禁、版本发布和无人值守验收尚未完成。后续恢复开发时，先在 A100 测试根 `/home/xmyf/wzd/` 验证，目录组织严格镜像正式 `/data/nvidia_origin_dataset` 与 `/data/nvidia_infer_dataset`；测试通过后再单独执行正式目录切换。恢复开发前仍须确认 A100 资源、下载策略和验收标准，并以独立 NVIDIA TODO 为任务追踪入口。

## 1. 文档目的

本文设计 NVIDIA PhysicalAI 开源数据集的第一版自动处理链路。它不是独立建设第二套平台，而是在自建数据集 V1 已实现的前提下，复用已有数据管理平台、Backend、MySQL、VLA Orchestrator、A100 SSH 执行能力、任务租约、日志、重试和产物血缘机制，增加 NVIDIA 数据集任务类型。

本文件与 `vla_self_dataset_pipeline_v1_prd.md` 共同作为当前 V1 实施基线。`vla_unattended_workflow_prd.md` 是长期概念方案；若其资源调度、Worker 或执行位置描述与本文件冲突，以两份路线 V1 PRD 为准。

第一版要把当前需要人工依次执行的流程：

```text
选择 chunk
-> 下载
-> 解压
-> Phase1 预处理
-> 导航生成和 VLM 复核
-> 场景描述生成
-> 结果校验
-> 原始数据备份到 NAS
```

收口为：

```text
用户在数据管理页面指定 chunk、原始数据回传开关和最终结果回传开关
-> 系统拆分并创建任务
-> Orchestrator 按自建/NVIDIA 两条逻辑队列在 A100 调度
-> 页面持续显示状态
-> 自动生成可用于训练的最终结果
-> 建立数据源、chunk、clip、步骤和产物之间的血缘
```

## 2. 前置条件与复用边界

本 PRD 不重复建设自建数据集 V1 已有能力。开发启动前，以下能力必须已存在且通过验收：

1. `rosbag-catalog frontend`、`backend`、MySQL 和 Orchestrator 已在内网管理机稳定运行。
2. 只有 Backend 可以访问和修改 MySQL；Frontend 和 Orchestrator 只调用 Backend API。
3. `PipelineRun`、`StepRun`、`Artifact`、`PipelineEvent` 和任务租约模型已经落地。
4. Backend 已具备幂等创建任务、原子领取任务、heartbeat、步骤状态回写、失败重试和取消排队任务的接口。
5. Orchestrator 已能从内网主动通过 SSH 连接唯一一台公网 A100，并能在网络闪断后恢复监控。
6. Backend 任务租约和 A100 远端槽位保护机制已经可用；本项目在此基础上使用分步骤资源池与资源租约，不再依赖整条 pipeline 的单一全局锁。
7. 数据管理页面已有处理任务列表、任务详情、步骤时间线、错误摘要和重试入口。
8. A100 已存在可运行的 `proj_nvidiadata_builder` 环境以及生产数据目录。

本项目复用上述通用能力，只新增：

- `NVIDIA_PHYSICALAI` 数据源类型；
- `NVIDIA_CHUNK` Pipeline 类型；
- NVIDIA chunk 提交和查询界面；
- NVIDIA 数据集身份、chunk 和 clip 元数据；
- NVIDIA 固定执行 DAG；
- A100 NVIDIA pipeline wrapper、校验器和机器可读运行协议；
- NVIDIA 专属的磁盘、网络、VLM 依赖检查；
- NVIDIA 产物和血缘展示。

当本项目接入后，两份 PRD 统一采用“双队列 + 配置化 Worker 池 + 分步骤资源租约”。自建路线的业务流程、状态机和产物协议不变，只需要让其 Worker 在共享步骤申请相同资源。V1 初始容量可以为 1，但不能把单任务限制写成数据库硬约束或固定全局锁。

## 3. 当前事实和约束

### 3.1 数据来源

NVIDIA 路线的原始数据不是 rosbag，而是 Hugging Face 数据集：

```text
nvidia/PhysicalAI-Autonomous-Vehicles
```

当前代码已经包含自动下载脚本：

```text
proj_nvidiadata_builder/scripts/phase0/download_physicalai.py
```

因此用户不需要先手动下载文件。用户只负责选择要处理的 chunk，Orchestrator 在 A100 上触发下载。

### 3.2 A100 目录契约

正式环境自动化必须沿用以下目录，不另建平行的正式数据目录：

```text
/data/nvidia_origin_dataset/data_sample_chunk<N>/
/data/nvidia_infer_dataset/data_sample_chunk<N>/infer/<clip_uuid>/
```

其中：

- `nvidia_origin_dataset` 是 A100 上的工作目录，保存 Hugging Face 下载文件和解压结果；两者在工作目录内可并存，但 NAS 原始备份不复制解压生成的派生文件。
- `nvidia_infer_dataset` 保存 Phase1 及后续导航、描述结果；
- `<N>` 为非负整数 chunk ID；
- `<clip_uuid>` 来自解压后的 egomotion 标签文件。

测试阶段使用 `/home/xmyf/wzd/` 作为隔离根，但只允许使用与正式目录同构的子目录：

```text
/home/xmyf/wzd/data/nvidia_origin_dataset/data_sample_chunk<N>/
/home/xmyf/wzd/data/nvidia_infer_dataset/data_sample_chunk<N>/infer/<clip_uuid>/
```

测试配置必须通过显式环境变量或 approved pipeline config 注入根目录，禁止把测试路径写成脚本默认的正式路径。测试完成切换到 `/data` 时，只允许变更配置和经过验证的部署目录映射，不得改变 chunk、clip、manifest、artifact 和血缘字段的组织语义。

### 3.3 运行资源

1. 只有一台公网 A100 运行自建数据集和 NVIDIA 数据集的后续流程。
2. 下载主要消耗公网带宽和磁盘写入。
3. 解压主要消耗 CPU、磁盘读取和写入。
4. Phase1 使用多进程，主要消耗 CPU、内存和磁盘 I/O。
5. 导航规则步骤主要消耗 CPU。
6. 导航复核和场景描述需要访问 `http://localhost:8002/v1/chat/completions`；该端点当前依赖 A100 上的 SSH 隧道连接另一台模型服务器。
7. 第一版不引入 Kubernetes、Argo 或 Airflow，继续使用现有 Python Orchestrator 和固定 SSH 命令模板。
8. 自建和 NVIDIA 使用两条逻辑队列；每条队列的 Worker 数量配置化，不同任务只有在当前步骤取得对应资源额度时才允许并行。

### 3.3.1 A100 资源复核结论

2026-09-10 对 A100 做只读检查时，机器状态为：

```text
CPU：128 核
内存：约 1.0 TiB，available 约 970 GiB
GPU：8 × NVIDIA A100-SXM4-80GB，检查时基本空闲
/data：7.0 TiB，总可用约 1.9 TiB，使用率 73%
系统负载：约 0.89 / 1.41 / 1.48
```

从当前容量看，同时运行“一个自建数据处理任务”和“一个 NVIDIA 下载任务”是可行的。主要风险不是 GPU，而是：

- 两条 Phase1 同时运行造成 CPU、内存和 NVMe I/O 竞争；
- 解压与 Phase1 同时大量读写 `/data`；
- 两条路线同时调用同一个 VLM 服务造成请求过载；
- NVIDIA 连续下载使 `/data` 剩余容量快速下降。

因此 V1 允许跨队列并行，但不允许两条完整 pipeline 无约束并跑。资源数据只是检查时快照，调度前仍必须执行实时 precheck。

### 3.4 当前代码的重要风险

1. 下载脚本默认目录 `/gpfs-data/mikelee/data` 与生产目录不一致，自动化必须始终显式传入 `/data/nvidia_origin_dataset`。
2. Phase1 默认输出目录 `/data01/mikelee/data` 与生产目录不一致，自动化必须始终显式传入 `/data/nvidia_infer_dataset`。
3. 下载脚本遇网络错误不会完成全流程自动重试，需要 wrapper 补充限次重试和退避。
4. 下载脚本当前使用 `HF_ENDPOINT=https://hf-mirror.com`，实际可用性需要在每次任务前检查。
5. 下载脚本当前没有显式固定 Hugging Face revision，无法保证未来重复运行得到完全相同的上游版本。
6. `unzip_data_files.py --delete` 会删除 ZIP；第一版生产任务禁止使用 `--delete`。
7. `infer_data_gen.py` 默认 `--reduce-on true` 会删除未被最终索引引用的图片；该行为属于生产参数，必须进入配置版本和任务审计。
8. Phase2 当前存在新旧两套导航入口，不能未经确认全部串联执行。
9. VLM 脚本包含固定模型地址和本地端口，需要在运行前做健康检查。
10. 多进程和多线程参数过大时会争抢内存、磁盘和 VLM 服务容量，不能让前端用户任意填写。

## 4. 目标与非目标

### 4.1 V1 目标

- 用户可以在数据管理页面提交单个、离散或连续范围的 chunk 编号；
- Backend 校验、展开、去重后，为每个 chunk 创建独立任务；
- NVIDIA 任务与自建数据集任务使用同一个 Orchestrator，但进入两条独立逻辑队列和可配置 Worker 池；
- Orchestrator 在 A100 自动完成下载、校验、解压、Phase1、导航、描述和最终校验；
- 每一步均有机器可读状态、日志、输入、输出和失败原因；
- 支持服务重启、SSH 闪断、下载失败和步骤失败后的安全恢复；
- 重复提交相同数据版本和 chunk 时不会重复生成并发任务或无条件覆盖已有结果；
- 页面能查看 chunk 下 clip 数量、处理进度、最终路径、质量结果和数据血缘；
- NVIDIA 长时间下载不阻塞自建数据集队列；共享 CPU、磁盘和 VLM 阶段通过可计数资源租约协调；
- 第一轮交付至少完成一个全新 chunk 的端到端自动处理验收。

### 4.2 V1 非目标

- 不自动发现 Hugging Face 新增了哪些 chunk；
- 不允许用户在页面填写任意数据集仓库、服务器路径、脚本路径或 Shell 命令；
- 不重写 NVIDIA 数据处理算法；
- 不自动处理全部历史 chunk；
- 不建设多 A100 资源池；
- 不做复杂 DAG 编辑器；
- 不支持同一个 chunk 内按任意 clip 自助编排生产任务；
- 不把 MP4、Parquet、JPG 或 NPY 文件内容写入数据库；
- 不自动删除下载 ZIP、解压数据或正式推理结果；
- 不在第一版解决训练平台如何消费、合并和版本发布全部数据集的问题；
- 不允许绕过质量校验强制发布；
- 不将旧版导航和新版导航同时作为正式结果。

## 5. 用户与使用场景

### 5.1 角色（V1 不实现权限管理）

| 角色 | 职责 |
|---|---|
| 用户 | 提交 chunk、查看任务和结果；V1 不区分用户角色 |
| 运维人员 | 维护配置、处理异常和重试任务；V1 不实现 RBAC |
| Orchestrator | 领取任务、执行步骤、回写状态和登记产物 |
| Backend | 唯一业务状态和数据库写入口 |

### 5.2 核心用户故事

1. 用户输入 `10`，系统自动处理 chunk 10，用户不再登录 A100 手动执行脚本。
2. 用户输入 `1,5,10:15`，页面预览将创建 8 个独立 chunk 任务，确认后批量入队。
3. 用户重复提交已经成功的 chunk，系统直接显示已有结果，并允许管理员选择“复用”或“创建新版本重跑”。
4. 自建数据集紧急任务到达时，可以立即进入独立队列；如果所需计算资源正在被 NVIDIA 占用，则按资源优先级在当前步骤完成后优先获得下一份资源额度，不必等待 NVIDIA 整条 pipeline 完成。
5. 下载过程中网络中断，系统自动退避重试；Orchestrator 重启后从已下载缓存继续，不重新创建任务。
6. 某个 clip 预处理失败时，chunk 任务进入失败或隔离状态，页面展示失败 clip 和原因，不把不完整结果标记为成功。

## 6. 产品架构

```text
用户浏览器
    |
    v
rosbag-catalog Frontend
    |
    v
rosbag-catalog Backend -----------------> MySQL
    ^                                        唯一数据库访问方
    |
    | 领取任务/heartbeat/状态/产物
    |
VLA Orchestrator（内网管理机）
    |
    | SSH 固定命令 + 远程状态查询
    v
公网 A100
├── Hugging Face 下载
├── /data/nvidia_origin_dataset
├── /data/nvidia_infer_dataset
├── proj_nvidiadata_builder
└── localhost:8002 VLM 端点
         |
         | 现有 SSH 隧道
         v
    多模态模型服务器
```

通信原则：

- A100 不主动访问内网 Backend；
- 内网 Backend 不在公网暴露；
- Orchestrator 主动 SSH 到 A100；
- 所有数据库操作收口到 Backend；
- A100 脚本通过本地状态文件和退出码向 Orchestrator 提供状态；
- A100 不持有 Backend Token 和数据库账号。

## 7. 任务提交设计

### 7.1 页面输入

新增“创建 NVIDIA 处理任务”页面，P0 字段如下：

| 字段 | 是否必填 | 说明 |
|---|---:|---|
| 数据集 | 是 | 固定为 `NVIDIA PhysicalAI Autonomous Vehicles`，不可编辑 |
| Chunk | 是 | 支持 `0`、`0,1,5`、`10:15`、`1,5,10:15` |
| Pipeline 配置 | 是 | 从管理员预置配置中选择；配置已固定数据 revision 和处理参数 |
| 场景描述 | 否 | 默认开启；仅管理员可关闭 |
| 原始数据回传 NAS | 否 | 默认开启；关闭后不执行原始下载数据 NAS 备份，仅保留 A100 原始目录和平台索引 |
| 最终结果回传 NAS | 否 | 默认关闭；打开后才同步 Phase1/Phase3 最终结果到 NAS final |
| 优先级 | 否 | 普通用户固定默认值，管理员可以调整 |
| 备注 | 否 | 用于说明用途，不参与命令生成 |

页面必须在正式提交前显示：

```text
输入：1,5,10:15
展开：1、5、10、11、12、13、14、15
将创建：8 个任务
已存在成功结果：2 个
已在排队或运行：1 个
预计新建：5 个
```

### 7.2 参数校验

- chunk ID 只能为非负整数；
- 范围使用左闭右开还是闭区间必须统一。V1 页面和 API 统一定义 `10:15` 为 10 至 15，包含 15，以兼容当前脚本行为；
- 单次提交默认最多展开 30 个 chunk，超过限制由配置控制；V1 不引入管理员权限判断；
- 去除重复编号并按升序保存；
- Backend 不接受路径、URL、Python 参数或 Shell 片段；
- Backend 将用户表达式展开后保存原始表达式和标准化列表，便于审计。

### 7.3 任务粒度

一个 chunk 对应一个独立 `PipelineRun`。批量提交仅创建一个 `SubmissionBatch` 用于页面聚合，不把多个 chunk 放进同一个长任务。

原因：

- 单 chunk 下载体积约 14 GB，处理耗时较长；
- 某个 chunk 失败时不应重跑全部范围；
- 可以对单个 chunk 取消、重试和调整优先级；
- 任务日志、磁盘统计和质量报告可以准确归属；
- 一个 chunk 内约有 100 个有效 clip，clip 作为子实体和指标，不在 V1 中独立进入全局队列。

## 8. 数据身份、幂等与血缘

### 8.1 数据源身份

NVIDIA 数据不使用 rosbag 轻量指纹。其稳定业务身份定义为：

```text
source_key = dataset_repo + dataset_revision + chunk_id
```

示例：

```text
dataset_repo     = nvidia/PhysicalAI-Autonomous-Vehicles
dataset_revision = <解析后的 commit SHA>
chunk_id         = 10
```

要求管理员发布 Pipeline 配置前解析并固定 Hugging Face commit SHA。只保存分支名或 `main` 不足以保证可复现。当前下载脚本未传 `revision`，需要增加该参数并写入 manifest。V1 的普通用户不选择 revision，Backend 从已批准的 Pipeline 配置中取得固定 SHA，保证创建任务时即可确定 `source_key`。

### 8.2 Clip 身份

```text
clip_key = source_key + clip_uuid
```

clip UUID 从以下文件名发现：

```text
/data/nvidia_origin_dataset/data_sample_chunk<N>/labels/egomotion/<clip_uuid>.egomotion.parquet
```

### 8.3 Pipeline 版本

相同 source 可以使用不同参数或代码版本重跑。结果身份定义为：

```text
dataset_version_id = source_id + pipeline_config_version + code_revision + run_sequence
```

数据库必须区分：

- 上游数据版本；
- 处理代码 Git commit；
- Python/Conda 环境标识；
- reduce 参数；
- 导航参数版本；
- VLM 模型标识和 prompt 版本；
- 实际运行次数。

### 8.4 血缘关系

```text
Hugging Face repo@commit
  -> NVIDIA chunk source
      -> downloaded archives/calibration
          -> extracted MP4/parquet
              -> clip source
                  -> inference_index_strict.csv
                  -> camera_images
                  -> history/future NPY
                      -> navi_route.csv
                          -> VLM navigation verdict
                              -> navi_text.csv
                  -> clip_discription_llm.txt
```

Artifact 只保存元数据、路径、大小、摘要和父产物关系，不保存大文件正文。

## 9. 数据模型增量

### 9.1 通用模型扩展

在已实现的通用模型基础上增加或扩展以下字段：

#### PipelineRun

```text
pipeline_type: SELF_BUILT_BAG / NVIDIA_CHUNK
queue_name: SELF_BUILT_QUEUE / NVIDIA_QUEUE
source_id
submission_batch_id
priority
pipeline_config_version
capacity_config_version
publish_final_to_nas     # 默认 false，任务创建后不可变
publish_origin_to_nas    # 默认 true，任务创建后不可变
status
submitted_by
submitted_at
executor_id
```

#### ExternalDatasetSource

```text
id
dataset_provider          # HUGGING_FACE
dataset_repo              # nvidia/PhysicalAI-Autonomous-Vehicles
dataset_revision          # resolved commit SHA
chunk_id
source_status
  origin_path
  nas_origin_path
infer_path
created_at
updated_at
```

约束：

```text
UNIQUE(dataset_provider, dataset_repo, dataset_revision, chunk_id)
INDEX(source_status, chunk_id)
```

#### DatasetClip

```text
id
external_source_id
clip_uuid
status
frame_count
valid_frame_count
error_code
metrics_json
```

约束：

```text
UNIQUE(external_source_id, clip_uuid)
INDEX(external_source_id, status)
```

`DatasetClip` P0 可以在 Phase1 完成后批量写入。逐帧信息由通用 `DatasetFrame` 表按批量接口写入；不得为每一帧单独发起 HTTP 请求或单独提交事务，避免写入效率和数据库膨胀问题。

为与自建路线的训练检索能力保持一致，NVIDIA 路线在发布前也应复用通用 `DatasetFrame` 帧索引模型；帧索引通过批量接口写入，保存 `chunk_id`、`clip_uuid`、`frame_id`、图片/NPY 相对路径、时间戳、导航、描述、标签和质量状态，不保存媒体二进制。若 NVIDIA 帧级检索不纳入本轮交付，必须明确标记为 P1，不能同时声称平台支持所有路线的逐帧检索。

#### ResourcePool、ResourceRequest 与 ResourceLease

```text
ResourcePool:
  executor_id
  resource_key
  capacity
  enabled
  config_version

ResourceRequest:
  id
  resource_key
  pipeline_run_id
  step_run_id
  executor_id
  units
  priority
  requested_at
  status                    # PENDING/GRANTED/CANCELLED/EXPIRED

ResourceLease:
  id
  resource_key
  pipeline_run_id
  step_run_id
  executor_id
  units
  slot_id
  owner
  token_hash
  acquired_at
  heartbeat_at
  expires_at
  released_at
```

资源申请先幂等创建 `ResourceRequest`。Backend 按 `priority DESC, requested_at ASC` 选择当前可满足的请求，并在单个数据库事务中锁定 `ResourcePool` 行、清理过期租约、检查已分配 `units` 后创建 `ResourceLease`。不能采用“先查询再插入”的非原子实现，也不能只依赖 Orchestrator 进程内锁。离散资源返回 `slot_id`；`VLM_PERMITS` 等计数资源可以令 `slot_id` 为空，只返回 units。容量为 1 是初始部署参数，不是模型上限。

### 9.2 复用模型

- `SubmissionBatch`：批量提交的页面聚合；如果自建 V1 尚未提供，可在本项目新增；
- `PipelineRun`：每个 chunk 一条；
- `StepRun`：每个 DAG 步骤和 attempt 一条；
- `Artifact`：chunk/clip 产物 manifest；
- `PipelineEvent`：只追加的状态和审计事件；
- 租约字段：继续使用自建 V1 既有实现。

## 10. 端到端处理流程

### 10.1 正常流程

```text
1. 用户在页面输入 chunk 表达式，并选择原始数据和最终结果是否回传 NAS；原始数据默认开启，最终结果默认关闭
2. Frontend 调用 Backend 预检接口
3. Backend 展开、校验、查询重复任务和已有结果
4. 用户确认提交
5. Backend 为每个新 chunk 幂等创建 NVIDIA_CHUNK PipelineRun
6. 任务进入 NVIDIA_QUEUE
7. Orchestrator 的 NVIDIA Worker 池按优先级和提交时间领取任务
8. Orchestrator检查 A100 SSH、磁盘、代码版本、HF 登录态和下载端点
9. Orchestrator 获取 NVIDIA 下载资源额度，wrapper 固定 revision 下载当前 chunk；此时自建队列可并行处理
10. wrapper 完成下载并释放下载资源租约
11. wrapper 校验 16 个预期下载文件
12. Orchestrator 等待并取得 COMPUTE_IO slot，wrapper 解压 7 路相机 ZIP 和 egomotion ZIP
13. wrapper 校验 MP4、timestamps、egomotion 和 calibration
14. wrapper 发现并输出 clip UUID 清单
15. wrapper 执行 Phase1 预处理和 reduce
16. validator 校验所有 clip 的索引、图片和 NPY
17. wrapper 执行导航 CPU 步骤，随后释放 COMPUTE_IO slot；导航复核前取得 VLM permits，完成后释放
18. wrapper 再次取得 VLM permits 并执行场景描述，完成后释放；此时自建 CPU 处理可以并行
19. validator 生成 chunk_manifest.json 和 quality_report.json
20. 帧索引器批量登记有效帧及其图片、NPY、导航、描述和质量字段
21. `publish_origin_to_nas=true` 时取得 NAS 发布资源，将 A100 原始数据目录同步到 NAS 原始备份 staging
22. 打开原始回传时校验 manifest/checksum 后原子发布 NAS 原始备份目录；关闭时记录跳过原因
23. Orchestrator 调用 Backend 登记 clip、产物、已执行的 NAS 回传动作和血缘
24. `publish_final_to_nas=false` 时任务进入 NVIDIA_DONE，页面显示 A100 最终路径和已执行的 NAS 路径
25. `publish_final_to_nas=true` 时继续将 A100 最终结果同步到 NAS final staging，校验后原子发布并登记 NAS_FINAL
26. 最终结果发布成功后任务进入 PUBLISHED，页面额外显示 NAS final 路径
```

对 NVIDIA 路线，`NVIDIA_DONE` 的含义是“A100 最终目录已通过质量校验，且所有创建任务时打开的 NAS 回传动作均成功或被明确记录为关闭”；`PUBLISHED` 在此基础上额外表示“用户明确开启最终结果回传，且 NAS final 已原子发布成功”。打开的任一 NAS 回传失败时任务不能进入完成态，应停留在对应发布状态或进入重试队列。

### 10.2 正式步骤状态

```text
CREATED
-> NVIDIA_QUEUE
-> PRECHECKING
-> DOWNLOADING
-> VERIFYING_DOWNLOAD
-> RESOURCE_WAIT
-> EXTRACTING
-> VERIFYING_EXTRACT
-> PHASE1_PROCESSING
-> PHASE1_VALIDATING
-> NAVIGATION_PROCESSING
-> DESCRIPTION_PROCESSING
-> FINAL_VALIDATING
-> NAS_ORIGIN_PUBLISHING
-> NVIDIA_DONE
-> [publish_final_to_nas=true] NAS_FINAL_PUBLISHING
-> PUBLISHED
```

失败和等待状态：

```text
RETRY_WAIT
FAILED
QUARANTINED
CANCELED
```

取消只允许发生在 `CREATED`、`SELF_BUILT_QUEUE`、`NVIDIA_QUEUE` 或 `RETRY_WAIT`。运行中的任务第一版不支持页面强杀，以免留下部分写入或破坏共享目录。

## 11. Pipeline 步骤和输入输出

### 11.1 PRECHECK

检查项：

- A100 SSH 可连接；
- `/data/nvidia_origin_dataset` 和 `/data/nvidia_infer_dataset` 可访问；
- 代码 revision 与 Pipeline 配置匹配；
- Conda/Python 环境可激活；
- Hugging Face Token 有效；
- `hf-mirror.com` 或配置的数据端点可访问；
- 下载根和输出根可用空间满足阈值；
- VLM 步骤启用时，`localhost:8002` 健康且模型标识符合预期；
- 同 chunk 没有其他非平台进程正在写目录。

磁盘估算不能只检查一个固定小阈值。根据现有实测，单 chunk 下载 ZIP 约 14 GB，保留 ZIP 并解压后原始根约 28 GB，Phase1 reduce 后仍会增加结果空间。V1 建议每个新 chunk 启动前至少预留 50 GB，并增加 15% 安全余量；上线前以一个真实 chunk 实测重新确定配置值。

### 11.2 DOWNLOAD

现有脚本：

```text
scripts/phase0/download_physicalai.py
```

自动化调用的逻辑命令：

```bash
python3 -u download_physicalai.py \
  --chunks <chunk_id> \
  --base-dir /data/nvidia_origin_dataset \
  --revision <resolved_commit_sha>
```

需要改造脚本以支持 `--revision`；若 `hf_hub_download` 返回实际 commit 信息，也必须写入 manifest。单个任务内部仍按 chunk 和文件顺序下载。V1 初始 `NVIDIA_DOWNLOAD capacity=1`；后续提高 capacity 和 `NVIDIA_WORKERS` 后允许不同 chunk 并行下载，但必须验证 Hugging Face cache、带宽和 `/data` 写入不会产生冲突。

成功条件：

- 7 个 camera ZIP 存在且非空；
- 3 个 label ZIP 存在且非空；
- 6 个 calibration parquet 存在且非空；
- 共 16 个预期文件；
- manifest 记录相对路径、大小和可获得的 ETag/commit 信息。

### 11.3 EXTRACT

现有脚本：

```text
scripts/phase0/unzip_data_files.py
```

调用约束：

```bash
python3 -u unzip_data_files.py \
  --chunks <chunk_id> \
  --base-dir /data/nvidia_origin_dataset \
  --workers <configured_workers>
```

禁止传入 `--delete`。当前只解压：

- 7 路 camera ZIP；
- `labels/egomotion` ZIP。

`egomotion.offline` 和 `obstacle.offline` 虽会被下载，但当前不进入主处理链，必须在 manifest 标记为 `DOWNLOADED_UNUSED`，不能误报为缺失步骤。

成功条件：

- 每路相机存在匹配的 MP4 和 timestamps parquet；
- egomotion parquet 存在；
- calibration 文件存在；
- 文件非 0 字节；
- 解压脚本验证结果无 missing 和 corrupt；
- 生成非空 clip UUID 清单。

### 11.4 PHASE1_PROCESSING

现有脚本：

```text
scripts/phase1/infer_data_gen.py
```

逻辑命令：

```bash
python3 -u infer_data_gen.py \
  --chunks <chunk_id> \
  --clips all \
  --source-dir /data/nvidia_origin_dataset \
  --output-dir /data/nvidia_infer_dataset \
  --parallel <configured_parallel> \
  --reduce-on true \
  --step <configured_reduce_step>
```

每个 clip 执行：

1. 读取 egomotion 和 7 路相机 timestamps；
2. 计算公共时间范围；
3. 校验 16 步历史、64 步未来和相机同步；
4. 解码 MP4 并生成缩放 JPG；
5. 保存 history/future NPY；
6. 生成严格索引；
7. 按配置 reduce，并删除未引用的 `_small.jpg`。

主要输出：

```text
/data/nvidia_infer_dataset/data_sample_chunk<N>/infer/<clip_uuid>/
├── preprocess_metadata.json
└── data/
    ├── inference_index_strict.csv
    ├── inference_index_origin.csv
    ├── camera_images/<camera>/*_small.jpg
    └── egomotion/frame_*_{history,future_gt}.npy
```

`--parallel`、`--step`、JPEG 质量和 reduce 开关必须来自管理员维护的 Pipeline 配置，普通用户不能修改。

### 11.5 NAVIGATION_PROCESSING

当前代码存在两套导航产物路径：

旧/兼容入口：

```text
navi_gen_rule.py
-> navigation/navi_text.csv
```

当前较完整的路线几何和 VLM 复核入口：

```text
navi_gen_route.py
-> navigation/navi_route.csv
-> navi_gen_llm.py 原地增加 is_llm_correct/llm_verdict
-> nav_gen_final.py
-> navigation/navi_text.csv
```

自动化 P0 以第二条链路作为候选生产基线，因为当前 `navi_gen_llm.py` 实际读取 `navi_route.csv`，`nav_gen_final.py` 也依赖其输出字段。正式上线前必须使用 A100 一个已知成功 clip 做回归对比并由算法负责人确认。确认后在 `pipeline_config_version` 中锁定唯一链路，不能同时运行两套脚本相互覆盖 `navi_text.csv`。

生产步骤建议固定为：

```text
navi_gen_route.py
-> navi_gen_llm.py
-> nav_gen_final.py
```

`navi_route_plot.py` 只用于人工调试，不属于 P0 发布条件。

导航成功条件：

- 每个有效 clip 有可解析的 `navigation/navi_route.csv`；
- `is_llm_correct` 和 `llm_verdict` 字段符合协议；
- 每个有效 clip 有 `navigation/navi_text.csv`；
- `navi_text.csv.frame_id` 与严格索引一致或满足已确认的覆盖规则；
- `final_nav` 不为空且取值/文本格式符合训练侧协议；
- VLM 调用失败不能被静默视为整步成功，必须统计失败数量和降级策略。

### 11.6 DESCRIPTION_PROCESSING

现有脚本：

```text
scripts/phase2/clip_llm_comprehension.py
```

输入：

- `inference_index_strict.csv`；
- `camera_front_wide_120fov` 抽样图片；
- VLM HTTP 服务。

输出：

```text
navigation/clip_discription_llm.txt
```

注意现有文件名使用 `discription` 拼写。V1 为兼容现有训练和已有数据保留该文件名，不在自动化过程中擅自改名；数据库 artifact 类型统一写成 `CLIP_DESCRIPTION`。

成功条件：

- 启用描述的每个有效 clip 都有非空文件；
- 文件头中的 chunk 和 clip 与当前任务一致；
- 输出正文可解析且包含至少一个有效帧范围；
- HTTP 失败、content 为空和模型返回格式错误分别记录错误码。

### 11.7 FINAL_VALIDATING

新增 `validate_nvidia_chunk.py`，生成：

```text
/data/nvidia_infer_dataset/data_sample_chunk<N>/
├── chunk_manifest.json
└── quality_report.json
```

至少检查：

- 发现的 clip 总数；
- Phase1 成功、失败和跳过 clip 数；
- 严格索引 CSV 可解析且非空；
- 索引引用的 7 路图片存在；
- history/future NPY 存在、可加载且 shape 正确；
- `preprocess_metadata.json` 可解析；
- 导航文件存在、字段正确、frame 覆盖率达标；
- 场景描述存在且非空；
- 所有文件均位于当前 chunk 根目录，禁止路径逃逸；
- 代码版本、数据 revision 和 Pipeline 配置已记录。

P0 默认采用严格发布策略：任一应处理 clip 失败则 chunk 不进入 `PUBLISHED`，而进入 `QUARANTINED`。后续如果业务允许部分发布，再增加明确的最小成功率配置和失败 clip 清单，不能在 V1 中隐式放宽。

### 11.8 NAS 回传策略

NVIDIA 任务将 NAS 回传拆分为两个相互独立的动作，不能用一个总开关同时控制：

1. **原始数据回传：任务级可选，默认开启**。创建任务时字段 `publish_origin_to_nas`（API）或“原始数据回传 NAS”（页面）默认为 `true`。打开时从 A100 origin 同步到 NAS 原始备份区；关闭时跳过传输，但必须在事件、manifest 和页面中明确记录。
2. **最终结果回传：任务级可选，默认关闭**。创建任务时字段 `publish_final_to_nas`（API）或“最终结果回传 NAS”（页面）默认为 `false`。关闭时只保留 A100 最终结果和平台产物索引；打开时才执行最终结果 `.incoming -> final` 原子发布。

两个开关必须分别写入 `PipelineRun` 的不可变配置快照，并进入 manifest、事件和审计记录。重试、恢复和人工重跑不得静默改变任一开关值；如需改变，必须创建新的 `PipelineRun`。

处理完成后必须保留 NVIDIA 原始下载数据。这里的“原始下载数据”严格指 `download_manifest.json.files` 列出的 Hugging Face 下载原件：当前为 10 个 ZIP 和 6 个 calibration Parquet。解压生成的 MP4、推理 Parquet、索引和其他处理产物属于 A100 工作目录派生文件，不得进入 NAS 原始备份。wrapper 生成独立的 `download_payload_manifest.json`，记录每个下载原件的相对路径、大小和 SHA-256；`raw_manifest` 仍可用于追踪 A100 工作目录，但不能作为 NAS origin 发布白名单。

仅当 `publish_origin_to_nas=true` 时，Orchestrator 才依据下载原件 manifest 从 A100 origin 根目录同步到 NAS；无论开关取值如何都不删除 A100 原始目录，不使用 `--delete`：

```text
A100:/data/nvidia_origin_dataset/<chunk_id>/
  -> NAS:/public/vla_dataset_builder_backup/nvidia_origin/.incoming/<dataset_revision>/<chunk_id>/
  -> 校验 raw_manifest.json/checksum
  -> NAS:/public/vla_dataset_builder_backup/nvidia_origin/<dataset_revision>/<chunk_id>/
```

NAS 正式目录只允许原子发布，传输中断只能留下 `.incoming`。回传成功后登记 `NVIDIA_ORIGIN_NAS` artifact 和 `SourceCopy`，记录数据集仓库、commit SHA、chunk ID、文件数、总字节数和 manifest hash；回传关闭时登记跳过事件，不创建该 artifact。原始数据与 A100 最终推理结果使用同一 `pipeline_run_id` 和 `source_id` 关联。

当 `publish_final_to_nas=true` 时，最终推理结果另行发布到独立的 NAS final 目录；当其为 `false` 时，禁止把最终推理目录误当作原始备份目录发布，也不得因为缺少 final 副本而伪造 `NAS_FINAL` artifact。两个开关都为 `false` 时，任务仍须完成质量校验和平台 Artifact 登记，但只保留 A100 结果。

## 12. A100 wrapper 与运行协议

### 12.1 新增统一入口

在 A100 的 `proj_nvidiadata_builder` 增加调度适配层，不改算法主体：

```text
scripts/run_nvidia_pipeline.sh
scripts/run_nvidia_step.py
scripts/validate_nvidia_chunk.py
scripts/write_nvidia_manifest.py
```

Orchestrator 只允许调用：

```bash
run_nvidia_pipeline.sh \
  --run-id <pipeline_run_id> \
  --chunk <non_negative_integer> \
  --config <approved_config_name> \
  --from-step <approved_step> \
  --resume
```

wrapper 负责：

- 激活固定 Conda 环境；
- 使用固定根目录；
- 校验 chunk 和配置参数；
- 按唯一 DAG 调用脚本；
- 记录 PID、开始时间、结束时间和退出码；
- 保存 stdout/stderr 日志；
- 原子写步骤状态文件；
- 检查已有产物能否安全复用；
- 禁止无条件覆盖或删除正式目录；
- 输出明确退出码。

### 12.2 机器可读状态

状态目录建议：

```text
/data/nvidia_pipeline_runs/<pipeline_run_id>/
├── run.json
├── logs/<step>.log
├── steps/<step>.json
├── manifests/
└── quality_report.json
```

每一步先写 `<step>.json.tmp`，写完并 fsync 后原子改名为 `<step>.json`。示例：

```json
{
  "schema_version": "nvidia-step-run-v1",
  "pipeline_run_id": "<uuid>",
  "chunk_id": 10,
  "step": "PHASE1_PROCESSING",
  "status": "SUCCEEDED",
  "started_at": "2026-09-10T10:00:00Z",
  "finished_at": "2026-09-10T10:18:20Z",
  "pid": 12345,
  "exit_code": 0,
  "attempt": 1,
  "metrics": {
    "clip_total": 100,
    "clip_succeeded": 100,
    "clip_failed": 0
  }
}
```

脚本打印了 `done` 但缺少状态文件、退出码非 0、校验失败三者中的任何一种，都不能判定步骤成功。

### 12.3 退出码分类

```text
0   成功
10  输入参数非法
20  前置依赖不可用
30  下载失败，可重试
31  下载内容不完整
40  解压失败，可按文件重试
41  解压校验失败
50  Phase1 部分或全部失败
60  VLM 服务不可用，可重试
61  VLM 返回格式错误
70  导航产物校验失败
71  描述产物校验失败
80  磁盘空间不足，需要人工处理
90  目录或版本冲突，需要隔离
99  未分类错误
```

## 13. 调度、优先级和多进程

### 13.1 两条逻辑队列

Backend 保存两条独立逻辑队列：

```text
SELF_BUILT_QUEUE：自建 rosbag 数据任务
NVIDIA_QUEUE：NVIDIA PhysicalAI chunk 任务
```

两条队列复用同一个 Orchestrator 服务，但由两个可配置 Worker 池分别领取：

```text
SELF_BUILT_WORKERS=1   # V1 初始值，后续可提高
NVIDIA_WORKERS=1       # V1 初始值，后续可提高
```

每条队列内部默认按以下顺序：

```text
priority DESC, submitted_at ASC
```

每个 Worker 同时只持有一个任务租约，但同一队列可以有多个 Worker。数据库不得建立“一条队列只能有一个 RUNNING 任务”的硬约束。这样 NVIDIA chunk 即使长时间停留在 `DOWNLOADING`，也不会占用 `SELF_BUILT_QUEUE` 的领取名额；后续增加 `NVIDIA_WORKERS` 后，也可以同时下载或处理多个不同 chunk。两条队列的任务租约、状态机、StepRun 和 Artifact 仍由同一个 Backend 管理，不部署第二套 Orchestrator 或数据库。

队列独立不代表共享资源无限制并发。Worker 领取任务后，每个步骤还必须取得对应的资源租约；暂时拿不到时进入 `RESOURCE_WAIT`，继续 heartbeat，但不启动远端进程。

### 13.2 分步骤资源池

| 资源池 | V1 初始容量 | 使用步骤 | 后续扩容方式 |
|---|---:|---|---|
| `NVIDIA_DOWNLOAD` | 1 slot | NVIDIA 下载与下载校验 | 网络和磁盘允许后增加 slot |
| `A100_COMPUTE_IO` | 1 slot | 两条路线的解压、Phase1、CPU 导航生成和重型结果校验 | 压测后增加 slot |
| `VLM_PERMITS` | 4 units | 两条路线的导航 VLM 复核和场景描述 | 增加 permits，任务按实际并发申请 units |
| `NAS_PUBLISH` | 1 slot | 自建最终结果及 NVIDIA 原始数据回传 NAS | NAS 吞吐允许后增加 slot |
| `DATASET_PATH:<key>` | 1 slot | 对同一 bag/chunk 正式目录的写入 | 永远保持 1 |

推荐并行组合：

| 自建任务当前步骤 | NVIDIA 当前步骤 | V1 是否允许 |
|---|---|---:|
| Phase1 | Download | 是 |
| Navigation CPU | Download | 是 |
| VLM/Description | Download | 是，但监控网络和模型服务 |
| Phase1 | Extract | 否，竞争 CPU 和 `/data` I/O |
| Phase1 | NVIDIA Phase1 | 否 |
| 自建 VLM | NVIDIA VLM | V1 默认否；提高 permits 后可受控并行 |
| NAS Publish | Download | 是 |

`NVIDIA_DOWNLOAD` 与 `A100_COMPUTE_IO` 是不同资源，因此长下载不会阻塞自建处理。若实际监控发现下载写盘明显拖慢自建 Phase1，可给下载进程设置低 I/O 优先级，或在高磁盘压力时暂缓发放新的下载资源租约，而不是重新合并两条队列。

### 13.3 Pipeline 内部并行

```text
每条逻辑队列活动 Pipeline：由对应 WORKERS 配置决定
两条队列合计活动 Pipeline：SELF_BUILT_WORKERS + NVIDIA_WORKERS
DOWNLOAD：单 chunk、文件顺序下载
EXTRACT：ThreadPoolExecutor，默认 workers=8
PHASE1：multiprocessing，默认 parallel=8
NAV_ROUTE：multiprocessing，初始 parallel=8
NAV_VLM：multiprocessing × ThreadPool，需压测后配置
DESCRIPTION：multiprocessing × ThreadPool，需压测后配置
```

这些默认值来自当前代码和历史用法，不应直接视为所有机器上的最优值。上线前需要采集 CPU、内存峰值、磁盘吞吐和 VLM 失败率，形成管理员维护的配置，例如：

```text
nvidia-prod-v1:
  nvidia_workers: 1
  extract_workers: 8
  phase1_parallel: 8
  reduce_on: true
  reduce_step: 10
  nav_route_parallel: 8
  nav_vlm_parallel: 8
  nav_vlm_intra_threads: 4
  description_parallel: 8
  description_intra_threads: 2
```

配置必须有版本，不允许在运行中修改已有任务的快照。提高外层 Worker 数时必须同步降低或重新评估每任务内部并发。例如由 `1 × phase1_parallel=8` 提升为两个并行任务时，应先压测 `2 × phase1_parallel=4`，而不是直接运行 `2 × 8`。

### 13.4 资源租约与槽位锁的实现

资源控制使用双重保护：

```text
Backend：原子创建带 TTL 的 ResourceLease
A100：对应远端 flock 文件
```

建议远端槽位锁：

```text
/tmp/vla_nvidia_download.slot-<N>.lock
/tmp/vla_compute_io.slot-<N>.lock
/tmp/vla_nas_publish.slot-<N>.lock
/tmp/vla_path.<safe_hash>.lock
```

任务租约表示“哪个 Worker 负责当前任务”，资源租约表示“当前步骤能否占用多少共享资源”，二者不能合并。Backend 分配 `executor_id`、`units` 和 `slot_id`，wrapper 只能取得所分配 slot 的 flock。Orchestrator 重启后必须同时对账任务租约、资源租约、远端 flock、PID 和状态文件。

VLM 使用 `units` 计数，不使用单一 flock：任务获得多少 `VLM_PERMITS`，其 `parallel × intra_threads` 就不得超过多少。这样未来可以让多个 VLM 任务在总额度内并行。资源租约由 Backend 原子分配，远端槽位 flock 作为防止手工脚本和异常进程绕过平台的第二层保护。

如果容量仍为 1，两条 Phase1 默认互斥；容量提高到 2 后，可以分配 `slot-0` 和 `slot-1` 同时运行。`DATASET_PATH:<key>` 仍保证同一个 chunk 或 bag 只有一个写入者。

V1 不进行运行中抢占。已经取得资源并启动的步骤执行到完成；等待资源的任务保持 `RESOURCE_WAIT`，资源释放后按优先级和等待时间获得资源。

### 13.5 单台 A100 扩容路径

并发能力通过版本化容量配置发布：

```text
concurrency-safe-1:
  self_built_workers: 1
  nvidia_workers: 1
  nvidia_download_slots: 1
  compute_io_slots: 1
  phase1_parallel_per_task: 8
  vlm_permits: 4

concurrency-safe-2:
  self_built_workers: 2
  nvidia_workers: 2
  nvidia_download_slots: 2
  compute_io_slots: 2
  phase1_parallel_per_task: 4
  vlm_permits: 8
```

以上第二档只是目标示例，必须通过实测后才能启用。特别需要验证：

- 两个下载任务是否会争用 Hugging Face cache、网络和 `/data` 写入；
- 两个 Phase1 各降低内部并发后，总吞吐是否高于单任务；
- 多任务同时解码视频时的内存峰值和磁盘延迟；
- 多个 VLM 任务在 permits 限制下是否稳定；
- 相同 chunk、相同 bag 和相同正式路径仍只有一个写入者；
- 输出内容与单任务基线一致。

每个 `PipelineRun` 必须保存容量配置版本和实际获得的 `executor_id/slot_id/units`。扩容时只发布新配置，不修改历史任务快照。监控超过阈值时停止发放新资源租约，并回退到上一档容量；已经运行的步骤不强制终止。

单机扩容优先顺序：

```text
1. NVIDIA 下载与自建处理并行
2. 多个 NVIDIA 下载并行
3. 增加 VLM permits，让多个 VLM 任务受控并行
4. 两个低内部并发的 Phase1 并行
5. 证明总吞吐提升后再继续增加 slot
```

## 14. Backend API 增量

### 14.1 提交接口

| 方法 | 路径 | 作用 |
|---|---|---|
| POST | `/api/v1/nvidia/submissions/preview` | 解析 chunk 表达式，返回重复、已有和待创建清单 |
| POST | `/api/v1/nvidia/submissions` | 创建 SubmissionBatch 和独立 chunk PipelineRun |
| GET | `/api/v1/nvidia/sources` | 按 revision、chunk、状态查询 NVIDIA 数据源 |
| GET | `/api/v1/nvidia/sources/{source_id}` | 查询 chunk、clip、运行和产物 |
| GET | `/api/v1/nvidia/submissions/{batch_id}` | 查询一次批量提交的总体进度 |

提交请求示例：

```json
{
  "dataset_repo": "nvidia/PhysicalAI-Autonomous-Vehicles",
  "chunk_expression": "1,5,10:15",
  "pipeline_config": "nvidia-prod-v1",
  "enable_description": true,
  "publish_origin_to_nas": true,
  "publish_final_to_nas": false,
  "note": "训练补充数据"
}
```

Backend 只接受管理员白名单中的 `dataset_repo` 和 Pipeline 配置。固定 commit SHA 由 Backend 从已批准的 Pipeline 配置快照中取得，不接收普通用户提供的 revision。管理员发布或更新配置时负责解析 revision 别名并保存 commit SHA；解析失败的配置不能进入可选列表。

### 14.2 复用 Orchestrator 接口

继续复用：

```text
POST /api/v1/orchestrator/leases/acquire?queue=<queue_name>
POST /api/v1/orchestrator/leases/{run_id}/heartbeat
POST /api/v1/orchestrator/leases/{run_id}/release
POST /api/v1/orchestrator/resource-leases/acquire
POST /api/v1/orchestrator/resource-leases/{lease_id}/heartbeat
POST /api/v1/orchestrator/resource-leases/{lease_id}/release
POST /api/v1/pipeline-runs/{run_id}/steps/{step}/start
POST /api/v1/pipeline-runs/{run_id}/steps/{step}/complete
POST /api/v1/pipeline-runs/{run_id}/steps/{step}/fail
POST /api/v1/pipeline-runs/{run_id}/artifacts
POST /api/v1/pipeline-runs/{run_id}/frames/bulk
POST /api/v1/pipeline-runs/{run_id}/publish
```

领取响应增加：

```json
{
  "pipeline_type": "NVIDIA_CHUNK",
  "source": {
    "dataset_repo": "nvidia/PhysicalAI-Autonomous-Vehicles",
    "dataset_revision": "<commit_sha>",
    "chunk_id": 10
  },
  "pipeline_config": "nvidia-prod-v1"
}
```

Orchestrator 根据 `pipeline_type` 选择服务端固定 DAG 实现，不根据用户文本动态生成命令。

任务领取时必须显式传入 `SELF_BUILT_QUEUE` 或 `NVIDIA_QUEUE`，一个 Worker 不能领取另一条队列的任务。资源领取接口先幂等登记 `ResourceRequest`，再按跨队列统一的 `priority DESC, requested_at ASC` 授予资源，避免低优先级任务因请求时序抢占高优先级任务。资源暂不可用时返回 `204 No Content` 或明确的等待结果，任务进入 `RESOURCE_WAIT`，不能把资源等待计为步骤失败。

### 14.3 幂等规则

- 所有写请求必须携带 `Idempotency-Key`；
- 同一批量请求重试返回同一个 `SubmissionBatch`；
- 同一 source、Pipeline 配置和代码版本只能存在一个排队或运行任务；
- 已有成功结果时默认复用，不新建任务；
- 管理员选择重跑时创建新的 `PipelineRun`，不得覆盖旧运行审计记录；
- 同 chunk 目录存在但数据库无成功记录时进入 `DISCOVERED_EXISTING` 对账，不直接跳过或覆盖。

## 15. 数据管理界面增量

### 15.1 导航入口

在现有“处理任务”模块增加：

```text
处理任务
├── 自建数据集
└── NVIDIA PhysicalAI
```

不新建一套独立前端工程，沿用自建 V1 的页面框架、样式、鉴权和 Backend 渲染方式。

### 15.2 NVIDIA 数据列表

字段：

| 字段 | 说明 |
|---|---|
| Chunk | chunk ID |
| 数据版本 | Hugging Face commit SHA 短值 |
| 状态 | 排队、下载、解压、处理、失败、完成等 |
| Clip | 成功数/总数 |
| 当前步骤 | 当前 StepRun |
| 提交人 | 用户身份 |
| 提交时间 | 入队时间 |
| 等待/运行时长 | 实时或最近刷新值 |
| 原始大小 | A100 origin 目录统计 |
| 结果大小 | A100 infer 目录统计 |
| 质量 | 通过、失败或隔离 |
| 最新错误 | 结构化错误摘要 |

筛选：

- chunk ID；
- 状态；
- 提交人；
- 数据 revision；
- 提交时间；
- 是否已有最终结果。

### 15.3 任务详情

展示：

- 数据集 repo、revision 和 chunk；
- Pipeline 配置和代码版本；
- 队列位置和优先级；
- 每一步开始/结束时间、attempt、退出码和耗时；
- 下载文件数和字节数；
- clip 总数、成功数、失败数；
- Phase1 有效帧数和过滤统计；
- 导航覆盖率、VLM 调用数和失败数；
- 描述成功率；
- A100 origin/infer 路径；
- chunk manifest 和 quality report；
- 产物血缘；
- 日志摘要和受控日志下载入口。

P0 操作：

- 创建任务；
- 取消排队任务；
- 重试可重试失败；
- 管理员调整优先级；
- 管理员对冲突任务执行隔离确认。

不提供删除 A100 文件和强制覆盖结果按钮。

## 16. 错误处理和恢复

| 场景 | 系统行为 |
|---|---|
| Backend 暂时不可用 | Orchestrator停止领取；远端已运行进程继续，恢复后对账 |
| A100 SSH 不可用 | `RETRY_WAIT`，指数退避，不创建新任务 |
| HF Token 失效 | `FAILED/PRECONDITION`，提示管理员更新 Secret |
| 镜像站不可用 | 按配置切换官方端点或退避，不能由用户传 URL |
| 下载中断 | 最多自动重试 3 次，利用 HF 缓存补缺失文件 |
| 下载文件缺失/0 字节 | 不解压，校验失败并重试下载 |
| 解压中断 | 重跑解压并再次按 ZIP 清单校验 |
| A100 磁盘不足 | `QUARANTINED`，禁止自动删除历史正式数据 |
| Phase1 部分 clip 失败 | 保存失败清单，限次重试后隔离 chunk |
| VLM 服务不可用 | VLM 步骤等待并重试，不重复执行 Phase1 |
| VLM 部分返回无效 | 按 clip/segment 重试并记录，不静默成功 |
| Orchestrator 重启 | 依据租约、远端 PID、StepRun JSON 和产物校验恢复 |
| 相同目录已有数据 | 比较 revision、manifest 和运行记录；不一致则隔离 |
| 用户重复提交 | 返回已有任务或结果，不重复排队 |

重试必须从最近一个验证通过的步骤开始。例如描述失败只重试描述，不重新下载、解压和执行 Phase1。

## 17. 安全边界（权限管理后置）

1. Hugging Face Token 作为 A100 上的只读 Secret 管理，不进入数据库、日志、镜像或 PRD。
2. SSH 私钥沿用自建 V1 的 Orchestrator Secret，Frontend 和 Backend 不持有私钥。
3. 所有远程命令来自代码内固定模板，chunk 必须转换为整数后再传递。
4. 用户不能提交任意仓库、revision 字符串、文件路径、并发值或环境变量。
5. A100 的正式 origin/infer 根目录禁止 Orchestrator执行递归删除。
6. `--force`、`--delete` 在生产配置中默认禁用；重跑需新建版本或进入管理员确认流程。
7. 页面日志需要过滤 Authorization、HF Token、SSH 参数和模型服务敏感信息。
8. 重试、取消和优先级调整必须写入 `PipelineEvent`；V1 暂不实现用户、角色和细粒度权限管理，先依赖内网部署和固定服务边界。

## 18. 可观测性

### 18.1 任务指标

- 排队任务数和最长等待时间；
- 每种 `pipeline_type` 的运行数、成功率和失败率；
- 每个步骤耗时；
- 下载字节数、平均速度和重试次数；
- 解压后字节数；
- clip 总数、成功数和失败数；
- 有效帧数和过滤比例；
- Phase1 CPU、内存峰值和磁盘吞吐；
- VLM 请求数、成功率、P95 延迟和解析失败数；
- A100 origin/infer 可用磁盘；
- SSH 隧道和 VLM 健康状态。

### 18.2 日志

日志按以下维度保存和查询：

```text
pipeline_run_id / step / attempt
```

Backend 只保存日志路径、摘要和最后若干 KB，不把完整长日志写进 MySQL。A100 日志设置保留周期，正式产物 manifest 长期保留。

## 19. 需要开发和改造的事项

### 19.1 rosbag-catalog Backend（P0）

1. 增加 `NVIDIA_CHUNK` Pipeline 类型和对应状态转换。
2. 增加 `ExternalDatasetSource`、`DatasetClip`、`ResourcePool`、`ResourceRequest`、`ResourceLease` 和可选 `SubmissionBatch` 模型及迁移。
3. 增加 chunk 表达式解析、预检和批量提交接口。
4. 扩展 Pipeline 创建服务，支持同 source/config 的并发幂等约束。
5. 扩展 Orchestrator 领取响应，返回类型化任务参数。
6. 增加 clip 批量登记和 quality report 登记能力，避免逐 clip 多次 HTTP 请求。
7. 增加 NVIDIA source、任务、步骤和产物查询接口。
8. 增加按 `queue_name` 原子领取任务，以及资源租约 acquire、heartbeat、release 接口。
9. 扩展优先级策略，默认降低 NVIDIA 批量任务优先级。
10. 所有数据库写入继续收口在 Backend service 层。
11. 增加原始数据 NAS 备份登记接口或复用 Artifact 接口，确保备份完成后才允许任务发布。

### 19.2 数据管理界面（P0）

1. 增加 NVIDIA 任务提交页面。
2. 增加表达式展开预览和重复任务提示。
3. 在统一任务列表增加数据路线筛选。
4. 增加 NVIDIA chunk 列表和详情页面。
5. 在任务详情展示步骤、clip 统计、路径、质量、日志和血缘。
6. 复用已有重试、取消和优先级调整组件。

### 19.3 Orchestrator（P0）

1. 根据 `pipeline_type` 选择 `SelfBuiltPipeline` 或 `NvidiaChunkPipeline`。
2. 增加 `SelfBuiltWorkerPool` 和 `NvidiaWorkerPool` 两个独立领取池，Worker 数分别由配置控制。
3. 增加 `ResourceLease` 客户端，按步骤申请 `NVIDIA_DOWNLOAD`、`A100_COMPUTE_IO`、`VLM_PERMITS`、`NAS_PUBLISH` 和路径锁，并使用返回的 `executor_id/units/slot_id`。
4. 增加 NVIDIA PRECHECK、步骤执行、状态解析和恢复逻辑。
5. 增加下载网络错误、VLM 错误和磁盘错误分类。
6. 支持从最近成功 StepRun 恢复。
7. 限制任务参数到固定配置白名单。
8. 收集并回写 chunk/clip 指标、产物和质量报告。
9. 在 `FINAL_VALIDATING` 成功后按 `publish_origin_to_nas` 决定是否执行原始数据 NAS 备份；只有 `publish_final_to_nas=true` 时才继续发布最终结果到 NAS final。所有打开的回传动作完成且关闭动作已记录时允许终止于 `NVIDIA_DONE`，最终结果回传开启并成功发布后才允许 `PUBLISHED`。

### 19.4 proj_nvidiadata_builder（P0）

1. 为 `download_physicalai.py` 增加 `--revision` 和机器可读下载清单。
2. 为下载补充 wrapper 级重试、退避和完整性校验。
3. 固定 `unzip_data_files.py` 不使用 `--delete`。
4. 为 Phase1、导航和描述脚本补充统一退出码和结构化汇总。
5. 使用样例锁定唯一导航生产链，避免两套入口覆盖结果。
6. 新增 `run_nvidia_pipeline.sh` 和 `run_nvidia_step.py`。
7. 新增 `validate_nvidia_chunk.py`。
8. 新增 chunk/source/final manifest 生成器。
9. 将 API URL、模型 ID 和并发参数移入受控配置，不接受普通用户输入。
10. 忽略 `.bak`、`__pycache__` 和历史入口，生产 wrapper 只引用白名单脚本。

### 19.5 部署配置（P0）

在自建 V1 的 Orchestrator 配置基础上增加：

```text
NVIDIA_CODE_ROOT
NVIDIA_ORIGIN_ROOT=/home/xmyf/wzd/data/nvidia_origin_dataset
NVIDIA_INFER_ROOT=/home/xmyf/wzd/data/nvidia_infer_dataset
NVIDIA_NAS_ORIGIN_ROOT=/public/vla_dataset_builder_backup/nvidia_origin
NVIDIA_NAS_FINAL_ROOT=/public/vla_dataset_builder_backup/nvidia_final
NVIDIA_RUN_ROOT=/home/xmyf/wzd/runs/nvidia
NVIDIA_DATASET_REPO=nvidia/PhysicalAI-Autonomous-Vehicles
NVIDIA_ALLOWED_REVISION
NVIDIA_PIPELINE_CONFIG=nvidia-prod-v1
NVIDIA_MIN_FREE_GB
NVIDIA_HF_ENDPOINT
NVIDIA_HF_TOKEN_FILE
NVIDIA_VLM_HEALTH_URL=http://localhost:8002/v1/models
EXECUTOR_ID=a100-main
SELF_BUILT_WORKERS=1
NVIDIA_WORKERS=1
RESOURCE_NVIDIA_DOWNLOAD_CAPACITY=1
RESOURCE_COMPUTE_IO_CAPACITY=1
RESOURCE_VLM_PERMITS=4
RESOURCE_NAS_PUBLISH_CAPACITY=1
```

以上为当前测试阶段配置。正式切换时将 `NVIDIA_ORIGIN_ROOT`、`NVIDIA_INFER_ROOT` 和 `NVIDIA_RUN_ROOT` 分别切换为 `/data/nvidia_origin_dataset`、`/data/nvidia_infer_dataset` 和 `/data/nvidia_pipeline_runs`；切换前必须完成测试根与正式根目录结构对照、空间/冲突检查、单 chunk dry-run 和回滚方案。`NVIDIA_NAS_ORIGIN_ROOT` 仅在任务的 `publish_origin_to_nas=true` 时使用，`NVIDIA_NAS_FINAL_ROOT` 仅在任务的 `publish_final_to_nas=true` 时使用。

Hugging Face Token 位于 A100，不挂载到内网 Compose。Orchestrator 只检查远端登录态和执行固定下载命令。Worker 数、资源容量和单任务内部并发必须分别配置，不能使用一个含义模糊的总并发开关。

## 20. 测试方案

### 20.1 单元和接口测试

1. chunk 表达式：单值、列表、范围、混合、重复、负数、反向范围、超大范围和非法字符。
2. 批量提交：部分已有、部分排队、部分新建时结果正确。
3. 幂等：重复请求不产生重复 Batch、Source 或 PipelineRun。
4. 并发：多个用户同时提交相同 chunk 只产生一个活动任务。
5. 状态机：合法步骤推进成功，越级和过期租约返回 `409`。
6. 优先级：自建任务和 NVIDIA 任务按配置正确排序。
7. clip 批量登记：重复上报不产生重复记录。

### 20.2 wrapper 和校验测试

1. 使用临时目录模拟 16 个下载文件，验证缺失和 0 字节检测。
2. 模拟下载中断，确认重试从缓存继续。
3. 模拟 ZIP 损坏，确认不进入 Phase1。
4. 模拟一个 clip 缺 MP4、timestamps 或 egomotion。
5. 模拟严格索引引用不存在的 JPG。
6. 模拟 NPY shape 错误或不可加载。
7. 模拟 VLM 拒绝连接、超时、空 content 和非法 JSON。
8. 模拟 Orchestrator在各步骤重启，确认从最后成功步骤恢复。
9. 验证 NVIDIA 下载和自建 Phase1 可以同时取得各自资源并运行。
10. 初始 `A100_COMPUTE_IO capacity=1` 时，自建 Phase1 与 NVIDIA Phase1 不能同时取得 slot。
11. 将 `A100_COMPUTE_IO capacity` 提升到 2 后，两个不同数据路径的任务可以取得不同 slot 并行运行。
12. 验证多个 VLM 任务获得的 units 总和不超过 `VLM_PERMITS capacity`，且各脚本实际并发不超过自身 units。
13. 验证同一 chunk 的 `DATASET_PATH:<key>` 永远只能分配给一个任务。

### 20.3 A100 端到端验收

选择一个尚未处理或明确允许用于测试的 chunk：

```text
页面提交
-> Backend 入队
-> Orchestrator 领取
-> A100 下载
-> 解压
-> Phase1
-> 导航
-> 描述
-> 最终校验
-> 原始数据回传 NAS
-> 默认页面显示 NVIDIA_DONE；打开最终结果回传开关时继续发布 NAS final 并显示 PUBLISHED
```

测试不得覆盖现有正式成功结果。首次可以使用独立测试 run 状态目录，但 origin/infer 的组织结构必须与正式目录一致。

## 21. 验收标准

V1 完成必须同时满足：

1. 普通用户无需 SSH 登录 A100，只通过页面选择 chunk 即可启动完整流程。
2. 单个、离散列表和范围表达式均可正确创建独立任务。
3. 同一 chunk 并发提交不会产生两个活动任务。
4. 自建和 NVIDIA 任务由同一个 Orchestrator 的两个 Worker 池管理，V1 初始每池一个 Worker，增加 Worker 后无需修改任务模型。
5. 所有步骤均有 Backend 状态、开始/结束时间、attempt、退出码和日志摘要。
6. 下载、解压、Phase1、导航、描述和最终校验全部自动执行。
7. 至少一个全新 chunk 从页面提交到默认关闭最终回传的 `NVIDIA_DONE` 全程无需人工干预，并另以一个明确开启开关的任务验证到 `PUBLISHED`。
8. 任务失败后可从最近成功步骤重试，不重复执行已验证成功的重步骤。
9. 最终页面可以追溯 Hugging Face revision、chunk、clip、代码版本、配置和最终文件路径。
10. 最终 `quality_report.json` 能证明所有预期 clip 的关键产物完整。
11. `FINAL_VALIDATING` 成功后，原始下载数据已完整同步到 NAS 原始备份目录，manifest/checksum 校验通过并登记 `NVIDIA_ORIGIN_NAS` artifact。
12. 原始数据 NAS 备份失败时任务不会进入 `NVIDIA_DONE` 或 `PUBLISHED`，可断点重试且不覆盖已有正式目录；最终结果回传关闭时不存在 `NAS_FINAL` artifact，开启时必须验证 `.incoming -> final` 原子发布。
13. NVIDIA 任务停留在下载阶段时，自建任务可以正常领取并进入 Phase1，不等待该 chunk 下载完成。
14. 任何生产自动化路径都不会调用 `--delete`，不会无条件 `--force`，不会递归删除正式数据。
15. 所有并发任务均受资源租约限制；提高容量后允许不同路径任务使用不同 slot 或 permits 并行，同一路径仍禁止并发写入。

## 22. 分阶段交付

### 第一阶段：最小闭环（P0）

- Backend 数据模型、任务类型、提交接口；
- NVIDIA 提交和任务详情页面；
- Orchestrator NVIDIA DAG；
- 两条逻辑队列、配置化 Worker 池和分步骤资源租约；
- 下载、解压、Phase1、导航、描述 wrapper；
- manifest、质量校验、失败恢复；
- 单个全新 chunk 端到端验收。

### 第二阶段：批量稳定性（P1）

- 批量提交聚合页；
- 磁盘和预计耗时展示；
- clip 失败明细和部分步骤定向重试；
- 单机多任务压测、容量调优和自动降载；
- VLM 服务熔断和限流；
- 队列等待时间估算；
- 告警通知。

### 后续优化（P2）

- 自动发现上游新增 revision/chunk，但仍需用户或策略确认；
- 多执行机或多 A100 资源池；
- 数据集级版本发布和训练消费登记；
- 按 clip 补算和选择性重跑；
- Airflow/Argo 迁移评估；
- 原始 ZIP 生命周期和自动清理策略。

## 23. 上线顺序

```text
1. 算法负责人确认 NVIDIA 正式导航链路
2. 固定 Hugging Face revision 和 Pipeline 配置
3. 开发 wrapper、状态文件和 validator
4. 扩展 Backend 模型、API 和状态机
5. 扩展 Orchestrator Pipeline 类型、双队列 Worker 池和资源租约
6. 增加页面
7. 本地 fake runner 验证队列、幂等和恢复
8. A100 单 clip 手工对照验证
9. A100 单 chunk 自动端到端验收
10. 开放普通用户单 chunk 提交
11. 开放受限批量提交
```

## 24. 待确认事项

以下事项不改变总体架构，但必须在编码或上线前确认：

1. Hugging Face 生产 revision 使用固定 commit SHA，还是由管理员维护可解析别名；推荐固定 SHA。
2. NVIDIA 当前正式导航链是否确定为 `navi_gen_route.py -> navi_gen_llm.py -> nav_gen_final.py`。
3. `navi_gen_rule.py` 的 `navi_detail_rule` 是否仍被训练侧消费；若需要，应作为独立 artifact 步骤而不是覆盖正式 `navi_text.csv`。
4. 场景描述是否为每个 V1 任务的强制发布条件。
5. `clip_discription_llm.txt` 的现有拼写是否已被训练代码硬编码。
6. A100 上 VLM SSH 隧道是否能作为长期服务自动恢复，以及健康检查的准确地址。
7. 一个 chunk 实际最坏磁盘占用和 Phase1 内存峰值。
8. NAS 原始数据备份目录的最终挂载路径和容量；V1 已要求将每个处理完成的 chunk 原始数据同步到 `NVIDIA_NAS_ORIGIN_ROOT`，并通过 staging、校验和原子发布完成。
9. 已有 `/data/nvidia_origin_dataset` 和 `/data/nvidia_infer_dataset` 数据是否需要只登记而不重跑；V1 默认只处理页面提交后的新增任务，不做历史全量入库。

## 25. 最终决策摘要

1. 不建设第二套调度系统，复用已经实现的 VLA Orchestrator。
2. 自建数据和 NVIDIA 数据使用统一任务模型、Backend API 和任务租约，但进入两条独立逻辑队列。
3. NVIDIA 以一个 chunk 为一个 PipelineRun，批量输入只作为多个任务的提交入口。
4. 用户只选择 chunk 和受控配置，不提供任意脚本、路径和并发参数。
5. A100 自动下载，不要求用户手动准备原始数据。
6. 测试阶段使用 `/home/xmyf/wzd/` 下与正式目录同构的 `data/nvidia_origin_dataset` 和 `data/nvidia_infer_dataset`；完成测试验收后，再单独切换到正式 `/data/nvidia_origin_dataset` 和 `/data/nvidia_infer_dataset`。
7. 每条队列 Worker 数和每类资源容量均配置化；初始保守运行，后续可在单台 A100 上增加计算 slot、下载 slot 和 VLM permits。
8. 下载数据由 Hugging Face repo、固定 revision 和 chunk ID 唯一标识。
9. 每个处理完成的 chunk 是否备份原始数据由 `publish_origin_to_nas` 决定，默认开启；最终结果仅在任务创建时显式打开 `publish_final_to_nas` 后回传 NAS，默认关闭。两个开关均须审计且互不控制。
10. 先在测试根完成一个 chunk 的无人值守端到端闭环和目录切换演练，再扩展批量效率、多资源调度和正式目录运行。
