# 水雾 v0.5 文档校验记录

2026-10-13，状态DESIGN_READY仅表示规划可接续开发；本轮优先水雾后端链路与原始信息，UI增量暂停。校验只覆盖文档与授权Git拉取，业务/质量/生产验收见 [ACCEPTANCE](ACCEPTANCE.md)、[SPRAY-RELEASE](SPRAY-RELEASE.md)，实际状态唯一见 [TODO §9](TODO.md#9-v05-水雾优先与生产接入2026-10-13)。

## 当前校验范围和证据

一次性校验脚本及结果在`/tmp/rosbag-scene-v05-audit/validate_docs.py`、`verification.json`，临时文件不属于业务实现或永久测试。实测2026-10-13T11:43:08.114708+08:00，12项检查全部PASS（63个改动链接/锚点、21张契约表、实际水雾依赖图、需求映射与历史/资产/差异核对）；这是文档检查结果，不能当作业务或生产PASS。

- 检查当前改动链接/锚点、契约表列数、REQ-17/18/19→AC→12S-A/B/C/D/11S映射及实际任务表无环依赖；UI不在水雾前置图。
- 核对角色绑定/协议、旧任务记录与外部HANDOFF历史保留；协调者在规划期间新增状态/派单不回滚、不当作本轮规划者执行。
- GitLab算法仓库197645e→be23177快进，只新增7张JPEG，算法代码未改；永久顺序/hash/尺寸清单为 [SPRAY-REFERENCES.json](SPRAY-REFERENCES.json)。本地缺图阻塞解除，生产安装仍未验收。
- 修正mapping_basis为代码接受的bag_storage_ns、去除重复带宽段、补充独立元数据hash/幂等冲突规则。7图Base64约20.25MB/pass，发布预算必须包含双pass及重试；500KiB与源代码bytes/1024过滤一致。
- 仓库提交只纳入本次规则/文档及自己的HANDOFF前缀；既有OCR/devflow/用户HANDOFF改动和未跟踪文件不纳入。共享根不在Git内，文档提交不代表整个外部包已推送。

本轮未业务开发、pytest/OCR/模型调用、生产SSH/数据库/NAS写入、Docker生命周期或角色启动；仅按用户指令拉取算法GitLab源码。新spray/profile/元数据接线、16B恢复缺陷收口、真实车辆/质量标注、处理机依赖与生产门禁仍由后续任务取证；不宣称今天已能上线。复用已有规划Skill，未创建无运行证据的新运维Skill或功能released日志。

## 当前提交与同步结果

2026-10-13规划交付收尾：12项文档检查PASS（最新检查2026-10-13T11:43:58.648168+08:00，63个链接/锚点、21张契约表、实际依赖/历史/参考图核对）；catalog纯文档提交`21673dae812cc94e2dd6807d579772ccac931ce1`（9份Markdown，+38），已推送`github/main`，远端与本地tip相同。仅提交自己的HANDOFF前缀，既有OCR/devflow/用户HANDOFF和未跟踪文件保留；外部共享包在Git外，本次没有业务实现/模型调用/生产部署。

## 历史 v0.4 校验（原文保留，UI优先级已由v0.5覆盖）

# 场景 v0.4 文档校验记录

状态：**DESIGN_READY / 文档检查 PASS**。检查对象为本轮场景目录隔离、处理机执行与基础界面规划，不是业务实现或生产验收。

需求和验收见 [PRD](PRD.md)、[ACCEPTANCE](ACCEPTANCE.md)，唯一任务状态见 [TODO §8](TODO.md#8-v04-最小闭环补齐规划2026-10-12)，开发恢复入口见 [SESSION-START](SESSION-START.md)。

## 1. 范围与实际校验

2026-10-12T19:22:55+08:00 执行一次性本地文档检查，退出码 0，11 项全部通过。脚本及 JSON 证据保存在 `/tmp/rosbag-catalog-v04-planning-audit/validate_docs.py` 和同目录 `verification.json`；临时证据不属于运行程序或永久业务测试。交付收尾再次检查结果以该 JSON 的 checked_at 为准。

| 检查 | 结果与边界 |
|---|---|
| 文档链接和锚点 | 新增/改动行的本地链接及新增文件链接有效；首次检查 66 个目标，无缺文件/标题。不追溯改写历史回执或旧巡检链接。 |
| 表格 | PRD/DESIGN/ACCEPTANCE 及 TODO §8 共16张契约表列数一致；旧 TODO 长历史区保留，不借本轮重排其记录。 |
| 需求→验收→任务 | REQ/AC-14→16A、15→16B、16→16C；16D覆盖新增验收及05/06/07/08/09必要回归，父16只聚合。 |
| 依赖与供应顺序 | 从实际TASK-16表提取的硬依赖与图一致，引用存在且无环。16B模块自测可先行，最终接线消费16A接受产物；16D等待16A/B/C全接受且合入固定SHA。 |
| 首波、共享文件和资源 | 建议A→16A、C→16B、B经07B检查点交接→16C；未释放时只有两个候选槽。配置/models/迁移由16A、执行/回报由16B、页面/集合路由由16C单写，TESTER独立取证。实际派单由协调者登记。 |
| 历史保留 | 与修订前备份逐字比较，TODO §1状态正文完全一致；原HANDOFF全文在当前文档中连续保留。旧07B派单、角色绑定、cron、审查授权与生产门禁未由本轮重置。 |
| 仓库差异 | `git diff --check`通过；仓库变更限定9份Markdown规则/入口/接入/架构/状态/生产清单文档，业务代码、运行配置和生成部署快照无本轮改动。未跟踪数据库、凭据文件及用户脚本不纳入提交。 |

需求和任务映射、文件owner、三槽接续及本轮停止点还经人工复核；机械检查不能替代业务验收。A100专项只补当前适用范围，原MN-v1验证时间和SHA明确标为历史快照，没有以旧摘要冒充修改后文件。

## 2. 本轮纠正及冻结结果

- 场景输入使用 `/public/rosbag_scene_processing/{incoming,ready,slices}`，测试使用 `/test/scene/{incoming,ready,slices}`；单Scanner双根及Backend共同校验，异常不默认触发自建。显式双用途兼容仍依据有效冻结用途，AC-14不再写成一律禁止自建。
- 场景非模型处理全部在处理机，正式本机代理尚待实现；远端仅收必要帧/参数。保留同一模型/NAS许可池，处理机工作盘到NAS先复制校验再同盘发布，不要求跨盘rename。
- 页面属于本轮最小闭环：场景八步真实详情；“切片、原始数据、全部”，原始数据覆盖自建、英伟达及场景输入，Web/API共享类型谓词。修正16C集合路由笔误为 `GET /api/v1/bags`，API字段及新profile示例同步目标契约。
- 修正上一版UI后置、已实现能力误写未实现、空缺任务状态列和无依据禁止显式双用途；旧TASK-10的API工程证据不替代本轮代理/目录/页面联合验收。

本地源码复核基线为catalog main `30e55a3`，证据定位：`ingest_service.match_profile_for_incoming`单根匹配、`source_service`未匹配Phase0分支、`bag_search_service` originals谓词、`app/web/pipelines.py`和`pipeline_detail.html`旧阶段展示、Orchestrator场景派发、现有`scene_result_query`及API路由列表、`scripts/`代理清单。未找到正式scene_host_proxy属于当前仓库事实，不据此断言其他主机现场无服务。

## 3. 未执行与交付边界

本轮没有业务开发、pytest/OCR、数据库迁移、Docker生命周期、SSH/远端操作、真实模型请求、NAS生产目录创建或处理机部署。用户本轮授权为文档修订；未来测试取证按ACCEPTANCE，由16D验证正式代理真实单包及浏览器/API，生产启用仍走TASK-11独立授权。状态DESIGN_READY只表示可接续开发。

可复用性检查：现有complex-task-planner已覆盖本次规划流程；新执行拓扑尚无运行证据，不新增运维Skill或正式released功能日志。后续实现owner按任务同步对应Skill与实际能力记录。

共享根位于Git仓库外。仓库commit只包含可追踪规则与文档入口，不代表外部PRD/DESIGN/TODO文档包已推送。提交和推送结果在收尾后追加于下一节。

## 4. 仓库文档提交

仓库 `/home/wang/work/rosbag-catalog` 文档提交 `c2018ddf01ebfb4d319706d79e3c0c5285b60c0a`（9份Markdown，+43/-2），提交前普通/暂存 `git diff --check`均通过。已执行 `git fetch github main`核对原tip=`30e55a3`，当前分支main待推送仅本次文档commit；`git push -u github main`退出码0，GitHub main从30e55a3推进至c2018dd。未推送GitLab origin或仓库外文档，未纳入任何用户未跟踪文件。
