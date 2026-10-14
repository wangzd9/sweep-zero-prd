# NVIDIA 删除扩展规划交接

## 2026-10-10：NC-v1 设计交付

- **交付：DESIGN_READY，文档可供后续开发；实现未开始。** 用户本次指定规划者，要求把删除能力扩展到 NVIDIA 数据集，已加载 `complex-task-planner`。
- 唯一新共享根：`/home/wang/work/doc/prd/rosbag-catalog-nvidia-cleanup`；入口 [SESSION-START](SESSION-START.md)，状态唯一来源 [TODO](TODO.md)，契约 [DESIGN](DESIGN.md)。本目录独立于上级正在运行的场景任务；没有修改其 TODO/租约/角色/cron。
- 最小链路：单 Chunk 预览/确认→A100 origin/infer/全部专属 run 清理→数据库事务→列表移除，保留 NAS/共享缓存/同批其他 Chunk，批次历史准确显示已清理。
- 关键新增：NVIDIA 独立开关、类型根矩阵、真实 owner/覆盖验证、Backend 提交围栏、远端 writer 锁前零业务写入、批次持久条目、旧键/旧批次阻断复活、新源代次及二次删除。
- 采用兼容范围为单行“数据库+A100”，保留 NAS；这是规划采用的默认边界，不冒充用户逐项确认。若用户要求整批或 NAS 一并删除，先修订需求和安全契约，不能沿本稿自动扩范围。

## 事实、风险与未验证项

- catalog 调查 HEAD：`74ba3bfa5d75d87db5f38ba83a65d8b9f888da38`，main。已有用户未跟踪诊断文件/数据库/公钥保持原样，未纳入文档或提交。
- NVIDIA 脚本本地 HEAD `52f65d1920e07a8d5ce5a92d5ae5fe14b9492147` 与当前批准配置 `code_revision=95f4ff65aa7f8e0e15047dcb6c9809891e15ecc3` 不同。未连接 A100，不能声称源码/现场版本相同；默认在 catalog launcher 外包锁，避免改业务脚本。
- 当前源码仅自建清理；NVIDIA create 未接围栏、launcher 未接 Bag writer 锁、批次缺 CLEANED 条目依据。详细证据符号见 DESIGN §1，历史测试数量不作为新能力证据。
- 旧删除专项的生产未开放描述已过时；catalog HANDOFF 记录 2026-10-08 自建清理成功。本轮未核验生产新状态，不修改旧历史、不把旧审查结果转为本专项通过。
- 待验证前提：存量 Chunk owner/manifest 完整性、历史 run/批次映射、实际批准脚本行为、A100 helper/锁根配置、test 根授权和资源空闲情况。这些影响对应清理操作/真实验收；不阻止本次文档交付。

## 接续与授权

- 首波候选 A=NC-01、B=NC-02、C=NC-03，三项接受后接 NC-04→NC-05→TESTER NC-06；按 TODO 完成事件重算，不等待无关整波。角色/群/cron **未绑定**，当前无派单，无业务进程。
- 用户本轮只授权调查和设计文档。开发、测试栈写入、远端真删、生产更新分别由后续明确任务启动；本稿不批准启动已确认之外的动作。
- 开发时协调者单写主文档、派单/合入，开发者独立 worktree；迁移链与既有场景专项协调，OCR串行共用锁；必要强审查在功能开发+常规测试之后由用户手动触发一包，只核对冻结 AC。
- 后续真实 test 根验收与生产发布保持 WAITING_AUTH；生产 Agent 不代用户确认删除。账号连接元数据只引用仓库外 `doc/password/rosbag-catalog-connections.md`，文档不记录秘密。

## 验证与沉淀

本轮适用验证是文档链接、JSON、REQ/AC/task 映射、DAG/owner/角色入口一致性和新增文档空白检查，具体结果见 [VALIDATION](VALIDATION.md)。未跑业务 pytest/MySQL/浏览器，未连接处理机/A100，未调用 OCR/模型，未部署或删除数据。

本目录在仓库外 `doc/` 中，父目录不是 Git 仓库，未建立业务代码 commit 或推送。可复用性检查：既有 planner Skill 覆盖本次规划；此为尚未实施验证的功能设计，不另建重复 Skill。

## 自动审查授权与开发日志规则（2026-10-12T11:11:58+08:00）

- 用户新增要求：支持自行指定时间段或本次任务完成前的审查授权，协调者可在有效授权内通过Codex调用审查者；全局滚动60分钟最多5次，周期报告说明授权/调用；根据实质进展更新开发日志。
- 入口 /home/wang/.codex/skills/complex-task-coordinator/scripts/strong_review.py；详细规则 /home/wang/.codex/skills/complex-task-coordinator/references/review-authorization.md。没有有效授权默认人工；同一消息不续期，换授权不重置额度，失败/超时/复审计入，结果仍由协调者核对原AC并裁决。
- development_log=DEVELOPMENT-LOG.md；交付/验证/审查/合入/阻塞/里程碑更新，正式功能日志依现有规则仅生成pending候选。
- 本次不创建实际授权、不发起付费调用、不重置任务/分支/旧证据；NVIDIA角色/cron仍未绑定，删除与生产门禁不变。后台在途工作不重启，后续回合加载新规则。
- 备份 /home/wang/.codex/skill-migrations/review-authorization-20261012-104349。

- 2026-10-12T11:21:40+08:00 本次配置验证完成：15项离线测试通过（假Codex进程，真实Git固定快照），4个Skill结构校验、Hermes加载/协调者cron注入、15个本地Skill链接与角色/任务/周期保留检查通过；两个项目的真实只读status可执行且不创建授权账本。证据 /home/wang/.codex/skill-migrations/review-authorization-20261012-104349/verification.json。未创建实际授权、未调用真实付费模型；真实新入口审查待用户明确授权后验收。

## 动态拆分与日志节点澄清（2026-10-12T12:13:42+08:00）

- 协调者Skill和规划者Skill升级至1.2.1：已授权原REQ/AC及既定契约内，协调者主动细化粗任务、先同步父子/依赖/卡片，再按实际可接角色补位，最多三路；在途先确认检查点交接，关键契约/范围变化升级。不能并行时明确原因和解除条件，不为满槽增加任务。
- 开发日志随实质事件更新；正式日志在功能完成且有验证证据后生成/合并pending并更新REVIEW.md，用户明确批准后approved，实际发布成功后released和公开页面。协调者组织测试者补证，不代日常测试或自行批准日志。
- 本轮仅更新协作规则、恢复入口及协调者cron提示；没有拆分/重派实际业务任务，不改变TODO、角色绑定、开发分支或既有门禁。NVIDIA专项仍未绑定/未启动；新规则由后续调度回合按最新状态应用。
- 备份：/home/wang/.codex/skill-migrations/dynamic-decomposition-20261012-120520。文档与Hermes加载验证结果将在本次完成后记录。

- 2026-10-12T12:24:09+08:00 本次规则/配置验证完成：协调者和规划者Skill结构校验通过，Hermes从唯一维护源加载1.2.1及拆分参考通过，两个协调者cron组装/注入/提示安全检查通过，11个本地Skill链接有效。两个项目TODO与角色绑定、所有cron调度/投递/其他角色提示保持。证据：/home/wang/.codex/skill-migrations/dynamic-decomposition-20261012-120520/verification.json。未进行真实角色运行、实际业务拆分或付费调用；后续调度/交接行为需由真实回合取证。

## 2026-10-12T18:34:01+08:00 空闲汇报调整

- 执行者/测试者有任务20分钟，确认无任务2小时一行无模型短报；协调者20分钟、五分钟巡检和即时事件保持。Skill与report gate已配置，12项隔离测试通过；实际新周期投递尚待观察。
- 主专项已配置四条no_agent空闲报告，原群/origin与有任务报告周期保持；未绑定专项不创建cron。未改业务状态、任务编号/分支、在途开发/测试或模型服务。备份：/home/wang/.codex/skill-migrations/idle-report-20261012-174657。

- 2026-10-12T18:44:40+08:00 空闲汇报配置验证完成：12项隔离路由验证、5个Skill结构/Hermes加载、四角色脚本输出及cron提示组装/原群投递配置核对通过；采样时A/C/TESTER确认空闲会跳过20分钟模型报告，B保持正常报告。验证 /home/wang/.codex/skill-migrations/idle-report-20261012-174657/verification.json；排队分析 /home/wang/work/doc/analysis/hermes-qwen-load-20261012/REPORT.md。未主动投递消息、调用模型或改服务器并发；新周期真实投递及持续性能收益待观察。并发会话追加的v0.4规划保留。
