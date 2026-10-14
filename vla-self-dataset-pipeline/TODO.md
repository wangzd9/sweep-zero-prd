> 2026-10-13水雾专项更新：受控test车辆真实首包生产上线验收PASS，业务3c9c496、本地同版本通过，文档63bfcf8已推github/main。水雾独立目录与处理机本地非模型执行不迁移既有自建/NVIDIA路线。任务权威状态与更广未完成矩阵见 /home/wang/work/doc/prd/rosbag-catalog-integration/TODO.md；结果 /home/wang/work/doc/analysis/spray-production-release-20261013/REPORT.md。19:00目标未达、新UI继续暂停。

# VLA 数据处理链路 V1 待办与进度

> 本文件是后续自建数据集开发的唯一任务追踪入口。每次开发前先阅读本文件；完成代码、部署或真实验证后，必须同步更新对应条目的状态、证据、验证结果和剩余风险。所有交互和记录使用中文。
>
> 状态：`[x]` 已实现并有真实证据；`[~]` 部分实现或局部验证；`[ ]` 尚未实现。PRD 是目标态，不能替代代码和运行结果作为完成证据。

## 2026-10-08 Phase0 GPU故障与无进展诊断待办

- [x] P0-4/P0-5只读诊断：生产任务`c92468135e2b40019d679e4f30313987`原attempt1停在相机提取，确认RTX5080要求Reset与09-30 Xid62/154；诊断提交`4f1011f`已推送github/main。后续恢复已获授权并执行，见下一条与HANDOFF，不再以初次只读状态为现状。
- [x] 用户已授权直接处理：2026-10-08 09:41:06维护重启恢复GPU，CUDA初始化/分配/同步通过；原attempt1进程树退出且状态对账为FAILED，原始NAS未改。
- [~] 原GPU故障任务继续验收：attempt2提取15848张图片后触发95%显存门禁及Xid31，已失败并保留；修复后attempt3长包五路抽帧148248张DONE，采样显存峰值596MiB、无新Xid。13:37最新只读对账：任务于13:20:16转FAILED，FRAME_INDEX_IMPORT读取A100 clip108描述文件SSH exit255；Phase0七步/上传/Phase1/Phase3各步及质量检查均DONE，尚未验收帧索引及发布结果。此为远端读取失败，不是新GPU故障；未重试，SSH具体原因待定位。全量抽帧所用仍为早期6922dc6，不宣称新正式构建全量重跑。
- [x] **处理机 Phase0 副本**的GPU队列与CUDA/NVDEC失败传播修复：最终`b9abece`10:27已激活，binary SHA256 `5df66ef10c828e61ad7671b2cdaf576be094284895d12b88cfbd213916d0cb84`；5项并发测试/ASan/UBSan/处理机编译及CTest通过，分配与解码第1/80次四项注入均exit1无done，636张JPEG与时间戳匹配旧二进制。全量长包抽帧实测版本为6922dc6，后续版本仅补异常分支。OCR high已修，2条notify_one medium为误报，剩1条low日志建议。副本源码4提交已推GitLab `zhangguowei.ai/vla_dataset_builder.git origin/main`，远端HEAD与本地同为`b9abece2fb4e7f16474100081e31e74e6d583c06`；此前失败是origin仍走HTTP，已切换SSH，本机SSH认证正常。此条记录10:27的历史副本同步；正式基线随后已补回并重新构建部署，当前版本见下一条及部署快照。处理机有备份及哈希记录，Catalog恢复记录102f1da/5f98d6a与推送纠正26395fc均已推github/main。
- [x] **补回正式自建脚本基线并验证可复现构建**：正式根`/home/wang/work/dataset_build/self_built_route/code/proj_self_dataset_builder_scripts`，GitLab `wangzhendong/dataset_build.git main=81b1e83`、独立源码分支`xunlingbagparse-source=657a2e0`均已推送，`.gitmodules`相对URL及固定gitlink已生效；保留原13提交与未跟踪缓存、备份Git bundle，干净递归克隆成功。正式五文件与最终b9abece逐字一致。处理机正式提交重新构建/CTest及四项GPU注入、636张图片/时间戳逐项对比通过；开发机补齐隔离动态库并完成同样GPU回归，两机binary SHA256同为`2f84236a79e73d87776185b16995b7674babc6d5ac063387b6f348229884b491`，receipt与回滚备份保留。A100 test/production通过严格parser-only模式同步且干净，五项队列测试通过；NVIDIA未改。Catalog最终质量门禁556 passed/10 skipped，部署后mock全链路PUBLISHED。新正式parser OCR两次超时不能记0 findings；同内容旧修复审查high已修，剩一条low日志建议。新运维工具提交75832f4、版本记录补强cd05af3均已推github/main，后者25项定向回归通过，测试适配9652e66已推送且26项定向/556项完整回归通过；最终mock run bbdb4b70a495451096121872b16970ed为PUBLISHED且运行版本95e183c对账无漂移，最新快照已由脚本生成。F-029日志为pending，独立审查存在超时与测试默认排除，未完整通过，已保留3条中/低建议及逐项判定，见HANDOFF；不把中止/超时/0 selected记为审查通过；未重启生产应用或打断在途任务。
- [ ] 补GPU健康门禁、无进展超时/完整进程树停止及步骤日志外置，验证GPU异常明确失败、日志清理不吞证据；本轮未开发，不改变其他任务完成状态。
- [~] 首次驱动异常溯源：13:31–13:37真实只读日志确认09-30 19:11:17为PMU halted，NVIDIA 610.57.04源码将其标记为fatal/reset-required；故障当天无整机休眠记录，已知前一平台抽帧17:28完成。RTD3省电/电源固件与平台交互为调查方向，但上游触发原因未闭环；仍需受控采样、RTD3对照和首次PMU/NvLog转储的厂商符号解码。本轮未改驱动或电源配置，诊断报告提交`8d326c4`已推`github/main`；证据与停止边界见`rosbag-catalog/docs/gpu-pmu-root-cause-20261008.md`及`.local/reports/gpu-rootcause-20261008/`。
- [x] 当前驱动与工具链适配只读核验：13:46–13:51确认610.57.04支持PCI2C59、Blackwell使用open模块正确，GSP/驱动库同版本，DKMS/headers/vermagic匹配6.8.0-138；正式解析器用Conda CUDA12.6而非系统默认11.5，sm80+PTX可前向兼容到GPU计算能力12.0，SDK13驱动要求满足。此条仅表示适配关系核验完成，不表示PMU根因消除或执行过升级；诊断提交`bb33d89`已推`github/main`，证据`.local/reports/gpu-compatibility-20261008/`和GPU报告的适配章节。后续如实施工具链整理，单独验证CUDA12.8+的sm120原生构建、保留A100的sm80/PTX与内容/异常/长包回归，本轮未实施。

## 2026-09-30 删除功能固定收口进展

- 用户要求直接完成现有功能，C1/C2/C3 已修复并有实证（`2ecd407`、`132fc72`、`acd6f59`）；全仓 525 passed，独占 MySQL 8.4 10 passed。
- 常驻 Compose MySQL 浏览器闭环、自建模拟 PUBLISHED+帧导入、confirm 后 worker 重启恢复通过；A100 测试根真实 writer 失联/孤儿子进程互斥通过。
- C4 常驻 SSH 真删终态已通过（真实 Phase1 写者阻断、同操作重启/SSH 失败恢复）；C5 只剩 OCR 最终结果。生产仍未发布。唯一剩余清单与证据见 `/home/wang/work/doc/rosbag-cleanup/TODO.md` 顶部，历史返修卡不再累加。

## 当前基线（2026-09-23，本地默认、处理机显式发布）

> 环境策略：系统只有本地测试和处理机生产两个逻辑环境。`mock|real` 是本地测试环境模式，L1～L4 是验证层级；本机 Phase0、NAS/A100 测试根不构成第三环境。只有用户在当前任务明确要求更新处理机时，才允许使用 `scripts/deploy_processing_machine.sh --apply --production`。详见 `rosbag-catalog/docs/local-test-environment.md`。

| 范围 | 当前事实 | 证据 |
|---|---|---|
| 自建输入 | Scanner 已完成多轮稳定、DB3 完整性、指纹冲突、incoming→ready 原子移动和“立即扫描”真实验收 | `app/scanner/`、提交 `5091fd4`、`d832832` |
| 自建处理闭环 | 生产历史已完成 Phase0、Phase1、导航/描述和发布；测试环境 real 已进一步验证 Phase3 导航/CoC/轨迹图/描述、质量、帧导入和 NAS test final 到 `PUBLISHED` | 生产流水线 `9dcbf06ef763438f873a6cd173d5fac2`；测试流水线 `6912262c698b4a85aaded5ba859fff41` |
| 结果与帧索引 | 统一 manifest/checksum、首条真实链路 747 条 DatasetFrame、生产绑定结果 34721 条对账、navigation/description 非空和三个结果 Artifact hash 一致已验收 | `scripts/result_validator.py`、`app/frame_importer.py`、迁移 `20260916_02` |
| 恢复与资源 | 普通重试自动从失败阶段继续；强制重试可选择 Phase0、Phase1、Phase3，按阶段失效派生数据并保留前置输入。平台和 A100 编排已有代码、单测与本地浏览器验证；三种强制起点仍待真实 A100 任务验收。代理运行文件/PID 恢复和 Phase1 SSH 未知启动结果对账已有代码和本地单测，但尚未完成处理机在途真实故障复验 | `app/services/pipeline_service.py`、`scripts/self_built_pipeline.py`、`tests/`、`HANDOFF.md` |
| 数据模型 | 本地与处理机迁移 head 均为 `20260921_02`；SourceCopy/Artifact 生命周期、统一中国标准时间、持久化自动重试字段和 NVIDIA 批量契约均已进入迁移链 | 处理机 revision `116b5ac`；迁移前双副本备份及真实恢复/回滚证据见 `HANDOFF.md` |
| 页面与部署 | Bag/扫描/流水线列表和详情已部署；流水线分页、表头排序、响应式、状态提示和静态资源指纹已在处理机验证；`/changelog` 已发布 F-002/F-003/F-006/F-013 | 发布批次 `prod-20260923-f002-f003-f006-f013`；处理机 revision `116b5ac` |
| NVIDIA | 已从本文件拆出独立任务追踪；当前仅保留单 clip 非下载历史验证，不纳入自建路线执行顺序 | `/home/wang/work/doc/todo/vla_nvidia_dataset_pipeline_v1_todo.md` |

## 当前状态复盘与执行优先级（2026-09-23）

本节是当前开发顺序的唯一有效版本；文末“历史开发顺序”仅用于追溯。当前自建路线已经完成“稳定输入→Phase0→Phase1/Phase3→质量校验→帧索引→NAS final→页面追踪”的生产闭环。2026-09-20 已完成处理机/A100/NAS 生产切换和单 Bag 验收；后续批量准入仍受 P0-1 业务质量门禁和生产数据保护规则约束。

本次复核以自建 V1 PRD、当前代码、迁移、`rosbag-catalog/HANDOFF.md`、本地 `224 passed, 1 warning` 质量门禁、测试环境真实 E2E 和已记录的生产验收为依据；批次 F 未部署处理机，未知的在途生产任务状态保持待确认。NVIDIA 路线不再在本文件内展开，详见独立 TODO。

### 已完成基线（不再占用当前开发批次）

| 能力 | 状态 | 已确认边界 |
|---|---|---|
| Scanner 稳定输入、指纹和 incoming→ready | `[x]` | 已真实移动和重启复验；NAS ready 后保持不可变 |
| Phase0/Phase1/Phase3 基线 | `[x]` | 生产历史导航/描述已执行且 CoT 保持 `SKIPPED`；测试环境 real 已验证当前四步 Phase3、747 帧质量映射和 NAS 测试发布，尚未生产发布 |
| DatasetFrame 批量幂等导入 | `[x]` | 真实导入 747 条；CSV schema、行号、批次和质量状态已存储 |
| 任务/资源租约和基础恢复 | `[~]` | 过期任务/资源收敛、heartbeat 和主动释放已有真实/本地证据；代理重启按运行文件/PID恢复、SSH 未知启动对账已有代码与单测，但处理机在途故障复验仍未完成 |
| NAS final 原子发布核心链路 | `[x]` | `.incoming` 无遗留、最终目录已发布且 manifest hash 一致；父产物关系已落地，只读保护和页面完整表达仍是当前缺口 |
| P0-2 MySQL 数据保护与生产切换 | `[x]` | 命名卷持久化、每 6 小时本地/NAS 双副本、7 天保留、隔离恢复、迁移回滚、百万帧容量/索引和生产单 Bag 切换均已验收；主动告警归入 P0-5 |
| SourceCopy/Artifact 生命周期模型 | `[x]` | `parent_artifact_id`、稳定唯一键、文件统计、`verified_at/deleted_at` 和代理清理回写已落地；页面完整表达仍归入 P0-3 |
| 流水线列表/详情与部署入口 | `[x]` | 处理机真实页面和静态资源版本一致性已验收；日志、heartbeat、质量摘要、冲突反馈和重试起点已在本地完成，生产发布验收归入 P0-5 |

### 当前未完成优先级

| 优先级 | 任务 | 状态 | 当前缺口/风险 | 完成判定 |
|---|---|---|---|---|
| P0-1 | 业务质量门禁和质量报告 | `[~]` | 现有 validator 能证明文件完整和 checksum 一致，但不能证明相机集合、NPY shape、轨迹及 description 覆盖率符合业务要求；空 navigation 是正常数据，不应作为发布阻断条件 | 根据输入/配置动态校验相机集合与数量、NPY shape、帧数和必要字段覆盖率；失败禁止 publish；质量结果结构化保存并在详情页展示，使用真实 Bag 验收 |

| P0-3 | 发布后不可变与完整血缘 | `[~]` | 数据模型已具备 `parent_artifact_id`、文件统计、校验/删除时间，代理清理回写和 NAS final 原子发布已实现；剩余缺口是 final 发布后只读保护，以及页面完整父子链和已删除路径语义 | final 发布后权限/不可变检查生效；详情页可从 Source 追到 final，展示父子产物并明确区分已删除路径 |
| P0-4 | 在途故障与恢复演练 | `[~]` | 持久化瞬时自动重试、最多两次退避、代理恢复和 SSH 启动结果对账已部署到处理机；尚未覆盖真实运行中的进程重启、SSH 临界断线、磁盘不足和 Backend 短暂不可用 | 在明确授权的处理机窗口注入故障；任务不重复执行、不永久 RUNNING，自动重试不超过预算，租约/资源最终释放，日志、事件和恢复步骤可复现 |
| P0-5 | 运维可观察性、告警和失败操作闭环 | `[~]` | 日志摘要/分页、Manifest/质量摘要、heartbeat、409/422 反馈、明确重试起点及自动重试计划/原因/次数页面已部署；自建路线失败信息已具体化（Phase0 日志末尾、Phase1 具体门禁项+exit code+日志末尾、Phase3 步骤/质量校验从远端 `phase3_run.json` 提取具体门禁/clip 原因，提交 `95f606d`；已随 2026-09-24 `740db18` 生产部署上线并重启代理，OCR 性能修复 `c0556a2` 待下次部署）；仍缺真实失败任务冒烟，备份失败、磁盘空间和 timer 失效无主动告警 | 处理机页面无需查库即可定位失败和重试计划；冲突/非法操作有可行动反馈；主动告警通道实测可达，并完成至少一个受控失败任务验收 |
| P1-1 | 资源等待、公平调度和单机并发验证 | `[~]` | 容量互斥、slot、heartbeat 和释放已完成，但缺少统一 PENDING 优先级、`RESOURCE_WAIT`、多 Backend/Worker 对账和容量大于 1 的收益验证 | Backend 按 `priority DESC, requested_at ASC` 公平授予资源；容量 2 返回不同 slot；多 Worker 不超卖、不饥饿，并以吞吐/失败率/磁盘指标决定是否提高生产容量 |
| P1-2 | DatasetFrame 组合检索与页面入口 | `[~]` | 批量导入和百万帧容量/索引基线已完成；仍缺按车辆/时间/标签/导航/质量/发布版本的完整组合查询、分页页面和“默认最新已发布合格版本”语义 | 完成组合查询与页面入口，默认只返回质量通过且最新发布版本，并可追到源 Bag 和 final Artifact；用既有百万帧基线复测查询计划和延迟 |
| P1-3 | 自动化测试矩阵和运维工具 | `[~]` | 当前本地质量门禁为 `129 passed`，已覆盖主要状态机、页面、迁移和本地模拟闭环；fake NAS/SSH、跨进程并发预算和故障注入仍分散 | 形成可重复脚本/测试矩阵，覆盖相同指纹并发、代理/SSH 故障、资源竞争、发布冲突、数据库恢复和磁盘不足 |
| P2-1 | Phase3 CoC 与轨迹诊断图接入 | `[x]` | 规则 CoC、轨迹图及其测试环境真实 Bag 发布闭环已完成并部署生产；新增 LLM CoC 已更新运行代码，但缺独立真实 vLLM 验收 | 既有测试流水线四步均 `DONE`，747 帧中 `VALID=567`、`INVALID_COC=180`，结果发布到 NAS 测试 final；既有生产 `SKIPPED` 历史不改写 |

自建 Phase3 新增的 LLM CoC 已随 F-016 发布到处理机 `0828e1c` 和 A100 production `a7b3b6b`：平台编排新增 `PHASE3_COT_LLM`，脚本校验逐帧 `cot_llm` 对齐及完成标记；空 `navigation` 不再阻断。定向测试和本地 mock 全链路通过，但 A100 test 单 clip 真实 vLLM 作业尚未验收；生产 attempt 9 在旧代理进程中运行，因缺 `cot_llm` 失败，不能视为新版真实验收。新代理现已重启并健康，后续需单独选择安全样本验证。

### 推荐执行批次

1. **批次 A：生产准入质量线（P0-1）**  
   优先补动态相机集合、NPY shape、轨迹和文本覆盖率等业务质量规则，结构化保存每项结果并阻止不合格数据发布。MySQL 数据保护、迁移演练和容量基线已完成，不再重复作为开发项；业务质量线完成前仍不能宣布可无条件批量接入生产数据。
2. **批次 B：发布数据不可变与血缘（P0-3）**  
   增加 final 发布后只读保护，并把已有 Artifact 父子关系、副本生命周期和删除状态完整展示到页面。该批次结束后，才能可靠回答“原始数据、处理中间产物和最终版本如何对应、当前文件是否仍存在”。
3. **批次 C：可靠性发布、主动告警与真实故障闭环（P0-4 + P0-5）**  
   自动重试迁移和页面已于 2026-09-23 发布；下一步在用户明确授权的生产窗口，用可控任务演练在途 Phase0/A100 重启、SSH 临界断线、Backend 暂不可用和磁盘不足，同时接入备份/磁盘/timer 主动告警。验收必须证明未知启动结果不会重复执行、自动重试不超过预算、租约最终释放且页面可解释恢复过程。
4. **批次 D：公平调度和规模能力（P1-1 + P1-2 + P1-3）**  
   先实现 `RESOURCE_WAIT`/全局优先级，再测试容量 2 和多 Worker；基于已完成的百万帧基线实现 DatasetFrame 组合检索和页面入口，并补可重复故障测试。只有吞吐提升且错误率、磁盘和 VLM 压力可控时才提高生产并发。
5. **已完成测试验收：Phase3 CoC 与轨迹诊断图（P2-1）**  
   A100 测试工作区和真实 Bag 已完成 CoC、诊断图、质量映射与发布门禁验收。后续只有在用户明确批准生产更新时才评估发布；现有已发布运行的 `PHASE3_COT=SKIPPED` 历史保持不变。
6. **边界说明：NVIDIA 不属于本 TODO**  
   NVIDIA 已迁移到 `/home/wang/work/doc/todo/vla_nvidia_dataset_pipeline_v1_todo.md`，其下载、批量、双回传开关和正式目录切换不再占用自建路线批次；两条路线脚本仓库、提交和验收分别维护。

### DatasetFrame 专项说明

- 当前状态（2026-09-21）：DatasetFrame 已实现从结果 `dataset_index.csv` 的解析、校验、分批 upsert 和幂等重放；处理机已部署迁移 `20260916_02`。流水线 `9dcbf06ef763438f873a6cd173d5fac2` 已在 Phase3 后真实导入 747 条，生产绑定流水线 `737d789c9cd340b0a9e7cf7ded295d7e` 的 34721 条记录已完成路径和 clip 命名对账；百万帧容量/索引基线已完成。剩余工作是完整组合检索、页面和发布版本语义，不再是导入能力。
- 开发边界：先针对自建 Phase1 结果 CSV；需要记录 CSV 版本、行号、clip/frame 唯一键、源文件和导入批次，错误行不得阻断已成功行但必须可追踪。
- 验收重点：空 CSV、重复行、字段缺失、非法时间戳、路径不存在、重复请求和部分失败重试；导入完成后页面能显示帧数量和导入批次。

### 结果质量门禁专项说明（2026-09-21 校准）

- 已新增 `scripts/result_validator.py`，统一生成 `result-manifest-v1`：记录相对路径、文件大小、单文件 SHA-256、总大小、文件数和 manifest hash。
- Phase0 宿主机代理在回写 `PHASE0_DONE` 前检查输出非空、无零字节文件和至少一个非空 MP4。
- A100 Phase1 代理在登记产物和执行帧索引导入前检查输出目录、非空 `dataset_index.csv`、非空 JPG/NPY；存在 `index_done.json` 时必须为 done。
- 初始提交 `b90d3a2` 的专项验证为 `pytest` 26 项、compileall、脚本语法和 `git diff --check`；后续真实 `PUBLISHED` 任务已完成全量 manifest/hash 对账。当前未完成的是根据输入配置动态判断相机集合/数量、NPY shape、轨迹及文本覆盖率等业务语义门禁；页面当前的“质量报告”主要汇总质量事件和 manifest，不等于完整业务指标报告。

## 自建路线 P0

### Backend、数据模型和接口

- [x] 基础 Bag/Source/PipelineRun、StepRun、PipelineEvent、Artifact、SourceCopy API；支持任务查询和回写。SourceCopy 已增加可空 `pipeline_run_id`，处理副本按 source/run/type/path 幂等登记；迁移 `20260917_01` 已在处理机升至 head，并回填可确定的历史运行归属。证据：`app/api/`、`app/services/`、`app/models.py`，代码提交 `525d67f`，文档提交 `7ac7608`、`fb343c9`。
- [x] 基础 Alembic 迁移可执行。证据：`alembic/versions/`、Compose 启动流程。
- [x] 严格状态机、非法转换 `409`、幂等键语义、租约过期保护：显式状态转换表、数据库锁定 claim、任务 lease token/heartbeat/过期失败补偿、`Idempotency-Key` 同参重放/异参 `409`、StepRun attempt 唯一约束和 retry attempt 递增均已落地。证据：`app/domain/transitions.py`、`app/domain/security.py`、`app/services/pipeline_service.py`、迁移 `20260915_02_pipeline_consistency.py`、`tests/test_pipeline_api.py`；多单位 ResourcePool 仍为后续项。
- [~] ResourcePool/ResourceRequest/ResourceLease：已接入 Orchestrator 资源申请、容量互斥、slot 分配、代理 heartbeat 续租及完成/失败释放；2026-09-20 根据真实任务 `737d789c9cd340b0a9e7cf7ded295d7e` 暴露的问题，将资源幂等键扩展为 `<run_id>:<attempt>:<purpose>:<resource_key>`，避免 Phase0 与 A100 共用 `A100_COMPUTE_IO` 时重放已释放 token。提交 `b5d703a` 已随处理机 revision `71f5b35` 部署；本地模拟流水线验证同一 attempt 的 Phase0/A100 请求独立且均释放。仍待全局 PENDING 优先级队列、RESOURCE_WAIT 状态和多进程抢占对账。
- [x] DatasetFrame 已接入结果 `dataset_index.csv` 导入：CSV schema/安全相对路径校验、每批最多 10000 行、错误行报告、`(pipeline_run_id, clip_id, frame_id)` 唯一 upsert、导入批次/源 CSV/行号记录和重复请求幂等。证据：`app/frame_importer.py`、`app/api/frames.py`、`app/services/frame_service.py`、`scripts/a100_host_proxy.py`、迁移 `20260916_02`；流水线 `9dcbf06ef763438f873a6cd173d5fac2` 真实导入 747 条。

### Scanner 和指纹

- [x] `rosbag-fast-v1` 指纹工具及 JSON CLI 已实现并用于源数据关联。证据：`scripts/compute_source_fingerprint.py`。
- [x] Scanner 通过 Backend API 注册 source/pipeline，支持稳定窗口、状态文件、扫描生命周期记录和 `/jobs` 页面“立即扫描”。默认根为 `/public/raw`，处理机当前由环境覆盖为 `/public/vla_dataset_builder_backup/raw_rosbags`。提交 `d832832` 真实验收：立即扫描 3 个目录、发现并更新 2 个 Bag、失败 0；已有 Bag 复用既有流水线，不自动重试历史 FAILED。
- [x] Scanner 输入门禁：metadata 声明 DB3 完整性、`.done` 不绕过完整性、多轮稳定、变化后 `INPUT_UNSTABLE/FINGERPRINT_CONFLICT`、状态原子写入均有测试；incoming→ready 使用目录级 `os.replace`，移动意图/移动后未登记可恢复，ready 不再扫描。处理机实测两个 Bag 从 `raw_rosbags` 原子移入 `ready_rosbags`，重启后 ScanJob 为 `directories=1,bags=0,failed=0`。

### Phase0 和 Orchestrator

- [x] Phase0 宿主机代理、独立工作目录、NAS 到平台机复制、脚本执行和七步状态回写已完成真实验证。证据：`scripts/phase0_host_proxy.py`、处理机 `rosbag-phase0-proxy.service`。
- [~] 已接入统一结果 validator：输出非空、零字节文件、MP4、Phase1 CSV/JPG/NPY、index_done 和 SHA-256 manifest；Phase0 复制前按“源大小 + 10 GiB 最低保留 + 1 GiB 余量”检查工作盘，并拒绝危险路径组件和输入符号链接。真实 Bag 的全量 manifest/hash 已复验；仍待按输入配置动态校验相机集合、NPY shape、轨迹和文本覆盖率等业务指标。证据：`scripts/result_validator.py`、`scripts/phase0_host_proxy.py`、`scripts/a100_host_proxy.py`、`tests/test_phase0_safety.py`。
- [~] Orchestrator 已通过 Backend 原子 claim、任务租约 heartbeat 执行队列，代理重启恢复和过期任务/资源收敛已部署；资源容量 1 已有线程并发自动化断言及处理机 MySQL 真实 `200/409` 互斥验证。完整 Worker 池、多单位 slot、跨 Backend 多进程竞争和公平等待队列仍待补齐。
- [~] 自动重试机制已部署（平台提交 `ae91d4d`、`2a28e90`，生产发布 `116b5ac`）：`PipelineRun` 持久化计划/原因/队列/次数，Orchestrator 对账到期后创建新 attempt；默认 60/120 秒退避、最多两次，仅覆盖已确认 `exit -9/137` 和可证明任务未启动的派发失败。本地新提交 `32ee918`、`0b384d1`、`f23ced4` 将人工普通重试改为自动按失败步骤与有效产物选择 Phase0/Phase1/Phase3 断点；强制重试可手选三个起点，从所选阶段重建并失效对应下游产物与帧索引，NAS 旧 final 不覆盖，新 attempt 使用独立版本目录。Phase1 续跑已补齐本地 Phase0 副本被清理后复用已登记且实际存在的 A100 origin；缺少本地和远端输入时明确拒绝，且在强制重试清理下游前完成检查。NVIDIA 暂仅提供普通重试。租约过期、派发超时/连接重置先对账，输入、质量、冲突、磁盘与配置错误保持 `FAILED`；本地质量门禁 `244 passed, 1 warning`、mock 到 `PUBLISHED` 和三档宽度 Chrome 交互通过，真实 A100 三起点和生产强制重试仍待单独验收与授权。
- [~] 失败恢复与重启对账：过期 `PHASE0_RUNNING/RUNNING` 与资源租约收敛已有真实证据；Phase0/A100 代理运行文件/PID 恢复、Phase1 SSH 未知启动结果对账和自动重试迁移已部署，但当前不能据此宣称处理机在途故障已复验。在途真实数据任务中断、宿主机异常重启和 SSH 临界断线仍待明确授权后验证。
- [x] 处理机本地副本生命周期清理：Phase0 成功回写 Step/Artifact/`PHASE0_DONE` 后删除当前运行 `input/`；A100 origin 经 rsync dry-run 校验且 SourceCopy/Artifact 登记成功后删除当前运行 `output/`；失败、冲突和远端不确定路径保留现场，NAS ready 不在清理范围。默认开关 `PHASE0_CLEANUP_ENABLED=1`，路径越界返回 `CLEANUP_REFUSED`，`cleanup.json` 追加记录 action。流水线 `18f49b2025f1419eb71178f5c396fcfa` 已真实验证成功/冲突/重试三种时序并最终 `PUBLISHED`；SourceCopy/Artifact 已通过迁移 `20260920_01` 增加 `deleted_at` 等生命周期字段，代理清理成功后会回写。
- [~] 自建 Phase1 三个脚本已登记并可执行；SSH 启动结果不确定已按远端 PID/结果文件对账，完整 Phase1 成功结果可以复用。三个脚本之间尚未持久化独立恢复检查点，脚本中途失败后仍以新 attempt 整体重入；统一 wrapper 和逐脚本断点恢复仍需补齐。
- [x] 自建 Phase3 当前代码已按 `PHASE3_NAV -> PHASE3_COT -> PHASE3_PLOT -> PHASE3_DESC` 接入独立 StepRun并执行质量校验；测试环境流水线 `6912262c698b4a85aaded5ba859fff41` 四步均为 `DONE`，747 帧中 `VALID=567`、`INVALID_COC=180`，NAS 测试 final 与 A100 manifest 一致。代码已随 F-013 发布到处理机；历史真实流水线的 `PHASE3_COT=SKIPPED` 保持不变，尚未提交新生产 Bag 验收。
- [~] **Bag 全量记录与 A100 数据清理**：已有 T-02～T-08 本地实现。2026-09-30 专项 REVIEW-T09 收尾：T-09A～F 全完成；T-09G 测试环境验收通过（`9e61673`）。独立生产复审 `a3b626c` NO-GO 后，C1～C5 固定收口清单全部 `[x]`（专项 `TODO.md` 页首为唯一剩余清单）：PROD-R1/R2 写锁缺陷已修（`2ecd407`，`review_a3b626c_repro.py` 2/2 通过、实测 HEAD 复核）；PROD-R3 MySQL 业务假通过已修（独占容器 10 passed）；PROD-R4 常驻测试装配收敛（worker 重启恢复 SUCCEEDED）；C5 OCR 缺口（`2ecd407` 核心 7 文件从未有效审查）2026-09-30 拆批补审闭合（批 A 2 low 已修 `d8ca1cf` + 复审 0 findings，批 B 无有效缺陷）。**C6 生产发布 2026-09-30 用户授权完成**：F-024/F-025/F-026/F-027 released `b7eb50b`，处理机部署 `61f9bab`（worker 容器+删除开关打开，A100 executor/authorize/锁根装配），本地收敛 `1b3025f` EXIT=0。**生产删除全链路验收以生成夹具 exit 0 通过**（驱动 `scripts/run_bag_cleanup_production_acceptance.py` run10：A 真删/B 部分失败+retry 续删/D writer 互斥零删除+释放收敛；A100 `bc_prod_*` 零残留、MySQL 自清、审计 3×SUCCEEDED）。**未收口**：回滚演练未做；既有生产业务数据的真实删除需单独授权。范围仍为 self_built 全部专属 DB 记录与 A100 归属数据；NAS/处理机本地/共享对象保留。详见专项 REVIEW-T09.md 与 evidence-20260930/。

### 结果和发布

- [~] A100 Phase1 产物路径和基础 Artifact/SourceCopy 登记已打通。
- [~] A100 结果校验：已实现 done、CSV、JPG/NPY 非空检查和 manifest/checksum；六/七路相机动态校验、NPY shape、轨迹/导航/描述覆盖率仍未实现。
- [x] 从 Phase3 结果 CSV 批量、幂等导入帧级索引和质量状态：真实任务 `FRAME_INDEX_IMPORT=DONE`，747 条 navigation/description 非空，已登记 `DATASET_FRAME_INDEX` Artifact。
- [~] A100 -> NAS `.incoming`、清单校验、原子发布和 `NAS_FINAL` 血缘闭环已真实完成：final 6308 个文件，`.incoming` 无遗留，三个结果 Artifact hash 一致；`parent_artifact_id` 已进入模型并贯穿已登记产物，剩余缺口是中断续传专项演练、发布后只读保护和页面完整展示父子链。

### 页面和部署

- [x] 流水线列表、详情、时间线、阶段汇总和脚本级步骤状态已实现并部署验证。证据：`app/templates/`、提交 `35aaf0c`。
- [x] 处理机一键同步与启动入口已提供：开发机执行 `rosbag-catalog/scripts/deploy_processing_machine.sh`，自动完成本地验证、排除敏感/数据目录的代码同步、应用镜像重建、服务启动和 Backend/Web 健康检查；支持 `--dry-run` 和目标环境变量覆盖。
- [x] A100 两套处理脚本已改为仓库拉取：测试使用 `update_a100_script_repositories.sh --environment test --check|--apply`，生产只读使用 `--environment production --check`，生产写入还必须加 `--apply --production`；命令经临时 SSH 反向隧道和 agent forwarding 对两个 GitLab 仓库执行 `git pull --ff-only`，并拒绝活动任务、脏工作区、错误 remote、非快进更新和跨环境路径。
- [x] 失败步骤重试、取消、409/422 冲突反馈、日志摘要分页、Manifest/质量报告、heartbeat 新鲜度和 Phase0/A100 重试起点已在本地详情页补齐；处理机真实失败任务冒烟仍需单独授权。NVIDIA 详情能力由独立 TODO 追踪。
- [~] Compose/systemd 已运行 frontend、backend、mysql、scanner、orchestrator；Phase0 通过宿主机代理执行。基础任务/资源租约已保护，资源池容量、slot 和并发配置仍需完善。

## 页面重构专项 TODO（对应 PRD 16、19.10）

### P0：任务可观察和可操作

- [x] **UI-P0-01 流水线列表基础信息**：列表展示 pipeline ID、数据类型、Bag 名称、队列、状态和更新时间；Source ID 因与 Bag 跳转入口重复不再展示，按界面要求同时移除“当前步骤”和独立“错误”列。流水线 ID 为中性黑色链接，状态颜色只绑定状态列，悬停 `FAILED` 显示错误详情。详细步骤、时间线和错误上下文继续由详情页承载。证据：提交 `5dfcf1e`、`tests/test_web.py` 和处理机真实页面。
- [x] **UI-P0-01B Bag 列表入口**：`/bags` 默认展示最近 Bag，不需要先提交筛选；筛选条件与列表在同一页面组合使用，并可按“自建数据集/NVIDIA 数据集”切换。证据：`app/web/bags.py` 的 `bag_list`、`app/templates/bags.html`；处理机实测 `/bags`、`?dataset_type=self_built`、`?dataset_type=nvidia_physicalai` 均返回正确页面。
- [x] **UI-P0-02 状态筛选和排序**：流水线按完整状态集合筛选，排序以黑色居中表头和上下双三角集成到流水线 ID、数据类型、Bag、队列、状态和更新时间；每页 25 条，分页为左侧摘要、中间页码、右侧跳转并保持筛选/排序参数。处理机 83 条真实记录共 4 页，已实测表头排序和跳页；自动化测试覆盖非法参数回退和超范围页码钳制。
- [x] **UI-P0-03 详情页阶段与脚本步骤**：按 Phase 分组展示每个脚本、attempt、状态、开始/结束时间、退出码、执行主机和错误摘要；现状：`pipeline_detail.html` 已展示阶段汇总和脚本级 StepRun，步骤执行表已按 `step_page` 每页 20 条分页（越界钳制、非法回退第 1 页），阶段总览基于全量步骤，与日志分页参数互不重置。证据：提交 `35aaf0c`、步骤分页提交 `db7c88e`（已推送 `github/main`）、`HANDOFF.md` 2026-09-24 条目和 `tests/test_web.py`。
- [x] **UI-P0-04 事件时间线**：详情页展示状态事件、领取、重试、取消、产物登记和错误事件，按 20 条分页，统一使用配置时区并提供空态；运行可观察性区域展示 heartbeat 新鲜度和当前 attempt。
- [~] **UI-P0-05 输入输出与血缘**：详情页已展示 NAS/平台机/A100 路径、Artifact、SourceCopy、指纹和 source→副本→产物血缘列表；提交 `525d67f` 修复同一 Source 多次运行路径混显。`parent_artifact_id`、文件统计和删除时间已进入模型，剩余工作是页面按父子关系串联完整产物链、展示更完整 manifest，并把 `deleted_at` 明确呈现为历史记录而非现存路径。
- [x] **UI-P0-06 操作按钮和并发反馈**：列表和详情页已有排队取消、失败重试、Bag/source 跳转，运行中不提供删除；页面对 Backend 的 `409/404/422` 返回可行动中文反馈并回到当前详情页。
- [x] **UI-P0-07 错误与日志摘要**：流水线列表不再占用独立错误列，`FAILED` 状态支持键盘聚焦和悬停查看错误详情；详情页展示错误分类、事件日志分页、失败步骤和质量摘要。
- [~] **UI-P0-08 Bag 详情联动**：Bag 详情已增加数据路线、source ID、指纹、源状态和最近 pipeline 跳转；流水线详情已显示平台机/A100/Phase3/NAS final，Bag 详情中的完整副本与步骤血缘仍需补齐。
- [x] **UI-P0-09 路线和禁用能力提示**：区分自建与 NVIDIA pipeline；列表和详情已显示路线标签，处理机实测通过。

### P1：效率和运维体验

- [~] **UI-P1-01 刷新控制**：按最新要求取消流水线列表 30 秒自动刷新，改为右上角手动刷新并保留当前筛选、排序和页码；详情页运行态 10 秒刷新仍保留，表单提交保护和刷新失败提示仍待补齐。
- [~] **UI-P1-02 查询筛选增强**：分页、页码跳转、保持状态/排序条件和空结果说明已完成；按 source、Bag、日期、数据类型、提交来源和错误类型筛选仍待实现。
- [ ] **UI-P1-03 队列与执行资源信息**：展示队列位置、预计等待时间、当前 Worker、执行主机、slot/units、资源等待原因和 heartbeat 新鲜度。
- [~] **UI-P1-04 日志查看**：P0 已提供事件日志摘要分页；按步骤下载原始日志、日志缺失/权限错误专用状态仍待补齐。
- [~] **UI-P1-05 质量报告**：P0 已展示质量事件和 Manifest 摘要；完整业务指标、quarantine 原因和发布门禁仍归 P0-1 质量规则专项。
- [ ] **UI-P1-06 血缘视图**：以简洁列表或 Mermaid/关系图展示 source -> copy -> step -> artifact -> final，支持点击跳转；不实现复杂拖拽 DAG 编辑器。
- [~] **UI-P1-07 失败恢复体验**：详情页已让用户选择 Phase0/A100/NVIDIA 重试起点，并显示自动重试计划、原因、次数和目标队列；历史 attempt 对比、代理恢复中/未知启动结果对账状态仍未形成专门视图。
- [x] **UI-P1-08 响应式和可访问性**：桌面固定左侧导航和表头，1100px 及以下切换为字段键值布局，手机导航三列两行；状态颜色始终配合状态文字，排序链接、分页和 FAILED 错误提示可键盘操作。Playwright 已验证 1440x900、1024x768、390x844 三档无横向溢出，处理机真实页面复验通过。

### 页面改造文件和验证入口

- [x] 主要改造文件：`app/templates/base.html`、`bags.html`、`pipelines.html`、`pipeline_detail.html`、`detail.html`、`app/static/app.css`；`/bags` 已重构为语义化表格，默认快速搜索、高级筛选分组、路线筛选、场景级联复选框和 Topic 可滚动面板已落地。
- [~] 页面与 API 已纳入当前 `228 passed, 1 warning` 本地质量门禁，覆盖默认列表、表头排序、分页/跳页、FAILED tooltip、重试起点、heartbeat、自动重试信息、静态资源指纹、当前 run SourceCopy 隔离及历史副本折叠；处理机已部署自动重试与最新详情页版本并通过健康和 `/changelog` 冒烟，各状态组合和运行态刷新仍需用真实任务专项验收。
- [~] 处理机页面验收：`http://192.168.2.134:8180` 健康接口、Bag 列表/路线筛选、流水线列表和详情已实测通过；列表页按要求仅手动刷新。详情页的真实运行态定时刷新、终态停止刷新，以及完整 manifest 可追溯仍需用成功任务专项复核。
- [x] 2026-09-15 检索筛选交互实测：处理机最新版 `/bags` 中高级筛选、场景面板和 Topic 面板均在正常页面流中展开并推动 Bag 表格下移；场景分类黑色、全局全选唯一，场景和 Topic 选择后触发框显示具体已选项。部署由 `scripts/deploy_processing_machine.sh` 完成，已自动处理旧版 Compose `ContainerConfig` 并通过 Backend/Web 健康检查。

## NVIDIA 路线边界（独立 TODO）

> NVIDIA 后续开发已拆分到独立追踪文档 `/home/wang/work/doc/todo/vla_nvidia_dataset_pipeline_v1_todo.md`。本节只保留历史基线，不再在自建路线 TODO 中新增 NVIDIA 任务或更新执行顺序。

- NVIDIA 仅保留历史验证事实；当前任务、开关语义、下载、批量、恢复和正式目录切换全部记录在 `/home/wang/work/doc/todo/vla_nvidia_dataset_pipeline_v1_todo.md`，本文件不再维护其状态。

## 可靠性和测试

- [~] 平台本地质量门禁当前为 `129 passed, 1 warning`，已覆盖状态机、幂等、任务/资源租约、SourceCopy/Artifact 生命周期、代理恢复、自动重试、结果校验、帧导入、数据库运维保护和主要页面；跨进程并发及完整故障注入仍未形成完整矩阵。
- [ ] fake NAS/SSH 临时环境、3～5 用户同时复制/登记、单台 A100 多 Worker 和并发预算压测，需形成可重复脚本并记录吞吐、失败率、磁盘与 VLM 指标。
- [~] 路径冲突、磁盘前置检查、代理隔离状态重启、遗留 `PHASE0_RUNNING`、资源租约过期及处理机 MySQL 真实备份恢复/容器重启已验证；在途任务中断、宿主机异常重启、Backend 暂不可用和 SSH 启动临界点仍未演练。

## 历史开发顺序（已废弃）

以下顺序对应早期状态机尚未完成时的阶段，现已由“当前状态复盘与执行优先级”替代，仅用于理解历史变更，不得据此新建任务。

## 更新规则

- 每项完成必须附代码路径、提交或真实命令结果；只有阅读代码不能标记 `[x]`。
- 跨仓库任务分别记录自建脚本、NVIDIA 脚本和 `rosbag-catalog` 的修改及提交。
- 发现实现与 PRD/TODO 不一致时，先更新本文件的事实基线，再继续开发。
- 每次更新同时维护 `rosbag-catalog/HANDOFF.md`，记录部署环境、运行状态、验证证据和下一步入口。

## 工程化工作流

跨项目开发代理接入另见 `/home/wang/work/doc/todo/rosbag_devflow_todo.md`；它不改变自建数据流水线和生产部署状态。

- [x] **OPS-SKILL-01 处理机部署 Skill**：已创建 `.agents/skills/processing-machine-deployment/SKILL.md`，沉淀代码同步、Compose 构建/重启、健康检查、页面实测和 `ContainerConfig`/同步不完整/Backend unhealthy 等常见故障处理；已通过 Skill 规范校验。
- [x] **OPS-SKILL-02 MySQL 备份恢复 Skill**：已创建 `.agents/skills/mysql-backup-recovery/SKILL.md`，固化双副本备份、隔离恢复、迁移回滚、容量基线、重启持久性和停止条件；真实处理机流程已验证。
- [x] **OPS-SKILL-03 功能更新日志 Skill**：提交 `93b735a` 创建 `.agents/skills/feature-changelog/SKILL.md`，实现 `pending -> approved -> released` 审批流、部署遗漏门禁和 `/changelog` 时间线；首批已批准日志已随 2026-09-20 系统更新进入生产。提交 `922c6b3` 进一步为每个功能分配稳定 `F-001` 编号、正文分点编号，并支持按编号批准、暂存和随实际发布启用；六条现有候选保持 pending，本地验证完成，编号增强尚未部署处理机。
