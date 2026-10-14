# NVIDIA 删除扩展技术设计

契约：**NC-v1 / DESIGN_READY**，2026-10-10。所有新增字段、表和行为均为目标态。
产品范围见 [PRD](PRD.md)，任务状态只读 [TODO](TODO.md)。

## 1. 证据基线与复用

catalog 调查 HEAD：`74ba3bfa5d75d87db5f38ba83a65d8b9f888da38`。
NVIDIA 脚本本地 HEAD：`52f65d1920e07a8d5ce5a92d5ae5fe14b9492147`；批准配置固定的 `code_revision=95f4ff65aa7f8e0e15047dcb6c9809891e15ecc3` 与本地 HEAD 不同。本轮未核验 A100 checkout；执行者不能把本地新脚本当已发布版本。

| 事实 | 可定位源码 |
|---|---|
| 类型限制、操作账本、finalize、根矩阵 | `app/services/bag_cleanup_service.py`：`_require_self_built_bag`、`build_source_snapshot`、`approved_roots_for`、`finalize_cleanup` |
| 纯解析器和计划摘要 | `app/services/bag_cleanup_plan.py`：`build_cleanup_plan`、`_build_expected_targets` |
| worker 目标推导、根比对、对账 | `scripts/bag_cleanup_worker.py`：`_expected_targets`、`_approved_roots`、`_run_execute` |
| 安全删除及持久写锁 | `scripts/bag_cleanup_executor.py`；`app/services/remote_bag_lock.py`（既有 `bag-baglock-v2`） |
| 源身份、批次与提交重放 | `app/services/nvidia_service.py`；`app/nvidia_configs.py`；`app/models.py` |
| 当前 NVIDIA 启动与生产者路径 | `scripts/a100_host_proxy.py`、`scripts/nvidia_pipeline.py`；NVIDIA 仓库 `run_nvidia_chunk.py`、`phase0/download_physicalai.py` |
| 围栏及通用写入口 | `app/services/source_fence.py`、`pipeline_service.py`，以及帧/产物/资源相关服务 |
| 页面限制及活跃操作过滤 | `app/web/bags.py`、`app/templates/bags.html`、`app/static/bag-cleanup.js` |

以上 catalog 路径相对 `/home/wang/work/rosbag-catalog`；脚本仓库根为 `/home/wang/work/dataset_build/nvidia_physicalai_route/code/proj_nvidiadata_builder_scripts`。参考旧设计：[自建删除](/home/wang/work/doc/rosbag-cleanup/DESIGN.md)。旧范围仅首版自建；本专项只覆盖 NVIDIA 增量，不重置旧状态。

## 2. 架构与身份不变量

继续由 Backend 唯一写数据库。浏览器只传 source_id/cleanup_id 与确认字段；worker 通过内部 API 领取；A100 executor 按签名、冻结目标和真实文件事实执行，不直连数据库。长任务不进入 Web 请求线程。

| 身份 | NC-v1 约定 |
|---|---|
| source_id | 沿用 `nvidia-chunk-{十进制 chunk}`，不改全项目 UID 格式；chunk 非负、规范无前导零，生成 UID 不得超过现有 26 字符列容量；必须核对 UID、`BagRecord.dataset_type`、metadata、名称。不能只根据前缀判类型。 |
| source_identity | `dataset_repo@resolved_dataset_revision:chunk:{chunk}`；repo/revision/chunk 是数据身份，不能用配置名或下载 endpoint 代替。 |
| 物理冲突域 | `(environment, canonical origin_root/data_sample_chunk{chunk})`；即使 revision 或配置不同，落在同一目录仍共用围栏和 flock。 |
| source_generation | 已有源代次，首次 1，重新导入由服务端从已成功清理墓碑推进到 +1；旧 run、回调及批次条目都保存原代次。 |
| worker generation / attempt | 仍分别表示清理租约代次与流水线尝试号，不等于 source_generation，不能拿来解除源墓碑。 |
| 历史操作 | cleanup_id 独立于 BagRecord，计划/结果/保留快照不会随删除或新代次改写。 |

规范源路径沿用 `BagRecord.relative_path` 的绝对 A100 origin 路径，不给 NVIDIA 添加 NAS 前缀剥离。身份缺失或互相矛盾时 `NVIDIA_IDENTITY_MISMATCH` 阻断。本期批准配置只覆盖现有 repo/根；未映射的历史根阻断该源，不能自动迁移或扫描所有 `/data`。

## 3. 目标解析、保留与覆盖

复用调用入口，增加按 dataset_type 分派的窄解析函数，不建设通用插件平台。自建 `bag-cleanup-plan-v1` 保持；NVIDIA 使用新 `nvidia-cleanup-plan-v1`，携带 `dataset_type`、`source_identity`、`source_generation`、`chunk`、根和配置快照摘要。inspection 仍复用 `bag-cleanup-inspection-v1` 的真实 lstat 事实。Backend/worker/executor 必须明确支持新 plan 版本；未知版本不可执行。新增计划须绑定能力版本，滚动更新期间旧 worker 不能领取不支持的计划。

### 3.1 路径矩阵（源码配置事实，不代表现场存在）

| 类别 | test 根 | production 根 | 唯一删除目标 |
|---|---|---|---|
| NVIDIA_ORIGIN | `/home/xmyf/wzd/test/rosbag-catalog/data/nvidia_origin_dataset` | `/data/nvidia_origin_dataset` | `<origin_root>/data_sample_chunk{chunk}` |
| NVIDIA_INFER | `/home/xmyf/wzd/test/rosbag-catalog/data/nvidia_infer_dataset` | `/data/nvidia_infer_dataset` | `<infer_root>/data_sample_chunk{chunk}` |
| NVIDIA_RUN | `/home/xmyf/wzd/test/rosbag-catalog/runs/nvidia` | `/data/nvidia_pipeline_runs` | `<run_root>/<完整 pipeline_run_id>`，枚举本源所有 run |

没有源码证据支持独立 NVIDIA phase3/staging 根，不套用自建的五根矩阵。当前生产者在 Chunk 目录下载、解压和推理，在 run 内存步骤、日志、manifest、attempt 历史与临时文件；父目标递归覆盖这些内容。目录内 `.cache` 等局部缓存一并删除；目录外共享 HF 缓存一律保留。

覆盖来源是 DB 全部 run（包含终态和软删索引）+ 每个 run 固定配置快照 + copies/artifacts + 远端 owner/运行标记。服务端枚举两类 Chunk 固定目录，并对批准 run 根做有界、只读 owner 清单核对，以发现未登记但明确属于该源的 run；仅有名称相似的孤儿 run 不加入目标。发现孤儿且没有 source_identity/chunk、完整 run ID 和版本的一致证据则 `OWNERSHIP_UNKNOWN`，不能忽略后宣布“全量”。有界检查超限时 `COVERAGE_INCOMPLETE`，不截断后确认。

建议首版保护上限：每源 256 个历史 run、1024 个归一化根目标，run 根每次分页 100 条、最多检查 10000 条；远端检查超时 120 秒。都是拟新增常量，NC-01 根据本地造数验证调优；不得静默截断，超限只阻断该操作，不要求本期建设全局目录索引平台。

### 3.2 归属与保留规则

- origin 的 `.download_contract.json`（repo/revision/chunk/endpoint）和可解析 download manifest 可提供归属证据；infer 的 `.pipeline_owner.json` 给出 run ID/revision，再与数据库 run 和 source_identity 核对；run 的 `run.json` 核对 run ID/chunk/revision/PID-start identity。owner 不要求指向最后一次 run，但必须属于本源批准历史。
- 空目录或下载尚未写完的目录，只有其来源被本期 writer 持久证据或已有 manifest 明确证明时才可删。仅“路径恰好匹配”不能自证归属；无证据的存量数据需要人工对账后重新预览。
- NAS 类型显式允许 `NVIDIA_ORIGIN_NAS`、`FINAL_DATASET`、`NAS_*`；路径仍按服务端批准 NAS 环境根核对。`A100_NVIDIA_RESULT`、`NVIDIA_FINAL`、`NVIDIA_RAW_MANIFEST`、`NVIDIA_DOWNLOAD_PAYLOAD_MANIFEST`、`NVIDIA_QUALITY_REPORT`、`NVIDIA_FRAME_IMPORT_MANIFEST` 和 NAS final artifact 根据 producer 的真实 path 分类；不能只凭 artifact_type 判删/保留。
- A100 path 必须完全落在上述批准目标子树；NAS/local path 进入 preserved；共享/未知存储阻断。外部 source 的 copy/artifact/frame 对目标子树或目标产物有引用则阻断，不修改其他源。
- 目标按规范绝对路径去重，移除被父目标覆盖的子目标但保留分类来源；不删除根目录本身、不允许通配符、前缀相近的 Chunk 或客户端路径。
- executor 继续拒绝树内/祖先符号链接、挂载点、越根、权限错误及 dev/inode 替换。`ABSENT` 只来自实际 ENOENT；未检查到、SSH 失败或进程结果未知均是 UNKNOWN。

worker 的 `_expected_targets` 和 `_approved_roots` 与 Backend 使用同一类型分派和批准矩阵。历史配置根只在同环境 allowlist 中认可；以新的当前配置覆盖旧快照或由客户端注入根均拒绝。

## 4. 现有 API 扩展与开关

复用，不创建第二套删除 URL：

| API | NC-v1 行为 |
|---|---|
| `POST /api/v1/sources/{source_id}/cleanup-previews` | 支持两种已知类型，202 返回 cleanup_id，只产生只读预览；未知类型 422。 |
| `GET /api/v1/bag-cleanups/{cleanup_id}` | 保留现有字段，新增 NVIDIA 身份、用户可读类别与保留说明；同会话查询保护不放宽。 |
| `POST /api/v1/bag-cleanups/{cleanup_id}/confirm` | 请求体仍为 digest/revision/nonce/acknowledged，extra=forbid；重新核对源代次、完整 run 集合、身份和引用，陈旧预览 409 PLAN_CHANGED。 |
| `POST /api/v1/bag-cleanups/{cleanup_id}/retry` | 只恢复已确认的原计划；新路径或新的 owner 导致对账阻断，不扩大目标。 |
| 内部 claim/heartbeat/report | 兼容旧 plan，新版本能力明确；NVIDIA claim 带源代次和完整冻结身份，未知版本 fail closed。 |

拟新增 `NVIDIA_CLEANUP_ENABLED=false`。NVIDIA 需同时满足既有 `BAG_CLEANUP_ENABLED`、新开关、会话/Origin 配置、worker 新版本、远端写锁支持。自建不依赖新开关。前后端用同一能力判断，不把全局开关直接映射为所有类型可删。

沿用签名会话 cookie、SameSite、Origin 白名单、短时 nonce、摘要、Idempotency-Key；不能新增无确认的 DELETE 路由。序列化清理查询时不得输出内部签名、密钥或 nonce 哈希。

## 5. 围栏、远端互斥与重新导入

### 5.1 Backend 事务

本源清理确认、NVIDIA 单/批创建和重新导入先锁同一规范 SourceOperationFence 行，再锁 BagRecord/run，形成统一顺序。首次创建围栏行由唯一 `(environment, path_hash)` 与 IntegrityError 重读处理，不靠进程内锁。围栏锁在同一数据库事务中保持到写提交。批量提交每个 Chunk 单独遵守该顺序，不把 30 Chunk 放进跨 SSH 长事务，也不跨 Chunk 多行逆序持锁。

preview 只快照不长期锁；confirm 在锁内重比 generation/run 集合/配置摘要，变化使计划失效。确认后 active fence 持续到双完成；活动/未知状态或 lease、auto_retry 都阻断。所有建 run/重试/自动激活/claim/资源/步骤/状态/产物/帧入口检查同一 fence 和源代次，源不存在时从 run 和 fence 审计判断已清理，不能因查不到 BagRecord 而直接放行。新 run 配置快照保存 `source_generation`，回调依赖服务端 run 对应代次，不接受客户端随意覆盖。

### 5.2 A100 writer

NVIDIA launcher 在第一个业务 mkdir、日志写入、下载或推理之前取得与删除方相同的 `(environment, source_id)` flock；整个远端进程树持有锁，不能在 nohup 派发后随启动 SSH 退出而释放。持久 writer session 写入 source_identity/source_generation/run/attempt/PID-start identity，删除方同时检查 flock 与未对账 writer 证据。

复用 `remote_bag_lock` 的 writer session/失联保留机制。现有 `launch.lock` 仅防同 run 重复启动，不能代替源写锁。Backend 围栏拒绝心跳不代表远端停止；SSH 断线、代理重启、holder 异常后，只要实际写者或身份未知就持续阻断删除。只在真实进程树退出并对账后释放，不自动 kill。

既有远端删除 meta 按稳定 Bag UID 保存终态，不支持同 UID 的下一次清理直接覆盖。NVIDIA 增量采用**稳定 flock + 按 source_generation 分离的删除 meta**：新 NVIDIA meta 文件在原锁根专用 `nvidia-generations/<lock_key>/g{source_generation}.json` 下，审计/未决 writer 检查跨代次共用。第一次与第二次清理记录都保留；锁 inode 不删除或重建。该路径不是数据清理目标。

签名材料增加 NVIDIA 协议版本、source_identity、source_generation；worker lease generation 仍独立。旧 self_built v2 的文件/摘要/行为保持兼容。未知协议、无源代次、新版 worker 搭旧 helper 时明确 `NVIDIA_LOCK_UNSUPPORTED`，不回退无锁执行。NC-03 必须验证相同 UID 重新导入后第二次清理，不仅验证首次删除。

### 5.3 重新导入与旧键

成功后保留 deleted fence。普通单/批提交已删源返回 409 SOURCE_CLEANED；UI/API 显式重新导入使用新幂等键：单 Chunk 增加可选 `reimport_cleanup_id`，批次增加 `reimport_cleanup_ids`（chunk 十进制字符串→cleanup_id，最多 30 项）。服务端核对该清理成功、环境/身份/目录匹配及墓碑代次，事务创建 source_generation+1；未知或非成功清理编号拒绝。

已有 ApiIdempotency 用新独立 operation `nvidia-chunk-create` 保存单 Chunk 提交回执，记录 source/run/generation/request_hash。删除时转成 CLEANED 历史回执并保留，不能被通用 source_id 幂等记录删除一起清掉。请求重放先查该回执并核对 hash：已清理始终 409 SOURCE_CLEANED（带历史 cleanup_id），即使新代次已创建；不返回一个已不存在的 run 当 created=false，不重建。历史 PipelineRun.idempotency_key 在删除前精确补回执；新提交同步写回执，不能依赖已删除的 PipelineRun 查旧键。

旧批次重放只返回原条目快照；即使状态曾为 SUBMITTING，其已清理条目也不能调用 create_chunk 重新创建。重新导入只能用新单请求或新批次，不能恢复旧批次把已删数据自动下载回来。重新下载可能命中已保留 NAS 目标，沿用发布器幂等/冲突检查，不覆盖 NAS 文件、不改变发布路径契约；冲突明确失败。

## 6. 批次持久条目与数据库 finalize

新增窄表 `SubmissionBatchItem`（目标模型）：

| 字段/约束 | 说明 |
|---|---|
| id | BIGINT PK，SQLite 用 Integer variant。 |
| batch_id、chunk | batch_id FK→submission_batch.batch_id RESTRICT；chunk 使用 BIGINT 并按现有 UID 容量校验；UNIQUE(batch_id, chunk)，每批最多现有 30 项。 |
| source_id、source_generation、source_identity | 稳定源快照；source_generation 的历史未知允许 NULL，不能猜填 1。 |
| pipeline_run_id | 历史 run ID，允许待提交为 NULL；不 FK 到待删除 run。索引 `(pipeline_run_id, state)`。 |
| state | PENDING / LINKED / CLEANED / UNKNOWN，和 pipeline status 分开。 |
| cleanup_id、cleaned_at | 独立清理编号/北京时间；没有 BagRecord FK，不随源删除。 |
| 索引 | `(source_id, source_generation, state)` 支持精确 finalize；不靠 JSON LIKE 查询全批。 |

`SubmissionBatch` 的 chunks_json/run_ids_json 仍作原提交快照，旧响应字段保留，不重排和删减；新条目是清理后可查的持久依据。迁移只建此小表和必要索引，不重建 DatasetFrame/旧主键。

创建新 batch 时先持久化全部请求槽位为 PENDING。每个 Chunk 在同一事务中完成 fence 检查、run 创建或复用、单提交回执、对应 item→LINKED 和 batch run ID 快照更新；不能沿用“create_chunk 内部 commit，之后再单独写 item”的窗口。NC-05 只为该链路提取可在调用方事务内运行的创建核心，单请求包装仍明确提交；批请求逐 Chunk 提交，不承诺整批原子成功。断线恢复按已落账 item 对账，不能重复创建。finalize 与 batch/link 的共同锁序为 fence→源/run→batch，GET 派生汇总不再进入源写入流程。

历史回填优先用 run 的 source/config 快照精确关联 batch；不能盲目 zip chunks 和 runs（重复提交可复用 run，SUBMITTING 可能只提交了一部分）。旧 run 未保存代次时，仅在源身份一致、BagRecord 代次和围栏/清理历史能证明归属时补代次；否则 NULL/UNKNOWN，不能猜 1。缺失 run、歧义映射记 UNKNOWN；未提交条目 PENDING，不伪造 CLEANED。无法证明准确性的批次只阻断其涉及源清理或该批次重放，不全项目停服。回填在隔离库演练、分批执行、记录未解决清单；downgrade 在存在清理历史/活动操作时拒绝丢审计。

finalize 沿用原顺序与单事务，新增：

1. 校验源代次、计划 run 集合完整、围栏仍归本操作、无活动/未知 writer、无跨源 frame/copy/artifact 及外部 parent_artifact 引用；不删其他源。
2. 同事务为所有精确引用待删 run 的 batch item 标 CLEANED（同 run 可被多个批次引用），写 cleanup_id/cleaned_at；保留 batch 及原历史字段。
3. 旧 NVIDIA 单提交键精确固化/转历史回执，独立清理账本与 batch 历史不清。
4. 删除 source 专属资源请求/租约、全部 DatasetFrame、Artifact/SourceCopy（含软删）、StepRun/Event/Run、BagFile/Topic/scene/purpose 等源关联，再删 BagRecord。frame 删除校验 source_id 与 run_id 双向：没有合法 run 的源孤儿帧不能漏删，错误指向别源 run 的帧阻断。
5. 更新 deleted fence 和操作 SUCCEEDED，统一由事务提交。任一步失败整体回滚，包括 CLEANED 标记，保留 DB_FINALIZING 恢复现场。

NAS 内容保留，NAS 的源业务索引仍删除；计划 preserved 中冻结路径、类型和现有 manifest/hash 摘要便于审计。Vehicle/Scene/ResourcePool/其他源/共享 SubmissionBatch/清理与提交历史不删除。

batch progress 返回原 runs 字段并保留每个条目槽位：LINKED 用实时 pipeline status；CLEANED 使用 `status=CLEANED`、历史 run/source/chunk、cleanup_id，不提供活动 run 详情链接；PENDING 仍表示尚未提交，不因其他条目完成而忽略。新增 `cleanup_summary={requested_count,cleaned_count,missing_count}`。全部已清理时 batch `status=CLEANED`；无 PENDING/UNKNOWN 且剩余存活 run 全完成、部分清理时 `PARTIALLY_CLEANED`；存活任务仍排队/运行/失败时沿用相应 pipeline 汇总并附 cleanup_summary。旧 SUBMITTING 的 PENDING 遇已删源只报告阻断，不将未曾绑定的条目伪造为 CLEANED。未知缺失 `NEEDS_RECONCILIATION`，绝不当完成。

GET 如继续写 batch 派生状态，需在写入时重读条目/行版本或锁 batch，防并发 finalize 后用陈旧 counts 覆盖；禁止 GET 恢复 SUBMITTING 或新建任务。查询每批最多 30 条，有界批量 join，不引入全库 JSON 扫描。

## 7. 状态、恢复与发布

复用状态：INSPECTING→PREVIEW_READY/BLOCKED→QUEUED→REMOTE_DELETING→REMOTE_VERIFIED→DB_FINALIZING→SUCCEEDED；异常 RETRYABLE_FAILED/NEEDS_RECONCILIATION，未确认可 EXPIRED。不把清理状态塞入 BagRecord.status 或 PipelineRun.status。

计划摘要绑定身份、源代次、完整目标、preserved、根/配置版本与归属证据摘要；执行结果写 result_json，不改确认计划。超时先 status/inspect 对账；部分删除按原 lock_generation 恢复，不能因新 worker 租约放松原签名。只有目标全部真实 ABSENT 才进入 DB_FINALIZING。DB 失败只重试 DB，操作围栏不自动解除。

本地迁移/后端/worker/远端 helper 按兼容能力先装配，新开关最后启用。仅部署 Python 文件不证明锁生效。真实测试只能在生成临时数据与授权 A100 test 根；生产源码/配置/数据库/目录写入保持独立用户授权、备份、`--apply --production`、业务验收与部署后本地收敛。

紧急关闭新预览/确认不能销毁已确认操作：worker 对原计划继续对账/恢复，或显式持有围栏等待人工维护，不能随开关关闭释放。禁止 downgrade 丢审计、清空 meta、回滚成旧无锁 writer 后继续处理同一清理源。生产发布后仍不能由 Agent 代用户确认实际删除。

## 8. 文件与资源 owner

| 写入范围 | owner/转交条件 |
|---|---|
| plan、worker 目标分派；后续 cleanup service/finalize/API/config | A：NC-01→NC-04，同一 owner 串行。 |
| models、迁移、batch item/提交历史；后续 nvidia service/schema/UI | B：NC-02→NC-05，NC-04 完成后再消费 finalizer 契约。 |
| source_fence、pipeline 通用围栏、remote_bag_lock、NVIDIA launcher/proxy | C：NC-03；提供 helper 后 NC-05 接 nvidia 创建入口。 |
| catalog `HANDOFF`、新共享 PRD/DESIGN/TODO、派单/decision、OCR、主分支合入 | 协调者；开发者只写独立回执。 |
| 迁移链 | B 单写，NC-02 派单时读最新 alembic head，不冻结虚构 down_revision；与场景专项协调者申请同一迁移串行资源。 |
| 集成 Compose/MySQL、browser、A100 test writer fixture | TESTER 使用固定快照；独占资源申请/释放有记录，不能改业务代码。 |
| OCR | 协调者串行，复用原全项目 OCR 锁，不另建绕过锁；新代码 ≤12 非文档文件/批，大文件按完整职责拆批。 |

不需要修改 NVIDIA 业务脚本即可在 catalog 远端 launcher 外包装 writer 锁；若真实代码证明必须改脚本，停止该增量并提交最小跨仓修订，不能自动覆盖 A100 checkout 或修改批准 code_revision。


<!-- a100-multi-node-amendment-mn-v1 -->
## 10. A100 双节点衔接契约（MN-v1）

2026-10-12新增规划补充；NC-v1任务/状态和删除范围不变。双节点技术契约见[MN DESIGN](/home/wang/work/doc/prd/rosbag-catalog-a100-multi-node/DESIGN.md)，任务见[MN TODO](/home/wang/work/doc/prd/rosbag-catalog-a100-multi-node/TODO.md)。仅当MN节点化能力被实现并接受后适用以下增量；不把NC未开发能力写成已实现。

- A保留本设计既有批准根；B使用MN profile的同名origin/infer/run根。目标按源全部run/copy/artifact的冻结节点解析，禁止把相同路径默认指向A，禁止扫描其他节点以猜测归属。多节点矛盾先阻断，不扩成跨节点批量删除。
- 节点化plan/inspection冻结node_id、environment、profile版本/摘要、根、source_generation及targets；上述字段进入digest、确认签名和执行器校验。物理冲突域扩展为`(environment,node_id,canonical_path)`，源业务身份/墓碑保持原协议，不能通过换节点绕过source围栏。
- 同一路径的跨源引用仅在同一节点构成物理引用；节点不明则阻断。Backend、worker、writer与executor使用同一节点profile和对应锁根，proxy实例必须校验自身node_id。
- §2～3的单A路径矩阵及nvidia-cleanup-plan-v1仍描述原A协议。包含B的新计划须使用明确的新节点化能力版本，旧helper不能领取。已经确认的旧A计划不原地补字段或升级，不扩大目标；不支持旧协议的候选须先完成兼容/对账再切换。
- UNKNOWN、未知启动、孤儿writer和持久UNKNOWN执行占用都阻断清理。proxy进程健康/短lease过期不证明无写者；恢复仅原节点、原快照、原确认范围，NODE_ID_MISMATCH/未知根拒绝。
- NAS、地图、共享模型和共享缓存保留规则沿原契约；节点化不新增删除授权。MN-03/06只衔接实际已接受的NC能力，不替代或复制NC-01～09派单。

NC相关消费者后续派单前须固定NC+MN已接受契约版本并由协调者核对共享文件owner；本轮不修改NC TODO、绑定、派单或历史证据。
