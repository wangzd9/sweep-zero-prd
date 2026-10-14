# 自建 VLA 数据集处理链条 PRD（V1）

**版本**：v1.6  
**状态**：第一版落地方案  
**日期**：2026-09-11  
**基础项目**：`rosbag-catalog`、`vla_dataset_builder`  
**详细代码分析**：`/home/wang/work/dataset_build/dataset_processing_analysis.md`

## 当前实现校准（2026-09-21）

本节是本 PRD 与当前代码、迁移、测试和真实验收结果的边界说明；原有章节继续保留为 V1 目标和设计依据。当前事实以代码、`HANDOFF.md`、`docs/project-status.md` 和唯一任务追踪文件 `/home/wang/work/doc/todo/vla_self_dataset_pipeline_v1_todo.md` 为准。

### 已落地能力

- Phase0 的唯一正式执行入口是处理机宿主机 `rosbag-phase0-proxy.service`；Compose 中的 Orchestrator 通过 Backend API 和本机代理调度，Backend 是业务数据库唯一写入口。
- 当前数据库为 MySQL 8.4，使用 Alembic；处理机 MySQL 使用命名卷，并由 systemd timer 每 6 小时分别备份到处理机和 NAS，保留最近 7 天。真实隔离恢复、迁移回滚和 DatasetFrame 容量/索引基线已完成。
- 正式路径为：NAS incoming `/public/vla_dataset_builder_backup/raw_rosbags`、NAS ready `/public/vla_dataset_builder_backup/ready_rosbags`、A100 staging `/data/xl_origin_dataset_staging/<run>/<bag>`、Phase0 `/data/xl_origin_dataset/<bag>`、Phase1/Phase3 `/data/xl_infer_dataset/<bag>`、NAS final `/mnt/nas_backup/vla_dataset_builder_backup/final/<dataset_version_id>`。
- 自建 clip 新输出统一使用 `<完整 bag_name>_clipNNN`；`input_clipNNN` 仅作为历史 Phase1 输入兼容格式，不得进入新的 Phase1/Phase3 结果、DatasetFrame 或 NAS final。
- Phase1 `dataset_index.csv` 已解析、校验并分批幂等 upsert 为 DatasetFrame；已有真实导入包括初始链路 747 条，以及生产路径绑定流水线 34721 条，均已完成对账。
- `result-manifest-v1`、文件 hash/大小/数量、`parent_artifact_id`、SourceCopy/Artifact 生命周期字段和基础血缘已落地；NAS final 使用原子发布。
- 自动重试已在本地实现：最多 2 次，退避 60/120 秒，仅对白名单故障重试；已确认退出码 137 和可证明未启动的连接/路由/代理拒绝故障。未知启动结果、租约过期、输入/质量/冲突/磁盘/配置/清理错误先对账或进入人工处理。该版本尚未部署到处理机。

### 尚未达到的目标态

- 动态相机集合/数量、NPY shape、轨迹覆盖率、navigation/description 覆盖率等业务质量规则，以及结构化质量报告和完整发布阻断语义仍未全部实现。
- final 发布后的只读保护、页面完整血缘视图、SourceCopy/Artifact 历史路径删除状态展示仍需补齐。
- 代理进程重启后按运行文件/PID 恢复、Phase1/SSH 未知启动结果对账和在途真实故障复验仍需继续；本地隔离测试已覆盖部分边界。
- `cot_gen_rule.py` 当前按范围记录为 `SKIPPED`，不应描述为已完成 CoT 能力。
- 本地是默认开发和测试环境；只有用户在当前任务明确要求并执行 `./scripts/deploy_processing_machine.sh --apply --production` 时，才更新处理机生产系统。

## 1. 文档目的

本文只设计自建数据集从车端采集到最终结果回传 NAS 的第一版自动化链路，不扩展为大而全的数据平台，不引入 Kubernetes、Argo、Airflow 或多 A100 资源池。这里的“不引入多 A100”不限制单台 A100 增加多个 Worker、计算 slot 或 VLM permits；单机并发上限由资源池配置和压测结果决定。

本文件与 `vla_nvidia_dataset_pipeline_v1_prd.md` 共同作为当前 V1 实施基线。`vla_unattended_workflow_prd.md` 是更长期的概念方案；如果其 Worker、GPU 调度或全自动 Phase0 描述与本文件冲突，以这两份路线 V1 PRD 为准。

第一版要解决的核心问题是：

```text
车端采集
  -> NAS 保存原始数据
  -> NAS Scanner 发现稳定目录
  -> 数据管理平台所在内网机器自动复制到本地工作目录
  -> 该机器上的 Phase0 Worker 执行 Phase0
  -> Phase0 完成后自动上传 A100
  -> 数据管理平台登记任务
  -> Orchestrator 按队列触发 A100 Phase1 及后续流程
  -> 监控 A100 状态并回写后端
  -> 最终结果从 A100 回传 NAS
  -> 建立原始数据、处理任务和结果之间的数据血缘
```

## 2. 已确认的现实约束

1. 数据管理平台以 `rosbag-catalog` 为基础。
2. 数据管理平台部署在内网一台长期在线机器上。
3. 该机器运行前端、后端、数据库和 Orchestrator。
4. 数据库第一版沿用现有 MySQL，不做历史数据库迁移。
5. 预计 3～5 个用户向 NAS 复制不同数据；Phase0 统一在数据管理平台所在内网机器上执行。
6. 用户只需将同一块硬盘中的原始数据复制到 NAS raw 目录。
7. 用户无需提交处理任务；Scanner 发现稳定数据后自动创建任务，平台机自动复制并执行 Phase0。
8. Phase0 结束后，由内网机器自动上传结果到唯一一台公网 A100。
9. A100 主要运行 Phase1 及之后的处理流程；Phase1 主要消耗 CPU、内存、磁盘，不假定必须使用 GPU。
10. A100 不主动访问内网后端，第一版由内网 Orchestrator 通过 SSH/rsync 发起连接。
11. A100 只有一台，因此后续任务必须排队并受资源配额约束；V1 初始可以只运行一个计算型任务，但 Worker 数、资源容量和单任务并发必须配置化，为单机提高并发预留能力。扩容时必须同时评估 CPU、内存、磁盘 I/O、网络、VLM 服务和 `/data` 可用空间，不能只增加 Worker 数。
12. NAS 保存原始数据和最终结果；Phase0 输入使用内网平台机本地暂存副本，不直接在 NAS 上进行高并发读写。
13. MySQL 只允许 `rosbag-catalog backend` 访问；Phase0 Worker、Orchestrator 和前端均通过 Backend API 读写业务数据。
14. A100 数据根目录、代码目录和 bag 级目录结构沿用当前生产环境，不另建一套平行目录规范。

## 3. 第一版目标与非目标

### 3.1 目标

- NAS 新增数据被 Scanner 发现后，内网 Phase0 Worker 自动执行 Phase0 并进入后续链路；界面只保留查看、重试和异常处理入口；
- 自动生成稳定的 `source_id`、`pipeline_run_id` 和 manifest；
- 自动将 Phase0 结果上传 A100；
- Orchestrator 以 `SELF_BUILT_QUEUE` 管理自建数据任务，并通过资源租约控制唯一 A100；
- 自动运行 Phase1、导航和场景描述等已确认步骤；
- 自动检查 done 文件、索引、图片和 NPY 引用；
- 自动将最终结果从 A100 回传 NAS；
- 数据管理平台可查看任务状态、日志摘要、路径和血缘关系；
- 支持断点续传、任务重试和 A100 暂时不可用；
- 3～5 个用户可以同时向 NAS 复制不同数据；Scanner、Phase0 和 A100 后续步骤均由统一队列和资源池控制，不互相覆盖。

### 3.2 非目标

- 不改写 Phase0、Phase1 内部算法；
- 不处理 NVIDIA 数据集；
- 不做 NAS 历史数据全盘治理；
- 不切换 PostgreSQL；
- 不部署 Kubernetes、Argo、Airflow；
- 不建设多 A100 调度；
- 不让大模型直接执行任意 Shell；
- 不把 DB3、图片和 NPY 正文存进数据库；帧级索引、标签、时间戳和文件引用写入数据库。
- V1 暂不建设用户、角色和细粒度权限管理，先依赖内网网络边界；后续单独增加 RBAC。

## 4. 产品角色和组件

### 4.1 组件

```text
内网管理机
├── rosbag-catalog frontend
├── rosbag-catalog backend
├── MySQL
├── rosbag-catalog scanner
│   └── 只调用 Backend API，不连接 MySQL
├── VLA Orchestrator
│   └── 只调用 Backend API，不连接 MySQL
├── Phase0 Worker / wrapper
└── 本地 Phase0 处理暂存目录

公网 A100（1 台）
└── Phase1/Phase3 处理环境

NAS
├── 原始 rosbag
└── 最终结果
```

### 4.2 数据管理平台职责

- 展示原始数据和批次；
- 保存 `source_id`、NAS 路径、文件指纹和车辆等元数据；
- 保存处理任务、步骤状态、日志地址、结果地址；
- 提供任务查询、手动重试和异常查看接口；
- 展示从原始 bag 到最终结果的血缘；
- 作为业务数据唯一写入口，负责幂等、状态机校验、租约和事务；
- 运行或接收 NAS 增量扫描结果，以轻量指纹登记 `NAS_RAW` 副本；
- 不在 HTTP 请求中同步执行长时间任务；由独立 Phase0 Worker 和 Orchestrator 异步执行。

### 4.3 Orchestrator 职责

- 通过 `rosbag-catalog backend` API 领取待处理任务；
- 按 `SELF_BUILT_QUEUE` 的优先级和提交时间调度，并按步骤申请 A100 资源额度；
- 通过固定 SSH/rsync 模板上传、执行和查询；
- 管理任务租约、资源额度和 A100 槽位锁；
- 监控远程进程、done 文件、日志和超时；
- 执行校验器；
- 触发 NAS 回传；
- 通过 Backend API 回写状态、指标和产物血缘；
- 不持有数据库账号，不导入数据库 ORM，不读取或修改 MySQL 表。

### 4.4 Phase0 Worker 职责

- 从平台领取 `PHASE0_QUEUE` 中待处理任务；
- 根据 Backend 返回的 NAS 路径，将原始 rosbag 自动复制到内网管理机的隔离暂存目录，并校验副本完整性；
- 从本地暂存副本读取原始 rosbag，执行现有 Phase0 算法；
- 检查 Phase0 输出完整性并生成 source/phase0 manifest；
- 将 Phase0 结果断点上传到 A100 独立暂存根；
- 通过 Backend 回写步骤状态、产物和错误；
- 不直接修改数据库，不在 Web 请求线程中运行长任务。

## 5. 端到端流程

### 5.1 正常流程

```text
1. 车端完成 rosbag 采集
2. 用户将硬盘数据复制到 NAS raw 目录
3. NAS Scanner 确认目录稳定，Backend 自动创建 source 和 `PHASE0_QUEUE` 任务
4. Phase0 Worker 将原始数据准备到内网本地暂存目录
5. Phase0 Worker 执行 run_phase0.sh
6. Worker 检查 Phase0 输出并生成 manifest
7. Worker 将 Phase0 结果暂存到 A100 `/data/xl_origin_dataset_staging/<pipeline_run_id>/<bag_name>/`
8. Worker 校验远端文件清单并通知 Backend 上传完成，Backend 使任务进入 SELF_BUILT_QUEUE
9. Orchestrator 领取任务后，将该 bag 原子移动到 `/data/xl_origin_dataset/<bag_name>/`
11. Orchestrator SSH 执行 A100 Phase1
12. Phase1 完成后执行结果校验
13. Orchestrator触发自建导航步骤
14. Orchestrator触发场景描述步骤（按配置启用）
15. Orchestrator生成最终 manifest 和 quality_report
16. 帧索引导入器按批次把最终有效帧及标签写入 MySQL
17. Orchestrator从 A100 `/data/xl_infer_dataset/<bag_name>/` 复制最终结果到 NAS final/.incoming
18. NAS 结果校验通过后原子发布
19. Orchestrator调用 Backend 记录 NAS final 路径、A100 路径和帧索引版本，任务进入 PUBLISHED
```

### 5.2 通信方向

```text
内网 Phase0 Worker -> 内网 Backend：登记、状态回写
内网 Phase0 Worker -> A100：rsync 上传 Phase0
内网 Orchestrator -> A100：SSH 执行和查询
内网 Orchestrator -> NAS：复制最终结果
内网 Backend -> MySQL：保存状态
内网 Orchestrator -> Backend API：领取任务、续租、状态和血缘回写
```

第一版不要求：

```text
A100 -> 内网 Backend
```

因此不需要暴露内网 Backend 公网端口。A100 只需要开放 SSH 端口，且 SSH 连接由内网管理机主动建立。

## 6. 用户操作方式

普通用户只需要完成两件事：

1. 将原始 rosbag 复制到 NAS raw 目录；
2. 等待 Scanner 自动发现并触发处理；界面用于查看状态、重试失败任务和检索结果。

Backend 创建任务并进入 `PHASE0_QUEUE`。平台机上的 Phase0 Worker 自动完成：

```text
校验 NAS Scanner 已登记且原始 rosbag 稳定
-> 读取 Backend 返回的 source_id 和 NAS manifest
-> 执行 Phase0
-> 校验 done/clip/相机输出
-> 生成 source_manifest.json 和 phase0_manifest.json
-> rsync 到 A100 staging
-> 校验远端暂存文件清单
-> 回写 phase0-complete，进入 SELF_BUILT_QUEUE
```

管理员诊断时可以在平台机执行统一 wrapper，但该入口也必须携带或创建 `pipeline_run_id`，并通过 Backend 回写状态，不能绕过调度器直接触发 A100 Phase1。

## 7. Phase0 输入输出约定

### 7.1 输入

原始目录必须至少包含：

```text
metadata.yaml
rosbag2_*.db3
```

开始 Phase0 前应确认 NAS 目录不再增长。Phase0 Worker 先从 NAS 将原始输入复制到平台机本地暂存副本，再从本地副本执行处理；不在 NAS 上直接运行 Phase0。平台机本地暂存目录按 `pipeline_run_id/bag_name` 隔离，Phase0 Worker 不在 Web 请求线程中运行。

### 7.2 Phase0 输出

```text
output_phase0/<bag_id>/
├── camera_extract_done.json
├── imu_done.json
├── planning_done.json
├── sample_done.json
├── clip_done.json
├── resize_done.json
├── mp4_done.json
├── scheduler_phase0.log
└── <clip_id>/
    ├── ins.json
    ├── planning.json
    ├── sample.json
    └── cam_*/cam_*.mp4
```

Phase0 Worker 必须检查：

- bag 级关键 done 文件存在且 status=done；
- 每个 clip 存在；
- 每个 clip 具备 6 路 MP4；
- MP4 非空且可读取；
- `ins.json`、`sample.json` 存在；
- 日志没有未处理异常。

## 8. A100 后续处理流程

### 8.1 A100 现有生产目录契约

```text
/home/xmyf/mikelee/proj_dataset_builder/scripts/  # 自建数据集处理代码
/data/xl_origin_dataset/<bag_name>/               # 平台机上传的 Phase0 结果，Phase1 输入
/data/xl_infer_dataset/<bag_name>/                # Phase1 及后续处理结果
/data/xl_maps/maps/dataset_map_<map_name>/        # 导航步骤使用的地图
```

V1 不再设计 `/data/vla_pipeline/incoming|work|published` 平行目录。自动化必须兼容 A100 已有脚本和数据组织：bag 目录名在 `xl_origin_dataset` 与 `xl_infer_dataset` 下保持一致，Phase1 继续使用：

```text
run_phase1.sh \
  --input-dir /data/xl_origin_dataset \
  --output-dir /data/xl_infer_dataset
```

为避免 Phase1 读取未上传完整的数据，新增独立传输暂存根：

```text
/data/xl_origin_dataset_staging/<pipeline_run_id>/<bag_name>/
```

校验成功后，再在 A100 同一文件系统内原子移动为：

```text
/data/xl_origin_dataset/<bag_name>/
```

暂存目录不能放在 `/data/xl_origin_dataset` 内：服务器现有 `scheduler_phase1.py` 会枚举输入根下的所有一级目录，并不会忽略点目录，否则 `.incoming` 也会被误当成 rosbag。暂存根是自动化新增的传输设施，不改变现有正式数据根目录。只有 Worker 领取任务并取得对应 `DATASET_PATH:<key>` 路径锁后，才把该 bag 原子移动到正式输入根；其他排队任务继续留在 staging。提高并发前必须先让 Phase1 只处理显式 `--bag-name`，不能再扫描并处理正式输入根中的其他目录。正式路径已经存在时，Backend 根据轻量指纹和任务状态决定复用或拒绝，自动化不得直接覆盖。

### 8.2 服务器只读复核结论（2026-09-10）

在 A100 上只读检查到：

```text
/data/xl_origin_dataset/rosbag2_JLL15SZTBR2510001_2026_09_08-09_57_23/
├── metadata.yaml
└── rosbag2_JLL15SZTBR2510001_2026_09_08-09_57_23_0.db3

/data/xl_infer_dataset/rosbag2_JLL15SZTBR2510001_2026_09_08-09_57_23/
├── *_done.json
└── <bag_name>_clipNNN/
    ├── cam_*/<timestamp>.jpg
    ├── trajectory/*.npy
    ├── dataset_index.csv
    ├── planning.csv
    ├── nav_done.json
    ├── clip_description.txt（已生成的 clip 才有）
    └── cot/cot_rule.json（当前仅占位结果）
```

这暴露出一项现存不一致：服务器唯一样例的 `xl_origin_dataset/<bag_name>` 是原始 rosbag，但当前 `upload_and_run_phase1.sh` 明确定义该路径应接收“完成后的 Phase0 bag”，`run_phase1.sh` 也把它视为 Phase0 输入根。V1 以当前可执行脚本契约为准：NAS 保存原始 rosbag，A100 的 `xl_origin_dataset` 保存 Phase0 结果。上线前必须盘点该目录；发现仅含 `metadata.yaml + DB3` 的目录时标记为 `LEGACY_RAW_CONFLICT`，不得覆盖或自动处理，由管理员决定迁出或保留。服务器本次复核未对该样例做任何改动。

同一样例只包含 5 路相机 topic 和 5 个相机结果目录，而当前上传脚本要求 6 路相机。它只能作为历史结构参考，不能作为 V1 的六相机验收样例；新数据按 `metadata.yaml` 和当前 `camera_config_6cams.yaml` 做六路完整性校验。

### 8.3 Phase1

Orchestrator 调用现有 `run_phase1.sh`：

```text
Phase0 output
  -> unzip_mp4.py：MP4 解码为 JPG
  -> gen_trajectory.py：生成 history/future NPY
  -> gen_inference_index.py：生成 dataset_index.csv
```

第一版建议参数：

```text
process_count: 8
max_bag_workers: 1
reduce_on: false
```

先保留 JPG，确认结果和备份成功后再考虑 reduce，避免删除唯一中间副本。

### 8.4 导航

调用 `phase3/nav_gen.py`，输入：

```text
dataset_index.csv
planning.csv
地图 `/data/xl_maps/maps/dataset_map_<map_name>/nav_detail.csv`
```

输出：

```text
dataset_index.csv 追加 navigation 字段
nav_done.json
```

地图缺失或地图名不明确时任务进入 `QUARANTINED`，不允许静默使用错误默认地图。

### 8.5 场景描述

调用 `phase3/description_gen_llm.py`，读取前向广角图片并调用 Qwen vLLM，输出：

```text
clip_description.txt
```

第一版该步骤可以配置为开启或关闭，但如果开启，必须检查返回 `content` 非空，不能只检查 HTTP 200。

### 8.6 CoT 现状

A100 样例存在 `<clip>/cot/cot_rule.json`，代码入口为 `phase3/cot_gen_rule.py`。但远端源码明确标记规则生成仍为 TODO，当前只按帧输出空 `cot` 占位值。因此 V1 可以登记该文件为 `COT_PLACEHOLDER` artifact，但不得把它视为有效真值或作为发布成功的必要条件；规则完善和多模态复核留到后续版本。

### 8.7 最终校验

必须同时检查：

- `index_done.json`、`nav_done.json` 等状态文件；
- `dataset_index.csv` 非空且可解析；
- 每行图片路径存在；
- history/future NPY 存在且 shape 合法；
- Planning 对齐字段符合阈值；
- navigation 覆盖率符合配置；
- 场景描述文件格式正确；
- manifest 和 checksum 完整。

## 9. A100 队列和 Orchestrator

### 9.1 队列与初始运行策略

多个 Phase0 Worker 可以处理不同 bag；Phase0 完成后任务进入自建数据专用逻辑队列：

```text
queue_name=SELF_BUILT_QUEUE
```

队列记录：

```text
pipeline_run_id
source_id
queue_name
submitted_at
priority
status=SELF_BUILT_QUEUE
```

队列内部默认按照 `priority DESC, submitted_at ASC` 执行。普通任务 priority 相同，即先进先出。管理员可以调整优先级，但必须留下审计记录。

V1 初始配置可以设置 `SELF_BUILT_WORKERS=1`、计算资源容量为 1，以降低首次上线风险；但这只是部署配置，不是数据库约束或代码上限。后续在同一台 A100 上压测通过后，可以增加 Worker 和资源容量，无需改变 PipelineRun、StepRun、Artifact 或状态机结构。

接入 NVIDIA 路线后，NVIDIA 使用独立的 `NVIDIA_QUEUE`。两条队列由同一个 Orchestrator 服务管理，不能因为 NVIDIA 长时间下载阻塞自建任务领取。

### 9.2 Worker 池

Orchestrator 按配置启动 Worker：

```text
SELF_BUILT_WORKERS=1   # V1 初始值，后续可提升
NVIDIA_WORKERS=1       # NVIDIA PRD 接入后启用
```

每个 Worker 每次只持有一个任务租约。数据库不得建立“一条队列只能有一个 RUNNING 任务”的硬约束；实际并发由 Worker 数和资源租约共同限制。

主循环：

```text
每 5 秒：
  1. Worker 调用 Backend，按 queue_name 原子领取任务
  2. 持续发送任务租约 heartbeat
  3. 检查 A100 SSH、磁盘、目录和代码版本
  4. 为 DAG 下一步骤申请所需资源额度
  5. 资源不足时进入 RESOURCE_WAIT，保持任务租约但不启动进程
  6. 获得资源后执行固定 wrapper
  7. 轮询 PID、机器可读状态文件、done 文件和日志
  8. 校验成功后推进下一步骤并释放资源
  9. 失败时分类、限次重试或隔离
 10. 通过 Backend API 回写状态、指标和产物
```

### 9.3 任务租约与资源租约

必须区分：

- 任务租约：表示哪个 Worker 负责当前 PipelineRun；
- 资源租约：表示某一步可以使用多少 A100 共享资源；
- 路径锁：保证同一 bag 或 dataset version 只有一个写入者。

资源池初始配置：

| 资源池 | V1 初始容量 | 使用步骤 | 后续扩容方式 |
|---|---:|---|---|
| `A100_COMPUTE_IO` | 1 slot | Phase1、CPU 导航、重型校验 | 压测后增加 slot |
| `VLM_PERMITS` | 4 units | 导航 VLM、场景描述 | 增加 permits 并按任务分配 units |
| `NAS_PUBLISH` | 1 slot | 最终结果回传 NAS | NAS 吞吐允许后增加 slot |
| `DATASET_PATH:<key>` | 1 slot | 对同一正式目录写入 | 永远保持 1 |

Backend 使用数据库事务管理 `ResourcePool` 和 `ResourceLease`；A100 再使用槽位级 `flock` 作为第二层保护。容量为 1 时使用 `slot-0`，容量提高后增加 `slot-1`、`slot-2`，不能继续使用一个固定全局锁阻止所有并发。

示例：

```text
/tmp/vla_compute_io.slot-0.lock
/tmp/vla_compute_io.slot-1.lock
/tmp/vla_nas_publish.slot-0.lock
/tmp/vla_path.<safe_hash>.lock
```

资源租约至少记录 `executor_id`、`units` 和 `slot_id`。当前只有一台 A100，`executor_id` 固定为该机器；提前保留该字段可以避免以后增加机器或拆分资源池时迁移核心运行记录。

### 9.4 SSH 执行原则

Orchestrator 只允许调用固定模板，例如：

```text
rsync Phase0 -> /data/xl_origin_dataset_staging/<run_id>/<bag_name>
atomic move -> /data/xl_origin_dataset/<bag_name>
slot flock -> run_phase1.sh --bag-name <bag_name>
slot/permit -> nav_gen.py --bag-name <bag_name>
slot/permit -> description_gen_llm.py --base-dir <single_bag_result>
```

不允许把用户输入直接拼接成任意 SSH 命令。A100 密钥放在权限受限的 Secret 文件中，不能进入数据库、日志或 PRD。

## 10. 多进程和单机并发控制

### 10.1 平台机 Phase0

Phase0 统一由内网平台机上的 `Phase0WorkerPool` 执行。每个 Worker 使用独立工作目录和 `pipeline_run_id`，不同用户任务不会互相覆盖。V1 初始建议 `PHASE0_WORKERS=1`，确认 CPU、内存和磁盘吞吐后再增加；Phase0 与 A100 后续处理使用独立资源池。

### 10.2 A100 Phase1

V1 初始建议：

```text
SELF_BUILT_WORKERS=1
A100_COMPUTE_IO capacity=1
每任务 Phase1 process_count=8
每任务 max_bag_workers=1
```

后续提高单机并发时，应同时调整外层任务数和单任务内部进程数。例如先比较：

```text
方案 A：1 个 Phase1 × process_count 8
方案 B：2 个 Phase1 × 每任务 process_count 4
```

只有方案 B 的单位时间总完成量更高，并且错误率、内存峰值、磁盘延迟处于阈值内，才把 `A100_COMPUTE_IO capacity` 和 `SELF_BUILT_WORKERS` 提高到 2。不能只增加 Worker 而保留每任务最大进程数。

### 10.3 Phase3 导航

导航规则主要消耗 CPU 和文件读取，可以在不同 bag 间并行，但每个任务必须先取得计算额度，并保证一个 clip 和一个输出目录只有一个写入者。

### 10.4 Phase3 VLM

VLM 不使用“整步独占锁”，而使用可计数额度：

```text
VLM_PERMITS capacity=4             # V1 初始值
一个任务申请 units=2              # 示例
任务实际 parallel × intra_threads <= 获得的 units
```

后续可以把容量提高到 8、16，并允许多个任务受控共享 VLM 服务。额度值必须通过压测确定，不能让每个脚本各自使用默认并发。导航 VLM 和场景描述使用同一个 `VLM_PERMITS` 资源池。

### 10.5 并发安全前提

提高 Worker 或资源容量前，必须满足：

- Phase1 可以按单 bag 运行，不再扫描输入根全部一级目录；
- 每个 run 使用独立日志和状态目录；
- 不同 bag 的正式输入、输出目录互不重叠；
- 临时文件名包含 `pipeline_run_id` 或写入任务私有目录；
- 地图只读；
- 共享缓存和固定文件不存在无锁覆盖；
- wrapper 只获取 Backend 分配的 slot；
- 同一 `DATASET_PATH:<key>` 容量永久为 1。

只要任一脚本仍会扫描并修改其他 bag，`A100_COMPUTE_IO capacity` 就必须保持 1。

### 10.6 资源监控与自动降载

Orchestrator 记录：

```text
CPU 使用率
内存峰值
磁盘剩余空间
磁盘读写吞吐和延迟
进程数
每个 Worker/slot 使用情况
VLM permits 使用量、请求数、耗时和失败率
每个步骤耗时
```

V1 可以人工根据指标调整容量。P1 增加自动降载：磁盘延迟、内存压力、剩余空间或 VLM 错误率超过阈值时，停止发放新的资源租约，但不强杀已经运行的步骤。

### 10.7 单台 A100 扩容路径

容量提升按配置档位发布，不能直接在线随意改数字：

```text
concurrency-safe-1:
  self_built_workers: 1
  compute_io_slots: 1
  phase1_process_count_per_task: 8
  vlm_permits: 4

concurrency-safe-2:
  self_built_workers: 2
  compute_io_slots: 2
  phase1_process_count_per_task: 4
  vlm_permits: 8
```

每个 `PipelineRun` 保存实际使用的容量配置版本，保证发生问题时可以还原运行条件。扩容流程固定为：

```text
隔离测试目录压测
-> 比较单任务和多任务总吞吐
-> 校验 CPU/内存/磁盘/VLM 指标
-> 验证输出一致性
-> 发布新的容量配置版本
-> 小流量启用
-> 达到阈值自动回退为上一档
```

扩容成功标准是单位时间完成的 bag 数增加，而不是同时运行的进程数增加。若两个并行 Phase1 的总完成时间、失败率或磁盘延迟劣于单任务模式，应保持 `compute_io_slots=1`，只提高下载、VLM 或其他已证明有收益的局部并发。

## 11. 数据库与数据血缘

第一版继续使用 `rosbag-catalog` 现有 MySQL，在其基础上新增处理相关表。

数据库边界是强制约束：只有 `rosbag-catalog backend` 持有 MySQL 连接信息并操作这些表。Frontend、Phase0 Worker 和 VLA Orchestrator 均调用 Backend API；即使它们与 Backend 部署在同一台内网管理机，也不得直接查询或更新数据库。这样可将幂等校验、状态转换、事务和审计集中在一个服务中，避免 Orchestrator 与数据库表结构耦合。

### 11.1 扩展现有 `bag_record`

当前 `rosbag-catalog` 已使用 `bag_record` 表记录原始 bag。V1 不再新增含义重复的 `data_sources` 表，而是在 `bag_record` 上补充指纹和源数据状态。现有 `bag_uid` 继续作为数据库唯一标识，并在新 API 中以字段名 `source_id` 对外返回，避免维护两套业务 ID。

```text
bag_uid（API 对外名称 source_id）
bag_name
dataset_type=self_built
vehicle_id
collected_at
nas_raw_path
file_count
total_bytes
fast_fingerprint
fingerprint_version
metadata_json
source_status
```

平台机路径、A100 路径和 NAS 最终路径不能放在 `bag_record` 单值字段中，统一进入 `source_copies` 或 `artifacts`，否则多人提交和多次重跑会互相覆盖。

### 11.2 `source_copies`

记录副本：

```text
source_id
storage_type: NAS_RAW / PLATFORM_LOCAL_RAW / A100_PHASE0 / A100_INFER / NAS_FINAL
host_name
path
manifest_hash
fast_fingerprint
verification_status
last_verified_at
```

### 11.3 `pipeline_runs`

记录一次完整处理：

```text
pipeline_run_id
source_id
pipeline_version
config_hash
submitted_by
submitted_at
status
current_step
started_at
finished_at
last_error
```

### 11.4 `step_runs`

记录每个阶段：

```text
step_run_id
pipeline_run_id
step_name
status
attempt
worker=orchestrator/a100
command_template
log_path
input_manifest_hash
output_manifest_hash
metrics_json
error_class
started_at
finished_at
```

### 11.5 `artifacts`

记录产物：

```text
artifact_id
source_id
pipeline_run_id
parent_artifact_id
artifact_type
storage_type
path
file_count
total_bytes
manifest_hash
schema_version
```

血缘关系：

```text
NAS 原始 bag
  -> 平台机本地原始副本
  -> Phase0 artifact
  -> A100 Phase1 artifact
  -> Navigation/Description artifact
  -> Final dataset artifact
```

### 11.6 帧级数据索引（百万帧规模）

Phase1/Phase3 生成的 `dataset_index.csv` 是后续训练检索的主依据。V1 在 Backend 中增加帧级索引表，但只保存结构化元数据、标签和相对文件路径，不把 JPG/MP4/NPY 二进制写入 MySQL。

```text
dataset_frame
  id BIGINT UNSIGNED AUTO_INCREMENT
  source_id / pipeline_run_id / artifact_id
  clip_id VARCHAR(128)
  frame_id INT
  sample_id VARCHAR(256)       # source_id/clip_id/frame_id
  ego_ts_us BIGINT
  camera_paths_json JSON       # 各相机 f0..f3 相对路径
  camera_ts_json JSON
  history_path VARCHAR(512)
  future_gt_path VARCHAR(512)
  planning_frame_id INT NULL
  planning_available TINYINT
  planning_ego_time_diff_ms DOUBLE NULL
  routing_path_index INT NULL
  navigation_text TEXT NULL
  description_text TEXT NULL
  labels_json JSON NULL
  quality_status VARCHAR(32)
  created_at / updated_at
```

约束和索引：

```text
UNIQUE(dataset_frame(source_id, clip_id, frame_id, pipeline_run_id))
INDEX(dataset_frame(source_id, clip_id, frame_id))
INDEX(dataset_frame(ego_ts_us))
INDEX(dataset_frame(planning_available, quality_status))
INDEX(dataset_frame(routing_path_index))
```

百万帧对当前 MySQL 可行。以每帧约 1～4 KB 的结构化字段估算，数据行本身约 1～4 GB，考虑二级索引、JSON、事务和增长余量，建议至少预留 10～20 GB 专用空间；真正占空间的是 NAS/A100 上的图片和 NPY，不进入数据库。写入必须按 1,000～10,000 帧批量提交，使用 bulk insert/upsert，禁止逐帧 HTTP 请求和逐帧事务。

V1 不为每帧建立几十个相机子表；相机路径和时间先以 JSON 保存，常用检索字段单独列。达到数百万帧后按 `source_id` 或采集月份进行分区/分表评估，先在 MySQL 8 使用逻辑分区预留能力；如果查询延迟、索引体积或并发增长超过阈值，再迁移帧索引到独立的 PostgreSQL/列式检索库，处理任务主库仍由 Backend 管理。

帧索引导入以 `dataset_index.csv` 的 `frame_id` 为主键来源，并通过 `source_id + clip_id + frame_id` 关联原始 bag、Phase0、A100 产物和 NAS final。重跑产生新的 `pipeline_run_id` 和索引版本，不覆盖旧帧记录；默认检索只返回质量门禁通过且最新发布版本的帧。

### 11.7 指纹和关联

用户没有 `upload_id` 也不影响关联。平台首次发现/提交时生成：

```text
source_id：长期业务 ID
pipeline_run_id：一次处理运行 ID
```

NAS 和平台机本地暂存区没有预先生成的 `upload_id`，但不再需要通过两处副本做指纹比对。Scanner 在 NAS 首次发现稳定 bag 时计算轻量指纹，由 Backend 幂等创建唯一 `source_id`；平台机复制和后续产物直接继承该 source_id。

V1 指纹算法定义为 `rosbag-fast-v1`：

```text
canonical_metadata = metadata.yaml 中以下字段规范化后的 JSON：
  storage_identifier
  relative_file_paths（排序）
  starting_time.nanoseconds_since_epoch
  duration.nanoseconds
  message_count
  topics_with_message_count 中的 topic/name/type/message_count（按 topic 排序）

db3_manifest = 每个 DB3 的：
  相对文件名
  文件字节数
  前 1 MiB SHA256
  后 1 MiB SHA256（小文件与前块重叠时只读一次）

fast_fingerprint = SHA256(
  "rosbag-fast-v1\n" + canonical_metadata + "\n" + canonical_db3_manifest
)
```

该算法只读取 `metadata.yaml` 和每个 DB3 最多约 2 MiB，资源消耗与 bag 总大小基本无关，适合 NAS 扫描和多个任务提交。文件必须停止增长后才能计算；指纹结果连同 `fingerprint_version`、文件数和总字节数一起提交。

关联流程：

```text
NAS 增量扫描 -> 计算 fast_fingerprint -> POST Backend -> 建立 NAS_RAW copy 和 source_id
平台机 Phase0 Worker 按 source_id 领取/复制原始 bag -> 建立 PLATFORM_LOCAL_RAW copy
Phase0 manifest 携带 source_id + fast_fingerprint
上传 A100 后登记 A100_PHASE0/A100_INFER artifact
最终回传 NAS 时 manifest 继续携带同一 source_id
```

平台机不再独立提交源数据；必须先由 NAS Scanner 发现并登记 source，Phase0 Worker 按 source_id 执行复制。`bag_name`、车辆和采集时间仅用于检索及辅助核验，不作为唯一键。

若同一指纹命中多个不一致候选，或元数据/文件大小一致但首尾摘要不一致，Backend 不自动合并，标记为 `FINGERPRINT_CONFLICT`。只有冲突或审计场景才异步计算 DB3 全文件 SHA256；正常链路不做全量哈希。Phase0 不再携带 DB3，因此必须把原始数据的指纹清单写入 `source_manifest.json` 并随 Phase0 结果上传，后续 A100 产物通过该清单继承关联，不能重新从处理结果推算原始指纹。

## 12. 状态机

### 12.1 Source 状态

```text
DISCOVERED
-> NAS_CONFIRMED
-> PLATFORM_COPY_CONFIRMED
-> READY_FOR_PHASE0
-> PHASE0_RUNNING
-> PHASE0_DONE
-> A100_UPLOADED
-> FINAL_PUBLISHED
```

### 12.2 Pipeline 状态

```text
CREATED
-> PHASE0_QUEUE
-> PHASE0_RUNNING
-> PHASE0_DONE
-> UPLOADING_A100
-> SELF_BUILT_QUEUE
-> RESOURCE_WAIT
-> A100_RUNNING
-> PHASE1_DONE
-> NAV_RUNNING
-> DESCRIPTION_RUNNING
-> QUALITY_CHECKING
-> COPYING_TO_NAS
-> PUBLISHED
```

失败状态：

```text
RETRY_WAIT
QUARANTINED
INVALID_INPUT
CANCELLED
```

### 12.3 状态推进原则

- 只有持有有效任务租约的 Orchestrator 可以请求推进 A100 阶段状态，是否允许转换由 Backend 校验；
- Phase0 Worker 只能提交 Phase0 和回写上传状态；
- 前端不能直接修改运行中状态；
- 状态推进必须附带 step_run_id、时间、Worker 和证据；
- 文件校验通过后才能推进成功；
- 发布成功后不允许回写覆盖正式产物。

## 13. API 最小集合

### 13.1 Phase0 Worker

```text
POST /api/v1/sources/register
POST /api/v1/pipeline-runs
POST /api/v1/pipeline-runs/{id}/phase0/start
POST /api/v1/pipeline-runs/{id}/phase0/complete
POST /api/v1/pipeline-runs/{id}/phase0/fail
```

`sources/register` 请求必须携带 `fingerprint_version`、`fast_fingerprint`、规范化文件清单和副本位置。Backend 以 `(fingerprint_version, fast_fingerprint)` 幂等查找或创建 source，并返回 `source_id`；Phase0 Worker 不得自行生成另一个业务 source。

### 13.2 NAS 扫描器

```text
POST /api/v1/sources/register
POST /api/v1/sources/{id}/copies
```

扫描器只发现同时具备 `metadata.yaml` 和至少一个 metadata 所列 `.db3` 的稳定目录。它计算 `rosbag-fast-v1` 后向 Backend 登记 `NAS_RAW` 副本，不直接写数据库，也不扫描历史数据；V1 只从启用自动化后的扫描游标向后处理新增目录。

### 13.3 Orchestrator

```text
POST /api/v1/orchestrator/leases/acquire?queue=SELF_BUILT_QUEUE
POST /api/v1/orchestrator/leases/{id}/heartbeat
POST /api/v1/orchestrator/leases/{id}/release
POST /api/v1/orchestrator/resource-leases/acquire
POST /api/v1/orchestrator/resource-leases/{id}/heartbeat
POST /api/v1/orchestrator/resource-leases/{id}/release
POST /api/v1/pipeline-runs/{id}/steps/{step}/start
POST /api/v1/pipeline-runs/{id}/steps/{step}/complete
POST /api/v1/pipeline-runs/{id}/steps/{step}/fail
POST /api/v1/pipeline-runs/{id}/artifacts
POST /api/v1/pipeline-runs/{id}/publish
```

`leases/acquire` 必须按 `queue_name` 在单个数据库事务中完成“选择任务、校验状态、创建任务租约、推进状态”，并返回 `lease_token` 和 `lease_expires_at`。资源领取接口先幂等登记 `ResourceRequest`，再按跨队列统一的 `priority DESC, requested_at ASC` 原子校验 `capacity`、已分配 `units` 和可用 `slot_id`，避免低优先级任务因请求时序抢占资源。后续 heartbeat 和状态变更必须携带对应租约令牌。Orchestrator 不提供直连 MySQL 的降级路径；Backend 暂时不可用时停止领取和推进任务，但不丢弃 A100 进程状态，恢复后依据远端进程、状态文件、done 文件和 manifest 对账。

### 13.4 幂等要求

以下请求必须幂等：

```text
source register
pipeline register
upload complete
step complete
publish
```

重复请求返回已有记录，不产生重复任务或重复产物。

## 14. 失败处理与重试

| 场景 | 处理方式 |
|---|---|
| Phase0 输出缺文件 | 不上传，标记 INVALID_INPUT |
| rsync 中断 | 断点续传，最多 5 次 |
| A100 SSH 不可用 | RETRY_WAIT，指数退避 |
| Phase1 进程退出 | 检查日志和 done，最多重试 2 次 |
| A100 磁盘不足 | 进入隔离，禁止自动删除正式数据 |
| Phase1 引用图片缺失 | 尝试重建索引 1 次，仍失败则隔离 |
| 地图缺失 | QUARANTINED，不使用默认地图 |
| VLM 超时 | 健康检查后重试 3 次 |
| VLM content 为空 | 视为失败，不得仅凭 HTTP 200 判成功 |
| Orchestrator 重启 | 根据 step_runs 和 done 文件恢复 |
| NAS 回传中断 | 断点续传，NAS final 不提前标记完成 |
| 重复提交同一 bag | 复用已有成功结果或创建新版本，不覆盖旧结果 |

## 15. 发布和目录原子性

### 15.1 A100 发布

```text
/data/xl_origin_dataset_staging/<pipeline_run_id>/<bag_name>/
-> 上传校验
-> 原子移动到 /data/xl_origin_dataset/<bag_name>/
-> Phase1/Phase3 输出到 /data/xl_infer_dataset/<bag_name>/
-> 最终校验通过后由 Backend 将对应 artifact 标记为可发布
```

### 15.2 NAS 发布

```text
/public/vla_dataset_builder_backup/final/.incoming/<dataset_version_id>/
-> 校验 manifest/checksum
-> 原子改名为 /public/vla_dataset_builder_backup/final/<dataset_version_id>/
```

V1 保持 A100 已有 bag 名目录约定。相同指纹的重复提交优先复用已有成功结果；需要重跑时创建新的 `pipeline_run_id`，但在覆盖既有 `/data/xl_infer_dataset/<bag_name>` 前必须人工确认或先形成版本化备份，自动流程不得无条件覆盖正式目录。NAS 正式目录不可覆盖，重跑必须生成新的 `dataset_version_id`。

## 16. 数据管理界面第一版

### 16.1 数据源列表

显示：

```text
bag 名称、车辆、采集时间、NAS 路径
Phase0 状态、A100 状态、最终发布状态
当前 pipeline_run_id、最新错误、结果路径
```

### 16.2 任务详情

显示时间线：

```text
源数据登记
-> NAS 确认
-> Phase0 完成
-> A100 上传
-> Phase1
-> 导航
-> 描述
-> 校验
-> NAS 发布
```

### 16.3 血缘页面

以树状形式展示：

```text
source_id
├── NAS 原始副本
├── 平台机本地原始副本
├── Phase0 artifact
├── A100 Phase1 artifact
├── Phase3 artifacts
└── NAS/A100 final artifact
```

### 16.4 操作边界（不含权限管理）

V1 暂不实现用户、角色和细粒度权限管理。页面提供数据检索、任务状态查看、日志查看、失败重试和结果查看；系统仍禁止执行任意命令、修改原始路径、删除正式结果或绕过质量校验。后续增加 RBAC 时沿用现有任务和审计模型。

## 17. 部署方案

### 17.1 内网管理机

使用 Docker Compose 部署：

```text
rosbag-catalog-frontend
rosbag-catalog-backend
rosbag-catalog-scanner
mysql
vla-orchestrator
```

Orchestrator 可以与 Backend 共用代码镜像但使用独立启动命令，也可以独立镜像。MySQL 仅对 Backend 所在 Compose 网络开放；scanner 和 Orchestrator 只配置 Backend URL 和各自的服务凭据，不注入数据库连接串。数据库通过持久化卷保存，密码通过环境文件注入。

### 17.2 用户端介质操作

用户不需要向平台机上传或拷贝数据，也不运行任何处理脚本。用户仅将车端硬盘直接挂载到 NAS，并把原始 rosbag 复制到 NAS raw 目录；复制完成后由 NAS Scanner 自动发现，平台机 Phase0 Worker 再按任务从 NAS 复制到本地工作目录。用户端不持有 A100 或数据库凭据。

### 17.3 平台机 Phase0 环境

平台机安装并固定 `vla_dataset_builder`、Conda、CUDA/ffmpeg（如实际脚本需要）和 `xlbp_parse` 环境。Phase0 Worker 在独立进程中运行，每个任务使用 `PHASE0_WORK_ROOT/<pipeline_run_id>/<bag_name>`。

### 17.4 A100

第一版不部署 K8s、Argo 或 Airflow，只保留：

- 固定 SSH 用户；
- 沿用 `/data/xl_origin_dataset`、`/data/xl_infer_dataset` 和 `/data/xl_maps/maps`；
- 新增独立上传暂存根 `/data/xl_origin_dataset_staging`，完整且领取任务后才原子发布为正式 bag 目录；
- 固定脚本版本；
- `flock` 锁；
- SSH key；
- 日志和结果目录。

## 18. 为什么第一版不选 Airflow/K8s/Argo

### Airflow

Airflow 能表达 DAG 和重试，但第一版只有一台 A100，流程步骤数量有限，使用 Python Orchestrator + SSH/rsync 更快落地。后续如果 DAG 变复杂、任务历史和运营需求增加，可把现有 Orchestrator DAG 迁移到 Airflow。

### K8s + Argo

当前只有一台公网 A100，Phase1 主要是 CPU/磁盘任务，且现有脚本依赖宿主机环境。K8s/Argo 会引入集群、镜像、网络、权限和 CUDA/ROS 兼容问题，不能作为 V1 前置条件。

## 19. 基于当前代码的改造清单

本章是 V1 的工程实施范围。标记含义：

| 优先级 | 含义 |
|---|---|
| P0 | 第一轮端到端必须完成，缺失时不能上线 |
| P1 | 主链路跑通后立即补齐，主要改善运维和可用性 |
| P2 | 后续优化，不阻塞 V1 |

### 19.1 当前代码基线与主要缺口

| 领域 | 当前已有能力 | V1 缺口 |
|---|---|---|
| 数据管理后端 | `app/main.py` 提供 FastAPI、Jinja2 页面、Bag 查询和单条 manifest API | 没有 source 指纹、Pipeline、Step、Artifact、租约和状态机 API |
| 数据模型 | `Vehicle`、`Scene`、`BagRecord`、`BagFile`、`BagTopic`、`ScanJob` | 没有副本、处理运行、步骤、产物和审计事件模型 |
| NAS 扫描 | `scanner.py` 可解析 metadata、校验 DB3 名称和大小，定时扫描已可运行 | 以 NAS 路径而非指纹去重；不能读取 DB3 首尾分块；独立 scanner 直接连接数据库 |
| 数据管理界面 | Bag 检索、详情、车辆、标签、NAS 扫描登记、扫描任务页面 | 不显示 Phase0/A100/NAS final 状态，没有任务队列、时间线、血缘和重试入口 |
| 平台机 Phase0 | `run_phase0.sh` 和 scheduler 已支持 done、resume、多 bag worker | 需要平台机 Worker、任务隔离、source manifest、Backend 登记和完成后上传 A100 |
| 平台机到 A100 | 现有脚本可校验 Phase0 输出并 rsync | 需要与 Phase0 Worker 解耦、写入 staging、进入平台队列，不能直接触发 Phase1 |
| A100 Phase1 | `run_phase1.sh` 支持 resume、reduce、多进程 | 默认扫描输入根全部一级目录，缺少明确的单 bag 调度参数和机器可读运行状态 |
| Phase3 | `nav_gen.py`、`description_gen_llm.py` 已可按 bag/clip 运行 | 缺少统一 wrapper、质量门禁和 Orchestrator 状态回报；CoT 仍是空值占位 |
| NAS 备份 | `backup_to_nas.sh` 可同步 raw 和 Phase0 并做 checksum 比对 | 与“NAS 只保留原始数据和最终结果”目标不一致，缺少 A100 final 回传工具 |
| 部署 | Compose 已有 frontend、backend、scanner、mysql | scanner 持有 `DATABASE_URL`；尚无 Orchestrator 服务、SSH Secret 和 NAS 写通道 |
| 测试 | 有页面、搜索、manifest、bagctl 基础测试 | 没有指纹、幂等、状态机、租约并发、远端失败恢复和端到端测试 |

### 19.2 数据库和迁移改造（P0）

#### 19.2.1 扩展现有模型

修改 `rosbag-catalog/app/models.py`：

1. 扩展 `BagRecord`，增加 `dataset_type`、`fingerprint_version`、`fast_fingerprint`、`metadata_json` 和 `source_status`；现有 `bag_uid` 作为 API 的 `source_id`。
2. 新增 `SourceCopy`，记录 `NAS_RAW`、`PLATFORM_LOCAL_RAW`、`A100_PHASE0`、`A100_INFER`、`NAS_FINAL` 各副本。
3. 新增 `PipelineRun`，记录一次端到端处理、`queue_name`、当前状态、优先级、提交者、`pipeline_config_version`、`capacity_config_version` 和最终 `executor_id`。
4. 新增 `StepRun`，记录 Phase0 上传、Phase1、导航、描述、校验、NAS 发布各步骤及 attempt。
5. 新增 `Artifact`，使用 `parent_artifact_id` 表达处理血缘。
6. 新增 `PipelineEvent`，以追加方式记录状态变化、操作者和错误摘要，页面时间线从该表读取。
7. 任务租约字段可以放在 `PipelineRun`：`lease_owner`、`lease_token_hash`、`lease_expires_at`、`heartbeat_at`。
8. 新增 `ResourcePool`，记录 `executor_id`、`resource_key`、`capacity`、`enabled` 和配置版本。
9. 新增 `ResourceRequest`，记录等待资源的 run、step、units、priority、requested_at 和 `PENDING/GRANTED/CANCELLED/EXPIRED` 状态，由 Backend 统一排序。
10. 新增 `ResourceLease`，记录 `resource_key`、`pipeline_run_id`、`step_run_id`、`executor_id`、`units`、`slot_id`、令牌摘要、heartbeat 和过期时间。
11. 新增 `DatasetFrame`，按发布版本记录逐帧时间、相机引用、轨迹、Planning、导航、描述、标签和质量状态；图片、NPY 正文仍只保留在文件存储。

必须建立的约束和索引：

```text
UNIQUE bag_record(fingerprint_version, fast_fingerprint)
UNIQUE source_copy(source_id, storage_type, host_name, path)
UNIQUE pipeline_run(idempotency_key)
UNIQUE artifact(pipeline_run_id, artifact_type, manifest_hash)
INDEX  pipeline_run(status, priority, submitted_at)
INDEX  pipeline_run(queue_name, status, priority, submitted_at)
INDEX  step_run(pipeline_run_id, step_name, attempt)
INDEX  pipeline_event(pipeline_run_id, created_at)
UNIQUE resource_pool(executor_id, resource_key)
INDEX  resource_request(executor_id, resource_key, status, priority, requested_at)
INDEX  resource_lease(executor_id, resource_key, expires_at)
```

`ResourcePool.capacity=1` 是 V1 初始配置，不是固定上限。资源申请必须先幂等创建 `ResourceRequest`，Backend 按 `priority DESC, requested_at ASC` 选择可满足的请求，并在单个数据库事务中锁定资源池、清理过期租约、校验已分配 `units` 后创建租约。不能由 Orchestrator 先查询再插入，也不能只依赖进程内信号量。离散资源返回 `slot_id`；`VLM_PERMITS` 等计数资源可以不返回 slot，只返回 units。

`fast_fingerprint` 在旧记录上允许暂时为空；只对非空值建立唯一约束。已有数据不做全盘补算，避免把历史治理带入 V1。

#### 19.2.2 引入数据库迁移

当前应用启动时使用 `Base.metadata.create_all()`，只能建缺失表，不能可靠升级已有表。需要加入 Alembic：

```text
rosbag-catalog/alembic.ini
rosbag-catalog/alembic/
rosbag-catalog/alembic/versions/<revision>_add_pipeline_tables.py
```

更新 `requirements.txt`、`Dockerfile.backend` 和 Compose 启动流程，在 Backend 启动前执行一次 `alembic upgrade head`。迁移前必须备份 MySQL；升级不得删除或重命名现有 Bag、车辆、标签、文件和 Topic 表。

### 19.3 Backend 领域层和接口改造（P0）

`app/main.py` 当前同时包含查询、页面和写入逻辑。V1 不要求重构全部旧代码，但新增能力要按边界拆分：

```text
app/api/sources.py
app/api/pipeline_runs.py
app/api/orchestrator.py
app/services/fingerprint.py
app/services/sources.py
app/services/pipelines.py
app/services/leases.py
app/services/artifacts.py
app/schemas/pipeline.py
```

所有数据库事务只能在 Backend 的 service 层完成。Frontend、Phase0 Worker、scanner 和 Orchestrator 都不得导入 `database.py` 或 ORM model。

#### 19.3.1 Source 与副本接口

| 方法 | 路径 | 调用方 | 作用 |
|---|---|---|---|
| POST | `/api/v1/sources/register` | Phase0 Worker、scanner | 按指纹幂等查找或创建 source，返回 `source_id` |
| GET | `/api/v1/sources/{source_id}` | Worker、界面 | 查询源数据、所有副本和最近处理状态 |
| POST | `/api/v1/sources/{source_id}/copies` | Phase0 Worker、scanner、Orchestrator | 幂等登记一个存储副本 |
| POST | `/api/v1/sources/{source_id}/fingerprint-conflict` | scanner、管理员 | 登记冲突证据并阻止自动合并 |

`sources/register` 在同一个事务内完成指纹查询和创建。并发提交遇到唯一索引冲突时重新查询已有记录并返回 `200`，不能产生两个 source。

#### 19.3.2 Pipeline 接口

| 方法 | 路径 | 调用方 | 作用 |
|---|---|---|---|
| POST | `/api/v1/pipeline-runs` | Backend Scanner、Phase0 Worker | 创建或返回幂等 run |
| GET | `/api/v1/pipeline-runs` | 界面 | 按状态、source、日期查询任务 |
| GET | `/api/v1/pipeline-runs/{run_id}` | Worker、界面 | 返回步骤、事件、产物和错误信息 |
| POST | `/api/v1/pipeline-runs/{run_id}/phase0/start` | Phase0 Worker | 记录 Phase0 开始 |
| POST | `/api/v1/pipeline-runs/{run_id}/phase0/complete` | Phase0 Worker | 提交 Phase0 manifest，进入 A100 上传 |
| POST | `/api/v1/pipeline-runs/{run_id}/phase0/fail` | Phase0 Worker | 登记 Phase0 失败 |
| POST | `/api/v1/pipeline-runs/{run_id}/retry` | 管理界面/自动恢复器 | 从允许的失败步骤创建新 attempt |
| POST | `/api/v1/pipeline-runs/{run_id}/cancel` | 管理界面 | 只允许取消排队或等待重试任务 |

每个写请求接收 `Idempotency-Key`。状态转换使用条件更新或行锁，非法转换返回 `409 Conflict`，请求内容错误返回 `422`，同一幂等键参数不同返回 `409`。

#### 19.3.3 Orchestrator 接口

| 方法 | 路径 | 作用 |
|---|---|---|
| POST | `/api/v1/orchestrator/leases/acquire?queue={queue_name}` | 按队列原子领取 `priority DESC, submitted_at ASC` 的任务 |
| POST | `/api/v1/orchestrator/leases/{run_id}/heartbeat` | 延长租约并报告当前步骤 |
| POST | `/api/v1/orchestrator/leases/{run_id}/release` | 完成、失败或主动释放租约 |
| POST | `/api/v1/orchestrator/resource-leases/acquire` | 幂等登记资源请求，并按全局优先级原子授予 units/slot |
| POST | `/api/v1/orchestrator/resource-leases/{lease_id}/heartbeat` | 延长步骤资源租约 |
| POST | `/api/v1/orchestrator/resource-leases/{lease_id}/release` | 步骤完成或失败后释放资源 |
| POST | `/api/v1/pipeline-runs/{run_id}/steps/{step}/start` | 创建或取得当前 attempt |
| POST | `/api/v1/pipeline-runs/{run_id}/steps/{step}/complete` | 携带输出 manifest 和指标完成步骤 |
| POST | `/api/v1/pipeline-runs/{run_id}/steps/{step}/fail` | 写入结构化错误和重试建议 |
| POST | `/api/v1/pipeline-runs/{run_id}/artifacts` | 登记产物及父产物 |
| POST | `/api/v1/pipeline-runs/{run_id}/frames/bulk` | 批量写入或幂等更新帧级索引 |
| GET | `/api/v1/frames` | 按标签、车辆、时间、导航、质量和 source 检索帧 |
| POST | `/api/v1/pipeline-runs/{run_id}/publish` | 质量门禁通过后登记 NAS final |

除任务领取接口外，所有 Orchestrator 请求必须携带任务 `lease_token`；资源相关请求还必须携带 `resource_lease_token`。Backend 只保存令牌摘要。过期租约不能推进状态；新 Worker 接管前必须完成 A100 进程、槽位锁、机器可读状态文件和 done 文件对账。

#### 19.3.4 审计（权限管理后置）

V1 暂不实现用户、角色、Scope、Token 和细粒度权限管理。任务仍记录提交来源、时间和运行事件，平台部署在受控内网；后续增加认证和 RBAC 时不得改变任务、帧索引和血缘模型。

### 19.4 轻量指纹工具改造（P0）

新增共享实现和命令行工具：

```text
rosbag-catalog/app/services/fingerprint.py
vla_dataset_builder/scripts/compute_source_fingerprint.py
```

两处必须使用同一份 `rosbag-fast-v1` 测试向量，保证字段排序、JSON 编码、整数表示、分块大小完全一致。建议把算法实现提取成小型纯 Python 包，两个项目锁定同一版本；如果第一轮来不及发布包，至少共享 fixtures 和 golden fingerprint，禁止各自凭理解实现。

当前 `MountedNasClient` 只有文本读取，需要增加受根目录限制的二进制分块读取能力。V1 推荐使用 Compose 中只读挂载的 `/mnt/nas_backup -> /nas:ro` 计算首尾摘要。DSM File Station 模式如果不能可靠执行 range read，则只登记候选元数据，不能伪造完整 `rosbag-fast-v1`。

工具必须输出机器可读 JSON：

```json
{
  "fingerprint_version": "rosbag-fast-v1",
  "fast_fingerprint": "<sha256>",
  "bag_name": "<name>",
  "file_count": 1,
  "total_bytes": 123,
  "files": []
}
```

### 19.5 NAS scanner 改造（P0）

当前 `app/scan_worker.py -> scanner.scan()` 直接使用 `SessionLocal` 写数据库。需要拆成：

```text
NAS 发现/metadata 解析/指纹计算
-> POST rosbag-catalog backend
-> Backend service 负责事务和入库
```

具体任务：

1. 保留 `scanner.py` 中路径校验、目录遍历和 metadata 解析逻辑，拆除独立 worker 的 ORM 写入依赖。
2. scanner 只处理 `metadata.yaml` 存在、metadata 所列 DB3 齐全且两次检查大小不变的目录。
3. 增加扫描游标或 `last_seen_mtime`，V1 默认只扫描启用时间之后的新增数据。
4. 为每个成功目录登记 `NAS_RAW SourceCopy`；重复扫描必须幂等。
5. Backend 创建任务后，Phase0 Worker 自动从 NAS 将 raw bag 复制到平台机本地工作目录，复制完成并校验后才进入 `PHASE0_RUNNING`。
6. 扫描错误通过 Backend 创建 `ScanJob/PipelineEvent`，不直接写表。
7. Compose 的 scanner 服务移除 `DATABASE_URL`，改为 `BACKEND_URL` 和 scanner 服务令牌。

手动 `/ingest/register` 仍可由 Backend 内部调用 service 入库，因为它本身就在 Backend 边界内；定时 scanner 进程不能直连数据库。

### 19.6 平台机 Phase0 Worker 开发（P0）

新增统一入口：

```text
rosbag-catalog/orchestrator/phase0_worker.py
vla_dataset_builder/scripts/run_phase0.sh
vla_dataset_builder/scripts/validate_phase0.py
vla_dataset_builder/scripts/compute_source_fingerprint.py
```

Phase0 Worker 顺序固定为：

```text
检查 NAS Scanner 已登记且原始 rosbag 已稳定
-> 读取 Backend 返回的 source_id 和 manifest
-> 校验 Phase0 done/clip/6 路 MP4
-> Backend 创建/领取 pipeline run
-> 生成 source_manifest.json 和 phase0_manifest.json
-> rsync 到 A100 staging
-> 远端按 manifest 校验文件数、大小和关键文件
-> Backend phase0-complete
```

CLI 至少支持：

```text
--source <raw_rosbag>
--output <phase0_output>
--pipeline-run-id <id>
--resume
--dry-run
```

本地保存 `.vla-submit/<pipeline_run_id>.json`，网络中断后重复执行可从同一 run 续传，不能重新创建任务。退出码要区分输入非法、Backend 不可达、SSH 失败、上传校验失败和平台拒绝。

现有 `upload_and_run_phase1.sh` 不再作为生产入口；A100 上传由平台机 Phase0 Worker 负责。现有 `backup_to_nas.sh` 不再备份 Phase0，原始数据仍由用户先复制 NAS；后续使用独立的 A100 final 回传工具。

### 19.7 VLA Orchestrator 开发（P0）

建议在 `rosbag-catalog` 下新增独立进程，但不与 Web 请求共进程：

```text
orchestrator/main.py
orchestrator/backend_client.py
orchestrator/ssh_runner.py
orchestrator/state_machine.py
orchestrator/validators.py
orchestrator/publish.py
orchestrator/command_templates.py
```

Worker 池需要完成：

1. 根据 `SELF_BUILT_WORKERS` 启动若干 Worker，每个 Worker 按 `queue=SELF_BUILT_QUEUE` 原子领取一个任务并持续 heartbeat。
2. 通过 SSH 校验 staging manifest、目标路径冲突、A100 磁盘和脚本版本。
3. 取得 `DATASET_PATH:<safe_hash>` 路径锁后，将当前任务从 staging 原子移动到 `/data/xl_origin_dataset/<bag_name>`。
4. 为当前步骤申请 `A100_COMPUTE_IO`、`VLM_PERMITS` 或 `NAS_PUBLISH`；根据 Backend 返回的 `slot_id/units` 获取对应远端 flock 后执行固定命令。
5. 监控进程 PID、退出码、日志和 done 文件，SSH 短暂断开后可以重新查询，不把断线直接当作任务失败。
6. 依次运行导航、场景描述和质量校验；CoT 占位步骤不进入 P0 成功条件。
7. 登记每一步输入/输出 manifest、指标和父产物。
8. 将最终结果回传 NAS staging，校验后发布并调用 Backend 完成任务。
9. 每步结束及时释放资源租约；根据错误分类执行限次重试，不自动删除 A100 正式目录。
10. Orchestrator 重启时恢复全部未结束 Worker，根据任务租约、资源租约、slot flock、PID 和状态文件对账。

固定命令模板只接受经过正则校验的 `bag_name`、整数并发参数、Backend 分配的 `slot_id/units` 和配置枚举，禁止拼接用户提交的任意路径或 Shell 片段。Orchestrator 本地日志按 `pipeline_run_id/step/attempt` 存放，并限制大小和保留周期。Worker 数增加后，各任务仍必须使用独立状态和日志目录。

### 19.8 A100 wrapper 和运行协议改造（P0）

不修改 Phase0/Phase1 算法，但需要补齐调度适配层：

1. 为 `run_phase1.sh` 和 `scheduler_phase1.py` 增加 `--bag-name` 或等价单 bag 过滤，避免一次调用扫描并处理正式根下所有目录。
2. 增加 `run_pipeline_step.sh`，统一激活环境、记录代码版本、参数、PID、开始时间、退出码和结束时间。
3. 每步先写 `<step>_run.json.tmp`，结束后原子改名为 `<step>_run.json`。
4. 每次运行的状态和日志固定写入 `/data/vla_pipeline_runs/<pipeline_run_id>/`，不能使用跨任务共享的固定状态文件。
5. Phase1 固定输入 `/data/xl_origin_dataset/<bag_name>`，输出 `/data/xl_infer_dataset/<bag_name>`，并取得该 bag 的路径锁。
6. `nav_gen.py` 对单 bag 运行，地图根固定 `/data/xl_maps/maps`。
7. `description_gen_llm.py --base-dir` 指向单 bag 结果目录，并检查 vLLM content 非空；实际并发不能超过获得的 `VLM_PERMITS units`。
8. wrapper 根据资源租约获得 `slot_id`，使用 `/tmp/vla_compute_io.slot-<N>.lock` 等槽位锁；不得继续硬编码唯一的 `proj_dataset_builder_phase1.lock`。
9. 增加 `validate_a100_result.py`，检查 CSV 可读性、所有相对路径、NPY shape、6 路相机列、导航覆盖率和描述格式。
10. 启动自动化前扫描 `xl_origin_dataset`，将仅含原始 DB3 的目录报告为 `LEGACY_RAW_CONFLICT`。

P1 再考虑把 A100 代码做镜像；V1 沿用已经可运行的 Conda/宿主机环境，避免镜像兼容性拖慢交付。

### 19.9 A100 最终结果回传 NAS（P0）

新增 Orchestrator 使用的发布工具：

```text
orchestrator/publish_to_nas.py
```

目录约定：

```text
NAS_FINAL_ROOT=/public/vla_dataset_builder_backup/final
<NAS_FINAL_ROOT>/.incoming/<dataset_version_id>/
<NAS_FINAL_ROOT>/<dataset_version_id>/
```

先 rsync 到 `.incoming`，根据 final manifest 校验文件数、总字节数和关键文件摘要，再在 NAS 同一文件系统原子改名。最终目录包含 `source_manifest.json`、`final_manifest.json` 和 `quality_report.json`，由此与 NAS raw source 关联。

Backend/scanner 继续只读挂载 NAS；只有 Orchestrator 获得限定在 `NAS_FINAL_ROOT` 的写权限。推荐使用 NAS 专用 SSH/rsync 账号，禁止给 Orchestrator 整个 `/volume1/public` 的删除权限。

### 19.10 数据管理界面调整（P0/P1）

当前界面是 Backend 渲染 Jinja2，`frontend` 镜像只是 Nginx 入口，因此 V1 不新建 SPA。修改 `base.html`、`bags.html`、`detail.html` 和 `app.css`，新增 `pipeline_runs.html`、`pipeline_detail.html`。

P0 页面：

| 页面 | 调整内容 |
|---|---|
| Bag 检索 | 增加 source 状态、最近 pipeline 状态、提交人和最终结果筛选 |
| Bag 详情 | 增加 `source_id`、轻量指纹、NAS/平台机/A100 副本、处理入口和血缘区域 |
| 处理任务列表 | 显示队列序号、状态、当前步骤、提交人、等待/运行时长和最新错误 |
| 任务详情 | 显示事件时间线、每步 attempt、日志摘要、输入输出、A100/NAS 路径和质量报告 |
| 扫描任务 | 增加新增 source、指纹命中、冲突和失败统计，不直接展示原始 JSON 错误字符串 |

P0 操作只包括：查看 Scanner 发现的数据、重试允许的失败步骤、取消排队任务。正常任务由 Scanner 自动创建和触发；所有按钮调用 Backend API，并处理 `409` 并发冲突；运行中的任务不能强制删除。

P1 增加自动刷新、队列预计等待时间、按用户筛选、日志分页和血缘图。V1 不实现复杂拖拽 DAG 编辑器。

### 19.11 Compose 和配置调整（P0）

修改 `compose.yaml`、`.env.example` 和 README：

```text
    frontend      -> 只访问 backend
backend       -> 唯一持有 DATABASE_URL
scanner       -> BACKEND_URL + SCANNER_TOKEN + NAS 只读挂载
orchestrator  -> BACKEND_URL + ORCHESTRATOR_TOKEN + SSH Secret + NAS final 写通道
mysql         -> 只在 Compose 内部网络开放
```

新增配置至少包括：

```text
BACKEND_URL
SCANNER_TOKEN_FILE
ORCHESTRATOR_TOKEN_FILE
A100_HOST
A100_PORT
A100_USER
A100_SSH_KEY_FILE
A100_STAGING_ROOT=/data/xl_origin_dataset_staging
A100_PHASE0_ROOT=/data/xl_origin_dataset
A100_INFER_ROOT=/data/xl_infer_dataset
A100_MAP_ROOT=/data/xl_maps/maps
NAS_FINAL_ROOT=/public/vla_dataset_builder_backup/final
ORCHESTRATOR_POLL_SECONDS
LEASE_TTL_SECONDS
EXECUTOR_ID=a100-main
PHASE0_WORKERS=1
PHASE0_WORK_ROOT=/data/vla_phase0_work
SELF_BUILT_WORKERS=1
RESOURCE_COMPUTE_IO_CAPACITY=1
RESOURCE_VLM_PERMITS=4
RESOURCE_NAS_PUBLISH_CAPACITY=1
SELF_BUILT_PHASE1_PROCESS_COUNT=8
```

密码、Token 和 SSH 私钥使用只读 Secret 文件挂载，不写进镜像、`.env.example`、数据库或日志。Backend ready check 增加迁移版本检查；Orchestrator ready 状态至少包含 Backend、A100 SSH、NAS final 写通道、资源池配置和磁盘检查。Worker 数、资源容量和每任务内部并发必须分别配置，不能由同一个 `MAX_CONCURRENCY` 模糊控制。

### 19.12 测试和验收工具（P0）

需要补充：

1. 指纹 golden test：同一 NAS bag 重复扫描得到相同指纹；改变 DB3 首块、尾块、大小或 metadata 后指纹不同。
2. Source 并发测试：5 个客户端同时注册相同指纹只生成一个 `bag_record/source_id`。
3. 状态机测试：合法转换成功，越级、重复和过期租约返回预期结果。
4. 任务租约测试：多个 Worker 竞争同一任务时只有一个领取成功；租约过期后可安全接管。
5. 资源租约测试：容量、units 和 slot 分配原子正确；过期租约可回收；容量为 2 时可以分配两个不同 slot。
6. scanner 测试：不再配置数据库也能通过 Backend 登记，未稳定和缺 DB3 的目录不入库。
7. Phase0 Worker 测试：任务隔离、断点恢复、重复提交、同名不同指纹和本地路径冲突。
8. SSH runner 测试：连接中断、远端非零退出、进程仍运行、done 缺失、磁盘不足。
9. A100 validator 测试：CSV、JPG、NPY、Planning、导航和描述异常均能阻止发布。
10. NAS 发布测试：中断后只能留下 `.incoming`，正式目录不可见；重试后只发布一个版本。
11. 初始容量测试：3～5 个用户先后向 NAS 复制数据，Scanner 创建任务后，`PHASE0_WORKERS=1` 时按队列顺序执行且不丢失、不覆盖。
12. 单机扩容测试：将 Worker 和计算 slot 提升到 2，两个不同 bag 可并行运行，同一 bag 路径锁仍只允许一个写入者。
13. 并发预算测试：两个 Phase1 的内部进程数总和不超过配置预算；VLM 请求并发不超过已分配 permits。

测试环境不能直接使用 A100 正式根目录。先使用本地临时目录和 fake SSH runner，最后选择一个明确的测试 bag 在 A100 测试根完成验收，验证通过后再开启生产路径。

### 19.13 代码文件影响清单

| 项目 | 文件或模块 | 动作 |
|---|---|---|
| rosbag-catalog | `app/models.py` | 扩展 BagRecord，新增 copy/run/step/artifact/event/resource request/resource lease 模型 |
| rosbag-catalog | `app/main.py` | 挂载新 router，旧页面逻辑保持可用 |
| rosbag-catalog | `app/scanner.py`、`app/scan_worker.py` | 分离扫描与入库，独立 worker 改调 Backend API |
| rosbag-catalog | `app/api/*`、`app/services/*`、`app/schemas/*` | 新增 Source、Pipeline、Lease、Artifact 领域实现 |
| rosbag-catalog | `app/templates/base.html`、`bags.html`、`detail.html` | 增加任务入口、状态和血缘 |
| rosbag-catalog | `app/templates/pipeline_runs.html`、`pipeline_detail.html` | 新增队列与任务详情页面 |
| rosbag-catalog | `app/static/app.css` | 新增队列、时间线、步骤和错误状态样式 |
| rosbag-catalog | `alembic/*` | 新增可回滚的数据库迁移 |
| rosbag-catalog | `orchestrator/*` | 新增 Worker 池、资源额度、调度、SSH、校验和发布服务 |
| rosbag-catalog | `compose.yaml`、`.env.example` | 收紧 DB 边界并新增 Orchestrator/Secret 配置 |
| rosbag-catalog | `orchestrator/phase0_worker.py` | 新增平台机 Phase0 队列、任务隔离和状态回写 |
| rosbag-catalog | `orchestrator/frame_indexer.py`、`app/services/frames.py` | 批量解析 `dataset_index.csv`、写入帧级索引并提供条件检索 |
| vla_dataset_builder | `scripts/compute_source_fingerprint.py`、`validate_phase0.py` | 新增关联指纹和 Phase0 门禁 |
| vla_dataset_builder | `scripts/upload_and_run_phase1.sh` | 停止直接触发 Phase1，改为平台提交或诊断用途 |
| vla_dataset_builder | `scripts/backup_to_nas.sh` | 移除 Phase0 备份职责或标记为旧工具 |
| A100 scripts | `run_phase1.sh`、`phase1/scheduler_phase1.py` | 增加单 bag 过滤，不改算法 |
| A100 scripts | `run_pipeline_step.sh`、`validate_a100_result.py` | 新增机器可读执行协议和质量门禁 |

### 19.14 第一轮交付顺序

第一轮不是只交付某个服务，而是交付一条可用的 MVP 端到端链路：

```text
1. 确认 A100 legacy raw 冲突处置和生产目录权限
2. 数据库迁移 + Backend source/pipeline/lease API
3. rosbag-fast-v1 + scanner API 化
4. 平台机 Phase0 Worker、manifest 和 A100 上传工具
5. A100 单 bag wrapper + validator
6. Orchestrator 队列、监控、重试和 NAS 发布
7. 数据管理任务列表、详情、状态和血缘
8. 单 bag 联调
9. 3～5 个用户并发向 NAS 复制数据、Scanner 自动建任务、Phase0 排队和故障恢复验收
```

步骤 1 是上线前置条件；步骤 2～7 可以分支开发，但必须在步骤 8 合并为完整链路。不能把“脚本能运行”视为交付完成，只有第 20 章全部 P0 验收项通过才算第一轮完成。

## 20. MVP 验收标准

### 20.1 主链路

1. 用户将新 bag 复制到 NAS raw 目录；
2. Scanner 自动发现并创建任务，平台机 Phase0 Worker 自动完成 Phase0；
3. 后端能够记录 source、run 和 Phase0 artifact；
4. Phase0 自动上传 A100；
5. A100 任务进入 `SELF_BUILT_QUEUE`；
6. Orchestrator 自动运行 Phase1；
7. Phase1 成功后自动运行导航和配置中的描述步骤；
8. 校验通过后最终结果自动回传 NAS；
9. 帧索引器以批量方式写入全部有效帧，页面可以按车辆、时间、标签和质量条件检索；
10. 数据管理平台显示完整任务时间线和血缘，且所有数据写入均经过 Backend；
11. 失败后可从失败步骤重试。

### 20.2 多人并发

1. 3～5 个用户可同时向 NAS 复制不同 bag；
2. 不同任务的本地工作目录、source_id 和 pipeline_run_id 不冲突；
3. V1 初始配置下 `SELF_BUILT_WORKERS=1`，任务按队列顺序执行，其他任务不丢失、不覆盖；
4. 在 fake runner 或隔离测试根中将 Worker 和 `A100_COMPUTE_IO` 容量提高到 2 后，两个不同 bag 可以并行处理；生产初始容量仍可保持 1；
5. 同一 bag 或同一正式输出路径始终只能有一个写入者；
6. 两个并行任务的进程总数、VLM 请求数和 NAS 发布数不超过分配的资源额度；
7. 每个任务都能看到队列、资源等待、当前步骤和执行 slot。

### 20.3 一致性和安全

1. 重复提交不产生重复 source 或重复成功 artifact；
2. A100 结果和 NAS 结果 manifest 一致；
3. 正式目录不可覆盖；
4. 后端不暴露公网写接口给 A100；
5. A100 只接受固定 SSH 用户和固定命令模板；
6. 日志不记录密码和私钥；
7. 未通过质量门禁的数据不能标记 PUBLISHED。
8. Orchestrator 容器内不存在 MySQL 凭据，停用 Backend 后不能直接推进数据库状态。
9. NAS Scanner 为同一 rosbag 生成稳定的 `rosbag-fast-v1` 指纹，重复扫描只关联同一个 `source_id`；平台机复制和 A100 产物继承该 ID。

## 21. 后续扩展

当 V1 稳定后再考虑：

- 将 Orchestrator DAG 迁移 Airflow；
- 根据压测逐步提高单台 A100 的 Worker、计算 slot 和 VLM permits；
- 自动降载和基于吞吐的并发参数调优；
- Agent/Skill 监督日志和低风险重试；
- PostgreSQL；
- NVIDIA 路线已由 `vla_nvidia_dataset_pipeline_v1_prd.md` 接入同一 Backend、Orchestrator 和资源池；后续优化（批量提交、下载吞吐和数据集版本发布）转到 NVIDIA PRD；
- 多台 GPU 机器；
- 统一训练数据 schema；
- 自动场景标签和 CoT 生成。

V1 的成功标准不是系统功能最多，而是新采集的一份自建 bag 能够稳定完成：

```text
平台机 Phase0 -> A100 Phase1/Phase3 -> NAS 最终结果 -> 数据管理平台完整血缘
```

并且 3～5 个用户可以同时向 NAS 复制不同数据而不发生任务冲突。
