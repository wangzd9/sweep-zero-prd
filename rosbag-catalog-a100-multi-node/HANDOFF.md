# A100 双节点专项交接

> 2026-10-12 场景v0.4补充：用户已确认只调整场景识别/切片执行拓扑，自建/NVIDIA仍用本专项。场景所有非模型处理在处理机，A100仅提供模型服务；本专项不接收其原包/切片、不分配执行/空间槽。恢复主线见 [SESSION-START](/home/wang/work/doc/prd/rosbag-catalog-integration/SESSION-START.md)，本专项不成为主线TASK-16前置；原授权/任务/现场快照不因本次文档更新改变。

版本：MN-v1，2026-10-12。状态：**DESIGN_READY，仅文档完成**。
开发/验证/启用状态唯一读取 [TODO](TODO.md)，恢复入口 [SESSION-START](SESSION-START.md)。

## 1. 本次授权、交付与停止点

用户本轮要求“PLEASE IMPLEMENT THIS PLAN”，所附方案明确“当前交付目标是完整开发文档”“本次规划不启动运行角色”。因此本次授权为落盘文档、增加上级入口及NVIDIA删除节点补充契约，未授权实现业务代码、启动开发者/TESTER/cron、远端安装或写入、生产部署及数据删除。

已确认：A/B各3槽，两路线共享；仅新增分流，历史原位；分配后固定节点；GPU不作门槛；B模型额度共用；B沿用A目录组织。用户选择固定任务预算，并选择“必填配置，实测后启用”，没有批准100/200GiB等默认值。

交付 PRD/DESIGN/TODO/ACCEPTANCE、五角色启动/绑定/协议、开发日志及文档验证。新绑定 control=UNBOUND，chat/cron/worktree均为空；没有派单、租约接管、合入、OCR或真实业务验证。上级入口更新不改变上级任务或已绑定运行角色。

## 2. 调查基线与事实来源

本轮本地调查 catalog `502bf8ec79690cf01e130cb0591121eb10e96af5`，main；自建脚本 `81b1e83a85cb6cc9fa7ffdf00cba144fba2b1241`；NVIDIA脚本 `52f65d1920e07a8d5ce5a92d5ae5fe14b9492147`。实际派单另冻结最新已接受base，调查hash不表示远端部署版本。

| 事实/差距 | 证据入口 |
|---|---|
| 单A100代理派发；A100/NVIDIA资源忙时等待会占用单线程轮询 | catalog `app/orchestrator.py` 的 `_dispatch` / `_acquire_resource_with_wait`。 |
| ResourcePool按executor_id/resource_key唯一；过期lease被剔除；slot当前按used生成 | `app/models.py`、`app/services/resource_service.py`。MN-04要修持久UNKNOWN计数与slot空洞行为。 |
| run/copy/artifact尚无节点字段；SourceCopy键不包含node | `app/models.py`；DatasetFrame可关联run/artifact，无需历史帧重写。 |
| 节点根/SSH在代理和环境契约固定A；health仅ok/active_runs | `scripts/a100_host_proxy.py`、`scripts/lib/environment_contract.py`。 |
| NVIDIA批准根固定A；源创建前写入绝对origin模板 | `app/nvidia_configs.py`、`app/services/nvidia_service.py`。 |
| 两路线/发布依赖经SSH回调；NAS实物校验及原子发布在处理机 | self_built_pipeline/nvidia_pipeline/nas_publisher/frame_importer相关代码。 |
| 自建Phase1 ffmpeg软件解码，Phase3为CPU规则/绘图及HTTP模型调用 | 自建正式脚本 phase1/phase3；ffmpeg默认可来自Conda，不能由登录PATH断言缺失。 |
| 模型脚本固定127.0.0.1:8002 | 自建phase3脚本和NVIDIA phase2脚本；前序只读核验A为SSH转发、B为Python服务。 |

仓库根 `/home/wang/work/rosbag-catalog`；自建正式根 `/home/wang/work/dataset_build/self_built_route/code/proj_self_dataset_builder_scripts`；NVIDIA正式根 `/home/wang/work/dataset_build/nvidia_physicalai_route/code/proj_nvidiadata_builder_scripts`。项目规则见仓库 AGENTS/LLM_DEVELOPMENT_RULES 和 `/home/wang/work/doc/todo/vla_self_dataset_pipeline_v1_todo.md`，NVIDIA另读相邻V1 TODO。

## 3. 前序2026-10-12只读现场结果

来源为本会话前序SSH/HTTP工具返回，本轮文档落盘未重复连接远端。以下为时间快照，不能当作后续启动实时健康。

| 项目 | A | B |
|---|---|---|
| 开发机SSH alias | a100-wzd | llm-server |
| 用户/hostname | xmyf / xmyf-node-214-2-7-6 | sysadmin / a100 |
| CPU线程/当时load | 128 / 约2.8 | 256 / 约20 |
| 数据挂载 | `/data` | `/home/sysadmin/data/disk03`，ext4/rw，sysadmin可写 |
| 当时剩余bytes | 301446713344，约281GiB | 5834070876160，约5.3TiB |
| 8002 | SSH监听转发到B | Python监听，`/v1/models`成功 |
| 业务目录 | 已核验xl_*、nvidia_*及wzd层级 | 目标`rosbag-catalog`根尚不存在 |

B的已返回model id：`/home/sysadmin/data/disk02/jc/models/qwen3.8-27b-fp8`。B GPU当时均有其他进程，但本期执行节点选择不依赖GPU空闲。

开发机到A/B SSH成功；处理机到A/B及A/B互相的SSH端口socket握手成功，未测大文件吞吐、未复制密钥。处理机到B的专用非交互SSH认证、远端写者/cleanup helper和运行Python路径仍待MN-09安装核验。

A/B当时都没有 `/mnt/nas_backup` 挂载，NAS发布沿现有处理机回传，不要求B挂NAS。B未核验具备A的专属checkout、依赖和地图；A/B登录PATH都未找到ffmpeg，此事实不等于Conda内不存在。

连接元数据和凭据引用继续维护在 `/home/wang/work/doc/password/rosbag-catalog-connections.md`，不向专项复制秘密。后续明确只读授权下，在开发机可复核：

```bash
ssh -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o UpdateHostKeys=no -o ControlMaster=no -o ControlPath=none -o ConnectTimeout=10 a100-wzd df -B1 /data
ssh -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o UpdateHostKeys=no -o ControlMaster=no -o ControlPath=none -o ConnectTimeout=10 llm-server df -B1 /home/sysadmin/data/disk03
```

以上只读命令不是MN-09远端安装/写入或MN-10生产部署授权，不从历史会话猜处理机的SSH身份。

## 4. 后续协调者恢复顺序

1. 读SESSION-START→ROLE-BINDINGS→协议→TODO→DESIGN→VALIDATION；核验当前授权是否已经包含后续本地开发。
2. 只读确认实际main、用户已有改动、其他专项在途owner/worktree/进程/共享文件。不得抢占场景专项或NC专项绑定/派单。
3. 将本专项五角色实际工作区/群/cron绑定补齐，明确control启用和用户授权；无Hermes群时使用实际会话协作且如实标未配置定时，不能编造群或cron ID。
4. 冻结MN-v1和实际base，开发者自行建专属worktree。按TODO派MN-01/02/03，供应接口接受后重算接续，不等无关整波。
5. 本地开发到MN-08收口即报告证据与剩余前提。MN-09/10仍为单独阶段，不因空槽或依赖齐全自动执行。

## 5. 尚待证实的启用前提

- 两路线任务峰值占用和安全余量：必须按代表性输入校准并明确支持范围。
- B的Python/ffmpeg/脚本revision/地图/权限、实际测试根/锁根、代理端口和处理机到B key认证。
- 6个执行任务的网络/CPU/磁盘与共享模型压力；当前仅证明连通性，不宣称吞吐达标。
- 新旧在途A租约与持久占用接管、旧清理确认计划及helper能力兼容。
- 生产备份、迁移、回滚及发布后本地收敛；所有生产动作待MN-10授权。

这些前提不阻塞按冻结契约开展本地模拟开发，阻止声称真实纳管已完成。

## 6. 审查、日志和可复用性

开发日志：[DEVELOPMENT-LOG](DEVELOPMENT-LOG.md)；OCR由协调者串行管理，代码类提交遵循项目每commit/范围审查和≤12文件职责拆批。强审查默认人工，入口为协调者Skill `scripts/strong_review.py`；有明确用户授权才自动调用，滚动60分钟最多5次。当前无自动审查授权、无实际调用记录。

功能开发完成并有证据后按项目既有feature-changelog流程生成pending及REVIEW；用户批准后approved，实际发布后released。本次规划不修改changelog候选或生产时间线。

可复用性检查：本次为尚未实施的节点架构与文档交接，已安装complex-task-planner覆盖；没有经真实运行验证的新操作流程，不新增或改写Skill。

本专项位于仓库外共享文档根，无Git仓库；文档验证与摘要索引保存于VALIDATION。catalog只增加文档入口/交接记录，提交和GitHub同步事实随后在本文件记录，不把无Git文档假称已推送。


## 7. 文档仓库提交回执

2026-10-12：catalog纯文档提交 `30e55a368688376bb35be58f4d6e69bc3568bf8c`（`Document A100 multi-node development handoff`），仅包含HANDOFF与docs/a100-multi-node-planning.md；`git push -u github main`成功，远端main与该commit一致。仓库外完整专项文档没有Git，未声称其已推送。代码OCR/业务测试不适用于此次纯文档提交；最终文档检查、原文保留及内容摘要见VALIDATION。

## 2026-10-12T18:34:01+08:00 空闲汇报调整

- 执行者/测试者有任务20分钟，确认无任务2小时一行无模型短报；协调者20分钟、五分钟巡检和即时事件保持。Skill与report gate已配置，12项隔离测试通过；实际新周期投递尚待观察。
- 主专项已配置四条no_agent空闲报告，原群/origin与有任务报告周期保持；未绑定专项不创建cron。未改业务状态、任务编号/分支、在途开发/测试或模型服务。备份：/home/wang/.codex/skill-migrations/idle-report-20261012-174657。

- 2026-10-12T18:44:40+08:00 空闲汇报配置验证完成：12项隔离路由验证、5个Skill结构/Hermes加载、四角色脚本输出及cron提示组装/原群投递配置核对通过；采样时A/C/TESTER确认空闲会跳过20分钟模型报告，B保持正常报告。验证 /home/wang/.codex/skill-migrations/idle-report-20261012-174657/verification.json；排队分析 /home/wang/work/doc/analysis/hermes-qwen-load-20261012/REPORT.md。未主动投递消息、调用模型或改服务器并发；新周期真实投递及持续性能收益待观察。并发会话追加的v0.4规划保留。
