# 开发日志

## 2026-10-14 v0.4 UI 恢复：A 叶 OCR 裁决收口返修 + 1012 大包进入取消流程

- **A 叶（查询/API）OCR 面收口，R1 返修交付并核验**：初 run `7a72eed8` 15:14:47 外层硬截止（`scene_result_query.py` 未完成）→ 唯一入口补审 `0aba25ee` 16:24 收口 rc=0、2/2 全覆盖（`bd0db1d..ff2a005`，identity 匹配）。合并裁决（16:42，`inbox/coordinator/TASK-16C-A/ocr-merge-ruling-20261014.md`；16:35 中间 verdict 对 F2 的 REJECTED 因理由不成立被 17:30 补段覆盖留痕）：CONFIRMED 2 条 low——`data_kind_case()` 全仓零调用死函数（C6 单源口径残留）+ `scene_original` 谓词缺子包排除（derivation 子合法组合，防御性）；docstring 条驳回。A 交付 R1 返修 `4838ef8`（17:15:40，+3/−15 仅 `bag_search_service.py`），协调者 17:20 机械核验独立复跑全绿（74 passed + 1 seed 固有）。
- **B 叶（Bag 三视图）OCR 收口，1 finding 转 A 清理**：run `513ab61d` 16:45 起跑、17:09:40 收口 rc=0（`bags.html` 单批）；唯一 finding=tab 已改名但同屏 `view_label`（A 叶 `bag_search_service.py:664`）仍旧名「原始包/全部/历史」，CONFIRMED UI 一致性低危，修复点超 B 授权，R1-2 续单 17:30 派 A（同冻结链 base 续 `4838ef8`）。B 叶 OCR 门禁满足，`e399daf` 冻结无待修。A 最终 head 冻结后做一次单文件增量 OCR（不逐 commit 两跑），A 叶接受门禁维持关闭至增量 OCR + TESTER 增量面。
- **1012 批次大包状态变化**：`scene-4acf689f`（16_02_03，10.1GB/跨 2-DB3）16:30 观测通知起 `SCENE_CANCELLING`、heartbeat stale、proxy_run absent；与 15:57:45 处理机 kernel OOM-kill scene proxy（22.8GB/30G，C obs77 16:06 只读实测、容器 15:57:52 拉新代次）时间线衔接，疑似 OOM 重启后租约/心跳断链进入取消流程，确切原因待 C 下轮只读核实。协调者不 kill/retry/不重烧模型；收敛 `SCENE_CANCELLED` 则本包转取消终态登记并调整 TESTER 大包验收面，取消失败回 RUNNING 则恢复原跨夜观察口径。批次其余（PASS 基线 3 包、flat 三提交、空包拒绝）口径不变。
- **B 叶（Bag 三视图）叶接受**：18:10 决策落盘（`inbox/coordinator/TASK-16C-B/leaf-acceptance-decision-20261014.md`）——交付冻结/机械核验/OCR（`513ab61d` 17:09 收口，唯一 finding 转 A 已随 `1489bc6` 闭环）/TESTER B 叶增量 PASS（pytest 11+真实 Chrome）/强审 NOT_REQUIRED 五项全过；A 叶 R1-2（`1489bc6`，17:40:26 单行 view_label）18:01 机械核验全绿，最终冻结 head 已定，单文件增量 OCR run `66ca40d3` 18:02 经唯一入口 SUBMITTED 在途。
- 证据：reviews/TASK-16C-A/ocr-run-20261014{,-retry1}/run/；reviews/TASK-16C-A/ocr-run-20261014-r12/spec.json（排除清单）；reviews/TASK-16C-B/ocr-run-20261014/run/service.log（17:09:40 收口）；inbox/coordinator/TASK-16C-B/leaf-acceptance-decision-20261014.md；inbox/coordinator/SPRAY-BATCH-1012-20261013/BATCH-STATUS.md 16_02_03 行 17:15 段。下一责任人：协调者（`66ca40d3` 收口裁决→A 叶接受→三叶固定集成候选）、TESTER（A 增量面+16D 联验，大包按取消链证据口径）、C（8180 SCENE_CANCELLED 收敛面只读核）、A/Codex 绑定线（flat 三提交推进，SCENE_EXEC_HOST 释放后）。

## 2026-10-13 v0.5 水雾优先规划修订

- 2026-10-13规划交付收尾：12项文档检查PASS（最新检查2026-10-13T11:43:58.648168+08:00，63个链接/锚点、21张契约表、实际依赖/历史/参考图核对）；catalog纯文档提交`21673dae812cc94e2dd6807d579772ccac931ce1`（9份Markdown，+38），已推送`github/main`，远端与本地tip相同。仅提交自己的HANDOFF前缀，既有OCR/devflow/用户HANDOFF和未跟踪文件保留；外部共享包在Git外，本次没有业务实现/模型调用/生产部署。

- 用户暂停UI增量，优先水雾链路及原功能保护；资料要求明确车辆/时区/批次/sensor profile、purpose=scene_slice与scene=spray。
- 新增三份水雾/资料/生产文档，主PRD/DESIGN/TODO/验收/启动/交接同步；16A DONE/16B门禁保留，16C安全暂停交接，新增12S-A/B/C/D及11S。
- 1012样本只读盘点8目录，4含前雷达、3缺topic、1空包；用户明确无车辆号。
- 用户授权算法仓库GitLab快进197645e→be23177，新增7图本地格式/尺寸/有序hash校验成功，原代码逻辑未变；参考图约20.25MB/pass Base64，首包预算必检。
- 未请求模型/业务开发/部署。文档校验与纯文档提交证据见VALIDATION；旧任务/绑定/用户工作区改动保持。

协调者维护实质进展摘要；TODO为唯一任务状态，TIMELINE保留原始事件。本文件不代表正式功能日志发布。

## 2026-10-12T19:15:26+08:00 规划者修订场景 v0.4 文档

- 用户确认：场景专用目标 `/public/rosbag_scene_processing/{incoming,ready,slices}`；仅场景识别/切片全部非模型步骤在处理机，远端只请求模型；基础界面纳入最小闭环。
- 文档：PRD/DESIGN/TODO/HANDOFF/SESSION-START更新；新增ACCEPTANCE及文档VALIDATION，补齐TASK-16A/B/C/D任务/owner/接续/失败恢复/测试证据；A100专项增加仅自建/NVIDIA范围说明，NAS与仓库架构/规则入口标目标态。
- 复核修正：去掉上一版无依据禁用显式双用途；修复空缺任务状态列、能力已实现却写未实现、UI后置的冲突；明确场景关闭/未匹配不得回退Phase0、正式本机代理及两查询共用分类。
- 保留：旧TASK-01～15及07B在途状态/派单，角色/群/cron/审查授权与生产门禁。未开发业务、未跑模型/业务测试、未部署或修改生成部署快照；不生成正式功能released日志。
- 下一步：文档检查后按 [SESSION-START](SESSION-START.md)交接；协调者在有效实施授权和07B检查点交接下派新叶任务，16D联合验收包含页面，生产启用仍独立。
- 交付收尾：11项文档检查PASS（链接/表格/需求任务映射/依赖/历史保留/差异），AC-14双用途边界及16C集合路由笔误再次修正。仓库9份文档提交 `c2018dd`，已推送github/main；完整共享文档仍位于Git外。校验记录见 [VALIDATION](VALIDATION.md)，没有业务实现或生产验收结论。

## 2026-10-12T11:11:58+08:00 协作能力更新

- 范围：Skill/Hermes协作配置，未改变本专项业务状态、派单、分支或实现范围。
- 变化：支持用户自定义时间/当前任务自动审查授权；统一调用记录与滚动60分钟最多5次，协调者周期报告显示授权/调用情况；协调者按实质进展维护本日志。
- 证据：强审脚本第一轮13项离线验证通过，Codex使用假进程，未发起真实付费审查；完整验证记录待本次配置核对后补入HANDOFF。
- 当前授权：本次只调整能力，不设实际审查授权，不启动NVIDIA专项或生产操作。后续真实用户消息决定授权范围和期限。
- 下一步：后续角色回合按新Skill/协议恢复；开发交付和正式日志批准仍使用原门禁。

- 2026-10-12T11:21:40+08:00 本次配置验证完成：15项离线测试通过（假Codex进程，真实Git固定快照），4个Skill结构校验、Hermes加载/协调者cron注入、15个本地Skill链接与角色/任务/周期保留检查通过；两个项目的真实只读status可执行且不创建授权账本。证据 /home/wang/.codex/skill-migrations/review-authorization-20261012-104349/verification.json。未创建实际授权、未调用真实付费模型；真实新入口审查待用户明确授权后验收。

## 2026-10-12T12:13:42+08:00 动态拆分与日志节点

- 范围：协作规则和Hermes调度提示，未改业务实现，无本轮业务commit。
- 变化：协调者主动在既定范围内拆粗任务，最多三路并发；父子不重复派单，在途先确认交接。开发日志随实质事件更新，正式日志按功能验证、用户批准、实际发布三个节点推进。
- 证据：协调者/规划者Skill 1.2.1、inbox/PROTOCOL.md；文档结构和Hermes加载验证待本次核对。
- 下一步：由后续协调者调度回合应用；测试/OCR/强审查及正式日志批准门禁保持。

## 2026-10-12T13:15:00+08:00 TASK-07A attempt-1 收口（机械核验+OCR，回派最小返修）

- 范围：TASK-07A（统一界面·可见性与检索，P1 提前，用户 09:45 授权），B `f94d006`（11 文件 +905/-30，零迁移）。
- 交付与核验：11:17 交付 REVIEW_PENDING → 协调者独立机械核验全绿（rev-parse 双核 base `453da0c`/`merge-base` yes、定向 6 passed 独立复跑 RC=0、零 alembic/状态机越界、页面实测 12 段 needle 证据核读一致、自包含 uvicorn 口径合规不触共享栈）。
- OCR：串行逐文件 8/8 app 文件有效覆盖（cron 420s 硬上限实测：多文件合批 context compaction 后单轮 reap，单文件 151-318s 收口，reap 后 `--resume` 断点续审）；唯一 findings=bags.html 2 处 medium（view-tabs 丢筛选=违反 §2.3 不回归、col-scene fixed 布局无宽度声明）→ 均 CORRECTION。
- 裁决：bag_role 独立下拉=接受现状不扩；07A attempt-1 暂不合入，回派 B attempt-2-r1 最小返修（base `f94d006`，只改 bags.html+bag-search.css）。
- 门禁变化：TASK-07 维持 RUNNING（07A 返修在途，07B/07C 串行待前置）；TASK-10 DONE/P0 收口、TASK-11 PRODUCTION BLOCKED、12-15 DEFERRED 均不变；main `453da0c`=origin。
- 强审查：无用户有效授权，NOT_REQUIRED 预判（P1 UI+只读 API 零迁移），维持人工触发，不阻塞合入链。
- 证据：decision `inbox/coordinator/TASK-07A/attempt-1-ocr-ruling-20261012.md`、OCR 账 `reviews/TASK-07A/attempt-1/ocr-batches.md`、返修单 `inbox/2号/TASK-07A/attempt-2-r1-dispatch.md`。
- 下一步：核 B attempt-2-r1 ACK/交付→增量 OCR（仅返修文件）→合入 main→TESTER 页面+API 独立验证→07A DONE→派 07B。

- 2026-10-12T12:24:09+08:00 本次规则/配置验证完成：协调者和规划者Skill结构校验通过，Hermes从唯一维护源加载1.2.1及拆分参考通过，两个协调者cron组装/注入/提示安全检查通过，11个本地Skill链接有效。两个项目TODO与角色绑定、所有cron调度/投递/其他角色提示保持。证据：/home/wang/.codex/skill-migrations/dynamic-decomposition-20261012-120520/verification.json。未进行真实角色运行、实际业务拆分或付费调用；后续调度/交接行为需由真实回合取证。

## 2026-10-12T14:10:00+08:00 TASK-07A attempt-2-r1 收口（机械核验+增量 OCR 全绿，合入 main caf385b，待 TESTER 独立验证）

- 范围：TASK-07A 最小返修 attempt-2-r1（OCR T07A-r1 唯一 findings 文件 bags.html 2 处 medium），B `8cc6b80`（3 文件 +51/-5，base `f94d006`，零迁移零越界）。
- 交付与核验：13:35 交付 REVIEW_PENDING → 协调者独立机械核验全绿（逐行 diff 语义核=tab 筛选保留+退化旧路径/col-scene 150px 闭合 9 列、定向 7 passed+ruff 绿独立复跑、rev-parse 双核 main `453da0c` 零漂移、`app/web/bags.py` 未动无 §五 申报情形）。
- OCR：增量串行 2/2 入选文件 0 findings（bags.html session 8055d30e 5m51s；bag-search.css 1373L 独立批 v1 420s cron reap 无 manifest 不可 resume 作废 → v2 session b105894b 4m9s 0 findings；tests default_path 排除先例）。账 reviews/TASK-07A/attempt-2-r1/ocr-batches.md。
- 裁决：ACCEPT_MERGED → --no-ff 合入 main `caf385b`（=origin 双核一致），合入后 sanity 7 passed RC=0；07A 仍 RUNNING 待 TESTER 合入后独立验证（三视图 tab 行为断言+渲染+attempt-1 面不回归）PASS 才写 DONE → 派 07B。
- 门禁变化：TASK-07 维持 RUNNING（07A 验证在途，07B/07C 串行待前置）；TASK-10 DONE/P0 收口、TASK-11 PRODUCTION BLOCKED、12-15 DEFERRED 均不变。
- 强审查：无用户有效授权维持人工触发，NOT_REQUIRED 预判（P1 UI+只读 API 零迁移）不变。
- 证据：decision inbox/coordinator/TASK-07A/attempt-2-r1-merge-decision-20261012.md、OCR 账 reviews/TASK-07A/attempt-2-r1/ocr-batches.md、TESTER 派单 inbox/TESTER/TASK-07A/post-merge-verify-dispatch.md。
- 下一步：核 TESTER 07A 合入后验证回执 → PASS 写 07A DONE + 派 07B；FAIL 按定位回派 B。

## 2026-10-12T15:09:00+08:00 TASK-07A DONE + TASK-07B attempt-1 派发（P1 场景线接续）

- 07A 收口：attempt-1 `f94d006`（11 文件 +905/-30）+ OCR 2 处 medium 返修 attempt-2-r1 `8cc6b80`（3 文件 +51/-5）→ --no-ff 合入 main `caf385b`；TESTER 合入后独立验证 **32/32 PASS**（finding #1/#2 行为断言 + attempt-1 面 12 段不回归 + pytest 7+329 RC=0，自包含 uvicorn 口径夹具 0 残留）→ **07A DONE**（decision `inbox/coordinator/TASK-07A/post-merge-verify-acceptance-decision-20261012.md`；强审查 NOT_REQUIRED）。
- 07B 派发：REQ-04/AC-04 人工纠错/下架（PATCH `scene-labels` + POST `withdraw` 四要素审计、保留原始模型结果、不删文件、父包 422、迁移最小含 downgrade 须真 MySQL 8.4 往返），owner B，base main `502bf8e`，派单 `inbox/2号/TASK-07B/attempt-1-dispatch.md`（待 ACK）；07C 预览串行待 07B 收口。
- 门禁：TASK-07 RUNNING（07B 在途）；TASK-11 生产维持 PRODUCTION BLOCKED；changelog F-035~F-039 pending 候选（`502bf8e`）等用户审批，发布随 TASK-11 后。

## 2026-10-12T18:34:01+08:00 空闲汇报调整

- 执行者/测试者有任务20分钟，确认无任务2小时一行无模型短报；协调者20分钟、五分钟巡检和即时事件保持。Skill与report gate已配置，12项隔离测试通过；实际新周期投递尚待观察。
- 主专项已配置四条no_agent空闲报告，原群/origin与有任务报告周期保持；未绑定专项不创建cron。未改业务状态、任务编号/分支、在途开发/测试或模型服务。备份：/home/wang/.codex/skill-migrations/idle-report-20261012-174657。

- 2026-10-12T18:44:40+08:00 空闲汇报配置验证完成：12项隔离路由验证、5个Skill结构/Hermes加载、四角色脚本输出及cron提示组装/原群投递配置核对通过；采样时A/C/TESTER确认空闲会跳过20分钟模型报告，B保持正常报告。验证 /home/wang/.codex/skill-migrations/idle-report-20261012-174657/verification.json；排队分析 /home/wang/work/doc/analysis/hermes-qwen-load-20261012/REPORT.md。未主动投递消息、调用模型或改服务器并发；新周期真实投递及持续性能收益待观察。并发会话追加的v0.4规划保留。

## 2026-10-12T19:0x:00+08:00 TASK-07B attempt-1 交付 + 机械核验全绿 + 串行 OCR 4/10 部分收口（未合入）

- 交付：B `f4bfcf2`（2 commit `5fa0942` 主体 + `f4bfcf2` corrected_label 域契约修正，11 文件 +1235/-4，base main `502bf8e` 祖先核通过，`receipts/TASK-07B/attempt-1.md` 17:15 落盘）。范围=REQ-04/AC-04 人工纠错/下架（PATCH scene-labels + POST withdraw 四要素、审计表迁移含 downgrade、保留模型原结果、下架退出默认检索 all 可见标注、父包 422）。
- 协调者独立机械核验全绿：定向 `test_task07b_manual_revision.py`+`test_task07a_visibility.py` **10 passed** 独立复跑；ruff 交付 app 文件 **All checks passed**（独立复跑）；alembic 单头 `20261012_01_scene_manual`；**真 MySQL 8.4 隔离库迁移往返**（UPGRADE/边界 INSERT/超宽 1406 真实生效/DOWNGRADE/RE-UPGRADE/CLEANUP 全 PASS，T03/T04 教训口径）证据独立复读；页面 smoke **26/26 PASS**；lastfailed 4 项=既有环境性（base 复现同口径）非本侧回归。
- 串行 OCR（账 `reviews/TASK-07B/attempt-1/ocr-batches.md`，flock 持 `ocr.lock` 逐文件单审）：**4/10 收口**=b1 迁移 0 findings / b2 `app/api/__init__.py` 0 / b3 `app/api/scene_manual_revision.py` **1 medium 属实**（非 dict JSON → 500，与文档化 422 面不一致，CORRECTION 待裁决）/ b4 `app/models.py` 0；**b5 service 383 行 4 轮 + b6 CSS 1 轮 420s reap=本机 Qwen 18002 队列 3-4 并发饱和**（vllm metrics 实测，非工具缺陷），b7-b10 未起跑。
- 裁决/状态：**07B 不合入**（OCR 门禁未收口）；B=交付冻结 REVIEW_PENDING；恢复入口=b5 再 2 轮 reap→`--max-tokens 30000` 降组或 NEEDS_MAIN_REVIEW，不无限重试；b3 裁决前置=OCR 收口（避免返修作废旧批）。
- 强审查：AUTHORIZED（grant `31dcbabe` 24h 至 2026-10-13 11:33:12），60min 0/5、累计 0、token 未知；07B 写接口面预判 REVIEW_NOW，待 OCR 收口后 pack，本轮不起跑。
- 门禁变化：TASK-07 RUNNING 不变（07A DONE main `caf385b`，07B 交付核验过、OCR 部分收口）；TASK-10 DONE、TASK-11 PRODUCTION BLOCKED、12-15 DEFERRED 均不变。
- 下一步：后续轮续跑 b5-b10 → OCR 收口后裁决 b3 medium（最小返修面=单文件 API 守卫）→ 强审查 pack → 合入 → TESTER 独立验证（派单第四节口径）→ 07B DONE → 派 07C。
- [2026-10-12 19:3x pending] TASK-07B 串行 OCR b5（`scene_manual_revision_service.py` +383）：前台 5 次 420s reap + r93 后台 pid 414832 随会话回收后，r94 于低负载窗口（18002 vllm 1 running/0 waiting 实测）以 Hermes 后台跟踪重启（`proc_7ea84d1aecc6` pid 434432，`--max-tokens 30000`，flock 持 `inbox/ocr.lock`）；OCR 4/10 收口不变（b1 迁移 0 / b2 api 注册 0 / b3 **1 medium CORRECTION 待裁决** / b4 models 0）；交付 `f4bfcf2` 仍 REVIEW_PENDING 未合入。

## 2026-10-12T21:55:00+08:00 TASK-07B attempt-1 OCR 收口推进 + CONFIRMED CORRECTION 裁决
- r95 detached 串行 OCR 21:26:34 收口收尾两批：b9 `app/templates/detail.html` RC=0（3 findings：1 HIGH + 2 LOW）+ b10 `app/web/bags.py` RC=0（0 findings）→ 累计收口 8/10。
- 协调者独立核代码确认两条 CONFIRMED CORRECTION：①b9-1 HIGH——detail.html:52 `corrected_label` 下拉列 7 选项（含 construction/congestion/night/rain/other），服务 `_VALID_LABELS`={slope,flat,unknown}，f4bfcf2 只改 service+tests 漏改模板 → 5 项提交必 422、合法 unknown 无选项（违反 AC-04 人工纠错可用性）；②b3 MEDIUM——scene_manual_revision.py `request.json()` 非 dict → 500 与文档化 422 面不一致。b9 LOW×2 + b8 LOW 非阻塞，随同一返修合并。
- b5（核心 service +383）/b7（css）低负载期（vllm running=4/waiting=1）`--resume` 最后一次 INFLIGHT（detached pid 607379，21:59 起）；再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁。
- 返修暂缓：等 b5/b7 收口后全部 findings 并入一次最小返修派 B（避免移动 HEAD 使在途 resume 失效）。
- 未生成正式功能 released 日志；无业务合入、无生产动作。

## 2026-10-12T23:05:00+08:00 TASK-07B attempt-1 串行 OCR 10/10 全收口 + R2 最小返修派发

- OCR 收口闭环：b5 `scene_manual_revision_service.py`（+383 核心服务面）resume 最后一次 RC=0 1800s（session 7d703528，3 findings）+ b7 `bag-search.css` resume 最后一次 RC=0 839s（session 997d0ddd，3 findings），22:43:38 detached done 落盘、无 NEEDS_REVIEW 文件；10 批合计 5 处 CONFIRMED CORRECTION + 6 处 LOW（b9-1 模板选项域 vs 服务校验域 HIGH / b3 非 dict JSON 500 vs 422 / b5-1 乐观锁非守卫写入 / b5-2 evidence 查询无 limit(1) / b7-1 下架徽章布局错位）。
- 协调者独立核代码裁决 v2 落盘（`inbox/coordinator/TASK-07B/ocr-r102-closure-ruling.md`）；R2 最小返修一次派 B（问题 ID 单 R2-1~R2-10，4 必改文件+1 可选，base f4bfcf2 续 commit，零新迁移零新依赖）。
- 未合入：07B 维持 REVIEW_PENDING（f4bfcf2）等 R2 交付→增量 OCR→强审查（24h 授权在案 0/5 期限 2026-10-13 11:33:12）→合入→TESTER 独立验证。TASK-16A（A 已 ACK 开工）/16B（C 已 ACK 开工）并行推进。
- 未生成正式功能 released 日志；无业务合入、无生产动作。


## 2026-10-13T01:45:00+08:00 07B R2 收口（OCR 5/5 + 强审查起跑）+ 16A/16B 交付冻结核验 + 串行 OCR 起跑（无合入）

- **07B（B，attempt-2-r2 `68b5188`，REVIEW_PENDING 未合入）**：R2 增量 OCR 5/5 全收口 rc=0（r105 detached 01:07:33 done；新 findings 仅 3 low 全在 api 文件=尾换行 R2-7 遗漏 + `raise from exc` maintainability 建议，**无 CORRECTION 级、不触发 R3**；r2b2 1 条 review_round_failed WARNING=round2 LLM deadline 偶发，findings 已产出非空跑）；协调者独立复跑全量 836 passed/1 failed（web 性能计时环境性，base 复现口径）。**强审查 REVIEW_NOW 01:49 起跑**（用户 24h 授权内，grant `31dcbabe…` 期限 2026-10-13 11:33:12，codex call `50c665e4…`，pack=`SR-07B-A2R2-20261013-pack.md`，冻结 target `68b5188`；审查面=R2 并发守卫/幂等/审计顺序语义 R1-R4，弱 OCR 行级能力边界外）；结果返回后分类裁决→合入（**迁移链顺序=07B 先**）→TESTER 独立验证（真 MySQL 并发守卫 409，B 申报留项）。证据：`receipts/TASK-07B/attempt-2-r2.md`、`reviews/TASK-07B/attempt-2-r2/ocr-batches.md`、`/home/wang/.hermes/cache/scratch/t07b_r2_ocr/`。
- **16A（A，`c30f048`+`79f6889`，REVIEW_PENDING 未合入）**：16 文件 +1147/-59 场景接收隔离（三根契约/Scanner 双根/profile intake_root_id 迁移/登记身份防线/用途路由零 Phase0）；协调者机械核验全绿（定向 25 passed 独立复跑、零 07B 冻结文件、merge-tree 干净）；**合入门禁=串行 OCR 14 app 文件在途 + 07B 合入后迁移 rebase 双头**；TESTER 16D 前独立验证。证据：`receipts/TASK-16A/attempt-1.md`、`reviews/TASK-16/16A-16B-ocr-batches.md`。
- **16B（C，`0208a73`+`9437308`，REVIEW_PENDING 未合入）**：5 文件 +2543/-0 处理机常驻场景代理（proxy 968 行 /run 台账幂等+kill -9 恢复+租约续写 / orchestrator 583 行八步编排 / 假 VLM 带宽证据面）；协调者机械核验全绿（定向 26 passed 独立复跑、零 app 越界、r104 预冻结口径核实=proxy 在位正常 OCR 路径）；**合入门禁=串行 OCR 3 文件在途（16A 后接）**；real 栈全链冒烟留 16A 接受后接续（16D 前）。证据：`receipts/TASK-16B/attempt-1.md`。
- 16A/16B 串行 OCR：01:49 detached 起跑（pid 959241，flock `inbox/ocr.lock`，§3.6 大文件独立批 `--max-tokens 30000`，tests 先例排除，单批 >30min 无收口记活动停滞告警不无限重试）。
- 未合入/未推 origin/无生产动作；TASK-11 生产门禁维持 PRODUCTION BLOCKED；12-15 DEFERRED 不变；16C 待 B 释放（07B 合入后）、16D WAITING 三前置。正式功能日志：本轮无完整功能收口（07B/16A/16B 均未合入），pending 候选待 07B 合入后随交付生成。


## 2026-10-13T02:15:00+08:00 07B 强审查返回 REWORK_REQUIRED + R3 返修派单 + 16A/16B OCR v2 纠正（无合入）

- **07B 强审查收口**（SR-07B-A2R2-20261013，call `50c665e4…`，02:06 SUCCEEDED）：**REWORK_REQUIRED**，4 CORRECTION（SR-01 纠错值未持久化 high / SR-02 守卫前关联 INSERT 并发 high / SR-03 幂等漏有效操作者 med / SR-04 再纠错覆盖首次模型投影引用 med）+ 1 VERIFICATION_GAP（SR-05 真并发 409 未验证 high）；协调者对 target `68b5188` 代码逐条核实全部属实（非误报）。tokens：in 656176（cached 569728）/ out 9229 / reasoning 4355，费用未知。结果 `reviews/strongmodel/runs/50c665e48cb3465c95d29da7bf1446ce/result.md`。
- **R3 最小返修单派 B**（`inbox/2号/TASK-07B/attempt-3-r3-dispatch.md`，base `68b5188` 续 commit，问题 ID R3-1~R3-4；改未合入原迁移加列口径，SR-05 真 MySQL 双连接取证留 TESTER post-r3 独立验证单避免自证）；07B 维持 REVIEW_PENDING 未合入（强审阻塞门禁在案）。
- **16A/16B 串行 OCR 纠正重跑**：v1（01:49 pid 959241）`-c <target>` 单 commit 口径漏审第一 commit 新增文件（两 commit 链）→ 02:03 kill；v2（02:04 pid 980094，`--from c2018dd --to HEAD` 逐文件范围模式）detached 在途，16A 14 批 + 16B 3 批（>500 行 `--max-tokens 30000`），账 `reviews/TASK-16/16A-16B-ocr-batches.md`；16A/16B 交付冻结 REVIEW_PENDING 不变，合入顺序=07B 先→16A 迁移 rebase 双头→16B 随批。
- 无合入/未推 origin/无生产动作。强审查授权：60min 1/5、累计 1、期限 2026-10-13 11:33:12；R3 收口后增量复审预计再 1 次（额度内）。

## 2026-10-13 05:53 16B proxy OCR NEEDS_REVIEW + 16A 增量 OCR 起跑

- **16B proxy OCR 3 次失败→NEEDS_REVIEW**：`scripts/scene_host_proxy.py`（968 行）首跑 rc=1（1440s LLM 队列超时，session `e2b8a607`）→ resume rc=1（1440s，session `10b08d5e`）→ 拆组 `--max-tokens 20000` rc=1（336s，session `2abf70dd`）。3 次均为外部 LLM 队列超时（budget_exceeded=false，vllm 18002 低负载），非工具/diff 问题。**16B 合入门禁冻结**（r125 既定政策）。
- **16B 已裁决 findings 暂缓返修**：orchestrator H1（EXTRACT stamp 先于 manifest 赋值→崩溃恢复重复计费）/M1（fail() 死代码+FAILED checkpoint 缺 manifest）/M2（DONE 前置跳过 evidence 审计缺口）=3 CONFIRMED CORRECTION（r123）+ fake_vlm medium/low 2 findings（r121）已裁决，返修单等 proxy OCR 解除后一次最小返修单派 C。
- **16A 增量 OCR 起跑**：b2 退出释放 `ocr.lock` 后，16A attempt-2-r1 增量（c30f048→3aee4d1）3 批逐文件单批起跑（pid 1284380，a-runner INFLIGHT）。16A 不受 16B 冻结牵连。
- **后续串行**：16A 增量→07B R3 增量 6 批→R3 强审增量复审→TESTER 07B-post-r3→07B 合入→16A 收口→16B 解除（proxy OCR 重试/裁决）→16B 收口→派 07C/16C。


## 2026-10-13 07:4x 07B R3 增量 OCR 收口 + R4 返修交付 + 强审增量复审 REWORK_REQUIRED + R4-01 契约裁决（无合入）

- **07B R3 增量 OCR 6/6 全收口**（r128-r130，06:37:35 done）：r3-1 迁移 rc=0 599s **2 findings（1 medium+1 low）** / r3-2~r3-6 全 0 findings（账 `reviews/TASK-16/16A-16B-ocr-batches.md` r130 段）。r3-1 medium=CORRECTION（downgrade 表存在守卫丢失，`68b5188` 原 no-op 安全被 R3 改写破坏）+ low=documentation（drop_column 往返风险未同步 docstring）→ **R4 最小返修单派 B**（r130 06:54，base `4baf79f` 仅迁移单文件 2 项，同根因两轮失败=升级用户）。
- **07B R4 交付核验**（B `62620a3` 07:15 交付冻结，base `4baf79f` 单 commit，迁移单文件 +31/−11）：协调者独立机械核验全绿（定向 12 passed 复跑 / ruff 单文件绿 / alembic 单头 `20261012_01_scene_manual` / diff 逐行零越界零 app 面 / ANCESTOR_OK）；**独立探针 `coord_r133_probe.py` 证 B 越界申报成立**——原始 `68b5188` 与 R3 `4baf79f` 表缺失态 downgrade 均在 `_indexes_of`→`get_indexes` 抛 NoSuchTableError（非派单 §一假设的 no-op 安全），R4 提升守卫覆盖整个表依赖块后 NO_EXCEPTION，故按 §三验证口径实现合理。R4 增量 OCR 单批 0 findings（session `5b9cc87c`）。
- **07B 强审增量复审 REVIEW_NOW→REWORK_REQUIRED**（call `a8febf1a19444ef9bd456c508c94b397`，r133 07:41 收口，grant `31dcbabe…` 期限 2026-10-13 11:33:12，rolling 60min 1/5、本授权累计 2，tokens in 530310/cached 471552/out 8293+reasoning 4334，费用未知）：唯一问题 **R4-01 medium CORRECTION**=「审计表缺失+evidence 列存在」合成态 downgrade 不抛异常但 drop evidence 列（值丢失），阻塞依据是协调者强审包 §2 不变量 3「全 no-op」措辞；R4 其余面（upgrade 零改动 / 正常态逐语句一致 / 越界申报成立不改正常态顺序 / docstring 同型先例 / 单头不变）全过。结果 `reviews/strongmodel/runs/a8febf1a…/result.md`、pack `reviews/TASK-07B/attempt-4-r4/strong-review/SR-07B-R4-20261013-pack.md`。
- **协调者契约负责人裁决 R4-01 非原 AC 违例、不返修**（`inbox/coordinator/TASK-07B/r4-01-adjudication-20261013.md`）：独立探针 `coord_r133_r401_probe2.py` 核实——该合成态**不可由正常 partial-upgrade 产生**（upgrade 先建审计表@L57 后加 evidence 列@L90，evidence 列无孤立态）；evidence 列 drop 是本迁移 upgrade 的对称逆操作（同对象 add↔drop）；R4-2 docstring 已文档化该值丢失=既定接受语义；审查者建议 early-return 会留孤立 evidence 列（upgrade 加/downgrade 没删）=行为回归故不采纳。冻结原始既定 AC（R4 派单 §三「表缺失态 downgrade 不抛异常」）R4 实测满足=修复有效；「全 no-op」系 pack 过度精确表述（已回改 pack §2 不变量 3=「审计表依赖块不抛异常」，澄清范围回冻结基线，审查者自留「契约负责人修正表述」口子）。
- **TESTER 07B-post-r 已派**（`inbox/TESTER/TASK-07B/post-r-dispatch.md`，target 固定 `62620a3`，PENDING 待 ACK）：07B 合入门禁唯一独立缺口=**07B-SR-05**（R2 强审高 VERIFICATION_GAP，真 MySQL 8.4.11 隔离库双连接同版本无关联子切片并发纠错 200/409 未验证，验 service 守卫并发语义 SR-02 修复面，与 R4 迁移面独立）+ R4 迁移面双库探针 + 07B 定向回归。**07B 当前不合入**（SR-05 未解除）；PASS→07B 整链合入（--no-ff，先于 16A rebase 双头）→07B DONE→派 07C/16C，FAIL→回派 B 定位（同根因两轮升级用户）。
- 无合入/未推 origin/无生产动作；16A 交付冻结 `3aee4d1`（等 07B 先合入 rebase 双头）/16B NEEDS_REVIEW 冻结维持；TASK-11 生产门禁维持 PRODUCTION BLOCKED；12-15 DEFERRED 不变。正式功能日志：本轮无完整功能收口（07B 未合入），pending 候选待 07B 合入后随交付生成。

## 2026-10-13 08:4x 07B 整链收口 DONE + 合入 `4b9f30a` + 16A rebase/16C 派单 + 16B proxy OCR 低负载第 4 次重试

- **07B（人工纠错/下架）收口链闭环**：TESTER 07B-post-r **08:21 交付 PASS 4/4**（`test-receipts/TEST-TASK07B-post-r/attempt-1.md`：SR-05 真 MySQL 8.4.11 独占容器双连接同版本无关联并发恰 200/409 守卫拒绝语义非 500 + row_version 只+1 + 审计恰 1 条 + MANUAL evidence 恰 1 行 / R4 迁移面真 MySQL+SQLite 双库 upgrade-downgrade-upgrade 三往返 RC=0 + 表缺失态 downgrade 不抛异常 + 新库数据可写抽查 / 定向 12 passed / 页面真实 HTTP 6 项口径（纠错表单/人工标签渲染/审计表/下架退出默认检索 all 可见）；环境用完即毁 0 残留）→ 合入门禁剩余证据全部解除。
- **合入**：07B 整链（`5fa0942`→`f4bfcf2`→R2 `68b5188`→R3 `4baf79f`→R4 `62620a3`，5 commit）`--no-ff` 合入 main **`4b9f30a`**（merge-tree 预核零冲突；合入前主仓 12 个诊断 untracked 文件 git reset 清出暂存区）→ 合入后 sanity 独立复跑全绿（alembic 单头 `20261012_01_scene_manual` / ruff 3 文件绿 / 07B 定向 12 passed RC=0）→ 双推 origin `4b9f30a`/github `4b9f30a` 一致。**07B 裁决 DONE**（decision `inbox/coordinator/TASK-07B/07b-done-merge-decision-20261013.md`；强审两轮 REWORK_REQUIRED 全闭环：R2 4C+1GAP→R3 修复→R4 增量复审 R4-01 契约裁决非 AC 违例；OCR 22 批全收口零未闭环 CORRECTION）。
- **正式功能日志**：F-040 `scene-manual-revision-withdraw` **pending 候选随交付收口生成**（`changelog/pending/scene-manual-revision-withdraw.yaml` + REVIEW.md 渲染，commit `3d2a075` 双推；标题/摘要/4 功能点按 changelog-workflow 口径写使用结果；**待用户批准，不自行 approved**）。
- **接续派单**：16A 双头前置解除 → **attempt-3-rebase 迁移接线单派 A**（`inbox/1号/TASK-16A/attempt-3-rebase-dispatch.md`：rebase 3 commit 链到 `4b9f30a`，仅 `20261013_01_scene_intake.py` down_revision 改接 `20261012_01_scene_manual`+自测；merge-tree 预核 `app/models.py` 自动合并零冲突）；B 释放 → **16C attempt-1 派 B**（`inbox/2号/TASK-16C/attempt-1-dispatch.md`，base `4b9f30a`，§8.4 口径：`GET /api/v1/bags` 集合路由+三视图/八步详情补齐，保留 07B 审计/修订面，文件边界按 §8.1）。
- **16B 冻结分支执行**：proxy OCR 低负载窗口（vllm 18002 起跑前实测 running=4/waiting=0）**第 4 次重试 detached 起跑**（pid 1516687 08:40:28，flock `ocr.lock`，机制复用 r125 拆组口径 fresh `--max-tokens 20000 --timeout 12`，硬截止 **09:20**；政策不变：rc=0→b1 H1/M1/M2+b3 2+proxy 全合并一次最小返修单派 C，rc=1→NEEDS_REVIEW 维持冻结**升级用户裁决不再自动重试**）。
- 门禁/角色：07B DONE 合入门禁解除；16A 合入门禁维持（rebase 单在途+TESTER）；16B 冻结（重试在途）；16D WAITING 三前置不变；TASK-11 生产 BLOCKED；12-15 DEFERRED。角色占用：A=16A rebase 待 ACK、B=16C 待 ACK、C=16B 冻结等重试、TESTER=空闲（07B-post-r 已交付收口；16A 验证单待 rebase 合入后 target 固定再派）。强审查授权期限内本轮零新增调用（滚动 60min 1/5 沿 07:4x 账）。


<!-- runtime-optimization-event-snapshot-20261013 -->
- 2026-10-13T09:41:33+08:00：角色运行优化已部署：5分钟脚本检查/事件唤醒，所有周期汇报no_agent短快照；协调者20分钟调度复核，原任务、分支、OCR与强审查门禁保持。模型处理后指纹ack，不预消费事件。Skill协调者/规划者1.3.0，执行者/测试者1.2.0。详细证据与回退：`/home/wang/work/doc/analysis/hermes-qwen-load-20261012/IMPLEMENTATION-20261013.md`；备份：`/home/wang/.codex/skill-migrations/event-snapshot-20261013-092938`。已在途旧回合自然结束，新轮实际ack跟踪中；未额外发群消息、未新增付费授权。

## 2026-10-13 09:4x TASK-16A 收口 DONE（TESTER post-merge 验证 PASS，main `6fb42c4`）

- **验证**：TESTER `t16a-post-merge-verify` attempt-1 09:32 交付 **PASS 3/3 范围项**（`test-receipts/TEST-TASK16A-post-merge/attempt-1.md`）：真 MySQL 8.4.11 隔离容器全链迁移三趟 RC=0（fresh `20260911_01`→head `20261013_01_scene_intake`→downgrade 至 `20261012_01_scene_manual` 双列 drop→再 head 双列恢复，`alembic_version` 序列取证，25 字符短名无 1406）；AC-14/08 迁移承载字段 MySQL 取证（`intake_root_id varchar(16) NOT NULL DEFAULT 'self_built'`+`ix_ingest_profile_root_enabled` 在列+历史行回填 IS NULL 计数 0、行身份不变）；SQLite 定向 7 文件 68 passed（16A 56+07B 12）。已知观察项 `test_web` 单跑顺序依赖失败=基线 `502bf8e` 既有，非 16A 回归（协调者 r138 独立二分口径，全模块 41 passed）。
- **裁决**：TASK-16A **DONE**（main `6fb42c4`=origin=github 三核一致；OCR 17 批全闭环零未闭环 CORRECTION：v2 14/14+增量 3 批+接线批 0 findings；强审查 NOT_REQUIRED=低风险接线面口径，decision `inbox/coordinator/TASK-16A/t16a-post-merge-verify-acceptance-decision-20261013.md`）。
- **角色/门禁**：A 释放转空闲待命（无满足条件叶任务，不扩需求）；B=16C RUNNING（记账修正，已 ACK 开工）；C=16B 冻结交付 `0208a73`（NEEDS_REVIEW，proxy OCR 4/4 连败待用户裁决）；16D 前置 16A 已接受、16B/16C 未完；TASK-11 生产 BLOCKED、12-15 DEFERRED 不变。
- **遗留**：16B real 栈全链冒烟（C 留项）待 16B 收口后 16D 前执行；F-040 pending 候选待用户批准；16A 正式功能日志候选待 16 聚合 DONE 时按整功能口径生成，不单独发布。

## 2026-10-13 10:2x TASK-16C 交付核验 + rebase 接线 + TESTER 独立验证派单（B 交付冻结 `ad37ae1`→接线 head `5c80857`）

- **B 16C attempt-1 交付冻结**（09:59，`ad37ae1` 8 文件 +957/−33，回执 `receipts/TASK-16C/attempt-1.md`）：场景八步详情（真实 StepRun 构建、终态停刷新、无 A100 面、NO_MATCH/NOT_APPLICABLE 区分不伪标 SUCCESS）、`GET /api/v1/bags` 集合路由（view/data_kind/dataset_type/purpose/时间边界/cursor，clamp 50..200，路由顺序先于 `/{bag_uid}` 已核）、data_kind 四类谓词+双用途双标（Web/API 同源 `data_kind_case`/`originals_view_condition` 不分裂）。自测 15 新用例全绿、全仓 876 passed/4 failed 均 base 既有（stash 复跑同口径）、ruff 绿、越界申报=无（`vehicle.name`→`vehicle_code` 为既有 `_bag_summary` 缺陷修复，非本单引入）。
- **协调者 r142 机械核验全绿**：base `4b9f30a` 与当前 main `6fb42c4`（16A）合入 19 文件**零交集**（comm 独立核）→ 协调者 rebase 接线单头（16A 已先合入 main，双头口径）→ 新 head **`5c80857`**（`6fb42c4` 祖先链，`git diff 4b9f30a ad37ae1` 与 `git diff 6fb42c4 5c80857` **逐字节一致**，rebase 后 15 用例复跑全绿，merge-tree 零冲突，路由顺序独立复核）。
- **OCR 面排队**：16C 7 非测试文件（§3.6 尺寸预检：无 >500 行文件，最大 pipelines.py +161/bag_search_service.py +135/scene_result_query.py +80，纯 SELECT 谓词无 DDL）排 16B proxy 第 7 次（在途持 `ocr.lock`）收口后逐文件小批串行。
- **TESTER 独立验证派单**（`inbox/TESTER/TASK-16C/t16c-independent-verify-dispatch.md`）：固定 head `5c80857`，§8.4 浏览器/API 清单 9 项（三类原始/切片/双用途/不相容空结果/集合路由/八步详情/运行环境区/旧界面兼容/SQLite 回归），本单无 DDL 不要求真 MySQL；不得触碰 16B worktree 与 `ocr.lock`。
- **并行事实**：16B proxy OCR **第 7 次在途**（r141 10:16 起跑，用户裁决「最优方式重试」口径=临时切 provider 直连 `192.168.2.45:8002/v1` 绕 18002 双跳 SSH 隧道掐长请求根因，finally 自动恢复配置，硬截止 11:16；rc=1→NEEDS_REVIEW 维持冻结升级用户 a/b/c 不自动第八次）。16A DONE(main `6fb42c4`)、07B DONE(`4b9f30a`)、16C REVIEW_PENDING、16B 冻结、16D WAITING 三前置未齐。强审授权期限 2026-10-13 11:33:12 内本轮零新增调用（60min 0/5、累计 2、在途 0、费用未知）。
- 下一步：16B 第 7 次收口→(rc=0) 16C 7 文件 OCR 串行→16C OCR 裁决→TESTER 16C 独立验证→16C 合入→DONE；rc=1 则 16B 维持冻结等用户 a/b/c 裁决。F-040 候选待用户批准。


## 2026-10-13 10:4x TASK-16B proxy OCR 第 7 次 rc=1（7/7 连败升级用户裁决）+ TASK-16C OCR 串行接续起跑

- **16B proxy OCR 第 7 次收口 rc=1 = 7/7 连败**（r141 用户裁决「最优方式」=直连 `192.168.2.45:8002`，授权内最后一次）：10:16:21 START → **10:32:51 DONE rc=1 dur=16m30s**（session `ba32eca1`，`scene_host_proxy.py` context compaction 阶段请求级 cancelled，in 160011+out 64415 budget_exceeded=false）。连败链 7/7：首跑 1440s / resume 1440s / 拆组 336s / retry#4 720s / retry#5 fresh+resume 双败 / 第 6 次 planning 275s cancelled 确诊 / 第 7 次直连 16m30s cancelled。**r143 实测环境根因=18002 双跳 SSH 隧道已断（Connection refused）、直连 8002 可用（http 200 / 0.06s）**——隧道是前 6 次底层环境根因，直连绕开隧道仍败于 LLM compaction 取消。
- **阻塞变化（升级用户裁决，不自动第 8 次）**：16B 维持 **NEEDS_REVIEW 冻结**、合入门禁关闭。已裁 findings 在案（orchestrator b1 H1/M1/M2 CONFIRMED CORRECTION + b3 fake_vlm 2 findings）但返修单暂缓。待用户 a/b/c：a) 修隧道或换审查方式再试 b) proxy 968 行更小拆组 c) 按已裁 findings 先行一次最小返修单派 C、proxy OCR 缺口记 NEEDS_REVIEW 遗留（d) 搁置 16B。
- **16C OCR 串行接续（本轮控制动作）**：16B 第 7 次 rc=1 释放 `ocr.lock`（fuser 核无在途）后，16C 7 非测试文件逐文件单批链 detached **pid 1682826**（10:39:01 START，首批 `app/web/pipelines.py` 在途）——`--from 6fb42c4 --to 5c80857` head 固定 `5c80857`，§3.6 尺寸预检 7 文件均 <500 行 diff 无需 max-tokens 拆组（pipelines +176 最大），tests 466 行按先例排除挂 TESTER；任一批 rc=1 单批 `--resume` 最后一次再败挂 NEEDS_REVIEW 冻结 16C 合入门禁（TESTER 独立验证不受牵连可并行取证）。
- **16C TESTER 独立验证 ACKED 在途**（10:33:33，`t16c-independent-verify-ack.md`）：固定快照 `5c80857`（独立核 diff 与 `4b9f30a..ad37ae1` 逐字节一致 sha256 8f0f0437…），worktree 起服务不切 main，不触碰 16B wt 与 ocr.lock，8.4 清单 9 项取证，报告 `test-receipts/TEST-TASK16C-independent/attempt-1.md` TEST_REPORT_PENDING。
- **状态汇总**：16A DONE（main `6fb42c4`）、07B DONE（`4b9f30a`）、16C REVIEW_PENDING（OCR 7 批在途 + TESTER 独立验证在途，双证据待收口后合入→DONE→16D 前置 2/3）、16B NEEDS_REVIEW 冻结（等用户 a/b/c）、16D WAITING 三前置未齐（16B 未接受）。强审期限 2026-10-13 11:33:12 内本轮零新增调用（60min 0/5、累计 2、在途 0、费用未知）。


## 2026-10-13 11:0x TASK-16C 串行 OCR 2/7 收口 + C5 双用途筛选 CORRECTION 裁决

- **16C OCR 链推进（2/7 rc=0）**：c01 `app/web/pipelines.py` 4 findings 全 low——协调者独立核=C1(:111 死分支)/C2(:163 死参数)/C3(:628 `scene_terminal` 模板零引用) CONFIRMED 死代码维护项 + C4(:113 冗余分支)**驳回**（与 C1 冲突：`run_failed` 集合实测不含 INPUT_INVALID，场景 SCENE_* 状态集无 INPUT_INVALID，「终态停刷新」口径与 16C 自身取证一致）；c02 `app/services/bag_search_service.py` 2 findings 全 medium——**C5(:312 双用途筛选与双标展示不一致) CONFIRMED CORRECTION**（CASE 单值口径致 `data_kind=self_built_original` 筛选漏双用途原包，`data_kind_context` 双标展示与 DESIGN §7.3.3 明文「可同时显示两个类型标记并命中两个筛选」冲突，代码注释亦自述「均可命中」）+ C6(:73 `data_kind_labels_for` 全仓零调用死代码) CONFIRMED。c03 `scene_result_query.py` 在途，c04~c07 排队（`--from 6fb42c4 --to 5c80857` head 固定）。
- **TESTER 16C 独立验证 PASS 交付（10:47）**：9 项场景取证全过（自包含 uvicorn 58 项探针+浏览器走查+集合路由 cursor/limit/422+八步详情+环境区+旧界面回归）、SQLite 全仓 898 passed 4 failed 均 base 既有、0 残留；MySQL 面口径=本单无 DDL 仅 SELECT 谓词不要求真 MySQL。16C 双证据面=TESTER PASS 已齐 + OCR 收口中（C5 返修后需 TESTER 复测谓词子项）。
- **16B 交互会话面记账（协调者不代管）**：用户 10:47 问询「为什么不用 --rule 提回合」后 10:48 挂 proxy OCR 第 8 次等待器（`--effort low`+6 项不变量背景约束+直连 8002+900s，对症 MAX_REVIEW_ROUNDS=2 长对话收敛失败真实终因；兜底 `ocr delegate` 规格+宿主代审口径在案），等 16C 链收口后自动接跑；r143「不自动第 8 次」政策由交互会话用户动作取代，16B 合入门禁维持关闭。
- **状态**：16A DONE（main `6fb42c4`）/07B DONE（`4b9f30a`）/16C REVIEW_PENDING（**合入门禁关闭=C5 CORRECTION，全批收口后一次最小返修单派 B**）/16B NEEDS_REVIEW 冻结（第 8 次等待器在途）/16D WAITING 三前置未齐。强审授权期限内（11:33:12）本轮零新增调用（60min 0/5 累计 2）。


## 2026-10-13 13:4x TASK-16B attempt-2-r1 交付冻结 + 机械核验全绿（增量 OCR 排队，未合入）

- **范围**：TASK-16B 处理机常驻代理最小返修 attempt-2-r1（proxy OCR 第9轮 7 findings 全 CONFIRMED），C `40ab818`（2 文件 +220/-11，base `0208a73`，仅 `scripts/scene_host_proxy.py` + 其测试，零越界）。
- **交付与核验**：13:38 交付 REVIEW_PENDING → 协调者独立机械核验全绿（`merge-base --is-ancestor` OK、numstat 43/10+177/1 与回执逐文件一致、wt 独立复跑定向 20 passed 12.16s、ruff/compileall clean）；修复面=H1 TOCTOU 接原子返回值 / H2 终态 post 前刷新 cur / H4 except Exception 扩失败收尾 / H5 config_hash 快照比对 fail-fast 下限（快照 entry 不存提交参数，取派单承认的下限口径）/ H6 fsync-before-replace / L1 attempt 过滤。
- **OCR**：增量批排队 `--from 0208a73 --to 40ab818`（单非测试文件小批，接 12S-B 链 c01/c02 后持 `ocr.lock` 串行），未收口不合入；12S-B c01 在途（pid 1897396，session `080bc21b` 13:42 仍写，健康）。
- **门禁变化**：16B 维持 REVIEW_PENDING 未合入（合入门禁=增量 OCR 零 CORRECTION + 强审 pack（6 修复范围）+ TESTER 面按既定口径）；12S-C 依赖（16B+12S-A+12S-B 已接受）继续不齐；TASK-11 生产 PRODUCTION BLOCKED 不变。
- **强审查**：授权 `auth-24h-20261013` 生效（grant `6b2d83fb9`，10-13 13:27:15 → 10-14 13:27:15），近 60min 0/5、本授权累计 0、在途 0；pack 待 OCR 收口后按范围判定，不提前调用。
- **下一步**：12S-B c01 收口裁决 → c02 → 16B r1 增量 OCR → 12S-A 增量 OCR → TESTER 12S-B 独立验证派单 → 16B 收口后重算 12S-C 依赖。正式功能日志随合入/验收后生成候选，不自行批准/发布。

## 2026-10-13 13:5x TASK-12S-B 串行 OCR c01 收口 8 findings 全 CONFIRMED + 合并返修裁决（未合入）

- **范围**：TASK-12S-B 水雾能力 attempt-1（spray 适配器 13 文件 +3136，head `f62a29c` base `6fb42c4`）串行 OCR c01 核心算法面（adapter/decode/render/model/segment 5 文件）收口 rc=0，session `080bc21b`，8 finding，~853862 tokens，23m5s。
- **裁决**：协调者逐条只读核 `wt-04a-t12sb` 代码实测 **8/8 CONFIRMED 误报 0**——S1[HIGH] 小图删除后模型循环仍遍历 `rendered_frames` 致 `FileNotFoundError` + 喂被过滤帧 + 时间轴/缓存帧数错位；S2[MED] 全新相对 `work_dir` 穿透 `exists()` 守卫 mkdir 落 CWD；S3[HIGH] `parse_pointcloud2` 固定尺寸读无越界守卫，截断 bag `struct.error` 逃逸 `_decode`（仅捕 `DecodeError`）破坏"存在但解不出=FAILED(DECODE_FAILED)"契约；S4[HIGH] intensity 未按 ROI mask 致 `cloud.colors` 恒不设置、强度水雾判别失效；S5/S6/S7[LOW] pcd_path 死分支、pointcloud 路线无 cancel_check、逐点上色热路径；S8[LOW] auto 双缺 topic 误报"未知路线 'auto'"。S1/S2/S3/S4/S8=CORRECTION 级，S5/S6/S7=维护项。
- **收口链**：c02 辅助配置面（7 文件）在途健康（node pid 1926290，13:51 START）→ 收口后合并 S1-S8+c02 findings **一次最小返修单派 B**（16C r144 同口径，不逐批返修）→ 交付冻结 → 机械核验 → 返修增量 OCR（小批）→ TESTER 独立验证（真实 decode/render/VLM 面留 TESTER 域）→ 合入 main → 12S-B DONE → 重算 12S-C 依赖（16B+12S-A+12S-B）。16B r1 增量 OCR 与 12S-A 增量 OCR 继续排队于 12S-B 全链后（`ocr.lock` 串行）。
- **门禁变化**：12S-B 维持 REVIEW_PENDING 未合入（3 个 HIGH 功能性缺陷未修，合入门禁关闭）；12S-C/12S-D 依赖继续不齐；16B/12S-A 面不变。
- **强审查**：本轮零新增（12S-B 强审判定待 OCR 全链收口+返修后按范围执行，grant `6b2d83fb9` 至 10-14 13:27:15，近 60min 0/5）。
- **证据**：`reviews/TASK-16/16A-16B-ocr-batches.md` r156 段；`~/.hermes/cache/scratch/t12sb_ocr/progress.txt` + `c01.log` 全文；`TODO.md` r156 段。候选日志，不自行批准/发布。

## 2026-10-13 15:2x TASK-16B r1 增量 OCR 收口 + 强审 SR-16B-R1 REWORK（5 项）+ r2 派 C（未合入）

- **范围**：TASK-16B 处理机常驻代理 attempt-2-r1 收口链（`40ab818`，6 修复 H1/H2/H4/H5/H6/L1）。
- **OCR**：固定入口 `ocr_runtime.py` 增量 run `0a77a83f`（`0208a73..40ab818`，单业务文件批）14:49:10 收口 **rc=0 0 findings**，coverage 1/1 fingerprint 匹配，971s；proxy OCR 9 轮连败后首次以固定入口闭环。
- **强审查**：`SR-16B-R1-20261013`（call `e7d6b921`，授权 `6b2d83fb9` 内第 1 次消费，1356669 in/9100 out/3838 reasoning，费用未知）**REWORK_REQUIRED=5 项阻塞全 CORRECTION**——R1-01[H1 高] worker 释放 ACTIVE 后迟到重复 /run 可再执行同 attempt（重烧模型）；R1-02[H2 高] 终态 post 失败无对账补报，步骤永久卡 RUNNING；R1-03[H4 高] _finish_failure 吞 SCENE_FAILED 上报异常仍清 recovery，失崩溃恢复入口；R1-04[H4 中] unlink 异常中断收尾 ACTIVE 幽灵残留；R1-05[H6 中] 原子写 replace 后未 fsync 父目录，首次创建台账掉电丢失。强审同时确认 H2 cur 刷新/H5 哈希口径/L1 attempt 过滤与代码契约相符（误吞窗口无独立反例）。
- **收口链**：r2 最小返修单已派 C（`inbox/3号/TASK-16B/attempt-2-r2-dispatch.md`，base `40ab818` 续 commit，5 条逐项+故障注入矩阵，12S-C 前置暂停等 r2）→ 机械核验 → 返修增量 OCR（固定入口）→ 强审增量复审（只 5 问题 ID，授权剩 4/5）→ TESTER → 合入 16B。
- **门禁变化**：16B 维持 REVIEW_PENDING **未合入**（5 项强审阻塞，合入门禁关闭）；12S-C 三依赖继续不齐；11S 生产门禁不变。
- **并行对账**：另一协调者回合 r161 段所称 `SR-T16B-20261013`/proc `7c3ad97051b2` 在途无账本落点（runs/ 仅 `e7d6b921`，active_calls 空），按未落地不追认，16B 强审事实面以 `e7d6b921` 为准。
- **证据**：`reviews/strongmodel/runs/e7d6b92127804c6cac00dfa4230af7a4/result.md`；`reviews/TASK-16B/attempt-2-r1/ocr/state.json`；`TODO.md` r162 段。候选日志，不自行批准/发布。
===
## TASK-12S-A 合入 DONE + 16B r1 增量 OCR 收口 + 12S-C 前置交付核验（2026-10-13 16:0x 记录，r165）

- **发生/记录**：2026-10-13 15:5x–16:1x +08:00，协调者 r165（prerun 指纹 2e34c39f）。
- **TASK-12S-A 转 DONE**：固定入口 OCR run `8540bf7e`（base `6fb42c4`→`77c395b`，4 批）b01–b04 全收口 **零 findings**（独立读 bNN.log+diagnosis：全部 complete rc=0、coverage 1/1、无 llm_errors）；TESTER 14:51 独立验证 PASS（真 MySQL 8.4 双库迁移往返 3×RC=0+零新增 DDL+坡道 seed 逐字段一致+spray 14 项行为 OK）在案；并行协调者回合已 --no-ff 合入 main `6c7d983`，r165 独立核（`77c395b` 祖先 OK、merge-tree 零冲突、app diff 逐字节一致）并**补推 origin**（合入后实测 origin 仍 `6fb42c4`，推后 `6c7d983` 双核一致）。水雾首包依赖线 12S-A 闭环。
- **TASK-16B r1 增量 OCR 收口裁决**：固定入口 run `0a77a83f`（`0208a73..40ab818`，proxy 单批）AWAITING_DECISION→裁决=**r1 弱 OCR 面解除（0 findings，coverage 1/1，batch_identity 一致，session `59b7741a`，in 734825/out 27169）**；16B 合入门禁**维持关闭**（强审 `e7d6b921` 5 项 CORRECTION 待 r2），r2 单 `attempt-2-r2-dispatch.md` 等 C ACK（C 15:4x 交付 12S-C 冻结后释放，同人串行先收 r2）。
- **TASK-12S-C attempt-1 前置交付冻结核验**：C 交付 `92dcb52` @ `wt-03b-t12sc`（消费基线=`40ab818` 链+merge main `6fb42c4` 零缺口+12S-A/12S-B 固定 SHA byte-identical 独立核 0 行；本单产品面仅 3 文件 `orchestrator +18/proxy +9/test +470`，零 app 行为面改动）；协调者机械核验全绿（定向 11 passed/回归合集 148 passed/ruff clean/祖先双核/零越界，独立复跑）；回执 §五两处口径（发布根=既有 `SCENE_SLICE_PUBLISH_ROOT` 场景子树、车辆信号=读父包 `bag.vehicle`）**裁决接受 C 现口径不返修**（12S-A 提交面 fail-closed 权威链在案）。状态=**REVIEW_PENDING 待接线核验、未合入**；收口链=增量 OCR（排队：12S-B s9_head→16B r2→12S-C 消费面）→强审 pack（`6b2d83fb` 剩 4/5）→三依赖全合入后接线核验单（TESTER 真链冒烟）。
- **门禁变化**：12S-A DONE 合入；16B 未合入（r2 等 C ACK）；12S-B 等 B S9b ACK+`s9_head`（16:30 前最佳，19:00 受控首包排程依赖线）；11S 生产门禁不变。
- **遗留/下一责任人**：B=S9b ACK+交付（16:30）；C=16B r2 ACK（同人串行）；协调者=r2/s9_head 收口链串行推进+17:30 发布决策材料汇总。
- **证据**：`inbox/coordinator/TASK-12S-A/attempt-1-ocr-closure-decision-20261013.md`；`inbox/coordinator/TASK-16B/attempt-2-r1-ocr-closure-decision-20261013.md`；`inbox/coordinator/TASK-12S-C/attempt-1-mechanical-verification-decision-20261013.md`；`reviews/TASK-12S-A/attempt-1/ocr/b0{1,2,3,4}.log`；`TODO.md` r165 段。候选日志，不自行批准/发布。

## TASK-12S-C 接线增量 OCR 收口（零 findings）+ r166 巡检收口（2026-10-13 16:3x 记录，候选）

- **发生/记录**：2026-10-13 16:23–16:3x +08:00，协调者 r166（prerun 指纹 efd77c34）。
- **TASK-12S-C 前置接线增量 OCR 收口**：固定入口 `ocr_runtime.py` run `5a071938`（`22ffb71..92dcb52`，仅 27 行业务增量 orchestrator+18/proxy+9，tests 470 行排除挂 TESTER）b01/b02 全收口 **rc=0 零 findings**，coverage 1/1 fingerprint 一致（b01 session `9ae2339a` 10m11s 325749 tokens / b02 `7874bec9` 4m57s 85253 tokens；b01 唯一 file_read 工具自错=start>end 非审查缺口）；导入的 12S-A/B/16B 代码按既定口径不重审（各自审查记录在案）。并行回合裁决 `reviews/TASK-12S-C/attempt-1/ocr-verdict.md` 经 r166 独立核 log/spec 事实一致予以认账，**12S-C 前置编码面 OCR 门禁解除**；强审判定 NOT_REQUIRED（27 行零 findings+模块级 TESTER 独立证据，完整水雾链归 12S-D 真实全链门禁）。12S-C 仍 REVIEW_PENDING 未合入，正式接线验收须等 16B+12S-B 最终接受合入（12S-A 已合入 `6c7d983` ✅）；r2 若改 proxy 则接线受影响项 TESTER 增量复验。
- **在途收口链**：C 16B r2（ACK 15:52，proxy+测试已改未冻结）→ 机械核验→返修增量 OCR（`40ab818..新head`）→强审增量复审（只 5 问题 ID，授权 `6b2d83fb9` 剩 4/5 期限内）→TESTER→合入 16B；B S9b（ACK 16:0x，decode.py 已改未冻结）→ `s9_head` 冻结后机械核验→增量 OCR（`f62a29c..s9_head`，16 条+S9 一次覆盖，队列首位）→TESTER 增量复验→合入 12S-B。19:00 受控首包三依赖=16B 合入+12S-B 合入+12S-C 接线核验。
- **升级/风险**：A 11S-PREP r1 装配返修（16:0x 派单+16:15 用户催办「催A开始干」）16:3x 实测零 ACK 零代码动作（`wt-01-t11sp` 停 `d8f7206`），催办 16:40 升级阈值已过→**协调者群回合升级通报用户**；17:00 冻结时限风险高，17:30 发布决策 G4 证据面按 r1 未完成口径汇总。TESTER 12S-BC-freeze 并行在途（16:19 ACK，A 面真实渲染中期回执 16:45 前=首包预算输入）。
- **强审查**：本轮零新增调用；grant `6b2d83fb9`（auth-24h-20261013）至 2026-10-14 13:27:15，近 60min 0/5、本授权累计 1（`e7d6b921`），在途 0，token 1356669 in/1247488 cached/9100 out/3838 reasoning（费用未知）。
- **证据**：`reviews/TASK-12S-C/attempt-1/ocr/{state.json,b01.log,b02.log,spec.json}`；`reviews/TASK-12S-C/attempt-1/ocr-verdict.md`；`inbox/3号/TASK-16B/attempt-2-r2-ack.md`；`inbox/2号/TASK-12S-B/attempt-1-rework-s9b-ack.md`；`inbox/TESTER/TASK-12S-BC-freeze/attempt-1-ack.md`；`TODO.md` r166 段。候选日志，不自行批准/发布。


- 2026-10-13T17:45:32+08:00 用户直接要求纠正执行/协调；Codex核实A副本16:58已成功、Docker迁移已完成、A/B尚未冻结、16B OCR4492b7f6在途，收窄各角色下一步并派TESTER固定r2独立验证。撤回重复副本实验与发布后补r1安排；TODO状态历史归档，当前行压缩。仅调度纠正，未合入/未发布/未新增强审调用。入口：inbox/control/SPRAY-CORRECTION-20261013.md。

## 2026-10-13T17:59:31+08:00 用户直接纠正调度

- 统一短恢复入口、五角色cron提示与唯一下一动作，归档巨长状态历史；撤回副本重复实验、发布后补r1及按时点自动放行；保护在途owner，未终止健康会话。
- B冻结f76e2a9，原16条+S9增量OCR01407cec85ec435ea1aed996d70ced09已独立服务启动；16B-r2 OCR完整已裁3条非阻塞，原授权内强审005277e6e60a43308431b5505f0bf6dc已启动；TESTER已ACK独立r2，S9单已派。
- A冻结769d69f，实际镜像仍tag，原pin项未关闭回原A最小续修。未改业务实现、未合入、未发布；G3/G4整体未齐，生产WAITING_GATES。入口inbox/control/SPRAY-CORRECTION-20261013.md。


## 2026-10-13T20:46:28+08:00 受控水雾生产首包收尾完成

main文档提交63bfcf8与业务3c9c496已推github/main；处理机/本地业务3c9c496。20:24生产业务完成、20:32:37最终独立验收PASS：原run attempt2八步DONE/SCENE_DONE、1切片1752消息/43,290,624bytes/12topics、AVAILABLE/current/test、获取200/北京时间/两次正式reconcile/源SHA通过。模型缓存cache_reused=true、新模型请求0，首轮12请求证据保留。

19:00目标未达。真实CIFS SQLite写锁以本地关闭建库→摘要核验复制NAS staging→同盘原子发布关闭；19相关回归及真实NAS夹具PASS。标准生产发布和本地mock闭环成功，旧页面/API正常，旧迁移前后记录数保持。用户本次不等待OCR，旧HARD_DEADLINE不记PASS。

TASK-16B/12S-A/B/C工程DONE，11S仅受控首包DONE；12S-D/12S更广真阴性/真实车/多DB3实采/批量规模继续PARTIAL，新UI不恢复。原协调/A/C三poll实测enabled=false，未触发新模型；临时专项已完成，强审授权按任务结束revoke（本授权4次、费用未知）。本轮不群发消息、不自动恢复旧cron。

证据：reviews/TASK-11S/production-first-bag-20261013.md；/home/wang/work/.local/spray-runtime/production-first-bag-3c9c496-verified.json及-verified-independent.json；仓库HANDOFF与docs/scene-processing-operations.md。功能日志F-041 pending未自行批准。下一步仅按用户新安排继续未完成矩阵。



## 2026-10-13T20:58:48+08:00 用户恢复飞书协作及1012生产批次

原始指令与本批HANDOFF、8包输入清单及A/B/C/TESTER派单已落盘，TASK-11S-BATCH-1012 READY。原首包PASS与生产3c9c496复用，临时接替结束；原生job恢复由外部交互短操作执行，未预称ACK/运行成功。测试车test，incoming/spray，上传原子落位/完整SHA，空包按输入拒绝。按需审查机制保留，旧强审grant不续。

## 2026-10-14T10:49:02+08:00 上线后角色收尾刷新

用户要求原五角色接续；已纠正临时接管/初次上传/等待绑定入口，新增原attempt收尾增补；三份10:23恢复与大包真实阶段作为接续事实。角色ACK由各角色自行写，定时机制/在途身份另取证；不重复部署、上传或模型调用，UI与平台大包优化继续暂停。入口 `inbox/control/POST-SPRAY-CLOSEOUT-20261014.md`。

## 2026-10-14T11:25:19+08:00 v0.4界面恢复与OCR遗留派单

用户恢复UI并要求旧OCR未修项入任务；15条逐项账和原7日志归档，A查询/API、B Bag三视图、C流水线详情三叶、TESTER16D准备、协调16R落单。未接受seed bd0db1d2a0fc293cb4562e2079e741739bacb0de 保留当前水雾代码，未合主仓/部署；角色ACK及真实开工另核，不伪造。入口 inbox/control/V04-UI-RESUME-20261014.md。

## 2026-10-14T13:37:00+08:00 v0.4三叶全部冻结交付+OCR首裁+返修闭环（协调者）

三叶开发交付齐：A查询/API `a1e416a`+断言转派`563a91a`+勘误`ff2a005`（C5/C6/C7/c03-02/03/04修复面，13:18）；B Bag三视图 `e399daf`（12:12）；C流水线详情 `522bb3f`+CC-R1返修 `ce5921d`（13:10）。协调者独立机械核验全绿（祖先链/零越界/diff面/测试复跑）。C叶OCR run `e7a5580c`（12:46收口，实际执行v1.13.0、spec冻结v1.12.13，版本漂移证据在裁决单）首裁：b01唯一finding CC-R1=c05-04血缘兜底li缺`<ol>`开始标签（测试只断`</ol>`掩盖半修）CONFIRMED回派，b02 0 findings；C4维持驳回；C面8条遗留对账落账。集成契约核验发现A/B交叉断言漏项（test_web 364/366）已勘误闭合。三叶集成候选 `1d7f15ce`（seed+A/B/C零冲突临时树）全仓 **1163 passed+4 failed 全为seed固有对照复现，零候选回归**（13:32实测）。TESTER 13:15开工C返修+A面独立验证。

**阻塞（用户面裁决）**：共享`~/.npm-global/bin/ocr` 12:24:22被未知写者由v1.12.13升级v1.13.0；唯一入口硬门禁仅核验v1.12.13，B/A叶OCR prepare被拒（OCR_VERSION_UNVALIDATED）。协调者不擅换二进制/不放宽门禁（ocr-runtime.md：工具版本变化须获授权维护者先验证并版本化入口）。选项：恢复v1.12.13或验证v1.13.0后更新入口。未接受/未合入/未部署；16D最终固定SHA待三叶验收齐后生成。

证据：inbox/coordinator/TASK-16C-C/ocr-attempt1-adjudication-20261014.md；inbox/3号/TASK-16C-C/cc-r1-rework-dispatch-20261014.md（含协调者核验段）；inbox/1号/TASK-16C-A/shared-test-assert-transfer-correction-20261014.md（含协调者核验段）；reviews/TASK-16C/OCR-LEGACY-20261014.md（13:23对账段）；事件COORDINATOR 4条（13:22:22×3、13:35:37×1）；TODO §8 A/B/C/D/R行。下一责任人：TESTER独立验证收口；用户裁决OCR工具链版本后协调者串行提交A/B叶OCR。

## 2026-10-14T13:53:01+08:00 规划：v0.4后的水雾生产收尾

用户指定自动绑定/幂等、异常输入结束恢复、真实质量血缘批量验收三项；新增12S-E/F和原12S-D的D1/D2，REQ/AC-20～22及完整卡同步，全部DEFERRED_AFTER_V04。当前16与已接受水雾首包不变；只文档DESIGN_READY，无业务开发/派单唤醒/生产或模型操作。入口SPRAY-POST-V04.md；动态状态TODO §11。
