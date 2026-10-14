# VLA 数据上传、处理与共享平台 PRD

**版本**：v1.1  
**状态**：方案评审稿  
**日期**：2026-09-08  
**适用项目**：`rosbag-catalog`、`vla_dataset_builder`

> **当前实现校准（2026-09-21）**：本文保留为早期平台化方案和需求背景，不作为当前实现基线。原文中的 PostgreSQL、个人电脑处理客户端、旧 Compose 结构和历史 NAS 全盘重建路线均已被当前实现替代或降为历史方案。当前实现基线以 `rosbag-catalog/docs/current_architecture.md`、`docs/production-cutover.md`、`HANDOFF.md` 和 `/home/wang/work/doc/todo/vla_self_dataset_pipeline_v1_todo.md` 为准：数据库为 MySQL 8.4，Backend 是唯一业务数据库写入口，Phase0 由处理机宿主机代理执行，本地默认测试，处理机仅在显式生产发布时更新。

## 1. 文档目的

本文定义从车端采集硬盘、分别拷贝到 NAS 和个人处理电脑、数据登记、批次管理、本地 phase0/phase1 处理、结果发布到 NAS 和公网 A100 的完整产品与技术方案。目标是把当前依赖人工拷贝、脚本命令和目录约定的流程，建设为可检索、可管理、可重试、可审计、可迁移的数据生产平台，并同时纳管历史数据。

本文只描述方案，不包含本次代码实现。实现时应以本 PRD 和现有代码的实际行为为准。

## 2. 现状与设计结论

### 2.1 当前能力

- `rosbag-catalog` 当前已具备 MySQL、NAS 定时扫描、ROS 2 SQLite3 bag 元数据解析、Bag/文件/Topic/车辆/场景索引、Web 检索和 systemd 部署；目标版本将数据库切换为 PostgreSQL，并重构为数据管理平台。
- `vla_dataset_builder` 已具备可运行的 phase0 和 phase1 wrapper，支持断点续跑、阶段完成标记和基本质量门禁。
- 当前 `upload_and_run_phase1.sh` 仍面向另一台远端处理机；目标改为任意满足环境要求的个人电脑本地完成 phase0 和 phase1，再将最终结果发布到 NAS 和 A100。
- 当前数据库不记录处理任务、阶段运行、产物、校验和及远端发布状态，因此无法可靠判断“是否已处理、处理到哪一步、结果是否完整”。

新旧系统边界：现有 `rosbag-catalog`（`192.168.2.37`）和其 MySQL 不参与新平台运行；数据管理平台的 PostgreSQL、backend、frontend 和 scanner 部署在约定的管理主机，个人电脑只运行可迁移的处理客户端。历史 NAS 原始数据由全盘扫描重新建库。切换期间旧系统保持只读，确认新平台稳定后再按运维策略下线，不做数据库记录迁移。

### 2.2 总体决策

`rosbag-catalog` 作为数据管理控制面和元数据中心，`vla_dataset_builder` 继续作为计算引擎；新增批次模型、可迁移处理客户端、产物发布器和数据库模型。

PostgreSQL、后端 API 和前端容器化并由 Docker Compose 统一管理。处理客户端不依赖固定主机，不纳入管理平台 Compose；它在当前个人电脑宿主环境运行，直接使用本机 Conda、CUDA、GPU、ffmpeg、硬盘工作区和 A100/NAS 网络。客户端通过后端 API 注册处理会话、回写状态和产物关联，不直接连接数据库。

数据边界固定为：

| 位置 | 保存内容 |
|---|---|
| NAS | 原始 rosbag、最终 phase1 结果、数据库备份 |
| 个人处理电脑本地磁盘 | 从同一车端硬盘拷贝的输入、phase0、phase1、中间文件、日志；任务成功后按策略清理 |
| A100 | 最终 phase1 结果及 manifest，用于公网训练/推理 |
| PostgreSQL | 批次、原始数据、任务状态、阶段状态、产物索引、校验和、审计信息；不保存大文件正文 |

NAS 不保存 phase0 中间结果。个人处理电脑不从 NAS 拉取原始输入，而是从与 NAS 相同的车端硬盘直接拷贝到本地工作区后完成全部计算；NAS 原始副本用于备份、登记、检索和结果关联。

## 3. 目标用户与使用场景

### 3.1 角色

- 数据管理员：登记车辆、维护场景标签、查看数据完整性、处理异常。
- 算法/数据工程师：查看任务和日志，手动触发、暂停、重跑阶段，下载或共享最终结果。
- 运维人员：维护 NAS、PostgreSQL、Compose 服务、处理客户端注册、A100 凭据和告警。

### 3.2 核心场景

1. 车端硬盘先拷贝到 NAS 作为原始备份，同时再拷贝到一台个人处理电脑；NAS 副本自动被发现并登记，并归入一个逻辑采集批次。
2. 只有位于指定目录或具有指定标签的数据自动排队；其余数据由用户在数据管理界面手动触发。
3. 处理失败可以按阶段重试，不重复处理已成功阶段。
4. phase1 完成后，最终结果同时发布到 NAS 和 A100；网络中断支持续传。
5. 用户先按批次浏览汇总信息，再进入批次查看原始 bag；可按车辆、上传时间、采集时间、标签、Topic 和处理状态检索。
6. 任意结果都能追溯到源 bag、流水线版本、参数、主机、GPU、日志和校验和。

## 4. 端到端业务流程

```text
车端硬盘
  -> NAS raw/.incoming/<upload_id>
  -> 稳定性检查与文件校验
  -> 保留现有物理目录或按新数据规范发布
  -> rosbag-catalog 扫描并写入 PostgreSQL
  -> 归入逻辑批次并计算触发策略
  -> 策略命中则自动创建 processing_job
  -> 未命中则等待用户在数据管理界面手动触发
  -> 处理人员在个人电脑注册处理会话，并从车端硬盘拷贝到本地工作区
  -> 客户端将本地副本与 NAS 原始记录按路径、metadata 和指纹关联
  -> phase0（GPU）
  -> phase1（CPU/内存/磁盘为主）
  -> 生成 manifest 与 checksums
  -> 上传 phase1 到 NAS final/.incoming
  -> NAS 校验后原子发布到 final/<dataset_id>
  -> 上传同一结果到 A100 临时目录
  -> A100 校验后原子发布
  -> PostgreSQL 标记完成
  -> NAS/A100 发布成功后按策略清理个人电脑工作目录
```

### 4.1 上传协议

上传方不得直接写正式目录。约定目录：

```text
/vla/raw/.incoming/<upload_id>/
/vla/raw/<dataset_id>/
/vla/final/.incoming/<dataset_id>/
/vla/final/<dataset_id>/
/vla/quarantine/<dataset_id>/
```

上传结束后执行 metadata、分片清单、文件大小和稳定性校验，校验通过后原子改名。`.done` 可作为上传方提示，但不能替代服务端校验。

上传方没有 `<upload_id>` 时不影响识别。`upload_id` 只是一次上传过程的临时追踪号，由平台在发现新目录时自动生成（例如 `scan-<scan_run_id>-<随机后缀>`），不是原始数据的业务主键，也不要求用户预先创建。扫描器先为每个目录建立 `upload_session`，通过路径、发现时间、稳定性检查和结果状态追踪上传过程；校验完成后关闭该 session，并将数据绑定到长期稳定的 `batch_uid`/`bag_uid`。

平台不能用上传时间作为唯一身份。原始数据唯一识别采用分层指纹：

```text
bag_uid = hash(storage_id + canonical_source_path)
content_fingerprint = hash(metadata.yaml 内容 + DB3 文件名/大小/mtime)
```

路径不变时重复扫描幂等；路径发生变化时先依据 metadata 起始时间、消息数、DB3 清单及可选内容摘要生成“疑似同一数据”，进入人工合并队列，不自动覆盖或合并。复制过程中路径或指纹变化时，原记录保留历史版本并回到 `WAITING_STABLE`。

### 4.1.1 原始目录与规范化策略

现有 NAS 原始路径可能只有类似 `/volume1/public/pnc/ros2bags/rosbag2_2026_06_26-14_39_01` 的简单目录，也存在日期、地点、分包和历史项目等多层结构。平台不以目录层级作为批次或唯一身份，采用以下策略：

1. **物理路径保持不动**：历史数据和已上传数据只读扫描，数据库保存 `source_path`，任何规范化都不移动、不重命名、不覆盖原始文件。
2. **逻辑规范化**：根据 metadata、目录名、父目录、采集时间、车辆标识和人工信息生成 `batch_uid`、`bag_uid` 与 `normalized_path`。`normalized_path` 是数据库和结果发布使用的逻辑路径，不代表 NAS 上已发生搬迁。
3. **新数据推荐目录**：`/vla/raw/<batch_uid>/<bag_uid>/`；上传临时目录使用 `/vla/raw/.incoming/<upload_id>/`。只有新建平台目录时才要求物理路径遵循该约定。
4. **历史映射表**：保存原始路径、规范化路径、映射原因、置信度、确认人和确认时间；无法可靠归并时建立独立批次并标记 `NEEDS_REVIEW`。
5. **可选物理整理**：一期不自动移动历史文件。未来如确需整理，必须由独立迁移任务执行复制/校验/原子切换，并保留旧路径别名和回滚记录。

本次方案已对 `/mnt/nas_backup` 做只读目录抽样：存在 `original_ros2bag/2025_1104/<地点>/split_bag_...` 等多层历史目录，也存在其他项目目录。因此批次归并必须支持“目录批次、时间窗口批次、人工批次”三种方式，不能只依赖 `rosbag2_时间` 文件名。

### 4.1.2 原始数据纳管门槛与 metadata 标签

全盘纳管只管理同时满足以下条件的目录：包含可解析的 `metadata.yaml`，且同目录至少存在一个 `*.db3` 文件；不满足条件的目录只写入扫描异常统计，不创建原始数据记录。扫描器不把 `.db3` 单文件、代码目录、结果目录、虚拟环境和临时目录当作数据。

`metadata.yaml` 可直接提取的标签分为两类：

- 技术标签：`storage_identifier`、metadata 版本、Topic 名称/类型、相机 Topic 是否齐全、INS/IMU 是否存在、消息数、时长、分片数和数据完整性结果。
- 时间/来源候选：采集开始时间、目录名时间、父目录地点/日期、文件名后缀中的车辆或设备候选标识。

metadata 通常不包含“雨天、行人、施工”等语义场景标签，不能臆造。此类业务标签来自 `catalog.json`（如存在）、上传表单、批次规则或人工标注；从 metadata 生成的标签必须标记 `source=METADATA`，候选车辆/地点必须允许人工确认。

### 4.2 触发策略

一期采用“PostgreSQL 状态轮询 + Compose 定时服务/客户端 API”，不引入消息队列。自动触发不是默认行为，必须经过触发策略判断：

- NAS scanner：每 5 至 10 分钟扫描，沿用现有 `rosbag-catalog` 扫描能力。
- job creator：扫描成功后，将 `RAW_VERIFIED` 且无活动任务的数据计算触发规则。
- 自动触发条件：数据路径命中配置的自动处理目录前缀，或数据/所属批次带有配置的自动处理标签，且策略处于启用状态。
- 不满足自动触发条件：只登记为 `READY_MANUAL`，不创建处理任务；用户在数据管理界面点击“触发处理”后才创建任务。
- processing client：运行在任意已安装依赖的个人电脑上，由处理人员选择一个待处理数据并创建处理会话；客户端可通过后端登记会话，也支持离线先处理、联网后补交状态。
- publisher：作为客户端阶段，负责从本地结果分别发布到 NAS/A100 并校验。

触发策略必须可配置、可审计：策略包含名称、目录前缀或标签、适用数据类型、流水线版本、优先级、是否启用和生效时间。手动触发必须记录操作者、原因和使用的策略/版本。

后续可同时支持多台个人电脑，通过客户端能力标签、任务认领和并发配额分配任务。

## 5. 数据状态与规则

### 5.1 Bag 业务状态

```text
DISCOVERED -> WAITING_STABLE -> RAW_VERIFIED
RAW_VERIFIED -> PROCESSING_QUEUED -> PROCESSING
PROCESSING -> PHASE1_READY -> NAS_PUBLISHING -> NAS_VERIFIED
NAS_VERIFIED -> A100_PUBLISHING -> A100_VERIFIED -> COMPLETED
```

异常状态：`FAILED_RETRYABLE`、`FAILED_PERMANENT`、`QUARANTINED`、`CANCELLED`、`MISSING`。

- 文件仍在上传、大小或 mtime 变化：`WAITING_STABLE`，不创建任务。
- metadata、DB3 清单、六路相机或 INS 不满足要求：`FAILED_PERMANENT` 或 `QUARANTINED`。
- 网络超时、磁盘不足、进程退出、远端不可用：`FAILED_RETRYABLE`。
- A100 暂时不可用不影响 NAS 结果完成，任务进入 A100 重试队列。

### 5.2 任务租约

`processing_job` 使用 `lease_owner`、`lease_until`、`heartbeat_at` 防止同一数据被多人同时处理。任务认领必须在事务中完成；租约过期后任务可由其他电脑重新认领。客户端注册 `processing_session`，记录电脑标识、操作者、工作目录、代码版本和环境信息。不同电脑可以并行处理不同任务；同一数据默认只允许一个活动会话，但管理员可显式创建新运行。

### 5.3 幂等要求

- 同一 NAS 路径和稳定 manifest 只对应一个 bag。
- 同一 bag 同一流水线版本和参数可复用成功阶段。
- 发布使用临时目录 + 校验 + 原子改名，半成品不可被检索或消费。
- 重试不得删除已确认的 NAS 原始数据和最终结果。

## 6. 数据库模型

数据库改用 PostgreSQL 15+。新系统保留现有 `bag_record`、`bag_file`、`bag_topic`、`vehicle`、`scene`、`scan_job` 的业务语义，但不迁移旧 MySQL 数据库记录。新 PostgreSQL 通过只读扫描 NAS 原始文件重新建立索引，新增批次、触发策略、处理和历史导入实体。使用 Alembic 管理 schema 迁移，不再依赖 `create_all()` 作为生产升级机制。

### 6.1 `data_batch`：一级数据显示对象

批次是平台的业务主对象，可以代表一次硬盘上传、一次车辆采集、一次人工导入或一组历史数据。字段至少包括：

```text
id, batch_uid, name, source_type, vehicle_id,
uploaded_at, collected_from, collected_to,
status, tag_summary, raw_root_path, description,
created_by, created_at, updated_at
```

批次页面显示：批次名称/编号、车辆、上传时间、采集时间范围、数据量、原始数据条数、标签、处理汇总状态、最终结果汇总和异常数。一个批次可以包含多个原始数据目录。

### 6.2 `bag_record`：二级原始数据显示对象

`bag_record` 表示一个可解析的 ROS 2 bag 或原始数据单元，增加：

```text
batch_id, source_path, normalized_path,
path_scheme, discovery_source, first_seen_at, last_seen_at,
upload_started_at, upload_completed_at, data_status,
normalization_status, content_fingerprint
```

原始数据显示：原始路径、规范化逻辑路径、metadata/DB3 文件、大小、Topic、消息数、车辆、标签、上传时间、采集时间、数据状态、处理状态、处理结果和异常信息。原始目录内容只读，不把图片、视频或 DB3 正文放入 PostgreSQL。

### 6.3 标签、车辆和关系

保留 `vehicle`、`scene`，将通用标签抽象为 `tag` 与 `bag_tag`、`batch_tag`。车辆表示采集主体；标签表示数据内容/业务属性；两者不可混用。批次级标签可以继承到原始数据，但原始数据可覆盖或追加标签。

### 6.4 `dataset_artifact`

记录可追踪产物：

```text
id, bag_id, kind, storage, relative_path,
size_bytes, file_count, checksum, checksum_algorithm,
status, created_at, verified_at
```

`kind`：`raw`、`phase1`、`manifest`；phase0 只保留本地运行记录，不登记为 NAS 产物。

### 6.5 `pipeline_run`

记录一次完整运行：

```text
id, bag_id, pipeline_version, git_commit, host_name,
gpu_name, nvidia_driver, cuda_version, python_version,
conda_environment, parameters_json, status,
started_at, finished_at, log_path, error_message
```

同一 bag 可以有多次历史运行，但只能有一个活动运行。

### 6.6 `stage_run`

固定阶段：

```text
LOCAL_COPY
PHASE0
PHASE1_UNZIP
PHASE1_TRAJECTORY
PHASE1_INDEX
NAS_PUBLISH
A100_TRANSFER
```

字段：`pipeline_run_id`、`stage`、`attempt`、`requires_gpu`、`input_path`、`output_path`、`command_json`、`status`、`exit_code`、`output_manifest`、时间和错误信息。

### 6.7 `processing_job`

字段：

```text
id, bag_id, pipeline_run_id, priority, status,
lease_owner, lease_until, heartbeat_at,
retry_count, max_retries, not_before, created_at, updated_at
```

建议索引：`status + priority + created_at`、`lease_until`、`bag_id + status`。任务可以处于 `READY_MANUAL`、`QUEUED`、`CLAIMED`、`RUNNING`、`WAITING_PUBLISH`、`SUCCEEDED` 等状态。

### 6.8 `processing_session` 与本地输入副本

处理客户端每次运行创建一个 session，记录：

```text
id, job_id, bag_id, operator, client_id, host_name,
source_disk_label, local_input_path, local_output_path,
input_manifest, input_fingerprint, pipeline_version,
git_commit, gpu_name, cuda_version, python_environment,
status, started_at, finished_at, last_heartbeat_at
```

`source_disk_label` 不是唯一身份，只用于说明本次从哪块车端硬盘拷贝；`input_fingerprint` 用于确认个人电脑副本与 NAS 原始记录一致。客户端必须在 phase0 前保存本地输入清单（相对路径、大小、mtime，条件允许时增加内容摘要），并将其与 NAS 的 `content_fingerprint` 关联。无法确认一致时允许继续人工强制运行，但必须标记 `INPUT_MISMATCH` 并禁止自动发布，除非管理员确认。

### 6.9 客户端与产物关联

`dataset_artifact` 增加 `processing_session_id`、`source_bag_id`、`manifest_hash` 和 `published_by_client_id`。NAS final 和 A100 目录中的 `manifest.json` 必须包含同一 `bag_uid`、`batch_uid`、`processing_session_id`、`input_fingerprint`、`pipeline_version` 和输出校验和，确保 NAS 备份、个人电脑结果和 A100 数据可以互相追溯。

### 6.10 `processing_trigger_policy` 与 `audit_event`

`processing_trigger_policy` 保存自动触发目录前缀、标签条件、流水线版本、启用状态和优先级；`audit_event` 保存扫描、批次归并、标签变更、手动触发、取消、重试、规范化和发布操作。

### 6.11 迁移与历史导入要求

当前项目通过 SQLAlchemy `create_all()` 建表，平台化前必须引入 Alembic。旧 MySQL 仅保留为历史系统只读参考和备份，不执行 MySQL 到 PostgreSQL 的数据迁移；新 PostgreSQL 的历史数据全部以 NAS 只读扫描结果为准。历史数据采用分阶段导入：先建立批次与原始数据索引，再异步解析 metadata、Topic、文件和标签；不能因升级重新复制大文件，也不能修改 NAS 原始目录。全盘扫描工具的纳管硬门槛是“同目录同时存在可解析 `metadata.yaml` 和至少一个 `.db3`”。导入过程可暂停、可重跑、可记录错误。

历史导入分三轮执行：

1. **盘点轮**：只遍历白名单根目录，记录路径、文件数、字节数、mtime、是否包含 `metadata.yaml`、目录类型和扫描错误；代码目录、虚拟环境、回收站和非数据目录进入排除清单。
2. **索引轮**：对可识别 bag 建立 `bag_record`，按父目录/地点/日期/连续分包和人工规则候选归并 `data_batch`；不能确认的记录标记 `NEEDS_REVIEW`，不自动合并。
3. **增强轮**：异步解析 Topic、车辆候选、标签和完整性；对历史已有结果只登记 artifact 和 manifest 摘要，不重新处理、不自动触发流水线。

历史导入应提供进度、暂停、失败重试、冲突列表和人工确认页面。历史数据默认 `READY_MANUAL`，只有用户明确触发或后续策略命中才进入处理队列。

### 6.10 `upload_session` 与扫描运行

`upload_session` 用于补足用户未提供 upload_id 的情况：

```text
id, generated_upload_id, scan_run_id, source_path,
first_seen_at, last_seen_at, stable_checks,
status, bag_id, error_message
```

`generated_upload_id` 只用于一次发现/校验过程；`bag_uid` 才是长期数据身份。`scan_run` 记录全盘扫描的开始结束时间、扫描根、发现数、纳管数、跳过数、异常数、断点游标和版本。两者均不要求写入 NAS 文件。

## 6.11 全盘扫描与入库脚本

交付独立的只读命令行工具（建议命名 `nas_catalog_import`），支持 `scan`、`resume`、`report`、`retry-errors` 四类操作：

```text
nas_catalog_import scan \
  --root /volume1/public \
  --include-prefix pnc/ros2bags \
  --db-url ... \
  --workers 4 \
  --batch-size 100
```

脚本要求：

1. 只读访问 NAS，禁止创建、删除、重命名、移动和修改任何原始文件。
2. 递归遍历白名单根目录，排除回收站、隐藏目录、代码仓、`.venv`、缓存和结果目录。
3. 先快速发现 `metadata.yaml`，再检查同目录 `.db3`；只有两者同时存在才进入纳管队列。
4. 分页/分批处理，保存断点游标和每批统计；中断后可从上次位置继续，不重复写入。
5. 解析 YAML、记录文件清单/大小/mtime、Topic、消息数、时长、技术标签和路径候选；解析失败写入错误表而不终止全盘任务。
6. 依据路径、metadata 时间和连续分包关系生成批次候选；不确定的批次标记 `NEEDS_REVIEW`。
7. 使用 `source_path + manifest/content_fingerprint` 幂等 upsert；不依据用户 upload_id，不覆盖已有人工标签和车辆关系。
8. 支持 `--dry-run`、速率限制、最大目录数、排除规则配置和 JSON/CSV 报告。

脚本可作为一次性历史导入工具，也可被 scanner 定期调用；历史全盘导入完成后，定时扫描只处理新增/变化路径。

## 7. 个人处理电脑工作区与执行契约

```text
/data/vla-work/
  active/<dataset_id>/
    raw/
    output_phase0/
    output_phase1/
    logs/
    manifest/
  failed/<dataset_id>/<run_id>/
```

执行器负责：

1. 由操作人员将同一车端硬盘中的原始数据拷贝到个人电脑本地工作区；不把 NAS 作为本次计算输入源。
2. 校验本地磁盘配额和 GPU 可用显存，并生成输入清单与指纹。
3. 将本地输入清单与 NAS 中已登记的 `bag_uid`/`content_fingerprint` 关联；找不到匹配项时允许先创建“待关联”会话，但结果发布前必须补齐关联。
4. 激活 `databuilder_env`，调用现有 `run_phase0.sh` 和 `run_phase1.sh`，不重写内部步骤。
5. 读取 `*_done.json`，并额外验证六路 MP4、视频 FPS、`dataset_index.csv` 和 CSV 引用文件。
6. 生成 manifest、日志和阶段耗时，通过 backend API 更新 heartbeat 和状态。
7. 将最终结果从个人电脑分别发布到 NAS final 和 A100；两边校验成功后按用户选择清理本地目录，失败任务保留可配置天数后再清理。

phase0 使用 GPU，默认整 bag 串行；phase1 主要使用 CPU、内存和本地磁盘，`process-count` 必须通过当前电脑基准测试配置，不直接沿用固定 30。每台电脑都必须执行环境自检并登记硬件/软件能力，流程不能依赖固定 IP、固定主机名或固定目录。

## 8. 管理平台部署与个人客户端边界

### 8.1 Docker Compose 管理范围

生产控制面部署在一台约定的管理主机上并使用 Docker Compose，至少包含：

```text
postgres       PostgreSQL 15+ 数据库，持久化 volume
backend        FastAPI/SQLAlchemy/Alembic API 与数据管理界面服务端
frontend       前端静态资源或 Node 构建后的 Web 服务
scanner        可选独立调度容器，负责 NAS 扫描与历史导入队列
```

`backend` 和 `scanner` 通过 Compose 网络访问 `postgres`；数据库端口只在管理主机本机或 Compose 内网可见，不暴露公网。前端与 backend 端口按内网访问策略发布在管理主机，前端只访问 backend API。生产环境使用 `.env`/Docker secrets，不把凭据写入镜像或仓库。

### 8.2 个人处理客户端边界

处理客户端运行在任意个人电脑，保持宿主机运行，不纳入管理平台 Compose：

- 直接使用本机 NVIDIA 驱动、CUDA、Conda `databuilder_env`、ffmpeg、本地磁盘和移动硬盘。
- 通过 HTTPS API 向 backend 注册客户端和处理会话、发送 heartbeat、回写阶段结果；客户端也必须支持命令行离线执行。
- 客户端不负责业务规则判断；自动/手动触发、权限和状态机由 backend 统一执行。
- 电脑更换后可使用同一 job 继续处理，但必须记录新的 `processing_session` 和输入指纹；禁止复用旧电脑的本地路径假设。

### 8.3 Compose 运维要求

PostgreSQL 使用命名 volume、健康检查、定期逻辑备份和恢复演练；backend 使用 Alembic 启动迁移；前端和 backend 使用固定版本镜像。Compose 只负责服务编排，不替代任务租约和数据状态机。

管理主机重启后的启动顺序为：PostgreSQL 健康 -> backend/Alembic -> frontend/scanner。个人电脑客户端不要求与 Compose 同机或同时启动；启动时先执行 backend 健康检查和本地环境自检，再创建/恢复处理会话。数据库 volume 必须位于管理主机本地磁盘，不得放在 `/mnt/nas_backup` 或其他 SMB/NFS 挂载上；备份文件才上传 NAS。

## 9. 产物与发布规范

### 9.1 NAS final 目录

```text
/vla/final/<dataset_id>/
  dataset_index.csv
  planning/
  trajectory/
  cameras/
  manifest.json
  checksums.sha256
```

NAS 不保存 phase0 MP4/JPG 中间目录。

### 9.2 Manifest 最低字段

`dataset_id`、源 bag 路径、流水线版本和 git commit、命令与参数、相机列表、clip/frame 数、视频 FPS、文件数、总字节数、checksum 算法与清单、运行主机、GPU/CUDA/Python 环境、创建时间。

### 9.3 A100 发布

个人处理电脑使用受限 SSH 账号和 SSH key 主动推送，采用 `rsync --partial --checksum`：

```text
/data/xl_infer_dataset/.incoming/<dataset_id>/
/data/xl_infer_dataset/<dataset_id>/
```

A100 端校验 `checksums.sha256` 后原子改名。A100 失败可独立重试，不阻塞 NAS 结果；两端均确认后才删除个人电脑本地工作目录。

## 10. 性能与容量策略

优先级：

1. 先从车端硬盘复制到个人电脑本地磁盘，再计算，避免直接在移动硬盘上进行大量随机 I/O；NAS 仅作为独立备份和结果存储。
2. 单电脑单 GPU 串行 phase0，避免显存和磁盘竞争。
3. phase1 调整 CPU worker，依据当前电脑 CPU、内存和磁盘基准测试设置。
4. 所有大文件传输支持断点续传；大量小文件可在 A100 传输时打包，但 NAS final 仍保留目录结构。
5. phase0 完成后删除可重建中间 JPG，但必须保留 phase0 MP4 直到 phase1 成功。
6. 数据库只保存索引和 checksum，不持续对每个 DB3 重算完整 SHA256；发现或发布阶段使用 manifest/快速指纹，定期抽检全量校验。
7. 在任务和阶段记录字节数、文件数、耗时、吞吐、GPU 利用率、峰值显存、磁盘余量。

开始拷贝和处理前必须检查个人电脑可用空间：建议至少为原始输入 + phase0 峰值 + phase1 峰值 + 20% 安全余量；不足时客户端拒绝启动并提示更换电脑或清理空间。

## 11. 数据管理界面需求

`rosbag-catalog` 的产品定位由“数据追溯”改为“数据管理”。页面导航至少包括：数据管理、批次、原始数据、处理任务、车辆、标签、系统设置。

### 11.1 数据检索

支持批次/原始数据两个对象的检索：名称或 UID、原始路径、规范化路径、车辆、标签、上传时间、采集时间、状态、处理状态、Topic、是否有最终结果。支持批量选择后追加标签、归并批次和手动触发处理。

### 11.2 一级：批次显示

批次列表是默认入口，以卡片或表格展示批次名称、车辆、上传时间、采集范围、原始数据条数、总大小、标签、处理完成数/失败数/待处理数。点击批次进入批次详情，可查看批次下的原始数据列表和整体处理操作。

### 11.3 二级：原始数据显示

原始数据列表/详情展示单个 bag 的原始路径、规范化路径、文件和 Topic 摘要、车辆、标签、上传时间、采集时间、稳定性/完整性状态、任务阶段、失败原因、NAS 原始位置、NAS 最终结果位置和 A100 位置。原始数据页提供“手动触发处理”“从阶段重跑”“重新发布结果”等操作，并要求权限和操作原因。

### 11.4 批次管理

支持创建批次、批量归入、拆分、合并、修改批次标签、指定车辆、补充备注。合并/拆分只修改逻辑关系，不移动 NAS 原始文件，必须产生审计事件。

## 12. 接口与服务边界

### 12.1 数据检索与详情

沿用现有 Bag、车辆、场景、Topic 查询，增加：当前业务状态、活动任务、最新 pipeline run、阶段进度、产物位置、manifest、checksum、失败原因和重试按钮。

### 12.2 任务控制台

支持按状态、车辆、采集时间、优先级和创建时间筛选；查看阶段时间线和日志；执行暂停、恢复、取消、重试、从指定阶段重跑、重新发布 NAS/A100。

### 12.3 资源与告警

展示在线处理客户端的 GPU、CPU、内存、磁盘、工作区、版本和当前 session；告警包括 session 心跳失效、磁盘不足、连续失败、NAS 不可达、A100 传输失败、输入指纹不一致和 checksum 不一致。

### 12.4 共享

结果详情提供 NAS 相对路径、A100 目标路径、manifest 下载和受控 rsync/SSH 命令。Web 不代理大文件。

建议新增内部接口：

```text
POST /api/jobs/{bag_uid}/enqueue
POST /api/jobs/{job_id}/cancel
POST /api/jobs/{job_id}/retry
POST /api/jobs/{job_id}/rerun-from/{stage}
GET  /api/jobs
GET  /api/jobs/{job_id}
GET  /api/bags/{bag_uid}/artifacts
GET  /api/runs/{run_id}/logs
GET  /api/clients/{client_id}/health
POST /api/batches
POST /api/batches/{batch_uid}/merge
POST /api/bags/{bag_uid}/trigger
POST /api/admin/history/import
POST /api/clients/register
POST /api/processing-sessions
POST /api/processing-sessions/{session_id}/associate-input
POST /api/processing-sessions/{session_id}/heartbeat
```

处理客户端通过 backend API 访问 PostgreSQL；客户端不直接连接数据库，不直接修改数据库字段，所有状态转换写入阶段记录和审计日志。

## 13. 安全、备份与审计

- NAS、PostgreSQL、A100 凭据只放 Docker secrets、Compose secret 或个人电脑权限受限的客户端配置文件，不写代码、普通数据库字段、命令行和日志。
- A100 使用受限远端账号、固定目录和最小 SSH 权限。
- Web 一期仅受信任内网；正式共享前增加登录、角色和审计。
- PostgreSQL 使用 `pg_dump`/`pg_restore` 周期备份并定期恢复演练；NAS 使用快照/备份保护 raw 和 final。
- 记录上传者、人工认领、标签变更、任务控制、重试、发布和清理操作。

## 14. 分阶段实施计划

### 阶段 1：数据边界与控制面

建立 `/vla/raw`、`/vla/final`、`.incoming`、quarantine 规范；实现稳定性判定、artifact/pipeline/stage/job/upload_session 表和按策略排队。同步交付只读全盘盘点/索引导入工具。

验收：半成品不进入可处理状态；重复扫描幂等；已有 bag 可回填；未命中目录/标签策略的数据不会自动排队。

### 阶段 2：可迁移个人处理客户端

实现客户端安装/环境自检、移动硬盘到本地工作区拷贝、输入指纹关联、session 心跳、日志、phase0/phase1 调用、断点续跑、资源检查和失败分类。

验收：同一客户端可完成真实 bag；更换另一台满足环境要求的电脑后可继续未完成任务；同一数据不会产生重复活动 session；客户端可以在 NAS 尚未完成扫描时先建立待关联 session，并在发布前完成关联。

### 阶段 3：NAS final 发布

实现 manifest/checksum、临时目录、原子发布、产物登记和结果检索。

验收：NAS 只保存 raw 与 phase1 final；结果半成品不可见；损坏可发现。

### 阶段 4：A100 分发

实现 SSH/rsync 断点续传、远端校验、原子发布和独立重试。

验收：A100 与 NAS manifest 一致；网络中断可续传；A100 故障不影响 NAS 结果。

### 阶段 5：运营平台

加入任务控制台、客户端资源监控、告警、权限、审计和恢复演练，支持多台个人电脑以能力标签和任务认领方式协作。

## 15. 一期验收标准

1. 新 raw bag 上传完成后，最长一个扫描周期内进入 `RAW_VERIFIED` 或明确异常状态。
2. 只有稳定、完整、未被处理且命中自动触发策略的 bag 才能自动创建 `QUEUED` 任务；其他 bag 必须人工触发。
3. 全盘扫描工具只将同目录具备可解析 `metadata.yaml` 和至少一个 `.db3` 的目录纳入原始数据，其他目录不创建 bag 记录。
4. 全盘扫描可断点续跑、幂等入库、输出异常报告，并且全程不修改 NAS 文件。
5. 一个真实 bag 可调用现有 phase0/phase1 完成，并校验六路相机、FPS、索引和引用文件。
6. 个人电脑重启、移动硬盘断开、网络中断或客户端退出后，任务可通过租约恢复，不产生重复活动运行。
7. phase1 结果在 NAS 和 A100 均使用 checksum 校验，临时目录不会被消费。
8. NAS 不出现 phase0 中间结果；个人电脑任务成功后本地工作区可按策略清理。
9. 页面能展示源 bag、任务、每个阶段、日志、manifest、NAS 路径和 A100 路径。
10. 失败可区分可重试和永久失败，支持从失败阶段重跑。
11. 数据库和 manifest 能回答：谁在何时用什么版本、什么参数、在哪台机器上生成了哪个结果。

## 16. 待确认事项

### 16.1 已确认

- NAS 为群晖 `WHBB`，实际地址为 `192.168.2.77`；原始数据共享为 SMB `public`。管理主机和个人处理电脑可按需挂载到 `/mnt/nas_backup`，NAS 端仍由 DSM File Station API 负责扫描和目录元数据访问。
- 管理主机负责运行 Docker Compose；个人处理电脑不固定为某一台机器，按客户端环境自检结果动态注册。
- 现有 `rosbag-catalog` 生产实例位于 `192.168.2.37`，当前是 systemd + Python 虚拟环境 + 原生 MySQL，并非新平台的一部分；旧 Web 入口为 `http://192.168.2.37:8180`，仅作切换期间只读参考。
- 新平台 PostgreSQL、backend、frontend 和 scanner 部署在约定的管理主机；个人处理电脑不固定为某一台机器。不执行 MySQL 到 PostgreSQL 的数据库记录迁移，历史索引通过 NAS 全盘只读扫描重建。
- 一期采用 Docker Compose 管理 PostgreSQL、backend 和 frontend；不部署 K3s/Kubernetes，也不引入消息队列。任务通过 PostgreSQL 状态轮询和服务端租约调度。

### 16.2 仍需业务决策

- A100 的 SSH 账号、目标目录、认证方式（建议专用账号和 SSH key）、网络出口策略、并发/带宽限制及远端校验命令。
- PostgreSQL 版本（建议 15 或更高）、管理主机本地数据库磁盘、数据库备份保留周期和恢复演练频率。
- NAS `raw`、`final`、`.incoming` 和 `quarantine` 的正式目录前缀；原始数据和最终结果的保留周期、删除审批、快照/回收站策略及容量告警阈值。
- 历史数据批次归并规则、`batch_uid`/`bag_uid` 的最终生成规则，以及无法自动归并时的人工确认流程；是否要求上传方提供 `catalog.json`/sidecar 元数据。
- 自动处理触发策略：数据稳定窗口、默认优先级、哪些标签/车辆/批次允许自动处理，以及人工触发是否需要审批和操作原因。
- Web 登录、角色权限、审计范围、局域网访问边界和 A100 结果是否允许通过公网下载；当前 Web 尚未具备生产级认证授权。

### 16.3 实施前必须核验

- 测量个人处理电脑到 NAS/A100 的实际网络吞吐、延迟和断线恢复行为；确认每台电脑工作区容量，按“原始输入 + phase0 峰值 + phase1 峰值 + 20% 余量”确定单任务门槛。
- 记录每台个人处理电脑的 GPU 型号、显存、驱动、CUDA、ffmpeg 和 `databuilder_env` 版本，并通过真实 bag 基准测试确定 phase0 串行策略和 phase1 CPU worker 数。
- 为新平台引入 Alembic 基线和 PostgreSQL schema；通过 NAS 全盘扫描结果核对原始数据数量、路径、状态分布、时间字段和重复路径，不做 MySQL 表级迁移。
- 为 PostgreSQL、backend、frontend 编写 Compose 健康检查、固定版本、持久化卷和密钥注入配置；数据库端口默认不对公网开放。
- 确认个人处理客户端访问 backend API 所需的地址、TLS/令牌、心跳和租约超时；确认更换电脑、移动硬盘断开、NAS 断线、A100 不可达时的恢复和重试行为。
- 建立 PostgreSQL 到 NAS 的定期 `pg_dump` 备份，并完成至少一次独立恢复演练；同时验证 NAS raw/final 快照和备份可恢复性。

## 17. 与现有代码的对应关系

- `rosbag-catalog/app/scanner.py`：保留 NAS 发现、metadata 解析和幂等索引，扩展稳定窗口、自动生成 upload_session、全盘历史扫描、manifest 和按策略任务创建。
- `rosbag-catalog/app/models.py`：保留现有 Bag/Topic/Vehicle/Scene 模型，新增 data_batch、标签关系、artifact、pipeline_run、stage_run、processing_job、trigger_policy、audit_event。
- `vla_dataset_builder/scripts/run_phase0.sh`：继续作为 phase0 计算入口，由个人处理客户端管理环境、GPU、日志和外部状态。
- `vla_dataset_builder/scripts/run_phase1.sh`：继续作为 phase1 计算入口，由个人处理客户端设置本地输入/输出和 CPU 并发。
- `vla_dataset_builder/scripts/backup_to_nas.sh`：不能直接承担新平台最终发布职责，应由带 manifest、原子发布和数据库状态回写的 publisher 替代或封装。
- `vla_dataset_builder/scripts/upload_and_run_phase1.sh`：不再作为主流程；其 rsync、远端锁和校验思路可复用于 A100 publisher。
