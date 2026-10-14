<!-- spray-post-v04-plan-20261014 -->
> **后续规划（2026-10-14T13:53:01+08:00）**：[水雾生产收尾](../../../rosbag-catalog-spray-pipeline/SPRAY-POST-V04.md)已按用户要求纳入[TODO §11](../../TODO.md#11-v04收尾后的水雾生产收尾2026-10-14)：自动绑定/幂等E、异常输入拒绝恢复F、原12S-D资料D1与独立实测D2。全部在当前v0.4收尾后由协调者核条件派单；当前仍按TASK-16执行，不抢占、不自动启用后续阶段。仅规划DESIGN_READY，未实现/未测/未部署。

> **当前执行决定（2026-10-14T11:25:19+08:00）：用户恢复 v0.4 最小界面闭环，并要求原 OCR 未修项进入任务。** 唯一入口 [V04-UI-RESUME-20261014](../../inbox/control/V04-UI-RESUME-20261014.md)；TASK-16C-A/B/C 三路开发、16D准备/固定快照验收、16R审查遗留并行。下面2026-10-13 UI暂停及旧“不恢复UI”仅为历史。水雾上线接受保留；大包优化仍等ros2_slice交付，其他DEFERRED不恢复。状态唯一见TODO §8。

# Bag 场景处理服务技术设计

版本：v0.5，2026-10-13。原 v0.3.2 段落保留历史设计背景；与 §7.3 冲突时以 §7.3 和 [PRD](../../PRD.md) v0.4 为准。已有代码和部署事实以仓库当前实现及部署快照为准，不将本轮目标写成已上线能力。

> **当前设计优先级**：沿用已上线水雾根/执行契约，恢复§7.3.3界面最小闭环；三owner、冻结seed与历史OCR处置按顶部当前入口。

## 1. 当前结构与复用边界

2026-10-13源码基线main=6fb42c4：16A已接受、16B分支代理尚待门禁、spray正式适配器未注册。下方10-12调查为历史来源，本轮不重做16A、不将待发布当已部署。

原设计调查基线为 2026-10-08 catalog d00c895。2026-10-12 本轮复核本地 main 为 `30e55a3`；现有未跟踪文件已保留，不属于本轮范围。该基线只用于定位代码，不代表生产部署版本，实施前重新冻结实际 base。

- Backend 是唯一业务写库边界。Scanner、Orchestrator、宿主机执行代理只通过 Backend API 写状态和结果，不新增数据库账号。
- source_service 已按绑定用途决定是否创建 PHASE0_QUEUE；但入口未匹配/开关关闭会按旧路径创建自建运行。v0.4 必须把场景根识别与场景自动调度开关分开，任何场景根异常都不得回退旧自建分支。
- BagRecord 角色/用途、场景 PipelineRun/StepRun、派生关系、分析版本、租约及源 fence 已实现，优先复用，不重新建一套场景索引或状态机。
- 当前 Scene 仅有名称/分类，是标签词表。能力注册与标签管理是两件事：加标签不会自动产生识别能力。
- 全局 fast_fingerprint 查找可能更新 Bag 路径；新子包不能调用这一逻辑后归并到父包。SourceCopy 表达内容不变的副本，不能承载切片血缘。
- ros2_slice 的 analysis_perform、segment_slope、切包 writer 通过适配器复用。现有函数会在抽帧失败时返回空列表，适配时必须区分失败与成功无命中，不能直接将 [] 视为 NO_MATCH。
- 当前最终 CSV 是 slice_message.csv；新服务不调用中间 CSV 回填/追加入口。现有源码保留作算法对照，首期在 catalog 集成模块适配，不改其硬编码入口或自建正式脚本根。
- MySQL 是统一结果事实来源；文件在 NAS，逐帧证据及日志作为 Artifact 引用。数据库中不存 Bag 二进制，也不混入 VLA DatasetFrame。

## 2. 场景能力注册与适配器（沿用已接受 P0 契约）

### 2.1 注册契约

维护者通过受版本控制的配置和已安装适配器维护能力注册表，Backend 校验并登记不可变版本；首期不开放注册任意 Python 路径、代码或模型地址的用户写接口。

每个能力版本至少包含：

| 项目 | 含义 |
|---|---|
| scene_code / capability_version | 稳定代码与不可变能力版本；显示名称可调整，代码不随名称改变。 |
| display_name / enabled | 名称、可选状态及不可用原因；源码存在不等于平台注册可用。 |
| adapter_key / adapter_revision | 服务端允许的适配器键与代码修订，不向用户开放任意执行路径。 |
| required_inputs / preprocessing_key | 所需 topic、消息类型及相机/点云预处理配置。 |
| parameter_schema / defaults | 类型、范围、必需项和默认值；拒绝未知参数。 |
| model_profile / rules_revision | 服务端模型配置、提示词及分段规则版本；凭据只保存引用。 |
| output_labels / publish_labels | 输出标签到场景标签词表的映射，及哪些标签可发布。 |

P0 仅启用 slope。slope 的输出包含 slope/flat，默认仅 slope 可发布；以现有参数 segment_len=15、overlap=3、min_effective=5 作为工程默认值，单位为秒，参数范围由该适配器 schema 约束。这不构成质量阈值已获验证的声明。

v0.5先新增spray；后续 narrow、vehicle、cart 逐类注册；缺材料或未实现者不作为可用能力返回。新增场景需要适配器实现或复用、注册版本与契约测试，可能需要发布代码，但不得修改核心调度或新增专用客户端 API 分支。

### 2.2 统一适配器协议

输入为已验证源 Bag、源代次/指纹、冻结能力和参数、受控工作目录及取消信号；输出为适用性、识别结果、区间集合和证据引用。预处理、分析及分段接口由注册表分派，通用 writer/校验/发布层消费统一结果，不按场景名称硬编码分支。

区间至少含 label、start_ns、end_ns、duration_ns、publish_target 和边界映射依据。任务状态与分析结果分开；适配器不自行登记 Bag、不直连 MySQL、不直接覆盖 NAS 发布文件。

相同源指纹、topic、抽帧配置可共享相机抽帧产物；模型结果缓存额外包含模型修订、提示词、规则、参数和输入摘要。点云能力可使用独立预处理，无需强行统一算法。每个 run/attempt 私有目录隔离可写文件，共享缓存只读复用；v0.4不为带宽优化新建缓存平台。

## 3. 接收配置、每包提交与自动调度（已有契约，v0.4 根隔离见 §7.3）

### 3.1 配置来源和覆盖

IngestProfile 描述接收入口 ID/版本、受控 incoming 前缀、默认用途、默认场景/参数、车辆解析与发布策略。目录前缀不可重叠或越界，发布根不能被当作原始接收根。维护者部署配置，Backend 提供查询；生产物理路径由环境配置给出，不在需求中猜写。

IngestSubmission 在上传前关联 profile_id、入口下目标 relative_path、用户选择、幂等键和有效配置快照。配置只在数据库登记，不能向不可变 Bag 目录塞入可变 sidecar。

| 输入情况 | 解析规则 |
|---|---|
| 未提交每包配置 | 使用匹配入口的有效默认值，首次通过接收校验时建立系统提交记录。 |
| 显式 purposes | 替换整个用途集合，只允许 scene_slice/self_built；不与默认用途并集。 |
| 未提供 scenes 且含 scene_slice | 使用默认场景集合；仍需校验能力可用。 |
| 显式 scenes 且含 scene_slice | 替换整个场景集合；去除重复代码并拒绝版本冲突，不补回其他默认场景。 |
| scene_slice 的 scenes 为空 | 拒绝无识别目标的配置，不静默全场景运行。 |
| 仅 self_built | 不创建场景任务；提交非空 scenes/场景参数视为配置错误。 |
| 单场景 parameters | 在所选能力版本默认参数上覆盖允许字段，类型/范围非法或未知字段明确拒绝。 |
| 未指定能力版本 | 在配置接受时固定当前启用版本，返回有效版本；之后不随“当前版本”指针漂移。 |
| 新入口缺有效默认且无每包配置 | 允许登记待处理并报告 CONFIG_REQUIRED，不自动创建处理任务。 |

v0.4 场景入口默认 purposes=[scene_slice]、scenes=[slope]，必须绑定专用物理接收根；旧入口保持自建流程。入口匹配规则及独立目录契约见 §7.3.1。

### 3.2 绑定、冻结与竞争

1. 配置 API 接受请求时验证入口、目标路径、能力和参数，保存有效快照并返回提交 ID。相同幂等键及相同请求返回同一提交；不同请求返回冲突。
2. 同一环境、入口、目标相对路径仅有一个活动待接收提交。不同请求不能抢占该路径；上传工具必须先完成配置登记再传输。后到配置不能偷偷改已由目录默认绑定的运行。
3. PENDING_INPUT 提交可经版本校验修改配置，Backend 对该记录加锁；Scanner 的绑定使用同一锁。绑定后修改拒绝，需显式新分析。
4. Scanner 在 incoming 阶段捕获提交/入口身份、原路径及配置 hash，并经过稳定性、完整性和指纹检查。原子移到 ready 后携同一身份登记，重启恢复不能重新按 ready 路径推断用途。
5. 原始 Bag 登记、提交 BOUND、源代次与调度事件同事务提交，配置在此冻结。稳定性校验失败不执行；移包与登记中断按现有 marker/fence 恢复并核对配置身份。
6. 后台消费持久调度事件，为所选用途分别创建运行；提交进入 SCHEDULED。派发失败可重试，不能留下“Bag 已登记但任务丢失”。
7. profile/能力更新不影响冻结快照，也不自动补跑历史。需修改已绑定包的场景或参数时，显式创建新分析版本。

自动调度唯一身份包含源 ID、代次、用途、配置 hash；初次注册必须防重复，显式重新分析以新分析版本区分。PipelineRun 的活动身份和现有“找此源任意运行”逻辑需按运行类型隔离，允许同一父包的场景和自建任务并存，但不重复启动相同用途/版本。两条流程均只读原始输入，使用不同输出目录。

## 4. 数据契约与 CSV 对应（沿用已接受 P0 契约）

### 4.1 数据分层

| 对象 | 目标字段与不变量 |
|---|---|
| BagRecord | bag_role=ORIGINAL/SCENE_SLICE/NOT_APPLICABLE；处理用途关联；切片 availability=PENDING/AVAILABLE/WITHDRAWN，与源状态、运行状态和当前版本分开。 |
| IngestProfile / IngestSubmission | 配置版本、路径绑定、来源、有效快照/hash、提交状态、row_version、源身份。 |
| SceneCapability | 能力版本及配置摘要；运行保存快照，版本不可原地覆盖。 |
| SceneAnalysisVersion | 父包+scene_code+分析版本，run_id、能力版本/config_hash、结果、预期与登记计数；父包+场景只有一个当前版本指针。 |
| SceneSegment | 属于分析版本的区间和标签、是否目标切片、映射/证据引用；包含 flat 等非发布分析结果。 |
| BagDerivation | child_bag_uid 唯一，parent_bag_uid、run_id、segment_id、slice_key、scene_code、start_ns/end_ns、artifact_id、config_hash；run_id+slice_key 唯一，父子 FK 均 RESTRICT。 |
| 标签证据 | bag_uid、scene_id、来源 MODEL/MANUAL/LEGACY_MANUAL、生成版本、原始判定引用和修订者/原因；bag_scene 是有效标签投影。 |
| Artifact / StepRun / 事件 | 复用任务证据及执行记录，重明细保存引用，不把整个逐帧列表追加到 BagRecord。 |

父包必须 ORIGINAL，首期禁止自引用、环和多父拼接。当前性由分析版本指针求得，不为换版批量改写所有历史 Bag；历史切片保留文件及原始标签。AVAILABLE 表示校验及登记通过，默认查询还须匹配当前版本。PENDING 不进入可用检索，下架单独审计。

### 4.2 替换 CSV 的业务对应

| 旧字段 | 新服务记录 |
|---|---|
| NO | 平台生成 Bag/区间身份；历史序号仅可作证据，不是唯一键。 |
| scene | 能力代码、区间 label 及模型来源的有效标签，不能直接混为采集意图。 |
| location / vin / vehicle_id | 父包采集元数据与车辆归属，子包继承；缺失允许明确为空。 |
| path_pre（中间 CSV） | 父 Bag UID、源副本及冻结输入证据，不靠路径关联父子。 |
| start / end / duration | SceneSegment 和 BagDerivation 的纳秒区间，时长由区间计算。 |
| path_nas / file_name | 子 Bag 路径、BagFile/BagTopic 及对应 Artifact。 |

执行器直接回报结构化区间和 manifest，Backend 落库；CSV 不再承载处理状态、任务队列或最终检索事实。本期不做历史 CSV 全量导入或导出；历史 cord 等场景代码不得擅自映射到新能力。

数据库纳秒用 BIGINT，API 用十进制字符串，区间为原 writer 的闭区间 [start_ns,end_ns]，manifest 明确声明。内部真实时间必须来自可靠整数时间映射，不能把已损失精度的浮点秒乘 1e9 当成恢复精度。保留 header 时间、bag 存储时间及映射依据；实际时间映射不能验证时阻塞真实切片发布。

子 Bag 与 Artifact 引用同一文件。Artifact.source_id 保持输入父包身份，BagDerivation 指向子包，不能假定两者 source_id 相等。父子指纹可相同仍不归并；专用派生登记不能走原始包 upsert/自动用途触发。

## 5. 异步执行与结果状态（已有状态机，v0.4补正式代理）

已有 pipeline_type=SCENE_SLICE、独立队列和适配器分派，复用现有领取/重试/资源服务，不走Phase0→Phase1默认状态跳转。正式代理和环境接线补齐见§7.3.2。

实际运行状态为 SCENE_SLICE_QUEUE→SCENE_RUNNING→SCENE_DONE/SCENE_PARTIAL_FAILED/SCENE_FAILED；取消为SCENE_CANCELLING→CANCELLED，先确认子进程停写再释放租约。步骤为PRECHECK、EXTRACT及所选场景的INFER/SEGMENT/WRITE/VALIDATE/PUBLISH/REGISTER。Web请求只创建/查询任务，不同步执行抽帧、推理、切包或大规模文件校验。

场景结果：

| 结果 | 判断依据及发布行为 |
|---|---|
| SUCCESS | 有有效目标区间且所有预期子包完成校验登记，可以切换当前版本。 |
| NO_MATCH | 有效输入和可解析推理结果确认无目标，保存空目标 manifest，不创建空 Bag，可切换为空当前结果。 |
| NOT_APPLICABLE | 缺少所需 topic 等输入适用性不满足，解释原因；没有识别结论，不替换既有当前结果。 |
| FAILED | 模型不可用、解码失败、无有效帧、缺配置/参考图、非法模型输出或执行/发布失败；旧结果不替换。 |

无法解析的模型返回保存为 UNKNOWN 证据，有限重试后仍未解决则 FAILED，不作为阴性。各选中场景独立完成；全无失败为 DONE，部分失败为 PARTIAL_FAILED，全部适用场景失败为 FAILED；全不适用可 DONE，但统计中不得计作成功阴性。

P0 仅一个坡道能力，但通过测试适配器验证多能力分派及部分失败结构。后续相机能力共享满足相同配置的抽帧产物，spray 走点云适配器。

沿用各场景原有分段和合法重叠，不跨场景合并。超出源范围的区间裁剪并记录，空或无消息片段不发布。多 DB3、乱序及重复时间需测试，不能未经验证照搬 reader 超过 end 就停止的假设。跨 DB3 的读取顺序和边界映射必须纳入真实验证。

## 6. 发布、幂等与当前版本（沿用已接受P0契约）

1. run/attempt 工作目录保存输入指纹、源代次、冻结配置、区间、日志及完整场景 manifest；重试复用稳定 slice_key，显式重新分析创建新版本。
2. 在 staging 写出 Bag，关闭 writer 后验证可打开、非空、topic/消息数量、时间范围和文件摘要。文件校验不等同于语义准确。
3. 同文件系统原子发布到 `SCENE_SLICE_PUBLISH_ROOT/<vehicle_key>/<scene_code>/<parent_uid>_<slice_uid>/`。未知车辆用 unassigned；目标存在仅在完整 manifest 和摘要一致时复用，否则冲突失败，禁止覆盖。
4. 执行面携租约、源代次、验证证据和 manifest 回报。Backend 验证执行身份、运行类型/场景、配置及受控输出路径，分批事务登记 Artifact、Bag/文件/topic、区间关系和模型标签。唯一 run+slice_key 约束防重复，先标 PENDING。
5. complete-scene 校验完整预期集合及摘要，再在父包+场景锁下原子切换当前版本并使本次有效切片可用。批次缺失、非法区间或未验证文件不能完成版本。
6. 文件已发布、数据库未登记时，恢复器经 Backend 按 manifest 补登记；已登记但未 complete 的新版本也不默认可见。所有恢复先对账，不能因 HTTP 超时假设远端未启动或未发布。
7. 新分析失败不换当前；成功无命中切为空目标结果；不同场景独立换版。并发重新分析以提交时分配的分析版本排序，较旧运行晚完成不得倒退当前指针，保留为历史。
8. 人工下架不删除文件，普通重试不能重新上架；新分析的独立新结果按新版本管理，并保留原修订历史。

模型纯推理可有界重试，不假设服务提供任务查询 API；执行启动、发布及资源占用超时需核对进程/产物。默认单 run 模型并发 1、瞬时失败最多 3 次尝试为工程建议，复用 VLM_PERMITS、NAS_PUBLISH，IO 限流由实测调整。P0 默认不要求预览视频，后续视频是非阻断产物，可单独补跑。

## 7. 服务接口与客户端（已有接口及v0.4扩展目标）

### 7.1 P0 API 契约

| 接口 | 行为和最小输入输出 |
|---|---|
| GET /api/v1/scene-capabilities | 返回已注册能力代码/版本、显示名、enabled、输入依赖、参数 schema/defaults 和不可用原因；只有可用能力可被选择。 |
| GET /api/v1/ingest-profiles | 返回入口 ID/版本、intake_root_id、相对路径要求、默认用途/场景和可选策略，不返回凭据。 |
| POST /api/v1/ingest-submissions | 输入 profile_id、relative_path、可选 purposes/scenes、idempotency_key；返回 submission_id、状态、row_version、有效配置/hash。新建 201，幂等回放 200。 |
| PATCH /api/v1/ingest-submissions/{id} | 仅 PENDING_INPUT 可修改选择；携 row_version、原因与写入身份，重新校验并返回快照；绑定后 409。 |
| GET /api/v1/ingest-submissions/{id} | 返回绑定源、配置、接收/调度状态、运行 IDs 或待处理原因。 |
| POST /api/v1/scene-analysis-runs | 对已登记且通过稳定性/完整性校验的 ORIGINAL 显式首次处理/重新分析，输入 source_id、scenes、idempotency_key；返回 202、run_id、分析版本和冻结配置；自动调度复用同一应用服务。 |
| GET /api/v1/scene-analysis-runs/{id} | 返回所选场景、步骤/结果、失败原因、分析版本、区间与切片计数及证据引用，不固定返回五类。 |
| POST /api/v1/scene-analysis-runs/{id}/results | 执行面专用，携租约、源代次、scene_code、版本、manifest 摘要及稳定区间/slice_key；分批幂等登记，浏览器不得伪造已验证产物。 |
| POST /api/v1/scene-analysis-runs/{id}/complete-scene | 执行面专用，校验完整 manifest，保存 SUCCESS/NO_MATCH 或其他终态并按规则换版。 |
| GET /api/v1/bags | 新增统一服务检索，支持 view=slices/originals/all、data_kind、既有 dataset_type、车辆/场景/时间/topic/关键词、role、purpose、parent_bag_uid、include_history、cursor、limit；默认当前可用 slices，分类及组合规则见 §7.3.3。 |
| GET /api/v1/bags/{uid} | 扩展现有 manifest，返回角色/用途、可用性、当前性、标签来源、版本与受控文件获取信息。 |
| GET /api/v1/bags/{uid}/lineage | 返回父包或游标分页子包、区间、任务及版本，允许显式查询历史。 |

所有新增查询 limit 默认 50、上限 200；结果登记单批最多 100 个区间/切片，超限拒绝而不是截断。Bag 检索按 started_at、bag_uid 倒序，空时间排在最后；血缘子包沿用此排序，区间按 start_ns、区间 ID 升序。cursor 包含对应排序及筛选上下文，用于翻页，不提供快照隔离承诺。字段类型、时间单位、结果结构和错误类别写入 OpenAPI，不能仅给 URL 清单。

配置提交示例（全部值为目标示例）：

```json
{
  "profile_id": "scene-isolated",
  "relative_path": "vehicle-A/rosbag2-example",
  "purposes": ["scene_slice"],
  "scenes": [
    {
      "scene_code": "slope",
      "capability_version": "slope-v1",
      "parameters": {"segment_len": 15, "overlap": 3, "min_effective": 5}
    }
  ],
  "idempotency_key": "upload-example-001"
}
```

relative_path 只在该入口根内解析，拒绝绝对路径、路径穿越及越界。模型 endpoint、系统凭据和物理发布根不可由提交覆盖。场景/参数错误为 422（UNKNOWN_SCENE、SCENE_DISABLED、INVALID_PARAMETERS），资源不存在 404，幂等键/路径抢占/冻结配置冲突 409，尚未通过源校验返回 409 SOURCE_NOT_READY，写入身份按现有保护返回 401/403。后台失败在任务结果返回，不用一次 HTTP 200 宣称业务成功。

显式场景运行创建时增加该 Bag 的 scene_slice 用途关联，不覆盖既有自建用途，不重新调度自建任务；仍要求 ORIGINAL 和源校验通过，不能借显式 API 绕过输入门禁。

现有 sources/register 和手动/批量登记扩展提交/入口及原接收路径证据，Backend 核对数据库快照再调度，不能信任调用者自报用途或 role。现有无新字段客户端按既有入口兼容，切片只走专用派生登记。重型验证由异步步骤完成，Backend 请求只处理有界结果校验/事务。

### 7.2 页面与写接口

新增 PATCH /api/v1/bags/{uid}/scene-labels 和 POST /api/v1/bags/{uid}/withdraw，带 row_version、原因、幂等键与可验证操作者证据；保留原始模型结果。P0 保存标签来源，P1 提供纠错界面和相应接口，不新增匿名可用写入口。

`/bags?view=slices|originals|all` 已存在；v0.4 最小闭环修正其标签和语义，详见 §7.3.3。`slices` 仅当前版本 AVAILABLE；`originals` 覆盖三类原始数据；`all` 包含原始、切片、历史及其他条目。旧 dataset_type 书签无 view 时仍按兼容规则进入可见结果。人工写接口和预览沿原 TASK-07 后续接续，不替代本轮页面修正。

### 7.3 v0.4 场景专用接收、执行与界面补齐

#### 7.3.1 NAS 根与用途路由

用户已确认生产目标逻辑根为 `/public/rosbag_scene_processing/{incoming,ready,slices}`。测试环境使用 `/test/scene/{incoming,ready,slices}`。逻辑根与处理机物理挂载通过现有 NAS 路径映射解析；当前配置尚未支持这些场景独立根。NAS 共享、物理挂载、同文件系统、权限、容量及目录隔离在部署前核实。旧生产 `NAS_SCAN_ROOT=/public/vla_dataset_builder_backup/raw_rosbags`、`NAS_READY_ROOT=/public/vla_dataset_builder_backup/ready_rosbags`、`NAS_FINAL_ROOT=.../final` 及 NVIDIA 根继续服务原业务；本轮只迁入新的场景任务，不自动搬迁历史文件或改写原 UID。

本轮采用**现有 Scanner 单进程、两个固定根上下文**，不另建扫描服务。每轮分别扫描旧自建根和场景根，一根故障不阻断另一根；每根有独立 journal、统计/ScanJob 和 incoming→ready 映射。全局 Settings 不得在循环中改写；原路径工具改为显式接收根上下文，缺省参数仅兼容旧自建调用。Backend 保存同一受控根映射并校验上报路径，不能只改 Scanner 环境变量。

| 新目标项 | 冻结契约 |
|---|---|
| `SCENE_NAS_SCAN_ROOT` / `SCENE_NAS_READY_ROOT` / `SCENE_SLICE_PUBLISH_ROOT` | 生产分别为上述 incoming/ready/slices；测试为 `/test/scene/incoming`、`/test/scene/ready`、`/test/scene/slices`。分别校验绝对逻辑路径、物理映射及根不重叠，旧 `NAS_*` 校验不替换。 |
| `intake_root_id` | 稳定枚举 `self_built`、`scene`；新增至 IngestProfile，缺字段的历史 profile 回填 `self_built`，不修改原 profile ID/version/hash。新场景入口为 `profile_id=scene-isolated`、初版 version=1，默认仅 scene_slice+slope；同根内匹配 incoming_prefix，跨根空前缀不得兜底。 |
| 接收上下文快照 | IngestSubmission 增加 nullable `intake_snapshot_json`，包含 schema_version=`scene-intake/v1`、environment、root_id、逻辑 scan/ready 根、profile ID/version。接受每包提交或系统默认提交时写入，绑定时补其已有 bound_incoming_path/bound_ready_path；恢复读取快照。根上下文与旧 EffectiveConfig/config_hash 分开，不重算已接受业务 hash。 |
| 路径占位和身份 | 继续复用 profile_id/version/relative_path 的摘要占位及唯一约束；profile 具体版本的 root_id 不可变，故能区分根。新 profile 不复用旧 profile_id；跨版本同一物理接收路径的活动提交在 Backend 有界加锁核验，拒绝抢占，不靠新增完整宽路径索引。 |
| 登记身份 | Scanner journal 与 register 请求携 root_id、原 incoming_path、ready path 和接收证据；Backend 由受控根重新验证。旧客户端缺 root_id 时，仅已验证的旧根可走旧兼容；场景 ready 即使缺 incoming_path 也不得落入自建默认。未知/矛盾根返回明确错误，不猜测。 |

场景根的默认提交只触发场景；保留用户显式提交 `self_built` 或双用途的既有兼容，只依据冻结用途创建对应运行，不隐式并集。旧自建根不因新场景默认配置新增场景任务。场景根无 profile/配置无效时返回可恢复 CONFIG_REQUIRED 或配置错误并停在接收/登记待处理；`SCENE_INGEST_ENABLED=0` 只暂停场景自动调度，不改变其来源身份，也不能作为默认触发 Phase0 的理由；有效冻结用途明确含 self_built 时，其自建分支仍按已有规则执行。异常恢复、人工/批量登记同样执行这个服务端防线。

显式self_built/双用途在场景根的输入兼容还需16A同步扩展Phase0代理的受控ready根与逻辑→物理映射；只接受已登记且冻结用途含self_built的源，不把任意`/public`路径放入白名单。输出/算法/A100后续契约继续旧自建路线，纯scene_slice不调用Phase0。本轮不迁移自建/NVIDIA执行位置。

incoming→ready 只在同一 NAS 文件系统内对校验合格的整个 Bag 原子 rename；ready、切片和旧根互不嵌套，目录穿越及符号链接越界拒绝。场景 staging 位于 slices 同一文件系统的 `.staging/<run_id>/<attempt>`，处理机本地 work 与 NAS 不同盘时先写/复制到 NAS staging 并校验，再 rename 发布，不能直接跨盘 rename，也不能修改原包。NAS 客户端支持与 Backend 物理挂载同时由 16A 供应，发布/complete/reconcile 只读核对同一受控物理根；不信任回报者自选 publish_root。

历史 submission/run 和其文件保留原路径及 hash，只用于原身份查询、恢复或完成；不因开启新根重建运行。启用前清点旧 PENDING_INPUT 提交/活动场景任务和 Scanner journal，先按原检查点完成或由用户显式处置，不自动搬包、重绑或重算配置。根级回滚先停新接收并等待已启动写者/已发布登记对账，再回滚代码/配置；包含 v0.4 新根记录时禁止回到会把场景输入当自建的旧版本。数据库 downgrade 只在无新记录的隔离库演练。

#### 7.3.2 处理机执行与远端模型

`SCENE_SLICE` 队列仍由 Orchestrator 领取，通过 `SCENE_PROXY_URL` 派发到**处理机本机**场景 worker/代理。处理机挂载 NAS 原包并在本机私有 run/attempt 目录完成 `PRECHECK → EXTRACT → INFER(仅请求模型服务) → SEGMENT → WRITE → VALIDATE → PUBLISH → REGISTER`。`EXTRACT` 解码和帧预处理、时间映射、切包 writer、文件摘要、manifest、NAS 发布、Backend 回报及恢复都在处理机；A100 不运行场景代码，也不存场景原包、切片或整包工作副本。自建/NVIDIA 的 A100 路线仍按各自专项执行。

`SLOPE_VLM_ENDPOINT` 指向受控远端模型服务；模型机只提供推理响应。请求限必要的抽样帧、模型参数及最小关联 ID，不传 ROS2 Bag、完整视频、发布产物或 NAS 路径作为执行输入；帧尺寸、频率、超时和 `VLM_PERMITS` 限额需在单包实测中记录。连接失败/超时不当作 NO_MATCH，保留步骤与证据并按原 run/attempt 对账、有限重试；模型结果版本及请求身份可追踪，不记录凭据或不必要的原始图像内容。处理机的 CPU、磁盘、NAS IO 和工作目录准入须覆盖峰值空间；模型许可只约束远端请求，不占 A100 存储/处理槽。验证需记录处理机与模型机间实际传输量及无整包上传证据，不能把低带宽风险留给部署阶段。

正式代理拟放 `scripts/scene_host_proxy.py`，执行编排独立模块复用现有 `app.scene` 适配器和 `scene_publish_service`，不把 scratch E2E 脚本当部署程序。`POST /run` 接收现有 Orchestrator dispatch_payload，先验证 SCENE_SLICE/run/源代次/任务及资源租约和受控配置，持久记录 `(run_id, attempt)` 后立即返回 `accepted=true`，后台执行；同身份重复请求返回同一接收结果、禁止第二个写者。`GET /health` 返回 active run 摘要，恢复文件记录进程身份和检查点。派发响应丢失需先按原身份对账再重发/标失败，不能假定未启动。处理机重启后先核验进程/已发布 manifest，终止旧写者后才能重试；持续续租，租约失效或收到取消后停止新写入/请求，对账后回报并释放许可。执行代理不得直连数据库。

工作根生产目标 `/home/data-process/rosbag_scene_work`，状态根 `/home/data-process/rosbag_scene_proxy_state`；本地测试对应 `/home/wang/work/.local/rosbag-catalog/scene-work` 和 `proxy-state/scene`。`SCENE_PROXY_URL` 保持已有配置名，生产必须指向处理机本机代理；生产端口由部署核实后配置，不猜占用。处理槽沿用 `SCENE_EXEC_HOST`（首期 1），模型许可沿用同一既有 executor_id 下的 VLM_PERMITS，NAS 发布许可同理；不能通过换 executor_id 创建第二套共享额度。先做本机磁盘/依赖预检和有界并发，首期不新建通用 CPU/磁盘调度器。

帧采样沿用已接受 `front-camera-jpeg-1hz` 和真实验证过的参数，重试及超时复用已有 HttpSlopeModelClient；调整分辨率/频率等影响识别内容的优化须升配置并重新核验质量。测试可注入有带宽上限的 HTTP 服务记录实际请求 bytes/帧数/重试与持续时间，另用经授权的真实模型做单包联调；不以系统级限速或批量网络压测作为最小闭环前置，不凭单包宣称生产吞吐达标。

#### 7.3.3 页面查询与步骤映射

`/pipelines/{id}` 必须先按 `pipeline_type` 分支，不能用 `source_id` 前缀或 Bag 的 `dataset_type` 推断场景任务。场景详情从已有 `SCENE_STEP_NAMES` 和真实 `StepRun` 构建总览；无记录标“未开始”，终态保持真实状态，Attempt 历史和错误可查。环境区只列处理机输入/工作根、场景 NAS 发布路径及远端模型服务身份；重试/取消按钮只展示该运行类型真实支持的动作，禁止自建 Phase0/Phase1/Phase3、A100 路径和强制重试选项误入场景详情。列表与详情使用同一类型/状态解释。

`/bags` 保留 URL 值 `slices|originals|all`，显示名改为“切片/原始数据/全部”。`slices` 为当前可用场景切片；`originals` 为所有原始输入：自建 `ORIGINAL`、场景源 `ORIGINAL`、英伟达输入记录（现有角色可能为 `NOT_APPLICABLE`，需按明确来源和非切片语义纳入）；`all` 包含这三类、场景切片、历史和其他既有记录。英伟达数据不得因角色枚举不同只在 `all` 可见；也不得把英伟达处理产物或场景子切片混入“原始数据”。类型筛选至少包含自建数据集、英伟达数据集、切片原始数据；数据来源、Bag 角色和处理用途分别建模/映射，避免用 `dataset_type=self_built` 单独推断“切片原始数据”。同包同时具多用途时只显示一条原始记录，筛选可命中相应类型。搜索、分页、状态、书签和详情跳转在三个视图间保持一致；测试包含英伟达真实形态记录和历史切片。

新增展示筛选参数 `data_kind=self_built_original|nvidia_original|scene_original|scene_slice`，不把“切片原始数据”伪装成新的 dataset_type，也不把 NVIDIA 的 bag_role 改为 ROS2 ORIGINAL。分类谓词：先按 SCENE_SLICE/有效 derivation 识别子包；NVIDIA 来源且非子包为 nvidia_original；ORIGINAL 且有 scene_slice 用途或已冻结 scene 根身份为 scene_original；ORIGINAL 且有 self_built 用途、或无任何场景依据的旧 self_built 记录为 self_built_original。双用途原包可同时显示两个类型标记并命中两个筛选，每个视图仍按 UID 去重。未知历史不猜类型，在“全部”保留并明确未分类。

两套查询入口使用同一分类/视图谓词：Web 的 bag_search_service 和 API 的 scene_result_query；当前仓库已有后者函数，但未发现 `GET /api/v1/bags` 集合路由，16C 要按 §7.1 以有界 GET 接线，不能把函数当已公开 API。旧 dataset_type 筛选/无 view 书签维持兼容，`data_kind` 与其并用取交集；不相容视图组合显示明确空结果，不静默丢条件；tab、分页、排序、筛选取消链接均保留相关参数并重置页码。原始记录不要求已处理成功、存在 Topic 或能打开 DB3，NVIDIA 的空采集时间/Topic 必须正常显示。

八步中文名为“输入检查、解码/抽帧、模型识别、区间生成、切包、产物校验、NAS 发布、登记/完成”。总览按运行类型及实际 StepRun 的最新 attempt 显示，未启动后继步骤不因 run 结束被伪标完成；NO_MATCH/NOT_APPLICABLE 的无需步骤标 SKIPPED 并给原因，历史状态不回写数据库。场景终态停止刷新，SCENE_FAILED/PARTIAL_FAILED 显示原错误；成功链接到 Bag 子包和原始父包。公共列表与详情优先判断 SCENE_SLICE，即使原始 Bag 带其他 dataset_type 也不能误分类；详情保留既有 07B 审计/下架组件，重试只用场景正常重试通路。

P2 插盘客户端先查询能力/入口、提交每包配置再传输，轮询提交/运行结果。大文件仍走 NAS 支持的传输方式；重传不改 Bag 内容或抢占已绑定配置。P3 统计接口复用数据库事实，范围见 PRD §6.2。

### 7.4 v0.5 水雾接入与原始信息契约

完整冻结内容见 [水雾设计](../../../rosbag-catalog-spray-pipeline/SPRAY-INTEGRATION.md) 和 [数据要求](../../../rosbag-catalog-spray-pipeline/RAW-DATA-REQUIREMENTS.md)：spray-v1点云适配、本机渲染/远端参考图双pass、整数bag storage ns轴、15秒/0.15/enter3/exit5等原实调规则、私有产物/版本缓存；source_metadata扩展提交API及intake_snapshot_json、独立hash和已有Vehicle绑定/父子继承；新增scene-spray窄前缀，不改scene-isolated坡道默认。16B代理通过原门禁后才做正式接线，不能复制未审代理绕开恢复缺陷。

2026-10-14已恢复§7.3.3、REQ-16及新GET集合API/页面需求；此前水雾独立发布不依赖UI的事实保留；水雾验收用已有run/results/Bag详情/lineage及文件获取，旧页面/入口回归保持。生产门禁见 [SPRAY-RELEASE](../../../rosbag-catalog-spray-pipeline/SPRAY-RELEASE.md)，状态见TODO §9；“含UI三项全接受”是原v0.4范围，不作为本轮水雾依赖。

## 8. 容量、归档与统计设计

### 8.1 P0 必要容量基础

P0 只落实不会导致后期重建业务身份/数据结构的基础，不开发完整大表治理系统。

| 范围 | P0 必须落实 | 责任/后置边界 |
|---|---|---|
| ID/FK | 新增高增长表用 BIGINT；旧 Bag/File/Topic 的类型、引用、剩余 ID 空间及锁影响先盘点，对外 bag_uid 不变。 | TASK-02：低成本兼容扩容可同批做；需大规模重建/长锁且不影响本样本处理的项目列入 TASK-15，写明风险和后续触发条件。不得一侧修改 FK 类型。 |
| 数据分层 | BagRecord 仅窄元数据，区间/标签来源/任务明细分开；逐帧结果、图片和大日志存产物引用，用途/场景关系可索引。 | TASK-02/04B：不通过大 JSON 检索用途，不把原始帧混入 DatasetFrame。 |
| 当前与历史 | 父包+场景当前指针、run+slice_key 和子包身份唯一；默认查询只展示当前可用结果。 | TASK-02/06A/06B：不通过换版逐条重写全历史，不为首次样例实现所有历史运营功能。 |
| 索引 | 首次迁移提供角色/状态/时间、场景反向关联、父包和分析版本区间排序的必要组合索引及唯一约束。 | TASK-02/06A：根据实际 SQL 核对，不无限追加冗余索引。 |
| 读写边界 | API limit 默认 50、上限 200；结果单批最多 100 项；新 JSON 字段写入默认 64 KiB，请求体默认 1 MiB；列表投影摘要，不无界展开 topic/子包/历史。 | TASK-03A/06A/06B/08：超限拒绝，历史值不截断，默认字段不包含逐帧明细；上限可版本化调整。 |
| 证据定位 | run/源代次、稳定 ID、时间/版本、schema_version、路径和摘要在结构化结果中保留。 | TASK-04A/04B/06A：P0 不实现通用冷存储搬运、热表删除或恢复调度器。 |
| 小规模检查 | 用首期真实样例和小规模 fixture 核对实际 SQL、索引、分页边界、查询次数及耗时/空间；报告数据规模和局限。 | TASK-06A/08：不设十万条门槛，不以此宣称生产容量；规模预测、压测和指标大屏留 TASK-15。 |

必要索引组合保留：

- BagRecord 的 (bag_role, availability, started_at, bag_uid)；车辆检索按实际 SQL 核对是否增加 vehicle_id 前缀。
- bag_scene 的 (scene_id, bag_id)，BagTopic 的 (bag_id, name)，用途关联的 (purpose, bag_id)。
- BagDerivation 的 (parent_bag_uid, scene_code, run_id, child_bag_uid)，SceneSegment 的 (analysis_version_id, start_ns, id)。
- 当前结果指针的父包+scene_code 唯一键，child_bag_uid 和 run_id+slice_key 唯一约束。

现有关键词 contains 不保证用 B-tree 索引。P0 优先验证角色/场景/来源/时间等结构化查询，记录关键词/topic 组合的成本和实际支持范围，不因此引入全文引擎或整库重建。若本次测试已经发现无法有界完成的查询，协调者记录范围限制或安排必要修复，不隐瞒或无限增加查询能力。

旧 ID 扩容若同批执行，须盘点全部 FK/隐式引用、保留原 ID，并在 MySQL 隔离库验证；SQLite 可用既有 DatasetFrame 的类型 variant，降级越界拒绝。若后置，TASK-02 回执必须明确旧类型、当前风险及后续任务，不能标“已完成扩容”。生产备份与授权要求保持不变。

### 8.2 批量扩张前容量门禁

TASK-15 为场景 Bag、区间、标签、派生和任务事件建立隔离合成数据集，覆盖典型父子比例、历史版本、多标签、时间范围和游标翻页；建议百万条区间级数据作为起始基线，实际预算及 SLO 由实测记录，不把建议写成已通过门禁。

报告包含插入/回报吞吐、当前版本查询、父子检索、场景筛选的 EXPLAIN ANALYZE、p95 和空间增长。索引应服务真实查询，不以全表 COUNT 或深 OFFSET 作为每次请求前置条件。现有 mysql_capacity_baseline.sh 只验证 DatasetFrame，不能直接作为本模块容量证据；若复用，需新增场景模型数据和查询。

按报告明确容量告警、保留周期和扩容触发值，达到经验证容量预算前预留处理窗口；未取得报告不得宣称无限扩展或批量生产就绪。十万/百万级完整测试不阻塞 P0 单包真实闭环；P0 仅落实 §8.1 的模型/访问边界和小规模检查，TASK-15 在获准批量扩张前验证完整规模、旧表风险、容量预算和必要改造。

### 8.3 冷热归档与完整性

核心 Bag、派生关系、当前版本、有效标签和最小任务摘要保持在线；稳定证据身份与定位字段应在 P0 建表/manifest 契约中落实，后续再实现归档搬运、热明细释放及恢复流程。历史逐帧证据、大日志及低频事件可按管理员保留策略转入冷存储；P0 默认不自动删除或归档业务记录。

归档建立批次 manifest（稳定记录 ID、源/任务/版本、schema_version、数量和摘要）及定位索引。历史查询先返回在线摘要与归档引用；需要明细时创建受控恢复任务，按稳定 ID 在隔离恢复区域核验并读取，不重新调度识别或重复注册 Bag。清除热明细前必须有可验证归档、恢复测试及适用授权，不能对原始 Bag/切片文件执行清理。

后续仅对独立日志/证据明细评估时间分区或归档表；MySQL 分区与外键/唯一键约束需单独验证，核心 Bag 和血缘不首期分区，也不按车辆或场景建动态表。

### 8.4 P3 分布统计

默认按当前版本 AVAILABLE 切片统计。片数和源包数分别 COUNT DISTINCT；时长分为每分组片段累计时长、同父包区间并集覆盖时长。总体多场景覆盖需再次跨场景求并集，不能把分组结果相加。

统计表/增量汇总可在规模化后引入，但须有幂等更新键、换版/下架/标签修订补偿及重建路径，不能每次打开图表扫描逐帧证据。采集日期来自父包时间，展示采用统一业务时区；API 纳秒不施加时区偏移，统计返回范围与刷新时间。

## 9. 清理、迁移、兼容与回滚

派生父/子包在旧清理 preview、confirm、claim、finalize 各阶段均拒绝。登记和清理竞争时锁同一源并核对 fence，FK RESTRICT 是最终防线；不能只隐藏 UI 按钮。父删除不级联删除子文件。

迁移只做本链路必要的角色/用途、配置、能力/分析/区间、血缘、标签证据和索引。既有 ID/FK 扩容按 §8.1 先评估，低成本兼容可合并，高成本重建显式后置，不作为首个测试样例前置；不覆盖原 ID/对外 UID。已有确认为 ROS2 的原始记录回填 ORIGINAL，非 ROS2 条目 NOT_APPLICABLE；无法确定者输出报告不猜测。既有用途、活动运行和人工标签保留，不全量补跑或顺带做历史治理。

新场景专用根的自动接收默认关闭，启用后只处理该根的新输入；关闭时仍识别场景来源并阻断自建回退。原基础页面目标暂停保留；既有查询的可见性不受场景调度开关影响。关闭调度停止新任务，不删除产物或切断查询。已有派生数据/活动任务或新根记录时拒绝破坏性 downgrade；升级/降级和恢复仅在隔离库验证。

生产迁移需当次独立授权、备份验证及现有发布脚本，不能把本文示例作为部署授权。测试和生产根/工作目录严格隔离，部署状态引用项目生成的部署快照，不手写或借用旧 HEAD。

## 10. 验证层次与建议默认值

- 契约/单元：配置覆盖、版本冻结、参数校验、测试适配器注册、各结果状态、时间精度、稳定幂等键、缓存失效。
- 隔离数据库/服务：三用途、同父并行任务类型、重复请求、绑定竞争、分批登记、换版顺序、发布断点及清理互斥。
- v0.4 本地真实链路：授权坡道 Bag 从场景专用测试根经正式代理到 API/页面获取，检查实际步骤、路径、消息、区间、请求 bytes 和源文件摘要；mock 仅证明契约。逐项验收见 [ACCEPTANCE](../../ACCEPTANCE.md)。
- 后续：逐场景真实材料和质量验收、人工修订和预览，水雾材料不足仅阻塞水雾；已在途 07B 按原检查点接续。
- P2/P3：客户端幂等传输和配置一致性、统计去重及换版补偿；扩张前独立容量与归档恢复验收。

每包用途、场景、最多三执行者、最小链路优先及首期边界为已确认选择；参数、运行时并发、分页与容量起始规模为工程默认，可版本化调整但不得改变已冻结运行。模型服务视觉能力、图像时间映射、坡道标注样本/质量阈值以及后续水雾参考图依赖均需实证，不以配置存在冒充验证。

任务与验收对应见 [TODO](../../TODO.md)，执行入口见 [HANDOFF](../../HANDOFF.md)。

## 11. 有界开发与并发集成

### 11.1 范围边界

当前补PRD REQ-16/05对应界面与历史OCR缺陷，已接受水雾AC-17/18/19及14/15保留并做必要回归；复用已接受Backend、双根Scanner、租约/发布/writer及16B正式代理。三路UI增量按当前入口恢复；插件市场、任意算法上传、通用调度平台、多场景上线和完整归档仍后置。错误/幂等/原始保护/可信时间不能省略。

P0 真包内容核验和技术能力探针证据保留，规模化标注及生产质量验收另行准备；不把工程闭环描述成准确率或生产容量验收。所有优化须说明本次实际问题和最小解法。历史 TASK-10 DONE 保留，本轮在16C三叶、固定候选16D和原OCR遗留16R处置完成后停止扩张；原12S-D广义质量缺口独立保留，UI发布按当前生产门禁。

### 11.2 模块子任务与可并行边界

TASK-04 拆为 04A（注册/类型/协议及测试能力）与 04B（坡道/时间/writer 真实适配）；TASK-06 拆为 06A（结果仓储、检索/血缘及验证接口）与 06B（执行回报 API、发布/恢复/版本切换联调）。仅拆已有产物，不新增功能。

- 04A 可与 TASK-02、03A 同时开发；04B 在 04A 接受后开始，不必等接收 API。
- 03B、TASK-05、06A 在 TASK-02/03A/04A 接受后均可开发。03B 消费正式配置/能力仓储；TASK-05 以固定的接收事件契约实现运行/调度，消费者测试可构造事件，不必等待 Scanner 开发；06A 以固定 RunContext/manifest 契约实现有界仓储和查询，未接真实执行回报前不能宣称发布完成。
- 06B 依赖 TASK-05/04B/06A，以真实租约/源校验/文件证据接入结果仓储，补完整发布恢复与当前版本切换。
- TASK-09 在 04B 后可独立做小样本真实能力/时间/内容验证；完整接收、运行、结果联调由 TASK-08 验证，不能以构造事件或替身替代真实链路。

共享契约由协调者维护在本文并固定版本：能力描述、提交/EffectiveConfig、区间/manifest、RunContextValidator、能力/结果 Repository 和接收调度事件。03A 负责配置 DTO；04A 负责能力/区间与执行协议；协调者在合入前确认字段/单位/状态一致，不能重复造不兼容类型。

已接受契约（2026-10-08）：

| 契约 | 版本 | 事实来源 | 消费方 |
|---|---|---|---|
| 配置解析与 DTO | scene-config-v1 | 终版 commit 67f9f4c（合入 8e97ef1，OCR 三轮返修收敛）：app/domain/scene_config.py、app/schemas/scene_config.py；早期 7714e89 内容已被替代 | 03B/05/06A |
| 能力注册与执行协议 | scene-capability/v1 | 终版 commit a23c541（合入 94cfc2f，OCR 三轮返修收敛）：app/scene/ 包、config/scene_capabilities.yaml、GET /api/v1/scene-capabilities；早期 28d958c 内容已被替代 | 04B/05/06A/06B |
| 结果仓储与查询数据层 | scene-result-store/v1 | 终版 commit e92ef17（--no-ff 合入 main **8bd5618**，2026-10-09，OCR 0 findings）：app/services/scene_result_service.py、app/services/scene_result_query.py、tests/test_scene_result_storage.py（25 项）；早期 c4ce66c 已被替代 | 06B |

- `CapabilityRead` 协议（03A 定义，4 方法）：capability_codes / enabled_capability / capability / latest_capability；`latest_capability` 返回该代码最近登记版本（无论启用状态），用于区分"未注册"与"已禁用"，并入 §2.1 能力描述的最小查询集。04A 的 `CapabilityRegistry`（get/resolve/list_descriptions）为同一读取语义的 YAML 注册表实现；03B 接真实仓储时须让两者字段对齐（scene_code、capability_version、enabled、disabled_reason/unavailable_reason、parameter specs、output/publish labels）。
- **字段漂移适配（03B 接线时统一）**：03A 消费侧 `CapabilityDescription.parameter_specs`/`unavailable_reason`/`required_inputs: tuple[dict]` 与 04A 供给侧 `parameter_schema`/`disabled_reason`/`TopicRequirement` 同义异名；以 04A 的供给侧字段名为准，03B 写一个适配函数双向转换，不得两侧各自硬编码。详见 03A attempt-2 回执的对照表。
- **两级 config_hash 关系**：03A 的 `EffectiveConfig.config_hash`（schema_version+profile_id+profile_version+排序后 purposes+冻结 scenes 含版本与完整参数）是整包提交快照身份，用于幂等回放与调度事件去重；04A 的 `config_hash`（scene_code+capability_version+最终参数）是单能力维度身份，用于冻结能力参数与 manifest 对账。前者可嵌套后者，05/06B 对账时不得混用同一字段名而忽略粒度差异。
- 04A 已挂载路由 `GET /api/v1/scene-capabilities`（dfd4f0e 合入路由总入口，实测 200）；03A 的 schemas 导出（IngestSubmissionRequest 等）已在 app/schemas/__init__.py 追加。
- 04A 终版接口面新增：`SceneAdapterError(code, detail)`、声明式 `ParameterConstraint` 跨字段约束（slope: overlap<segment_len）、版本数字后缀排序、YAML 加载错误统一 `CONFIG_LOAD_ERROR`；03A 终版新增：`SceneConfigError` 对 NaN/Inf/不可哈希用途的拒绝、重复场景去重语义。下游（04B/05/06A/06B）以终版签名为准。
- **结果仓储契约（scene-result-store/v1，06A 终版 e92ef17 确认，06B 直接引用）**：① 完整性门禁 `expected_segment_count == registered_segment_count` **等值比较**（同基数 = manifest 全部区间数，含 flat 等非发布）；可发布子集另走 `list_segments(publish_only=True)` 与 manifest `expected_slice_keys` 核对，不混入段数基数。② `switch_current` 有界 3 次重试后 409（重放语义），新版失败保旧 current 不动。③ 幂等写路径（登记/换版/切 current）IntegrityError 兜底：已是目标态→200 重放，冲突→409 DUPLICATE_CONFLICT，其他→留痕 500。④ 零 schema 变更（guarded UPDATE / NOT EXISTS 均 DML，两后端同义）；06B 不另建切片索引。⑤ PENDING/未 complete 版本 current=False 默认不可见。
- **用途调度事件契约（purpose-schedule-event/v1，2026-10-08 协调者冻结）**：生产者=03B（Scanner 绑定完成/手动登记同事务），消费者=05（队列领取与运行创建）。最小字段集（JSON，持久 outbox 表/记录，幂等去重键=`event_id`）：
  `event_id`（UUID，唯一）、`source_id`、`source_generation`、`parent_bag_uid`、`purpose`（scene_slice|self_built，每用途一条事件）、`scene_code`、`capability_version`（冻结后固定）、`capability_config_hash`（04A 单能力维度）、`effective_config_hash`（03A 整包快照维度）、`submission_id`（目录默认绑定生成的系统提交亦有 ID）、`profile_id`、`profile_version`、`frozen_at`（CST）。
  规则：同一 (source_id, source_generation, purpose, capability_version, capability_config_hash) 只创建一次运行（05 幂等）；self_built 用途事件不携带 scene 字段（保持现有自建流程入口语义）；03B 不得内嵌推理，05 不得改 03B 的 source_service/Scanner 文件；字段增减须回协调者升版本。

### 11.3 文件责任与隔离

| 任务 | 主责任范围 | 共享/集成规则 |
|---|---|---|
| TASK-02 | app/models.py、Alembic、血缘基础、清理守卫 | 迁移链只有一个负责人；后续必要模型改动先交协调者安排，不并发覆盖。 |
| TASK-03A | 配置 DTO、纯解析、读取协议、对应测试 | schemas 总导出在合入时由协调者更新，不和 04A 抢类型。 |
| TASK-04A/04B | 注册/协议及坡道/writer 适配、对应测试 | 前后子任务顺序交接，同目录写权限在验收后转给下一 owner。 |
| TASK-03B | 接收 API/服务、source_service/catalog_ingest/Scanner | source 接收入口归本任务，TASK-05 不同时改该文件。 |
| TASK-05 | pipeline_service、队列/状态、Orchestrator/执行代理 | 队列/状态枚举只有本任务 owner 写；接收事件由约定的 outbox/接口消费。 |
| TASK-06A | 结果仓储、Bag 查询/血缘服务、对应测试 | 只实现数据和验证边界，06B 接续正式回报/发布；与 03B 的接收文件分开。 |
| TASK-06B | 结果/complete-scene 路由、发布/恢复及执行接口 | 真正校验租约、源代次和 manifest 后可用，不把替身用于生产结果登记。 |
| TASK-08/09/10 | 各自验证脚本、证据与任务回执 | 缺陷修复回原 owner 或由协调者重新指定，不自行跨任务改码。 |

Backend 路由总入口、schemas 总导出、共享运行配置及集成分支由协调者串行合入；后续 owner 可以变更，所有权按任务授予和释放，不永久绑定某个 Agent。变更需影响另一 RUNNING 任务时先协调，记录受影响契约和要重跑的验证。

最多三个执行者使用独立工作树/分支、样例目录和日志；实际 MySQL 迁移、NAS 发布及 GPU/模型验证按资源约束串行/租约控制，不因开发三并发就将 GPU 并发改为 3。队列派发、领取、验收及消息接续由当前主协调者执行，具体流程见 TODO §6/7，不开发新的调度服务。

## 12. 共享文档与证据更新契约

PRD/DESIGN/TODO/HANDOFF 由协调者单写；执行者写拟新增的专属 `receipts/<TASK-ID>/attempt-<n>.md` 并通知。首次领取才创建回执，不为规划建一批空文件。回执不是第二套任务列表，TODO 是状态事实来源。

每份回执记录任务/尝试/owner、需求/接口版本、工作树和 base commit、实际输出 commit/diff、允许范围、验证命令/退出码和 AC 证据、未执行项/阻塞、需要的文档修订及建议可解锁任务。代码必须被验证并合入约定集成基线，下游才认为依赖可用；“分支已写完”或执行者自报不等于 DONE。

协调者收到回执后完成独立验收、更新 TODO/HANDOFF、必要时修订 DESIGN/PRD，然后重算 READY 并派发空闲执行者。契约变更需要评估已完成证据是否失效；不得改文档来使失败测试自动通过。实现涉及仓库公共记录时按项目规则更新实际能力/架构/项目 HANDOFF，生成的部署快照不得手改。详细单写责任和更新时机见 HANDOFF §5。


<!-- a100-multi-node-entry-mn-v1 -->
## A100 双节点纳管独立专项入口

2026-10-12：[开发文档入口](../../A100-MULTI-NODE.md) / [角色启动](../../../rosbag-catalog-a100-multi-node/SESSION-START.md)。MN-v1仅文档DESIGN_READY；任务状态只在专项TODO维护，五角色未绑定，未开始业务开发、远端写入或生产启用。此入口不改变本文件既有任务状态、编号、派单、授权或角色绑定。

## 12. v0.4之后的水雾生产收尾契约

阶段门、状态机/源身份/幂等/上传稳定与拒绝恢复、公共文件顺序owner和真实质量用例已冻结于 [SPRAY-POST-V04](../../../rosbag-catalog-spray-pipeline/SPRAY-POST-V04.md)。这是REQ-20～22对原接收/保护/质量AC的具体化；不改当前v0.4 scope，也不追溯宣称生产已具备新能力。

接收绑定不受模型执行槽约束；快指纹不能唯一确定源。INPUT_REJECTED是新增待开发的提交接收终态，绑定状态BOUND/SCHEDULED和模型结果SUCCESS/NO_MATCH/NOT_APPLICABLE/FAILED保持独立；首期逻辑隔离不搬删原包。F增量DDL/API必须保持旧记录/幂等hash/冻结快照，E/F公共ingest/API串行交接。真实质量仍按原12S-D及新增AC-22，不把适用性检查、test或合成多DB3当真实验收。
