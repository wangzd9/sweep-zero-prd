# NVIDIA PhysicalAI 数据集处理链路 TODO

更新时间：2026-09-23  
PRD：`/home/wang/work/doc/prd/vla_nvidia_dataset_pipeline_v1_prd.md`  
平台仓库：`/home/wang/work/rosbag-catalog`  
NVIDIA 脚本仓库：`/home/wang/work/dataset_build/nvidia_physicalai_route/code/proj_nvidiadata_builder_scripts`  
状态：批次 A～D 的代码和测试环境验收已完成；chunk30～33 已覆盖两个回传开关四种组合、真实 NAS 发布、血缘和容量 1 并行公平性。批次 E 的只读盘点、配置隔离、preflight 和回滚方案已完成；正式单 Chunk与生产部署仍未执行。2026-09-23 已补齐“下载原件 manifest”契约：NAS origin 只接收 Hugging Face 下载清单中的 10 个 ZIP 和 6 个 calibration Parquet，不接收解压派生文件。

## 1. 使用规则

- 本文件是 NVIDIA 路线唯一任务追踪入口；自建路线继续使用 `vla_self_dataset_pipeline_v1_todo.md`。
- 当前开发默认在本地隔离环境和 A100 `/home/xmyf/wzd/test/rosbag-catalog/` 测试根完成。旧 `/home/xmyf/wzd/data/*`、`/home/xmyf/wzd/runs/*` 仅作只读兼容快照；未经用户在当前任务明确授权，不得写入 `/data/nvidia_origin_dataset`、`/data/nvidia_infer_dataset` 或正式 NAS final。
- 系统只有本地测试和处理机生产两个逻辑环境；mock/real 是测试执行模式，NAS/A100 测试根属于本地测试环境，不构成第三环境。
- 测试目录必须与正式目录同构：
  - origin：`/home/xmyf/wzd/test/rosbag-catalog/data/nvidia_origin_dataset/data_sample_chunk<N>/`
  - infer：`/home/xmyf/wzd/test/rosbag-catalog/data/nvidia_infer_dataset/data_sample_chunk<N>/infer/<clip_uuid>/`
  - run：`/home/xmyf/wzd/test/rosbag-catalog/runs/nvidia/<pipeline_run_id>/`
- 原始下载数据回传 NAS 使用任务级 `publish_origin_to_nas`，默认 `true`；最终结果回传 NAS 使用独立的 `publish_final_to_nas`，默认 `false`。
- 两个开关都关闭时，质量通过后进入 `NVIDIA_DONE`；最终结果开关开启且 NAS final 原子发布成功时进入 `PUBLISHED`。
- 只有代码、测试或真实运行证据支持时才能标记 `[x]`；局部实现使用 `[~]`，未开始使用 `[ ]`。
- 平台和 NVIDIA 脚本是两个独立仓库，必须分别提交、分别记录 revision，不得复制目录或混合提交。
- 每项完成后同步本文件和 `rosbag-catalog/HANDOFF.md`；功能开发取得验证证据后生成待审更新日志，不得自动批准或发布。

## 2. 当前事实基线

### 已确认完成

- [x] 平台已有 `NVIDIA_QUEUE`、`NVIDIA_DONE`、NVIDIA claim/dispatch 分支和 NVIDIA 重试起点。
- [x] 平台已有单 chunk 创建入口 `POST /api/v1/nvidia/chunks` 和简易 `/nvidia` 页面。
- [x] A100 代理已拆出 `scripts/nvidia_pipeline.py`，并通过固定 NVIDIA 脚本入口执行任务。
- [x] 独立 wrapper `run_nvidia_chunk.py` 已完成 chunk 2 的单 clip、非下载测试，覆盖解压、Phase1、导航、VLM、final 和原始数据 NAS 回传。
- [x] A100 test/production 各有独立 NVIDIA Git 工作区和固定软链接；测试任务只使用 `/home/xmyf/wzd/test/rosbag-catalog/{repos,code}/nvidia`，生产 `/home/xmyf/wzd/{repos,code}/nvidia` 不随测试更新。

### 仅部分完成

- [x] 单 chunk 与批量控制面均已具备 preview/create、approved config、revision/config 快照和双回传开关；批量支持表达式解析、SubmissionBatch、幂等续建和聚合进度。
- [x] wrapper 已接入固定 revision 下载、完整性校验和八步 DAG；chunk30 的全量 100 clips 与后续组合任务已有真实验收。
- [x] wrapper 已生成 raw/chunk/quality 三类机器可读报告并执行发布前质量门禁；另生成 `download_payload_manifest.json`，以下载清单中的原件作为 NAS origin 白名单。
- [x] PRECHECK 到 FINAL_VALIDATING、NAS_BACKUP、NAS_FINAL 已映射为独立 Backend StepRun；质量失败不会进入完成态。
- [x] A100 测试数据已由旧式 `/home/xmyf/wzd/data/nvidia/origin|infer` 原子迁移为同构根 `data/nvidia_origin_dataset|nvidia_infer_dataset`，chunk 2 原有数据保留。
- [x] 平台已有任务、租约、heartbeat、事件、Artifact 和 SourceCopy 公共能力；NVIDIA 已登记 raw manifest、quality report、A100 结果、NAS origin/final 的父子血缘。

### 关键能力状态

- [x] 固定 Hugging Face commit SHA 的自动下载、缓存续传、退避重试和下载完整性校验已实现；真实 chunk0 下载 16 个对象约 15.1 GB，并据此修复了解压后文件数误判。
- [x] NVIDIA chunk/clip 业务质量报告和严格发布门禁已实现，并已用于真实全新 Chunk 验收。
- [x] 最终结果 NAS 回传开关已进入任务契约且默认关闭；开启时使用 staging、manifest 对账和原子发布，失败不会进入 PUBLISHED。
- [~] 批量 chunk 提交和中断续建已实现，容量 1 的并行等待与释放已验证；更高容量收益、版本发布和正式目录切换仍未完成。

## 3. 当前状态复盘与执行优先级

| 优先级 | 任务 | 状态 | 启动条件 | 完成标准 |
|---|---|---:|---|---|
| P0-0 | 冻结路径、状态和回传契约 | `[x]` | 本 PRD 已更新 | 测试/正式根、两个完成态、原始/最终回传语义进入配置、模型和测试 |
| P0-1 | Pipeline 配置、数据身份和提交模型 | `[x]` | P0-0 | 固定 repo/revision/config；支持单 chunk 幂等提交和不可变两个回传开关 |
| P0-2 | 自动下载与原始数据校验 | `[x]` | P0-1 | 固定 revision、受控 endpoint、缓存续传、限次退避、文件清单和冲突校验已通过单测/A100 小型验证 |
| P0-3 | 分步骤 DAG、状态回写和恢复 | `[x]` | P0-1 | PRECHECK 到 FINAL_VALIDATING 均有独立 StepRun，可从最近安全检查点恢复 |
| P0-4 | manifest、质量报告和发布阻断 | `[x]` | P0-2/P0-3 | chunk/clip/文件/索引/NPY/导航/描述规则形成结构化报告，不合格阻断完成态 |
| P0-5 | NAS 原始备份与可选 final 发布 | `[x]` | P0-4 | origin 默认回传但可关闭；final 默认不回传，两个动作分别原子发布并登记血缘 |
| P0-6 | NVIDIA 创建和详情页面 | `[x]` | P0-1/P0-3 | 页面支持开关、配置、步骤、质量、路径、错误和恢复入口 |
| P0-7 | 本地和 A100 测试根端到端验收 | `[x]` | P0-2～P0-6 | chunk30～33 覆盖四种开关组合，完整质量、实际 NAS、Artifact/SourceCopy 与终态一致 |
| P1-1 | 批量表达式与 SubmissionBatch | `[x]` | P0-7 | 支持单值、离散、闭区间、混合、预览、去重、幂等续建、聚合进度和最多 30 个 chunk |
| P1-2 | 公平资源调度与容量压测 | `[x]` | P0-7 | 默认容量 1 下 chunk32/33 同时提交，等待 heartbeat、公平取得、失败释放和最终释放均有真实证据；未提高默认容量 |
| P1-3 | 故障注入和运维闭环 | `[~]` | P0-7 | 下载断线内部重试、磁盘门禁、NAS 冲突、空闲代理重启和活动进程启动阻断已验证；明确 Backend 短断、独立 SSH 临界断线和在途 Phase0 重启仍待补测 |
| P2-1 | 正式 `/data` 目录切换 | `[~]` | P0/P1 验收且用户明确授权 | 只读盘点、同构配置、preflight 和回滚方案已完成；正式单 Chunk及批量开放保持禁止 |

## 4. 推荐执行批次

### 批次 A：契约和最小单 chunk 控制面

- [x] **NVIDIA-P0-01**：新增 approved pipeline config，固定 `dataset_repo`、解析后的 commit SHA、代码 revision、并发参数、VLM 配置和测试根。证据：`config/nvidia_pipeline_configs.json` 及配置加载校验测试。
- [x] **NVIDIA-P0-02**：PipelineRun 已固化 `pipeline_type`、config snapshot、source identity、`publish_origin_to_nas=true`、`publish_final_to_nas=false`；迁移 `20260921_01` 已通过 SQLite 往返和本地 MySQL 8.4 部分失败续跑验证。
- [x] **NVIDIA-P0-03**：已新增 configs、单 chunk preview/create API；数据库活动身份唯一约束、同参重放和异参 `409` 已由 API 测试覆盖。
- [x] **NVIDIA-P0-04**：`/nvidia` 已加入两个独立开关及提交确认页，默认值和活动任务提示已由页面测试及桌面/390px 运行截图验证。
- [x] **NVIDIA-P0-05**：A100 `--check` 确认无运行任务和目标冲突后，以原子 rename 把旧 origin/infer 迁移到同构测试根，并创建 `/home/xmyf/wzd/runs/nvidia`；未覆盖数据、未访问正式 `/data`。

### 批次 B：下载、DAG 和恢复

- [x] **NVIDIA-P0-06**：`download_physicalai.py` 支持固定 `--revision`、受控 endpoint、机器可读清单和明确退出码；脚本仓库提交 `d4107cf`。
- [x] **NVIDIA-P0-07**：wrapper 支持 HF 缓存续传、60/120 秒退避、最多三次下载尝试；SSH 启动未知时先对账远端状态/PID，平台单测覆盖；脚本仓库提交 `d4107cf`，平台后续提交锁定最终 revision。
- [x] **NVIDIA-P0-08**：PRECHECK、DOWNLOAD、VERIFY_DOWNLOAD、EXTRACT、PHASE1、NAVIGATION、DESCRIPTION、FINAL_VALIDATING 映射为独立 StepRun，NAVIGATION 的 rule/route 作为同一原子步骤记录。
- [~] **NVIDIA-P0-09**：恢复文件记录远端 PID、启动时钟、当前 step、attempt 和运行目录；代码、代理重启恢复单测及 A100 小型验证已完成，尚未做在途任务的真实代理重启故障复验。
- [x] **NVIDIA-P0-10**：解压不传 `--delete`，已有文件按 CRC/大小一致性复用；内容冲突、符号链接和路径穿越停止并返回冲突码，脚本仓库提交 `311b0f5`。

### 批次 C：质量、NAS 和血缘

- [x] **NVIDIA-P0-11**：生成 `chunk_manifest.json`、`raw_manifest.json` 和 `quality_report.json`，包含 schema version、revision、config、文件数、大小和 SHA-256；脚本仓库 `6300c66`。
- [x] **NVIDIA-P0-12**：校验 clip 清单、7 路图片、CSV、NPY shape、轨迹、导航和描述覆盖率；强制项失败阻断完成态。
- [~] **NVIDIA-P0-13**：`publish_origin_to_nas=true` 时已依据 `download_payload_manifest.json` 发布到 `nvidia_origin/.incoming/<revision>/<chunk>`，校验后原子切换；真实微型白名单 rsync、NAS 原子发布、复用和冲突均通过，但尚缺一个全新真实 Chunk 按新下载原件边界完成完整 origin 发布。关闭时不传输 origin。
- [x] **NVIDIA-P0-14**：`publish_final_to_nas=false` 时不执行 final rsync、不登记 NAS final Artifact，并进入 `NVIDIA_DONE`。
- [x] **NVIDIA-P0-15**：`publish_final_to_nas=true` 时使用 final `.incoming`、manifest 对账和原子发布，登记父子 Artifact/SourceCopy 并进入 `PUBLISHED`。
- [x] **NVIDIA-P0-16**：详情页展示 Hugging Face revision、代码 revision、Chunk、下载端点、两个回传开关和更新后的阶段列表。

### 批次 D：端到端验收和批量能力

- [x] **NVIDIA-P0-17**：本地 fake NAS/SSH 已覆盖 origin/final 四种开关组合及 `NVIDIA_DONE`/`PUBLISHED`，既有测试同时覆盖幂等、NAS 冲突、SSH 未知启动恢复、质量失败和资源租约释放；定向测试 `25 passed`，全量门禁 `168 passed, 1 warning`。
- [~] **NVIDIA-P0-18**：真实 chunk30～33 在新测试根完成 origin/final 四种组合；旧验收已证明状态、质量、manifest、父子 Artifact 和实际目录一致，但 origin 部分使用旧整目录发布语义，需按下载原件 manifest 新契约复验。
- [~] **NVIDIA-P0-19**：origin/final 实际 NAS 发布、关闭时的 `SKIPPED`、父子 Artifact、SourceCopy 和 `.incoming` 清理均已对账；final 组合已到 `PUBLISHED`，origin 需补全新下载原件边界的全新 Chunk 证据。
- [x] **NVIDIA-P1-01**：实现单值/离散/闭区间/混合表达式 parser、去重与最多 30 个限制，新增 preview/create/progress API、`SubmissionBatch` 迁移、幂等重放/中断续建和聚合进度页面；支持部分已有任务与新任务混合提交。
- [x] **NVIDIA-P1-02**：chunk32/33 同时提交时由唯一 `A100_COMPUTE_IO slot-0` 串行执行，等待任务持续 heartbeat，前序释放后后序立即取得资源，最终两者完成且代理 `active_runs=[]`；基于证据保持默认容量 1。

### 批次 E：正式目录切换，默认禁止执行

- [x] **NVIDIA-P2-01**：已只读盘点正式 origin/infer：chunk0～29 均存在、`/data` 最新约剩 626 GiB、VLM 健康、生产代码为 `b6c2823`，正式 run 根尚不存在；历史目录冲突会阻断覆盖式验收。
- [x] **NVIDIA-P2-02**：test/production approved config 只允许环境名、三类根路径和批量开关不同；平台与 A100 代理均精确校验根路径，自动测试证明跨环境配置被拒绝。
- [x] **NVIDIA-P2-03**：新增只读 `scripts/nvidia_production_preflight.py` 和 `docs/nvidia-production-cutover.md`，覆盖空间、冲突、代码 revision、软链接、活动任务、VLM、切换门禁和回滚；本轮用户授权完成准备，但明确不执行处理机部署或正式数据写入。
- [ ] **NVIDIA-P2-04**：正式目录执行单 chunk 验收后再开放受限批量；不得直接全量处理历史 chunk。

### 批次 F：NVIDIA 帧级入库（DatasetFrame）

> 目标：NVIDIA chunk 流水线终态前，把产物内每帧结果导入 `DatasetFrame`，与自建链路同表、同 `sample_id` 规则（`{source_id}/{clip_id}/{frame_id}`），网页统一可查/可筛。仅平台仓库改动，A100 脚本仓库、表结构、`/frames/bulk` API 本期不动。

- [~] **NVIDIA-P1-10 帧级入库**：新增 `scripts/nvidia_frame_importer.py`（解析 strict 索引 + navi_text + clip 级 description，拼相机/egomotion 相对路径，生成原始行走 `/frames/bulk`），在 `nvidia_pipeline.py` 于 `NAS_FINAL` 之后、`PUBLISHED`/`NVIDIA_DONE` 之前插入 `FRAME_IMPORT` 本地步骤（RUNNING/DONE/FAILED，不开新 run 状态）。**代码+单测已完成**（`tests/test_nvidia_frame_importer.py` 21 用例 + `tests/test_nvidia_pipeline_frame_import.py` 6 用例，NVIDIA 定向 50 passed，真实 chunk0 样本解析 114 帧、相机时间 114 个不同取值验证字段契约）；待本地 Compose 实测（P1-11）后转 [x]。
  - **字段契约**：`ego_ts_us=strict.ego_ts 原值`（clip 相对 µs），`timestamp_ns=ego_ts_us*1000`；`{cam}_f{n}_ts_ms=round_half_up(strict.{cam}_f{n}_ts/1000)`（.5 进位，加边界测试），`{cam}_f{n}_ts_us=strict.{cam}_f{n}_ts 原值`（随原始行进 `payload_json` 保留精度）；相机集合从 strict 列名 `camera_*_f{0-3}_idx` 推导并与既定 7 相机校验，整路缺失即失败；`*_image=camera_images/{cam}/{idx:06d}_small.jpg`，`history/future_gt=egomotion/frame_{ego_idx:06d}_{history|future_gt}.npy`，均相对 `clip_data_root`；`planning_available=1`、`planning_frame_id=frame_id`、`planning_ego_time_diff_ms=NULL`、`quality_status=VALID`、`navigation=navi_text.final_nav`、`description=clip_discription_llm.txt`（clip 级填充每帧）；`csv_schema_version=nvidia-infer-index-v1`。
  - **clip_data_root**：A100 `{output_path}/infer/{clip_id}/data`；NAS `{final_path}/infer/{clip_id}/data`（`publish_to_nas` 复制的是该目录内容，不再追加 `data_sample_chunkN`）。
  - **导航/重复门禁**：strict 内重复 `frame_id`、navi 缺 ID 或重复 ID、strict/navi frame_id 集合不相等 → 导入失败（首版无容错阈值）；每帧 `navigation` 必须命中。
  - **文件核对**：NAS 分支复用 `infer_manifest`（逐文件 SHA-256，`files[].path` 相对产物根、前缀 `infer/{clip}/...`）核对引用图片/npy 存在性；A100 分支每 clip 一次批量 `sh -c` `test -f`（汇总任一缺失返回非零，路径 `shlex.quote` 安全传递，不逐图 SSH）。
  - **manifest 身份绑定**：首次提交帧前用 `register_artifact`（固定 `artifact_id={run_id}-nvidia-frames` + **attempt 无关**幂等键）持久化绑定 `infer_manifest_hash`；重试时同键同参重放，manifest 变化 → 409 失败提示人工处理，不自动清表；沿用现有表与 bulk API，不新增删除/断点 API。
  - **开关**：`nvidia_pipeline_configs.json` 加 `frames_import`（JSON 布尔，`nvidia_configs._validate_config` 强校验非 bool 即拒）；test 显式 `true`、production 显式 `false`；proxy 从 `snapshot["frames_import"]` 读取，历史 snapshot 缺字段保持关闭（不做 `bool("false")` 宽松转换）。改动含 `a100_host_proxy.py` 配置传递。
  - **验收**：入库帧数 = 各 clip strict 唯一 `frame_id` 之和（不以 `preprocess_metadata.num_valid_frames` 为准）；`GET /frames?source_id` 抽查路径存在、payload 含 `*_ts_us`、navigation/description 命中；幂等重放无重复行；自建链路回归全绿。
  - **已知数据事实**：chunk0 example 样本 `infer_data_reduce` 只删图不删 npy，但 strict 有 24/114 行引用磁盘缺失 npy（example 为手工示例）；生产 wrapper 保留全量 npy。单测用仓库内构造的完整夹具；外部真实样本仅可选集成测试。
- [ ] **NVIDIA-P1-11 本地 Compose 实测**：测试环境跑一个真实/构造 NVIDIA chunk 到 `FRAME_IMPORT`，核验 `DatasetFrame` 行数、路径、幂等与页面帧查询；本地栈 `local_stack.sh test` 收敛。
- [ ] **NVIDIA-P1-12 生产灰度**：用户授权后，生产单 chunk `frames_import=false→true` 验证一个 chunk 再保留开启；处理机部署与本地收敛按既定流程。

## 5. P0 验收门禁

- [x] 本地单元/API测试覆盖 chunk、幂等、配置快照和两个回传开关的默认值及不可变性。
- [~] wrapper 测试已覆盖下载重试、解压冲突、缺文件/空文件、CSV 图片引用、NPY 和描述缺失；ZIP 损坏及 VLM 拒绝/超时/非法 JSON 的完整矩阵仍需补齐。
- [x] 所有远端命令由 approved config 和固定参数模板生成，endpoint 使用白名单，路径受 test/production 精确根约束，不接受用户 Shell 或任意 Python 参数。
- [~] 原始数据回传的 staging、checksum、真实 NAS 发布和关闭时跳过记录已实现并通过微型白名单、原子发布和冲突验证；旧 chunk30/33 的 origin 证据仍是整目录语义，尚缺全新真实 Chunk 按 10 ZIP + 6 calibration Parquet 下载原件清单发布的完整验收。
- [x] final 关闭/开启、原子发布、同内容复用/冲突保护和真实 NAS final 均已验收。
- [~] 单测覆盖租约、heartbeat、恢复文件和释放；真实 Backend 中断暴露旧 lease 无法重新认领，代理重启矩阵未完成。
- [x] A100 测试/正式根可机器校验，测试配置不能指向 `/data/nvidia_*`，正式配置不能指向 `/home/xmyf/wzd/test/*`；生产代码和数据本轮未修改。
- [x] 全新 chunk 的四种开关组合分别达到预期 `NVIDIA_DONE`/`PUBLISHED`，页面、数据库、manifest 和实际目录一致。

## 6. 当前禁止事项

- 不得把测试环境四组合验收描述为正式 `/data` 已准入或处理机已发布。
- 不得在未固定 Hugging Face commit SHA 时创建可发布的数据版本。
- 不得把 `publish_origin_to_nas` 默认设为关闭；不得把 `publish_final_to_nas` 默认设为开启；两个开关不得互相控制。
- 不得在测试阶段写入正式 `/data/nvidia_origin_dataset`、`/data/nvidia_infer_dataset` 或批量修改已有目录。
- 不得通过 rsync/scp 覆盖 A100 NVIDIA 代码仓库；继续使用独立 Git 工作区更新流程。
- 不得因 HTTP/SSH 超时直接重跑未知状态的远端下载或处理步骤，必须先对账 PID、状态文件和产物。

## 7. 更新记录

- 2026-09-28：生产 chunk31 run `4fb4e1dc55be4a6491de95e8501677a5` 因 VLM 单 clip 间歇性非法 JSON（```json 围栏包裹/截断）致 `clip_discription_llm.txt` 缺失，attempt 1/2 两次 `QUALITY_DESCRIPTION_FAILED`——旧脚本对单 clip 报错仍退出码 0，DESCRIPTION 标 SUCCEEDED，resume 永不重算。用户授权后在 A100 单 clip 重生成描述（第二次成功），attempt 3 质量门禁通过，16:55:46 收敛 `NVIDIA_DONE`（该配置 `publish_final_to_nas=false`，NVIDIA_DONE 即预期终态），origin 发布 NAS `/mnt/nas_backup/vla_dataset_builder_backup/nvidia_origin/33f9bf44…/data_sample_chunk31`（15G）。脚本仓库提交 `95f4ff6`（基线 `52f65d1`）加 clip 级幂等：`clip_llm_comprehension.py` 已有非空描述即 skip、`navi_gen_llm.py` 已有 `is_llm_correct`/`llm_verdict` 列即 skip，两脚本 `grand_err>0` 退出码 1 使步骤如实 FAILED——此后 retry 只重算失败 clip（几十秒/~9k token），不再整 chunk 23 分钟 + ~96 万 prompt token。新增 `tests/test_phase2_clip_idempotent.py` 5 用例，`26 passed`；ocr 审查 session `14a9e337` 0 findings；已推送内网 GitLab 并经 `update_a100_script_repositories.sh --environment production --apply --production` 同步 A100 生产脚本根（A100 revision=95f4ff6，同步时无活动任务），A100 实测单 clip 0 秒 skip。未做：`navi_gen_final.py` 幂等、`call_vllm` 解析层非法 JSON 加固（待用户拍板）。
- 2026-09-23：批次 D 在双环境测试 real 模式完成真实收口。chunk30 `true/false -> NVIDIA_DONE`、chunk31 `false/false -> NVIDIA_DONE`、chunk32 `false/true -> PUBLISHED`、chunk33 `true/true -> PUBLISHED`；NAS origin/final、父子 Artifact、SourceCopy、manifest 和实际目录一致。chunk32/33 并行证明默认容量 1 的等待、公平取得和最终释放。真实 Hugging Face `IncompleteRead` 暴露 wrapper 退避期间中间 `FAILED` 被代理过早确认的问题，平台提交 `0fe7e4b` 改为结合 PID/start ticks 对账，chunk33 在同一 wrapper 内跨三次断线完成。处理机、A100 `/data` 和 NAS 生产目录未写，正式单 Chunk仍受批次 E 门禁。

- 2026-09-23：修正 NVIDIA 原始 NAS 回传边界。脚本仓库提交 `52f65d1` 新增 `nvidia-download-payload-manifest-v1` 和 `download_payload_manifest.json`，仅从 `download_manifest.json.files` 生成下载原件清单（当前 10 个 ZIP + 6 个 calibration Parquet），与包含解压产物的 `raw_manifest` 分离；平台提交 `4c4ee6d` 让 `NVIDIA_ORIGIN_NAS` 发布、rsync 白名单和 NAS 原子验收均消费该清单，阻止 MP4/推理 Parquet 等解压派生文件进入 origin。脚本仓库单测 `21 passed`，平台全量测试 `228 passed, 1 warning`，Ruff、compileall、Compose、diff 检查通过；A100 测试工作区已同步 `52f65d1`，真实微型白名单 rsync 与 NAS publish/reuse/conflict 通过。由于尚未用全新真实 Chunk 按新边界完成完整 origin 发布，NVIDIA-P0-13/P0-18/P0-19 保持 `[~]`，处理机和正式目录未更新。

- 2026-09-21：完成批次 B 代码和测试收口。NVIDIA 脚本仓库提交 `3fdd74f` 增加输出归属/导航原子步骤，提交 `311b0f5` 增加不可覆盖解压、CRC/大小复用、路径/符号链接冲突保护；A100 测试工作区已通过独立 Git 流程更新到 `311b0f5`。平台侧锁定 `code_revision=311b0f5a8e097b8cad5f6ea0787b6e91a087ed3e`，定向测试 `21 passed`，全量质量门禁 `149 passed, 1 warning`，本地 Compose 闭环流水线 `a66495af3f8f405eaf4a1e4c497ea159` 到达 `PUBLISHED` 并导入 DatasetFrame；A100 测试根完成 compile/help、非法契约和输出目录冲突小型验证。未执行真实大文件下载、全新 chunk 端到端、在途代理重启故障复验、处理机生产部署；质量 manifest、NAS final 和正式目录仍属批次 C/E。
- 2026-09-21：完成批次 C 代码和本地验证。脚本仓库提交 `6300c66c07772eafc31150751324fe909ac43209` 与 `b6c28232e1609ce7f37c2994bc5e161c2406240e` 增加 raw/chunk/quality 三类 SHA-256 报告、7 路相机/严格 CSV/NPY/导航/非空描述质量门禁；平台提交 `b415f02`、配置锁定提交 `38ecc40` 已推送 `github/main`，接入 origin revision staging 原子发布、final NAS 开关、父子 Artifact/SourceCopy、manifest Artifact 枚举和 NVIDIA 详情契约展示。脚本测试 `18 passed`，改动文件 Ruff/compileall/diff 检查通过；平台全量质量门禁 `153 passed, 1 warning`；A100 测试工作区已更新至 `b6c2823`，本地隔离流水线 `ed6108b657ed43ee80a662cdfbf80bcb` 到达 `PUBLISHED`。待审日志为 `F-010`，保持 `pending`。未执行真实全新 Chunk 下载、四种 NAS 开关组合、在途代理重启故障复验和处理机生产部署，批次 D 保留真实端到端验收。
- 2026-09-22：批次 D 完成本地验收与批量控制面，平台提交 `850ea9f` 已推送 `github/main`。新增迁移 `20260921_02`、Chunk 表达式解析、SubmissionBatch preview/create/progress API、批量页面、聚合进度、幂等重放与 `SUBMITTING` 中断续建；fake NAS/SSH 覆盖 origin/final 四种开关组合，分别收敛到 `NVIDIA_DONE`/`PUBLISHED`。全量质量门禁 `168 passed, 1 warning`，SQLite 迁移 upgrade/downgrade/upgrade 和本地 MySQL 8.4 `20260921_02 (head)` 通过，本地模拟流水线 `bcd4e9f9104e4568b7583b3c3f0d0c06` 到达 `PUBLISHED` 并导入 DatasetFrame，批量页面和 `1,5,10:12` 预览 API 实测通过。A100 测试根仅有已有 chunk 2，未执行全新 Chunk 下载、四组合真实 NAS、资源容量压测或生产部署，因此 P0-18/P0-19/P1-02 保持未完整验收。
- 2026-09-22：继续执行批次 D/E。真实 chunk0 流水线 `c366af344d414c45be1f0dd365210d75` 完成下载、解压、100 clip Phase1、导航和导航 VLM；脚本提交 `240dc62` 修复下载 manifest 的 16 个对象与解压后 2233 个文件混淆，提交 `b959d9b` 补上 DESCRIPTION 中的 `clip_llm_comprehension.py`。新测试根复制单个 230 MB clip 后真实生成 39 帧采样、4 个区间的场景描述，旧兼容快照未修改。期间本地 Backend 中断导致 lease 过期，远端成功回写得到 409，完整 Chunk未到发布态。正式 chunk0～29、约 626 GiB 剩余空间、权限、代码和 VLM 已只读盘点；目标 `b959d9b`/候选 chunk30 preflight 因生产代码仍为 `b6c2823` 正确阻断。同构配置和回滚文档完成，正式批量保持关闭。平台完整门禁 `188 passed, 1 warning`，本地模拟流水线 `d34cb14d5a3246e2804b42b930892c96` 到达 `PUBLISHED`。本轮未部署处理机、未更新 A100 生产代码、未创建 `/data/nvidia_pipeline_runs`、未写正式 `/data`。
- 2026-09-22：上述真实质量修复已合并到待审日志 `F-010`，状态保持 `pending`，未批准、未发布。
- 2026-09-21：从自建路线 TODO 中拆出独立 NVIDIA 追踪文档；明确原始数据回传使用默认开启的 `publish_origin_to_nas`，最终结果回传使用默认关闭的 `publish_final_to_nas`，两者独立控制；当时测试根为 `/home/xmyf/wzd/`。2026-09-22 起新任务已迁至 `/home/xmyf/wzd/test/rosbag-catalog/`，旧根冻结为只读兼容快照；两者的目录组织均镜像正式 `/data/nvidia_origin_dataset`、`/data/nvidia_infer_dataset`，正式目录切换保持独立 P2 门禁。
