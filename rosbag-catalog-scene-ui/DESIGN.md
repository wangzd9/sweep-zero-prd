# 场景最小界面闭环技术设计

需求包：`rosbag-catalog-scene-ui`。本次整理仅迁移文档内容归属，不更新实现、验收、部署、授权或任务状态。REQ/AC/TASK沿用原编号，不因拆包重新编号或重新派发。

当前任务状态、派单与角色运行仍由[原唯一TODO](../rosbag-catalog-integration/TODO.md)、[现行启动入口](../rosbag-catalog-integration/SESSION-START.md)和原绑定维护；本包[TODO](TODO.md)只导航，不建立第二份可写任务状态。历史混合正文保留在[整理前归档](../rosbag-catalog-integration/archive/pre-reorganization-20261014/)，其中暂停、待发布等旧描述不作为当前执行指令。

## 1. 依赖与公共契约

公共身份、配置冻结、结果/运行状态、current/发布、根隔离、处理机/模型边界唯一正文见[基础DESIGN](../rosbag-catalog-scene-foundation/DESIGN.md)。本包只定义查询分类、Web/API一致性、页面与动作呈现；继承基础API的限额、排序、cursor筛选上下文及错误类别，不复制状态机或发布算法。

基础依赖为原16A/16B、结果查询/血缘和原07A/07B的已接受产物，实际固定SHA与接受证据从原TODO/派单核对。水雾资料与算法规则归水雾包，不作为UI重新识别前置。

## 7. 服务接口与客户端（界面归属）

### 7.2 页面与写接口

以下保留原TASK-07接口契约，不是本次额外新增实现派单；实际接受与启用范围仍核原任务证据。

新增 PATCH /api/v1/bags/{uid}/scene-labels 和 POST /api/v1/bags/{uid}/withdraw，带 row_version、原因、幂等键与可验证操作者证据；保留原始模型结果。P0 保存标签来源，P1 提供纠错界面和相应接口，不新增匿名可用写入口。

`/bags?view=slices|originals|all` 已存在；v0.4 最小闭环修正其标签和语义，详见下一节。`slices` 仅当前版本 AVAILABLE；`originals` 覆盖三类原始数据；`all` 包含原始、切片、历史及其他条目。旧 dataset_type 书签无 view 时仍按兼容规则进入可见结果。人工写接口按原TASK-07既有接受证据核对；预览仍按原阶段门后置，不替代本轮页面修正。

### 7.3 v0.4 场景专用接收、执行与界面补齐

接收根/执行部分仅引用基础包§7.3.1～2，本包正文只维护页面部分。

#### 7.3.3 页面查询与步骤映射

`/pipelines/{id}` 必须先按 `pipeline_type` 分支，不能用 `source_id` 前缀或 Bag 的 `dataset_type` 推断场景任务。场景详情从已有 `SCENE_STEP_NAMES` 和真实 `StepRun` 构建总览；无记录标“未开始”，终态保持真实状态，Attempt 历史和错误可查。环境区只列处理机输入/工作根、场景 NAS 发布路径及远端模型服务身份；重试/取消按钮只展示该运行类型真实支持的动作，禁止自建 Phase0/Phase1/Phase3、A100 路径和强制重试选项误入场景详情。列表与详情使用同一类型/状态解释。

`/bags` 保留 URL 值 `slices|originals|all`，显示名改为“切片/原始数据/全部”。`slices` 为当前可用场景切片；`originals` 为所有原始输入：自建 `ORIGINAL`、场景源 `ORIGINAL`、英伟达输入记录（现有角色可能为 `NOT_APPLICABLE`，需按明确来源和非切片语义纳入）；`all` 包含这三类、场景切片、历史和其他既有记录。英伟达数据不得因角色枚举不同只在 `all` 可见；也不得把英伟达处理产物或场景子切片混入“原始数据”。类型筛选至少包含自建数据集、英伟达数据集、切片原始数据；数据来源、Bag 角色和处理用途分别建模/映射，避免用 `dataset_type=self_built` 单独推断“切片原始数据”。同包同时具多用途时只显示一条原始记录，筛选可命中相应类型。搜索、分页、状态、书签和详情跳转在三个视图间保持一致；测试包含英伟达真实形态记录和历史切片。

新增展示筛选参数 `data_kind=self_built_original|nvidia_original|scene_original|scene_slice`，不把“切片原始数据”伪装成新的 dataset_type，也不把 NVIDIA 的 bag_role 改为 ROS2 ORIGINAL。分类谓词：先按 SCENE_SLICE/有效 derivation 识别子包；NVIDIA 来源且非子包为 nvidia_original；ORIGINAL 且有 scene_slice 用途或已冻结 scene 根身份为 scene_original；ORIGINAL 且有 self_built 用途、或无任何场景依据的旧 self_built 记录为 self_built_original。双用途原包可同时显示两个类型标记并命中两个筛选，每个视图仍按 UID 去重。未知历史不猜类型，在“全部”保留并明确未分类。

两套查询入口使用同一分类/视图谓词：Web 的 bag_search_service 和 API 的 scene_result_query；`GET /api/v1/bags` 集合路由须与后者服务正式接线，不能把函数或seed中的路由存在当已接受公开API；历史“尚无路由”的调查结论保留在归档，本次实现/接受事实按固定候选证据核实。旧 dataset_type 筛选/无 view 书签维持兼容，`data_kind` 与其并用取交集；不相容视图组合显示明确空结果，不静默丢条件；tab、分页、排序、筛选取消链接均保留相关参数并重置页码。原始记录不要求已处理成功、存在 Topic 或能打开 DB3，NVIDIA 的空采集时间/Topic 必须正常显示。

八步中文名为“输入检查、解码/抽帧、模型识别、区间生成、切包、产物校验、NAS 发布、登记/完成”。总览按运行类型及实际 StepRun 的最新 attempt 显示，未启动后继步骤不因 run 结束被伪标完成；NO_MATCH/NOT_APPLICABLE 的无需步骤标 SKIPPED 并给原因，历史状态不回写数据库。场景终态停止刷新，SCENE_FAILED/PARTIAL_FAILED 显示原错误；成功链接到 Bag 子包和原始父包。公共列表与详情优先判断 SCENE_SLICE，即使原始 Bag 带其他 dataset_type 也不能误分类；详情保留既有 07B 审计/下架组件，重试只用场景正常重试通路。

P2上传客户端与P3统计不属于本轮UI，后置范围见[基础PRD](../rosbag-catalog-scene-foundation/PRD.md)。

## 8. 集合API责任

`GET /api/v1/bags`：新增统一服务检索，支持 view=slices/originals/all、data_kind、既有 dataset_type、车辆/场景/时间/topic/关键词、role、purpose、parent_bag_uid、include_history、cursor、limit；默认当前可用 slices，分类及组合规则见 §7.3.3。

该集合查询消费上节唯一分类/视图谓词，Web/API不得各自重写分类。所有组合条件取交集，双用途按UID唯一；非法日期和未知参数按既有错误契约明确拒绝。分页/结果/JSON与请求限额以及源时间格式统一引用基础DESIGN §7.1/8.1。

## 9. 三路接口与文件owner边界

分类/呈现规则以上节迁移自原DESIGN §7.3.3的正文为准。data_kind 枚举不变，集合 GET 路径不变；双用途用多成员谓词，两类都命中、UID只一条。子包=SCENE_SLICE角色或有效血缘；NVIDIA非子包即使角色NOT_APPLICABLE/无topic/时间也进入原始数据。Web/API 条件取交集、不静默丢筛选。A 保持 seed 的公开函数名/返回形状与模板分类标签字段；如需改接口，先在本入口登记 A/B 消费约定，再由协调者派相应 owner，小范围顺序接线，禁止自行越界。

A 独占 app/services/bag_search_service.py、app/services/scene_result_query.py、app/api/sources.py、tests/test_task16c_ui_minimal.py（只改本查询面断言）及新 test_task16ca_*.py；B 独占 app/web/bags.py、app/templates/bags.html 及新 test_task16cb_*.py；C 独占 app/web/pipelines.py、app/templates/pipeline_detail.html 及新 test_task16cc_*.py。原恢复入口说明seed已在sources router暴露集合GET；这只描述开发起点，不替代接受证据，本轮无须扩写路由总装配文件。静态资源若确需改，先申请精确 owner 交接。共享旧测试文件其他 UI 断言由 B/C 提出，协调者转 A 单写，禁止多人并改。

开发者独立worktree/branch和固定seed来自原派单；共同旧测试其他断言由B/C提出、协调者转A单写。接口变化先登记A/B消费约定和受影响owner，不并发改共享测试或原冻结树。实际owner/attempt从现行派单核，不因本次拆包重新分配。

## 10. 集成、原OCR遗留与停止条件

查询/API、Bag三视图、流水线详情无相互开发硬依赖，共同使用固定开发起点和契约；A接口变化只阻塞B对应接线。任一叶冻结后独立测试、适用OCR和逐项裁决可先行；三叶接受后统一固定集成候选，16D联合验收通过再聚合接受。各叶seed..head审查不能替代父任务包含seed的完整增量范围核验。

原15条发现和水雾发布覆盖债只在[原遗留账](../rosbag-catalog-integration/reviews/TASK-16C/OCR-LEGACY-20261014.md)与[16R裁决](../rosbag-catalog-integration/reviews/TASK-16R/attempt-1-disposition.md)追溯，不复制其状态。C4驳回保持；c03/c05待核项按当前代码/复现最小修复，不能把OCR建议直接变成业务需求。已接受生产事实保留，未覆盖范围如实列明，不把rc=0、PREPARED或超时当零发现/通过。

发现schema/状态机/算法变化需求、生产写、未知在途写者或文件冲突时保存证据交协调者，继续独立无冲突项。真实浏览器不可用标BLOCKED_BROWSER，不能以HTTP200替代。当前授权/工具入口/租约按原运行协议核，不在本包新造批准或启动机制。

原正文来源：[原DESIGN](../rosbag-catalog-integration/archive/pre-reorganization-20261014/DESIGN.md)§7.2/7.3.3与[当前UI恢复入口](../rosbag-catalog-integration/inbox/control/V04-UI-RESUME-20261014.md)。
