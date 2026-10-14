# 场景最小界面闭环验收契约

需求包：`rosbag-catalog-scene-ui`。本次整理仅迁移文档内容归属，不更新实现、验收、部署、授权或任务状态。REQ/AC/TASK沿用原编号，不因拆包重新编号或重新派发。

当前任务状态、派单与角色运行仍由[原唯一TODO](../rosbag-catalog-integration/TODO.md)、[现行启动入口](../rosbag-catalog-integration/SESSION-START.md)和原绑定维护；本包[TODO](TODO.md)只导航，不建立第二份可写任务状态。历史混合正文保留在[整理前归档](../rosbag-catalog-integration/archive/pre-reorganization-20261014/)，其中暂停、待发布等旧描述不作为当前执行指令。

## 本轮 v0.4 恢复验收增补（2026-10-14T11:25:19+08:00）

AC-16/AC-05恢复：切片/原始数据/全部三视图；Web/API共同分类、双用途双命中UID唯一、NVIDIA真实形态、合法无血缘历史切片、过滤/分页/cursor/日期422；八步真实latest attempt状态/终态停刷新/无自建动作及路径误显、取消页无JS异常；原包↔子包↔场景run追溯及受控获取。保留旧自建/NVIDIA/坡道和07B回归。

必需固定集成SHA、真实浏览器DOM/console/network、严格MySQL关键查询与真实已接受首包产物获取证据；seed/mock/旧TESTER PASS不能替代新候选。15条原OCR逐项新SHA/复验或有据裁决，C4驳回保持，发布coverage债按16R明列。缺条件NOT_RUN/BLOCKED，不伪PASS。原12S-D真阴性/实车/跨DB3广义矩阵仍独立保留；本轮不增加真模型运行或新生产写。当前派单见 [inbox/control/V04-UI-RESUME-20261014.md](../rosbag-catalog-integration/inbox/control/V04-UI-RESUME-20261014.md)。水雾首次发布输入要求在水雾包维护，不把重新跑首包当UI前置。

独立验证必须固定包含开发起点和三叶的集成SHA、环境与配置摘要，使用已有已接受真实首包产物核父子获取。准备与叶增量验证可先行，最终16D只能针对协调者提供的完整固定候选；原12S-D质量矩阵独立，不以UI验收外推。

## 2. AC 和最小取证

| 验收项 | 场景与应有结果 | 证据 | 实现owner |
|---|---|---|---|
| AC-16.1 真实场景详情 | 页面按pipeline_type显示“场景切片”，八步中文名/真实状态/最新Attempt/错误/产物可查；本机执行与远端模型明确，父子链接有效；无自建阶段/A100路径/不适用强制重试。 | 浏览器截图/DOM和API/StepRun对照，成功/失败/取消/无命中各一类；终态停止刷新，历史记录不被页面回写。 | 16C |
| AC-16.2 三视图 | Tab标签严格为“切片、原始数据、全部”；切片仅当前可用结果；原始数据含自建、英伟达、切片原始数据；全部含原始及当前/历史/待完成/下架切片和其他旧条目。 | 三类原始+多状态子包的固定UID期望集合，Web与正式集合API对照；英伟达NOT_APPLICABLE/空Topic仍可见，原始视图无场景子包。 | 16C |
| AC-16.3 类型/筛选/兼容 | data_kind分类与dataset_type/role/purpose独立；双用途原始记录只显示一行、可命中相应两类；tab/分页保留筛选，旧书签/自建/NVIDIA导航与详情可用。 | 每类筛选UID集合、组合空结果/未知参数、分页无重复和条件保留、旧入口浏览器/API回归。 | 16C |

## 3. AC-05获取与旧功能回归

| 验收项 | 场景与应有结果 | 证据 | 实现owner |
|---|---|---|---|
| AC-05/06/07/08/09 回归 | 专用目录真实坡道包→自动调度正式代理→非空可打开切片→发布/登记/current→页面/API获取；原包不变、父子可追溯、重复重试不重复产物，质量只声称小样本工程核验。 | 一条贯通时间线、run/source/child UID、完整manifest和实际Bag消息/topic/存储域边界/hash、获取路径实际可读。 | 16D，缺陷返所属owner |

原包↔子包↔场景run双向追溯、受控获取路径和文件实际可读必须共同取证；固定UID期望集合与Web/正式集合API一致。保留旧自建/NVIDIA导航/详情、坡道、07B审计/修订/下架和旧书签。

对已接受正式链路产生的真产物核对run/source/child UID、版本、车辆、区间、manifest/物理文件和获取，不以mock、seed或单页面200代替。基础AC-05/06/07/08/09的不变量引用[基础验收](../rosbag-catalog-scene-foundation/ACCEPTANCE.md)；当前UI不重新烧模型、不新做生产写，不因在途大包未终态延后既有产物的页面验证。

## 4. 原OCR与独立取证

原15条逐项记录新SHA/独立复验或有据裁决；同一实现可关闭两个来源但保留各来源ID。C4驳回维持，未启动步骤仍按真实“未开始”显示；其余项不得为凑审查通过引入错误状态。16R须明确当前已覆盖、后续替代、真实未覆盖范围和处置依据。

浏览器记录真实DOM、console、network及各成功/失败/取消/无命中/不适用页面，核最新attempt、终态停止刷新和无自建动作误显。严格MySQL关键查询覆盖双用途双筛选、NVIDIA真实形态、合法无血缘历史切片、过滤/分页/cursor/日期边界和非法日期422，不能只用SQLite全绿外推。

真实浏览器不可用标BLOCKED_BROWSER；缺候选、输入、环境或证据标NOT_RUN/BLOCKED，seed/mock/旧PASS不替代新候选。详细证据字段与结论规则引用基础验收§4。

## 5. 完成、失败接续与边界

各叶固定交付经独立验证和适用审查裁决接受后，形成包含seed与完整变更的集成候选；16D联合浏览器/API/MySQL/旧功能通过，16R有据处置后，父16按原AC收口。当前状态与接受决定仍在原TODO/派单/回执，不在本文件另建验收结果表。

缺陷返原owner最小修复；发现基础状态/身份/发布或schema需要改变，交协调者评估影响包和证据失效，不能在UI侧临时绕过。07C预览、统计和其他场景不顺带恢复。水雾真阴性/实车/真实跨DB3/批量质量与生产准入归水雾包，已受控test首包接受事实不重置。

原验收来源：[整理前ACCEPTANCE](../rosbag-catalog-integration/archive/pre-reorganization-20261014/ACCEPTANCE.md)顶部恢复增补及§2 AC-16；原发现/测试明细见[遗留账](../rosbag-catalog-integration/reviews/TASK-16C/OCR-LEGACY-20261014.md)和[现行UI派单入口](../rosbag-catalog-integration/inbox/control/V04-UI-RESUME-20261014.md)。
