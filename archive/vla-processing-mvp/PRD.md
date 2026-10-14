# VLA 数据处理可迁移流程 MVP PRD

**版本**：v0.2  
**状态**：快速交付方案  
**日期**：2026-09-09  
**目标项目**：`vla_dataset_builder`  
**配套平台**：现有 `rosbag-catalog`（仅做轻量关联，不进行大规模改造）

> **当前实现校准（2026-09-21）**：本文是早期 MVP 方案，保留用于说明最初的可迁移处理目标，不作为当前实施依据。当前系统已演进为由 `rosbag-catalog` Orchestrator、PipelineRun/StepRun、任务与资源租约、处理机宿主机 Phase0 代理及 A100 代理组成的完整链路；数据库实际为 MySQL 8.4，正式架构和验收边界请以 `vla_self_dataset_pipeline_v1_prd.md`、`rosbag-catalog/docs/current_architecture.md` 和 `HANDOFF.md` 为准。

## 1. 目标

本项目的首要目标不是建设完整数据管理平台，而是尽快把当前人工执行的 VLA 数据处理工作变成一条可重复、可迁移、少人工参与的生产流程：

```text
车端采集
  -> 同一块硬盘分别拷贝到 NAS 和个人处理电脑
  -> 个人电脑一键运行 phase0/phase1
  -> 处理结果上传 NAS 和 A100
  -> 后端记录处理结果并与 NAS 原始数据关联
```

第一轮交付必须完成 MVP 端到端闭环：从本地输入准备、phase0、phase1，到 NAS/A100 发布、manifest 生成、后端状态回写和 NAS 原始数据关联。phase0 是技术验证起点，但不能作为第一轮单独交付的终点；自动标签和 Agent 化仍放到后续迭代。

## 2. 明确不做的事情

本 MVP 不做：

- PostgreSQL 切换；继续使用当前 `rosbag-catalog` 的数据库和连接方式。
- MySQL 历史数据迁移。
- NAS 历史数据全盘治理和重新归档。
- 物理搬迁、重命名或整理历史 NAS 目录。
- 分布式调度平台、Kubernetes、消息队列和多机资源编排。
- phase0/phase1 内部算法重写。
- 一期多模态模型自动标注的完整闭环。

“分布式”在本阶段仅理解为：多台同型号个人电脑都能够独立运行同一套处理流程；不建设中心化计算集群。

## 3. 现状技术基线

### 3.1 `vla_dataset_builder`

当前代码已经提供：

- `run_phase0.sh`：rosbag 原始数据到 phase0 结果；
- `run_phase1.sh`：phase0 结果到 phase1 训练索引；
- phase0 断点续跑、阶段完成标记、六路相机检查和视频 FPS 门禁；
- phase1 解帧、轨迹生成和 `dataset_index.csv` 生成；
- `upload_and_run_phase1.sh`、`backup_to_nas.sh` 中已有 rsync、远端执行和校验思路。

MVP 只在这些 wrapper 外部增加“一键入口、环境检查、输入登记、结果上传和状态回写”，不改内部处理步骤。

### 3.2 原始数据约定

原始数据是 ROS 2 bag，通常表现为一个目录，其中包含：

```text
metadata.yaml
rosbag2_*.db3
```

`.db3` 是 rosbag2 使用 SQLite3 存储的分片文件后缀，不代表普通业务数据库。`metadata.yaml` 描述存储格式、时间、消息总数、Topic、消息类型和分片清单。

## 4. MVP 端到端流程

```text
车端采集硬盘
    ├── 拷贝原始数据到 NAS（备份副本）
    └── 拷贝同一原始数据到个人电脑本地工作区
                         ↓
                 一键处理脚本
                         ↓
          环境检查 + 输入清单/指纹
                         ↓
                 phase0（GPU）
                         ↓
                 phase1（CPU为主）
                         ↓
             结果校验 + manifest
                    ├────┴────┐
                    ↓         ↓
                 NAS 备份    A100 使用目录
                    └────┬────┘
                         ↓
                 后端状态回写
                         ↓
                  NAS 扫描关联
```

NAS 不是本次计算输入源。个人电脑从车端硬盘直接读取，NAS 用于备份、原始数据登记和最终结果备份。

## 5. 一键处理脚本

### 5.1 目标命令

建议新增统一入口：

```bash
./run_pipeline.sh \
  --input /media/user/disk/rosbag_xxx \
  --work /data/vla_work \
  --nas-result /mnt/nas_backup/vla/final \
  --a100-host <host> \
  --a100-path <path>
```

日常用户只需要选择原始数据目录并执行一个命令。脚本负责调用现有 `run_phase0.sh` 和 `run_phase1.sh`。

### 5.2 脚本职责

1. 检查 Linux、NVIDIA 驱动、GPU、CUDA、Python、Conda 环境、ffmpeg、rsync、磁盘空间。
2. 检查输入目录同时包含可解析 `metadata.yaml` 和至少一个 `.db3`。
3. 从输入目录生成 `input_manifest.json`，记录相对路径、大小、mtime；条件允许时计算内容摘要。
4. 生成本次 `processing_run_id`，记录电脑、用户、代码版本和参数。
5. 将输入复制到本地工作区，不直接在移动硬盘上执行大量随机读写。
6. 调用现有 phase0；成功后按配置调用 phase1。
7. 校验阶段完成标记、六路视频、FPS、索引文件和引用文件。
8. 生成统一 `manifest.json` 和 `checksums.sha256`。
9. 将最终结果分别上传 NAS 和 A100，支持断点续传和失败重试。
10. 处理结束后向 `rosbag-catalog` 后端发送处理状态和 manifest 摘要。
11. 根据用户选择清理本地工作区；默认保留失败任务和最近一次成功结果。

### 5.3 一键脚本模式

```text
check       只检查环境和输入
run         执行 phase0 + phase1
phase0      只执行 phase0
phase1      基于已有 phase0 执行 phase1
publish     只上传已有最终结果
resume      从最近成功阶段继续
```

第一轮交付必须支持 `check`、`run`、`resume`、`publish`，其中 `run` 要能够完成一次真实数据的 phase0 → phase1 → 结果校验 → NAS/A100 发布 → 后端回写闭环。

## 6. 个人电脑可迁移要求

### 6.1 统一运行包

提供以下任一形式的可迁移包：

- 推荐：代码仓库 + 固定 Conda 环境安装脚本 + 配置模板；
- 可选：同型号电脑使用的离线 Conda 环境压缩包；
- 不要求 GPU 容器化，避免 NVIDIA 驱动、CUDA 和 ffmpeg 兼容问题。

所有路径通过参数或环境变量配置，不允许写死用户目录、主机名、GPU 编号或 NAS 挂载路径。GPU 编号默认自动选择，也支持 `--gpu` 指定。

### 6.2 环境自检结果

脚本输出并保存：

```text
host_name, client_id, os, cpu, memory, disk_free,
gpu_name, gpu_memory, driver, cuda, python,
conda_environment, ffmpeg, git_commit, pipeline_version
```

不同电脑的硬件信息只用于运行记录和性能分析，不影响数据业务身份。

## 7. NAS 与本地结果关联

### 7.1 不依赖 upload_id，采用分层关联

用户把硬盘拷贝到 NAS 时不需要提供 `upload_id`。但不建议每次关联都对整个 DB3 做全量 SHA256：大文件多、耗时长，会占用移动硬盘/本地磁盘和 CPU；如果多人同时调用接口，还会造成重复读取和并发压力。

MVP 采用“本地生成一次轻量 manifest + 后端幂等关联 + 必要时异步强校验”的分层方案：

**第一层：快速指纹（默认）**

```text
fast_fingerprint = SHA256(
  metadata.yaml 的规范化内容
  + 按相对路径排序的 DB3 文件名
  + 每个 DB3 的文件大小
  + rosbag metadata 的起始时间/时长/消息数
)
```

不把路径、上传时间和 mtime 作为唯一身份，因为同一份数据在 NAS 和个人电脑上的路径、复制时间和 mtime 可能不同。该指纹只读取 metadata 和文件目录项，通常不需要读取 DB3 正文。

**第二层：辅助匹配**

当快速指纹未命中时，使用目录名、metadata 起始时间、时长、消息数、DB3 文件清单和父目录日期/地点做候选匹配，输出候选及置信度，不直接自动合并。

**第三层：强校验（按需、异步）**

仅在多个候选冲突、用户要求确认或发现内容疑似变化时，对 DB3 计算全量 SHA256/分块摘要。强校验由后台任务执行，不在 HTTP 请求中同步执行；结果缓存到数据库，后续复用。

最佳实践是由一键处理脚本在读取移动硬盘时生成一次 `input_manifest.json`，并将同一份 manifest 摘要随处理结果上报。NAS scanner 对 NAS 副本生成同算法的 fast_fingerprint。这样不需要用户输入 upload_id，也不要求修改 NAS 原始目录。

NAS 扫描器发现原始目录后生成 `nas_record_id`/`bag_uid`。个人电脑处理时生成 `processing_run_id`，完成后上报 manifest 摘要和结果信息。后端按 fast_fingerprint 优先、metadata 候选辅助、强校验兜底的顺序关联。

### 7.2 关联状态

```text
UNMATCHED
MATCHED_BY_FINGERPRINT
MATCHED_BY_METADATA
NEEDS_MANUAL_CONFIRM
```

未关联成功的结果允许保留在个人电脑，但不得自动标记为正式可共享结果；用户可在数据管理页面选择 NAS 原始记录完成关联。

### 7.3 并发与幂等要求

- 关联接口只接收 manifest 摘要和候选信息，不在请求中扫描 NAS 或读取 DB3。
- `fast_fingerprint`、`bag_uid`、`processing_run_id` 建立唯一约束；重复请求返回已有关联结果，不重复创建记录。
- NAS scanner 使用单实例锁或 PostgreSQL advisory lock，同一 NAS 路径同一时间只允许一个扫描任务。
- 处理结果回写采用幂等 PUT/重试语义；网络重试不会生成重复 processing run 或重复 artifact。
- 多人可以同时处理不同 bag；同一 bag 默认只允许一个活动 processing run，管理员强制重跑时生成新的 run 版本。
- 强校验和 NAS 扫描放入后台任务，限制并发数和读取速率，避免多人操作拖垮 NAS。

### 7.4 Manifest 必填关联字段

NAS final 和 A100 结果必须包含同一份：

```json
{
  "processing_run_id": "...",
  "nas_record_id": "...",
  "bag_uid": "...",
  "source_path": "...",
  "input_fingerprint": "...",
  "pipeline_version": "...",
  "git_commit": "...",
  "output_checksums": "..."
}
```

## 8. 后端最小改造

不重做 `rosbag-catalog` 数据管理界面，只增加最小接口和字段，优先采用独立处理记录表或 JSON 扩展字段：

```text
POST /api/processing-runs/register
POST /api/processing-runs/{id}/heartbeat
POST /api/processing-runs/{id}/complete
POST /api/processing-runs/{id}/fail
POST /api/processing-runs/{id}/associate
GET  /api/processing-runs/{id}
```

最小记录内容：原始 NAS 记录、处理电脑、操作者、输入指纹、phase0/phase1 状态、结果 NAS 路径、A100 路径、manifest、日志路径和错误信息。`register/associate/complete` 接口只处理小型 JSON 元数据，不在接口线程中执行目录递归、DB3 全量哈希或文件上传。

NAS scanner 只增加“扫描新增目录并尝试关联”的能力，不处理历史数据。扫描仍以同时具备 `metadata.yaml` 和 `.db3` 为纳管门槛。

## 9. 处理结果发布

### 9.1 NAS

最终结果写入临时目录，校验通过后再改名：

```text
/vla/final/.incoming/<bag_uid>/<processing_run_id>/
/vla/final/<bag_uid>/<processing_run_id>/
```

NAS 保存原始数据和最终 phase1 结果，不保存 phase0 中间结果。

### 9.2 A100

由个人电脑主动使用 SSH/rsync 上传：

```text
<a100_root>/.incoming/<bag_uid>/<processing_run_id>/
<a100_root>/<bag_uid>/<processing_run_id>/
```

A100 端校验 manifest 和 checksum 后原子发布。A100 暂时不可用时，NAS 发布不应被阻塞，客户端可稍后单独执行 `publish`。

## 10. 第一轮 MVP 端到端交付计划

第一轮不是按“先交付 phase0、再逐步补齐外围能力”的方式验收，而是围绕一条真实数据端到端闭环组织开发。内部实施顺序如下，但最终以全链路通过作为交付标准。

### 第 1 步：建立可迁移运行环境并验证 phase0

- 在一台目标型号电脑上固定环境；
- 用一个真实 bag 验证一键 `phase0`；
- 验证断点续跑、日志、六路 MP4、FPS 和失败退出码；
- 形成环境安装和自检脚本。

### 第 2 步：接入 phase1、本地 manifest 和统一校验

- 一键执行 phase0 -> phase1；
- 生成输入/输出 manifest；
- 保存 pipeline 版本、代码提交、电脑环境和参数。

### 第 3 步：接入 NAS/A100 发布

- NAS final 临时目录和校验；
- A100 rsync/SSH 断点续传和校验；
- publish 可独立重试。

### 第 4 步：接入后端回写和 NAS 关联

- 处理开始/阶段完成/处理失败/发布完成回写；
- 新增 NAS 扫描结果与 processing_run 的自动关联；
- 无法关联时提供人工确认入口。

### 第 5 步：在第二台同型号电脑复现

- 使用相同安装包和配置模板；
- 运行环境自检；
- 任选一台电脑执行同一 bag 的 `check/run/publish` 验证。

## 11. 后续多模态和 Agent 预留

phase1 结果包含图片、轨迹、Planning 和 `dataset_index.csv`，后续可在不改变前处理流程的情况下增加：

```text
phase1 final
  -> 本地 Qwen 多模态模型
  -> 图片/场景/行为自动识别
  -> 标签、解释或思维链结果
  -> 标注质量检查
  -> 训练数据筛选或再次处理
```

预留要求：

- 标注结果必须引用 `bag_uid`、`processing_run_id`、帧 ID 和图片路径；
- 模型名称、模型版本、提示词版本和推理参数写入 manifest；
- 模型生成结果与人工确认结果分开保存；
- Agent 只能调用已登记的处理/发布命令，不能直接删除 NAS 原始数据；
- 自动迭代必须保留每次输入、输出和决策日志。

这一部分不是第一轮 MVP 阻塞项；第一轮必须先保证 phase0/phase1、结果发布、manifest 和后端关联稳定。

## 12. MVP 验收标准

1. 同型号电脑按文档完成环境安装后，可以通过一条命令启动处理。
2. 真实 rosbag 可在本地完成 phase0；失败能够定位到具体步骤。
3. phase0 支持断点续跑，重复执行不会破坏已完成结果。
4. phase1 能基于 phase0 输出完成，并生成可校验的 manifest。
5. 个人电脑不从 NAS 拉取原始输入；输入来自与 NAS 相同的车端硬盘副本。
6. 最终结果能分别上传 NAS 和 A100，网络中断后可继续上传。
7. NAS 原始记录与个人电脑结果能够通过指纹/metadata 建立关联，无法关联时进入人工确认。
8. 处理状态和结果路径能够回写现有后端。
9. 不修改历史 NAS 数据，不迁移 MySQL，不引入新的数据库系统。
10. 第二台同型号电脑可以复现第一台电脑的处理结果。
11. 多人同时提交关联请求时接口保持幂等，不产生重复记录；全量强校验在后台限流执行，不阻塞页面请求。

### 12.1 第一轮交付完成定义

必须使用一份真实新增数据完成以下连续链路，并以最后一步成功作为 MVP 交付通过：

```text
移动硬盘输入
  -> 本地输入清单/指纹
  -> phase0 成功
  -> phase1 成功
  -> manifest/checksum 生成
  -> NAS final 发布并校验
  -> A100 目标目录发布并校验
  -> 后端回写 processing_run
  -> NAS 原始记录与处理结果关联
```

其中任一步失败都必须能看到明确错误、保留日志，并通过 `resume` 或 `publish` 继续；不能以“phase0 已完成”作为第一轮交付完成的依据。

## 13. 成功指标

- 单个 bag 从插盘到启动处理不超过 3 个手工步骤；
- phase0/phase1 不需要手工逐步复制命令；
- 处理失败可通过 `resume` 或 `publish` 恢复，不需要从头开始；
- NAS 和 A100 结果均有 manifest 和 checksum；
- 处理人员无需手工维护 Excel 才能知道结果对应哪个原始数据；
- 新电脑加入流程的主要工作变成安装运行包，而不是修改脚本。

## 14. 明确结论

本 PRD 的第一轮交付目标是“在同型号电脑上通过一键命令完成一次真实数据的端到端处理和共享”。数据库、数据管理界面只做支撑性最小改造，不切换数据库、不做历史迁移、不扩张为完整平台。只要输入副本、NAS 原始记录、处理运行、NAS 结果和 A100 结果通过 manifest/指纹关联起来，后续的多人协作、自动标签和大模型 Agent 都可以在这条稳定链路上继续建设。
