# NVIDIA 删除扩展任务单

版本：NC-v1，2026-10-10。**唯一任务状态源**。
本轮授权仅规划；所有开发任务保持 PLANNED，未派发、未开工、未验收。READY 表示后续启动开发时通过候选检查，不代表此次已授权执行。

## 1. 状态、范围与基线

PLANNED→READY→IN_PROGRESS→REVIEW_PENDING/TEST_REPORT_PENDING→DONE；阻断使用 BLOCKED，后续范围 DEFERRED；真实远端/发布步骤 WAITING_AUTH。文档 DESIGN_READY 不把 NC-01～09 标 DONE。

调查 base：catalog `74ba3bfa5d75d87db5f38ba83a65d8b9f888da38`，主分支 `main`。协调者派单时冻结最新验收 base，记录与调查版的相关差异；每名开发者自行创建 `feat/nvidia-cleanup/<task>-<attempt>` 专属分支/worktree，不能直接在用户主工作区实施。

本专项与上级场景切片 TASK-01～15、旧删除 T-/C- 编号分开，不复制或覆盖其业务状态。新根角色全部未绑定，不能复用上级 cron 让它自动领取本专项。

## 2. 完整依赖与验收映射

| task | 产物/推荐 owner | 硬依赖 | AC | 当前状态 |
|---|---|---|---|---|
| NC-01 | NVIDIA 安全计划与 worker 目标/根分派；A | 无 | 02、03、07 | PLANNED |
| NC-02 | 批次持久条目、历史回填和提交回执基础；B | 无 | 05、06、08 | PLANNED |
| NC-03 | 源围栏事务助手、NVIDIA 远端 writer/代次锁；C | 无 | 03、04、07、08 | PLANNED |
| NC-04 | 统一清理 API、快照/确认/finalize、新开关和装配；A | NC-01、NC-02、NC-03 | 01、02、03、04、05、07 | PLANNED |
| NC-05 | NVIDIA 创建/重导入接线、批次历史与页面；B | NC-02、NC-03、NC-04 | 01、04、06、08 | PLANNED |
| NC-06 | 固定候选独立 MySQL/浏览器/故障与兼容验证；TESTER | NC-04、NC-05 | 01～09 | PLANNED |
| NC-07 | 功能批次审查、纠错收口与真实验收包；COORDINATOR | NC-06 | 09，核对01～08证据 | PLANNED |
| NC-08 | 授权 A100 test 根实物删除/恢复/再导入验证；TESTER | NC-07 | 02、03、04、07、08、09 | WAITING_AUTH |
| NC-09 | 用户授权的生产迁移/部署及本地收敛；COORDINATOR | NC-08 | 09 | WAITING_AUTH |
| NC-D01 | 批量删除、NAS 删除、全局共享缓存 GC | 不进入本期 DAG | 无 | DEFERRED |

表中 AC 数字完整前缀为 `NC-AC-`，定义见 [ACCEPTANCE](ACCEPTANCE.md)。NC-07 是收口任务，不重复派一套实现；NC-09 完成不代表已代用户执行生产删除。

## 3. 三槽首波与接续

启动前置：用户后续要求实施、协调者确认本专项与已有任务的开发槽/文件资源不冲突、冻结 base 与 NC-v1 契约、完成角色绑定。没有这些前置不实际派单。

| 槽 | 推荐首波 | 后续候选 |
|---|---|---|
| A | NC-01（纯解析器及 worker） | NC-01/02/03 全接受后 NC-04。 |
| B | NC-02（models/迁移/条目与回执基础） | NC-04 接受后 NC-05；不能提前接线清理按钮。 |
| C | NC-03（围栏/远端 writer） | 关键路径返修优先；空闲不自动增加任务。 |
| TESTER 独立槽 | 首波无整链验收，按固定子候选可独立核验锁生命周期或迁移 | NC-04/05 接受且同快照可用后 NC-06；只独立测试，不作为第四开发者。 |

首波文件边界：A 不改 models/nvidia_service/source_fence；B 不改 cleanup_service/remote locks/proxy；C 不改 models/迁移/nvidia_service。共用 Backend 装配接线归 NC-04；消费者在供应方接受前只做合同替身验证，不能报联调通过。

| 完成事件 | 重算候选与限制 |
|---|---|
| NC-01/02/03 任一个 ACCEPTED | 检查其余两项；三项齐全才有 NC-04，不等无关整波。 |
| NC-04 ACCEPTED | NC-05；新开关仍关闭，UI/API 不提前开放。 |
| NC-05 ACCEPTED | 冻结集成候选给 NC-06，同时核对所有供应提交均被包含。 |
| NC-06 TEST_REPORT_PENDING | 协调者核验证据后接 NC-07；失败按问题 ID 回原 owner，不整体重做。 |
| NC-07 收口 | NC-08 仍要授权测试根、代理配置与远端版本事实；不因依赖满足自动真删。 |
| NC-08 ACCEPTED | NC-09 继续等生产授权和备份/回滚检查。 |
| 契约/提交变化导致原证据失效 | 撤回受影响验收，暂停对应消费者，追加有界复验；不是重新启动全部任务。 |

## 4. 任务卡

所有卡的固定 base/worktree/实际 owner/attempt 由协调者在派单填入，目前均**未派发**。以下文件路径相对 catalog 仓库，改名或越界必须先报最小修订。

### NC-01：计划及覆盖

- REQ：02/03/07；硬依赖无，接受后候选 NC-04。
- 输入：DESIGN §2～4、现有 self_built plan 与 inspection、NVIDIA 配置及 producer owner 格式；最小阅读 `bag_cleanup_plan.py`、`nvidia_configs.py`、`nvidia_pipeline.py`、旧 plan/worker 测试。
- 修改范围：`app/services/bag_cleanup_plan.py`、拟新增 `nvidia_cleanup_plan.py`（纯函数）、`scripts/bag_cleanup_worker.py` 的目标推导/根/版本部分及相应 tests。需要 cleanup_service 根函数改动时留给 NC-04。
- 输出：新 plan/schema、明确保留类型、跨源/owner/孤儿/有界覆盖、Backend 与 worker 同源分派；不得只改 UNSUPPORTED_DATASET 判断。
- 验证：双环境矩阵、多 run、父子去重、download 失败残留、相邻 chunk33/chunk330、共享目录、未知 owner、NVIDIA_ORIGIN_NAS 保留、旧 self_built 回归；worker 版本不支持拒绝。
- 停止：缺 owner 或历史非批准根输出 blocker/清单；不“自动修好”现场或发 SSH。
- 回报：`receipts/NC-01/attempt-N.md`，包含 commit、文件、契约、命令结果、未执行项。协调者 OCR 串行。

### NC-02：持久历史基础

- REQ：05/06/08；硬依赖无，候选 NC-04。
- 最小阅读：DESIGN §5.3/6、`models.py`、`nvidia_service.py` 的原批次/键逻辑、alembic 当前 head、MySQL 测试脚本。
- 修改范围：`app/models.py`、一个新的 Alembic revision、拟新增 batch item/提交回执服务文件、对应隔离迁移/数据测试；不改 nvidia_service 接线（NC-05 owner）。
- 输出：SubmissionBatchItem 的窄字段/索引/唯一约束、精确历史 backfill、ApiIdempotency 的 NVIDIA 持久回执 helpers、UNKNOWN 清单与受影响源定位。
- 验证：SUBMITTING 部分 run、多个批次引用同 run、run 缺失与歧义、重复回填、MySQL upgrade、历史清理存在时 downgrade 拒绝；迁移失败不遗留半回填假 CLEANED。
- 迁移串行资源由 B 申请；不在用户 DB 运行测试，不固定过时 down_revision，不引入批次整表 JSON 扫描到常规查询。
- 回报：`receipts/NC-02/attempt-N.md`，含 schema/SQL 证据与数据回填限制。协调者 OCR 串行。

### NC-03：写者互斥和代次

- REQ：03/04/07/08；硬依赖无，候选 NC-04。
- 最小阅读：DESIGN §2/5/7、`source_fence.py`、`pipeline_service.py`、`remote_bag_lock.py`、`bag_cleanup_executor.py`、`a100_host_proxy.py`、`nvidia_pipeline.py`、既有并发/孤儿 writer 测试。
- 修改范围：上述围栏/锁/helper/executor/NVIDIA launcher/proxy及匹配 tests；不改 models、迁移、nvidia_service、cleanup_service 的事务接线。新增助手接口按 NC-v1 给 NC-04/05 消费。
- 输出：同路径 fence 行锁助手、旧 run 缺源/代次检查、稳定 flock/跨代次 writer 证据、代次隔离 meta 与签名、锁前零业务写入、SSH/孤儿保留、版本能力探测。
- 验证：真实本地子进程树、SSH 断线模拟、holder 退出但子写者存活、同 UID 二次清理/旧代次重放、身份签名篡改；现有自建 v2 全部保持。
- 停止：远端 helper 不支持即失败，不绕过签名；如需改 NVIDIA 脚本仓库先提交跨仓最小设计修订，不更新 A100 checkout。
- 回报：`receipts/NC-03/attempt-N.md`，附实际 PID/start、锁/退出/目录证据。协调者 OCR 按职责拆批串行。

### NC-04：清理事务闭环

- REQ：01/02/03/04/05/07；依赖 NC-01/02/03 被接受且进入指定 base，候选 NC-05。
- 最小阅读：DESIGN 全文、三个供应方回执、`bag_cleanup_service.py`、`bag_cleanup.py`、`config.py`、现有 finalize/API/worker MySQL 测试。
- 修改范围：cleanup_service、cleanup API/schema、config、必要 worker/service 装配/Compose 环境变量、finalize/API 测试；不改 B 的 models/迁移或 C 的远端协议。
- 输出：两类型快照/开关/确认重核、持锁事务、REMOTE_VERIFIED→finalize、精确批次标记及提交回执保留、源孤儿帧策略、完整 rollback、自建派生保护。
- 验证：真实隔离 MySQL confirm/create 竞争、远端完成后 DB 注入失败（所有 DB 与 batch 标记回滚）、frame 双向归属、外部产物父引用、重驱不再远端删除；未知 plan 版本拒绝。
- 停止：实际根/版本未知不能设置 PREVIEW_READY；生产新开关默认关闭；本地 Compose 专项需要协调者资源预约。
- 回报：`receipts/NC-04/attempt-N.md`。适用静态/pytest/Compose 验证与协调者 OCR，无生产操作。

### NC-05：用户链路和提交历史

- REQ：01/04/06/08；依赖 NC-02/03/04，候选 NC-06。
- 最小阅读：DESIGN §4～6、PRD 用户旅程、供应回执、`nvidia_service.py`、`schemas/requests.py`/`responses.py`、`web/bags.py`/`pipelines.py`、bags/cleanup/nvidia 模板与 JS。
- 修改范围：NVIDIA service/schema/API 消费接线、Bag/NVIDIA web 页面、静态 JS、页面/API/批次测试；不改共享数据模型/迁移（已冻结）或 finalizer。
- 输出：单/批创建围栏先于键重放的源安全检查、持久历史回执、run/回执/item 同事务落账（拆除旧 create_chunk 提前 commit 窗口）、旧 SUBMITTING 不复活、显式 reimport 的新代次与旧键语义、batch progress CLEANED/缺失处理、NVIDIA 清理按钮与恢复上下文。
- 验证：单/批预览与创建、活跃 fence 409、旧键/旧批次重放、混合终态/运行/已清理、全部清理、reimport 两次竞争只创一代、HTTP 非安全上下文幂等键 fallback、取消/刷新/分页保留。
- 停止：清理开关关闭或 helper 不可用时不能仅显示按钮；不加大文件上传、新权限体系或整批删除。
- 回报：`receipts/NC-05/attempt-N.md`，截图/接口/SQL 结果分开；协调者 OCR 串行。

### NC-06：独立综合验证

- 固定集成 SHA（必须含 NC-01～05），TESTER 自行独立只读工作区，不修改业务实现；完整输入见 [ACCEPTANCE](ACCEPTANCE.md)。
- 先核验开发者证据，再按关键风险复现 MySQL 竞争/回滚、本地实际 writer 进程、浏览器闭环、自建兼容和再导入后二次删除。模拟远端与真实 A100 分开报告。
- 使用专属 Compose 项目/临时卷、生成数据和隔离路径。记录版本、迁移 head、退出码、期望/实际、状态链、目标/保留摘要、SQL 与进程身份。
- 结果 `test-receipts/NC-06/attempt-N.md`，状态 TEST_REPORT_PENDING；只报告问题，不跑 OCR、不合入。无匹配样本/工具明确 NOT_RUN。

### NC-07：审查与收口

- 依赖 NC-06。协调者核对固定 SHA 自测/独立证据/OCR覆盖；必要强审查默认由用户手动触发一次功能批次包；有效自定义时间/任务授权内可由协调者通过统一脚本限额调用Codex，重点是删除归属、writer 互斥、批次重放/新代次三个已有 AC，作用门禁为真实删除准入。
- 输出 `reviews/NC-07/` 的完整代码定位、diff、AC 映射、反例、运行证据和待裁决问题。强审查不得扩展功能或凭旧审查 PASS 覆盖新代码。
- 原问题违反 AC 才最小返修；验证缺口只补必要证据；范围外建议 DEFERRED。同根因两轮未解决升级。无论人工或授权内调用，未获有效审查结论时如实留待审，不记 DONE。

### NC-08：授权 test 根真实验收

- 依赖 NC-07，加用户明确授权远端测试、真实 test 代理/helper 版本及测试根；当前 WAITING_AUTH。
- 生成至少两个互不干扰 Chunk、两个专属 run、共享/NAS 哨兵；真实 SSH 删除、故障恢复、writer 阻断、显式重导入后二次清理。不得复用存量数据或 production `/data/nvidia_*`。
- 输出 `test-receipts/NC-08/attempt-N.md`，记录实际目录/版本/进程/摘要、退出码；没有真实执行不能报 A100 通过。完成后向协调者交证据，不自行生产发布。

### NC-09：发布与本地收敛

- 依赖 NC-08，另需用户当次生产更新授权；当前 WAITING_AUTH。
- 核验 MySQL timer/可校验备份、隔离迁移回归、在途任务与旧 helper 兼容、关闭/恢复方案、批准配置，不影响已有任务；生产使用 `deploy_processing_machine.sh --apply --production`。
- 新 helper/worker/backend 能力齐全后才开 NVIDIA 开关；生产检查页面/API/版本和自建冒烟。发布后同工作区 `local_stack.sh up`、`local_stack.sh test`，生成部署快照，分别记录生产/本地结果。
- 如需验证生产真删由用户在页面确认精确计划；Agent 不代点。功能日志只生成 pending，用户批准后按实际发布记录，不能由文档 DESIGN_READY 自动发布。

## 5. 串行资源与结束

迁移链、集成 Compose/MySQL、A100 测试 writer fixture 和 OCR 各自串行；三个代码槽不等于三个同时迁移/删除槽。原场景专项共享资源仍占用时本专项排队，禁止另建锁绕过。

本轮文档结束后停止实施。后续 NC-06/07 满足本地开发收口可提交结果；NC-08/09 不自动解除授权门禁。NC-D01 不因空闲或“顺手”实施。
