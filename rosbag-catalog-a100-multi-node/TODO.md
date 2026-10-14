# A100 双节点纳管任务单

> 场景v0.4补充：本表MN任务只纳管自建/NVIDIA；主线TASK-16的处理机执行和基础界面不等待MN。场景仅调用共享远端模型，不领取A/B执行/存储槽。MN状态/owner/依赖保持本表，主线状态只读 [上级TODO §8](/home/wang/work/doc/prd/rosbag-catalog-integration/TODO.md#8-v04-最小闭环补齐规划2026-10-12)。

版本：MN-v1，2026-10-12。**唯一业务任务状态源**。
文档 DESIGN_READY；本次仅规划文档授权。所有开发任务未派发、未 ACK、未开工、未验收，不把下表推荐角色当实际 owner。

## 1. 状态和派单基线

PLANNED → READY → IN_PROGRESS → REVIEW_PENDING / TEST_REPORT_PENDING → DONE；失败/缺输入为 BLOCKED，后续远端阶段 WAITING_AUTH，范围外 DEFERRED。

调查 catalog base：`502bf8ec79690cf01e130cb0591121eb10e96af5`，主分支 main；脚本调查 base 见 [HANDOFF](HANDOFF.md)。协调者在后续实施授权、文件/资源冲突核查及绑定完成后冻结实际派单 base，不能直接用可能已变动的调查版。开发者自己从该 base 建 `feat/a100-multi-node/<task>-<attempt>` 分支/worktree；TESTER 使用独立固定快照。

源需求/验收唯一契约为 MN-v1；本专项与上级 TASK-、NVIDIA 删除 NC-、旧清理 T-/C- 独立，不复制其状态或借用其已授权阶段。

## 2. 完整依赖与验收映射

| task | 产物 / 推荐角色 | 硬依赖 | REQ / AC 尾号 | 当前状态 |
|---|---|---|---|---|
| MN-01 | 节点配置、模型迁移、历史解析基础 / 开发者1（角色 A） | 无 | 01、03、04、08、09 | PLANNED |
| MN-02 | 代理多实例、批准根、探测及部署模板 / 开发者2（角色 B） | 无 | 01、03、06、08 | PLANNED |
| MN-03 | 节点路径、访问及清理纯契约适配 / 开发者3（角色 C） | 无 | 04、05、07、09 | PLANNED |
| MN-04 | 原子分配、占用、预算、队列接线 / 开发者1 | MN-01、MN-02 | 02、03、04、06、08、09 | PLANNED |
| MN-05 | 两路线、恢复、帧读取及 NAS 回传接线 / 开发者2 | MN-03、MN-04 | 01、02、04、05、06、08 | PLANNED |
| MN-06 | 查询页面及实际清理入口接线 / 开发者3 | MN-03、MN-05 | 07、09 | PLANNED |
| MN-07 | 固定集成候选独立综合验证 / TESTER | MN-05、MN-06 | 01～10，本地部分 | PLANNED |
| MN-08 | 功能批次审查、纠错收口与真实交接包 / COORDINATOR | MN-07 | 10，核对01～09 | PLANNED |
| MN-09 | 预算校准、B 环境准备及 test 根真实验收 / 后续派单 | MN-08 | 01、03、05、06、08、10真实部分 | WAITING_AUTH |
| MN-10 | 生产迁移、启用、本地收敛与回滚检查 / 后续派单 | MN-09 | 09、10生产部分 | WAITING_AUTH |
| MN-D01 | 历史迁移、运行中切换、自动复制、GPU调度、动态预算及管理平台 | 不进入本期 DAG | 无 | DEFERRED |

REQ/AC 完整前缀分别为 MN-REQ-/MN-AC-；定义见 [PRD](PRD.md) 和 [ACCEPTANCE](ACCEPTANCE.md)。MN-08 是聚合收口，不重复派一套实现；MN-09/10 必须单独满足环境及授权，不因依赖齐全自动执行。

## 3. 三槽首波、接续和共享 owner

本表的 A/B/C 是开发角色，**不是执行服务器 A/B**。首波只能在后续有效实施派单后开启。

| 开发槽 | 首波 | 后续候选 |
|---|---|---|
| 角色 A | MN-01 | MN-01/02 接受后 MN-04；不等待无关 MN-03。 |
| 角色 B | MN-02 | MN-03/04 接受后 MN-05。 |
| 角色 C | MN-03 | MN-05 接受后 MN-06。 |
| TESTER独立槽 | 固定子候选的关键风险核验可按派单先做 | MN-05/06 同快照可用后 MN-07。 |

首波边界：MN-01 单写 models、迁移、平台 config、node_profiles、公共字段定义和历史定位助手；MN-02 单写代理、environment_contract、代理部署模板及自己的 tests；MN-03 只写新增节点路径/清理契约纯模块及自己的 tests，不提前改公共 schema 或清理事务。MN-02/03 可按 DESIGN 的明确契约用替身验证，不在供应方未接受时报告联调通过。

后续 models/迁移始终由角色 A 单写；代理及 self_built/nvidia_pipeline 由角色 B 单写。MN-06 接受公共 schema 的单写交接后才扩查询序列化；如需改源围栏等 MN-04 文件，协调者先记录交接检查点并确认原 owner 空闲。共享迁移链、路由装配、平台配置不并写。测试栈、MySQL迁移、真实模型、NAS发布及远端安装均单独登记资源 owner，开发三槽不代表资源三并发。

| 完成事件 | 重算候选与限制 |
|---|---|
| MN-01 ACCEPTED | 检查 MN-02；两项齐全可派 MN-04。 |
| MN-02 ACCEPTED | 检查 MN-01；不因 MN-03 尚未结束延误 MN-04。 |
| MN-03 ACCEPTED | 检查 MN-04；齐全才派 MN-05。 |
| MN-04 ACCEPTED | 供应契约进入 base；检查 MN-03，派 MN-05。 |
| MN-05 ACCEPTED | 派 MN-06；TESTER可核验固定链路子候选，不能提前宣称全套通过。 |
| MN-06 ACCEPTED | 冻结含 MN-01～06 的集成候选，派 MN-07。 |
| MN-07 报告接受 | 进入 MN-08 原 AC 审查/收口，失败按问题ID回原 owner。 |
| MN-08 收口 | 准备 MN-09 安装/校准包，仍等明确授权及预算/测试根输入。 |
| MN-09 接受 | 准备 MN-10 备份/在途兼容/回滚包，继续等生产授权。 |
| 契约变化或证据失效 | 撤回受影响验收并暂停相关消费者，保留无关已接受结果；不整体重启。 |

## 4. 任务卡公共要求

每次派单填入 task/attempt、实际 owner、固定 base、worktree、MN-v1 版本和授权阶段；目前这些运行字段均未绑定。全部任务为叶任务，MN-08为收口聚合。首次领取创建 ACK/回执，不为规划预造空派单。

最小公共阅读：本专项 PRD、DESIGN、ACCEPTANCE、HANDOFF、项目 AGENTS/LLM_DEVELOPMENT_RULES 及相关仓库外 V1 TODO。回执 `receipts/<task>/attempt-N.md` 记录 commit、允许文件、命令/退出码、AC证据、失败恢复、未执行项、契约变更建议和接续候选；开发者不更新共享 TODO。

开发自测须覆盖允许实现风险与适用静态检查；每个代码类 commit 的 OCR 由协调者串行组织，按非文档文件职责拆批，默认每批 ≤12。强审查默认人工，在已完成批次后核对原 AC，不设置逐任务付费门禁。发现身份/根/幂等/状态契约需变化、触及未授权生产或共享文件冲突时停止受影响动作并升级，继续独立可行工作。

### MN-01：节点与历史定位基础

- REQ/AC：01、03、04、08、09；依赖无；接受后候选 MN-04。
- 输入/最小阅读：DESIGN §2～3、models/config、nvidia_configs、source_copy_identity_key、迁移链和历史 run/copy/artifact 查询。
- 允许文件：`app/models.py`、`app/config.py`、拟新增 `app/node_profiles.py` / `app/services/node_history_service.py`、公共 schema 字段、一个 additive Alembic revision及配套 tests。不得改代理、orchestrator、清理事务或正式配置。
- 产物：A/B profile 严格校验；BIGINT预算/占用字段及索引；历史 A 与 NAS/local 分离；未启动/未知启动的明确盘点结果；副本旧键兼容接口。首期不重写历史帧、不建节点管理数据库。
- 自测/独立场景：缺预算仍可查询恢复、错根/环境/盘、历史 A/NULL/B、同源冲突、旧回调幂等、隔离 MySQL upgrade及 B 依赖存在时 downgrade 拒绝。提交 SQL/计数和解析证据。
- 停止：生产迁移/回填未授权不执行；迁移 head 已变先重新冻结 down_revision；不伪造生产并发配置。

### MN-02：双代理和探测

- REQ/AC：01、03、06、08；依赖无；接受后候选 MN-04。
- 输入/最小阅读：DESIGN §1～2/4～5、a100_host_proxy、lib/environment_contract、remote_execution、proxy_recovery及systemd模板。
- 允许文件：上述代理/环境/恢复/连接助手、`deploy/systemd/` 模板及本地测试配置模板和对应 tests。不改 models、平台 config/node_profiles 或业务服务；消费 MN-01 契约用替身，不抢配置 owner。
- 产物：按节点实例验证身份、独立状态和锁根；批准路径 profile 化；真实远端容量/写权限/文件系统探测；未知远端进程对账证据；A既有入口兼容和 B安装清单。
- 自测/独立场景：同名 run 状态不串节点、节点/环境不匹配零写入、SSH不可达、错挂载、容量样本、孤儿状态和旧恢复文件。探测有界，不能只返回进程 ok。
- 停止：不在 B 创建目录、安装依赖、复制密钥或更新 systemd；B尚未核验的运行路径明确待确认。

### MN-03：节点路径与清理纯契约

- REQ/AC：04、05、07、09；依赖无；接受后候选 MN-05、MN-06。
- 输入/最小阅读：DESIGN §3/7、artifact/frame/source 服务、现有 cleanup plan与worker、NC设计及实际功能基线。
- 允许文件：拟新增 `app/services/node_path_service.py` / `app/services/node_cleanup_contract.py` 和其 tests。不改 models/schema、现有 plan/cleanup事务、worker/executor 或UI。
- 产物：run/artifact节点定位与不一致拒绝；NAS/local语义；节点＋路径比较；节点化计划digest/能力版本输入契约与旧A兼容解析。纯模块不执行SSH、不删文件。
- 自测/独立场景：A/B同路径、new缺节点、legacyA、NAS/local、帧节点矛盾、未知根、签名字段变化、旧无节点plan只允许A原范围。
- 停止：NC若尚未实施只交契约适配，不把实现NC全功能扩入本期；实际协议不一致提交最小设计修订。

### MN-04：分配、预留和队列

- REQ/AC：02、03、04、06、08、09；依赖 MN-01/02 接受且进入 base；接续 MN-05。
- 输入/最小阅读：DESIGN §4～5、供应回执、resource_service、pipeline_service、source_fence、api/resources/pipelines、orchestrator、公共schema。
- 允许文件：拟新增 `app/services/node_allocation_service.py`，上述资源/任务/围栏/API/调度/schema接线及tests；models/迁移只由原owner最小修订。不改代理及算法脚本。
- 产物：allocate-node API、HELD/UNKNOWN持久计数、真实槽空洞分配、预算/revision事务、源归属锁、过期lease兼容和非阻塞release-claim；新托管A100任务不能绕过准入。
- 自测/独立场景：隔离MySQL多进程同节点/同源争用、flush后回滚、commit响应丢失、revision旧样本、旧attempt/TTL、缺预算、A满B可派、模型全局pool不复制。不能用threading.Lock替代数据库原子性证据。
- 停止：源围栏/新节点可绕过历史墓碑、迁移或锁顺序冲突时升级，不新造长SSH事务。

### MN-05：两路线完整接线

- REQ/AC：01、02、04、05、06、08；依赖 MN-03/04；接续 MN-06。
- 输入/最小阅读：DESIGN §5～6、所有供应回执、自建/NVIDIA流水线、代理依赖、nvidia_service/config、nas_publisher/frame_importer。
- 允许文件：`scripts/a100_host_proxy.py`、`self_built_pipeline.py`、`nvidia_pipeline.py`、`nas_publisher.py`、proxy_backend/恢复助手、`app/services/nvidia_service.py`、`app/nvidia_configs.py`、必要帧导入接线及tests。公共装配/schema变更先接owner交接，不新增迁移。
- 产物：冻结节点贯穿上传/下载/launch/read/manifest/frame/回传；NVIDIA未分配不误认A输入；执行快照与业务revision分离；模型/NAS许可共享；原节点重试及UNKNOWN对账。
- 自测/独立场景：A/B×两路线本地闭环、路径记录逐步一致、质量/帧/发布完整、SKIPPED按配置、上传后校验才清Phase0副本、超时不双启动。
- 停止：本期不改Phase0算法、不自动提交其他脚本仓库代码或更新远端checkout；脚本路径确有阻碍先提交跨仓最小修订。

### MN-06：页面、访问和清理接线

- REQ/AC：07、09；依赖 MN-03/05；接续 MN-07。
- 输入/最小阅读：DESIGN §7、纯模块/流水线回执、web/templates/source/artifact/frame、cleanup_service/plan/worker/executor、现有NC能力版本。
- 允许文件：查询和web相关服务/API/模板/JS、cleanup计划/服务/worker/executor与tests；responses等公共schema先由协调者记录MN-04/05后的单写交接。不得改models/迁移或在途代理。
- 产物：节点展示和访问正确；节点纳入计划/digest/确认/能力和物理围栏；旧A计划不改写，新B计划旧helper拒绝；原节点清理恢复及保留范围一致。
- 自测/独立场景：浏览器/API、节点/根签名篡改、跨节点同路径保护、源所有run覆盖、UNKNOWN不当ABSENT、历史A回归；NVIDIA删除按实际已接受能力验证，未实施增量列条件证据。
- 停止：不扩成跨节点批量删除，不更改已确认目标；生产删除及新NC功能未授权不执行。

### MN-07：独立综合验证

- REQ/AC：01～10本地部分；依赖MN-05/06；接续MN-08。固定候选须包含MN-01～06，TESTER在独立工作区取证。
- 输入：[ACCEPTANCE](ACCEPTANCE.md)、开发回执、commit/profile清单；允许范围为 `test-receipts/MN-07/`、`reports/MN-07/`、sessions/TESTER及自身events，不改业务实现。
- 产物：隔离MySQL真实事务、占用与恢复、两路线替身闭环、页面/API、清理兼容的逐AC判定，区别mock/实物/未执行；回执 `test-receipts/MN-07/attempt-N.md`。
- 停止：候选变化/缺供应提交/共享测试栈被占用则报告阻断；不自行创建新开发标准、不跑OCR、不真删生产数据。

### MN-08：审查与开发收口

- REQ/AC：10及原01～09证据；依赖MN-07接受；接续MN-09仍需授权。
- COORDINATOR核对真实代码和回执、串行OCR并按原AC准备人工强审查包；仅有有效用户审查授权才经统一脚本自动调用，滚动60分钟最多5次。记录原话/期限、次数/在途、结果及未知费用，不假称授权。
- 允许写本专项共享文档、reviews/decision/回执汇总，不代开发或日常测试。问题以ID最小回派，独立验证补原AC；范围外建议不增加门槛。
- 产物：固定批次、证据索引、每项问题判定、接受/合入记录、MN-09具体安装/校准输入。纯文档状态不冒充已接入。

### MN-09：真实节点准备与预算校准

- REQ/AC：01、03、05、06、08、10真实部分；依赖MN-08；WAITING_AUTH，非当前允许动作。
- 输入：明确只读或测试根写入授权、安装清单、实际端口/状态/锁根/SSH key引用、脚本/helper revision、A/B各自test根、NAS test根、代表性源和模型额度。
- 拆成可验收子步骤：只读现状和已有任务占用证据 → 授权B环境/专属Git准备 → 两路线峰值/预算记录 → 两节点测试根闭环及故障恢复。预算未填写不启用新任务；不会自行选100/200GiB等默认值。
- 产物：真实证据、运维批准的bytes配置及覆盖输入范围、两节点目录/身份/模型/NAS核验；回执 `test-receipts/MN-09/attempt-N.md`。
- 停止：不得把过去只读SSH授权扩大为安装/远端目录写入；不借test名写生产、共享模型/缓存或NAS原始内容。

### MN-10：生产启用与本地收敛

- REQ/AC：09/10生产部分；依赖MN-09；WAITING_AUTH。协调者派具体发布操作，只有当前任务明确生产授权且项目规定 `--apply --production` 才执行。
- 输入：MySQL备份timer及可校验双副本、冻结候选和profile、旧在途占用接管/空闲证据、旧清理计划兼容、冲突及回滚检查表。
- 产物：迁移/代理/容器/业务各层实测、生产单样本与既有A回归、本地相同或更新版本的 `local_stack.sh up/test`；生成部署快照不手改。实际发布后才处理released功能日志。
- 停止：存在B绑定数据禁止回退到A-only版本或删节点字段；生产成功而本地失败必须分别报告并继续收敛，不能报完整闭环。

## 5. 收口与剩余前提

本次文档检查通过后停止，五角色未绑定，不自动创建派单/cron。后续协调者重新确认主分支与其他在途专项；只在授权、依赖齐全、证据有效、无文件/资源冲突且角色可接时从本表派单。代表性预算数值、B运行依赖、处理机到B专用SSH身份和真实端口/锁根仍是MN-09前提，不阻止本地契约开发，也不伪称生产准备完成。
