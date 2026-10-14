# 2026-10-14 需求文档拆分与兼容说明

此次整理把 `doc/prd` 从平铺文档与场景混合需求根，调整为按独立业务目标组织的需求包。只改变文档归属、导航与兼容入口，不重置 TASK/REQ/AC、attempt、已接受快照、测试结论、审查裁决或授权边界。

规范需求目录和当前运行根分开记录。场景基础、界面、水雾的业务文档已拆分，当前五角色运行资料仍留在 `rosbag-catalog-integration`；本次没有完成其运行根迁移。

## 一、正文与完整包迁移映射

下表路径均相对 `/home/wang/work/`。每个旧路径保留一个相对符号链接，指向新位置的唯一原件；目录行包含该专项的全部文档和证据，不复制两份包。

| 旧路径 | 规范新路径 |
|---|---|
| `doc/prd/vla_self_dataset_pipeline_v1_prd.md` | `doc/prd/vla-self-dataset-pipeline/PRD.md` |
| `doc/todo/vla_self_dataset_pipeline_v1_todo.md` | `doc/prd/vla-self-dataset-pipeline/TODO.md` |
| `doc/prd/vla_nvidia_dataset_pipeline_v1_prd.md` | `doc/prd/vla-nvidia-dataset-pipeline/PRD.md` |
| `doc/todo/vla_nvidia_dataset_pipeline_v1_todo.md` | `doc/prd/vla-nvidia-dataset-pipeline/TODO.md` |
| `doc/prd/vla_unattended_workflow_prd.md` | `doc/prd/vla-unattended-workflow/PRD.md` |
| `doc/prd/vla_data_platform_prd.md` | `doc/prd/archive/vla-data-platform/PRD.md` |
| `doc/prd/vla_processing_mvp_prd.md` | `doc/prd/archive/vla-processing-mvp/PRD.md` |
| `doc/prd/rosbag-catalog-integration/a100-multi-node/` | `doc/prd/rosbag-catalog-a100-multi-node/` |
| `doc/prd/rosbag-catalog-integration/nvidia-cleanup/` | `doc/prd/rosbag-catalog-nvidia-cleanup/` |
| `doc/prd/rosbag-catalog-integration/SPRAY-INTEGRATION.md` | `doc/prd/rosbag-catalog-spray-pipeline/SPRAY-INTEGRATION.md` |
| `doc/prd/rosbag-catalog-integration/RAW-DATA-REQUIREMENTS.md` | `doc/prd/rosbag-catalog-spray-pipeline/RAW-DATA-REQUIREMENTS.md` |
| `doc/prd/rosbag-catalog-integration/SPRAY-REFERENCES.json` | `doc/prd/rosbag-catalog-spray-pipeline/SPRAY-REFERENCES.json` |
| `doc/prd/rosbag-catalog-integration/SPRAY-RELEASE.md` | `doc/prd/rosbag-catalog-spray-pipeline/SPRAY-RELEASE.md` |
| `doc/prd/rosbag-catalog-integration/SPRAY-POST-V04.md` | `doc/prd/rosbag-catalog-spray-pipeline/SPRAY-POST-V04.md` |

旧 PRD 文件名及两个旧 TODO 仍可访问；读写实际落在对应唯一正文，不维护兼容副本。迁移涉及的 Markdown 链接按新正文位置重定位。旧目录中的历史文件名与事实记录继续保留，不据整理日期重判任务状态。

A100、NVIDIA 清理的包内 `ROLE-BINDINGS.json` 的 `project_root` 更新到各自规范根。它们的元数据归属调整不等于建立角色群、注册 cron 或激活任务；是否绑定与可执行仍按实际配置核实。

## 二、原场景混合主文档拆分

原 `rosbag-catalog-integration/{PRD,DESIGN,ACCEPTANCE}.md` 内容按下列需求归属拆分，原编号与契约要求保留：

| 规范需求包 | 归属内容与入口 |
|---|---|
| [rosbag-catalog-scene-foundation](rosbag-catalog-scene-foundation/README.md) | 场景公共接收、能力与执行、源身份/代次、冻结配置、幂等、租约、发布和公共验收；接口与共享契约以本包设计为唯一源 |
| [rosbag-catalog-scene-ui](rosbag-catalog-scene-ui/README.md) | 场景最小界面闭环、视图与详情、查询追溯、界面相关返修和原 OCR 遗留任务定位 |
| [rosbag-catalog-spray-pipeline](rosbag-catalog-spray-pipeline/README.md) | 水雾专项需求与验收、算法/参考图/输入资料、发布、生产批次与后续收尾 |

三包分别建立 README、PRD、DESIGN、ACCEPTANCE、TODO 定位、INTERACTIONS 和 HANDOFF 入口；专项正文采用链接引用，不复制另一份契约或状态机。

旧三份混合主文档的历史正文保存到 [rosbag-catalog-integration/archive/pre-reorganization-20261014](rosbag-catalog-integration/archive/pre-reorganization-20261014/README.md)。旧 PRD、DESIGN、ACCEPTANCE 路径继续存在，保留原章节标题作为跳转入口；当前业务契约读取对应新包，历史快照不作为第二份当前规范。

旧 `A100-MULTI-NODE.md`、`NVIDIA-CLEANUP.md` 改为各独立包的导航；原 `SESSION-START.md`、`HANDOFF.md` 增加归属说明，继续接续原角色身份和有效派单。

## 三、活跃运行资料保持原根

当前实际协作根仍为 `/home/wang/work/doc/prd/rosbag-catalog-integration`。下列内容未按需求复制或迁出：

- `TODO.md`：场景基础、界面、水雾当前任务唯一可写状态。新三包 TODO 只提供归属与章节定位。
- `inbox/`：协调者与 A/B/C/TESTER 派单、ACK、控制材料和有效协议。
- `receipts/`、`test-receipts/`、`reviews/`：开发、独立测试、OCR/强审与裁决原件。
- `sessions/`、`events/` 及已有兼容会话/事件入口：保持原身份与历史链路。
- `ROLE-BINDINGS.json`、角色租约、OCR 锁、锁目录和运行控制数据：保持原根，不复制运行所有权。
- 角色注册表、Hermes 原生 cron 的项目绝对根和会话入口：本次不切换到新三个需求根。
- 原 `TIMELINE.md`、scratch、review-bundle 等历史日志与证据：继续保留，不把目录整理当清理授权。

各新包 `INTERACTIONS.md` 按 TASK-ID/attempt 链接上述原件；水雾 `runs/1012-20261013/` 导航链接原批次状态、交接与验收，未另建批次状态源。

保持运行根的技术原因是现有运行工具实际依赖完整项目根。`role_runtime.py` 校验 `ROLE-BINDINGS.json` 中的根；`role_observer.py` 对材料执行 `resolve()` 后的根内边界检查，并通过固定目录与 `rglob()` 采集派单和回执。若把这些目录拆成跨需求软链接，解析后可能落到原根以外而被拒绝，目录遍历也不能假定会穿透符号链接。不能仅通过文件移动和软链接宣称运行流程已兼容。

本次相对符号链接只用于已迁出的正文与两个原本独立的专项包。对仍在途的场景任务，不移动派单、会话或租约，避免双写、重复领取和身份分叉。

## 四、后续运行根切换

后续在任务安全检查点按以下顺序完成运行拆分，不在普通巡检中复制 TODO 或相同群绑定：

1. 核实当前角色、task/attempt、固定提交、有效派单、进程和租约，保存可以接续的检查点。
2. 为当前要激活的需求确定完整运行根和唯一 TODO；按原 TASK-ID 保留相关派单、ACK、回执、审查和证据关联。
3. 同步核对运行工具的路径边界/扫描能力、ROLE-BINDINGS、角色注册表、cron 绝对根、会话入口及角色资源占用，禁止新旧两根同时调度同一身份。
4. 验证派单可见、会话可续、互斥与队列有效、角色空闲/繁忙判定正确、证据与报告来源一致，再切换唯一运行入口。
5. 旧根保留明确导航与必要兼容入口；记录权威切换检查点。验证不通过时恢复原入口，保留完整原证据。

建包、调整绑定元数据和实际运行切换是不同动作。目录整理不新增业务开发、群通知、模型调用或生产授权，也不宣称当前任务已完成。

## 五、以后新增需求的规则

独立目标默认建在 `doc/prd/<独立需求名>/`，与现有需求同级。先判断业务目标与验收边界，再确定文档根，不因为同仓或复用 A/B/C 就追加到最早的需求目录。

原目标的缺陷、漏项、补验和后续阶段保留在所属包；单个 TASK 是包内执行单元，不为每个 TASK 建独立需求根。一次测试、真实验收或生产批次归入所属包的 `runs/<批次编号>/`。

跨包依赖引用唯一契约、固定交付版本及接受证据。总索引只负责导航；各包任务状态只维护一份，后续阶段与运行激活条件按有效派单接续。[返回需求总索引](README.md)。
