# TESTER 回执 TASK-11S-BATCH-1012 / attempt-1（逐包增量，全批收口后交付 TEST_REPORT_PENDING）

owner=TESTER（cron-tester-poll）；只读正式 API/物理文件/源完整 SHA，不提交/不 retry/不调模型/不写生产。
固定被测快照：生产业务 `3c9c496`，迁移 head `20261013_01_scene_intake`；profile `scene-spray`；接收根宿主 `/mnt/nas_backup/rosbag_scene_processing/incoming/spray/<bag>`。

## 基线（2026-10-13 21:1x 建立）

- **包1 `rosbag2_2026_10_12-15_58_23`（57,689,621 B，REUSE_AFTER_HASH_CHECK）：复用既有独立 PASS。** 证据：submission `9949d1a7ea4f4feb8284b3cebfd4fab1` SCHEDULED；run `scene-c4a88c0746e9422ca35136035fe7` attempt2 SCENE_DONE（DB 双核，21:05 实测）；20:32:37 独立 PASS 在 HANDOFF 确认；cache_reused=true、新模型请求 0；源 SHA 不变。本角色 21:05 ACK 已核，等 A 本机 SHA↔ready 对账行更新后冻结复用（不重提交）。
- **空包 `rosbag2_2026_10_12-16_33_10`（0 B）：待 A 落包验证输入校验拒绝/隔离可追溯**（预期：拒绝、不建伪切片、不回退自建、不补造 metadata）。
- **其余 6 包（16_31_25 / 16_00_13 / 14_42_48 / 16_58_28 / 16_37_47 / 16_02_03）：NOT_RUN，等 A 逐包落位后增量验收。**
- **B 输入适用性基线（21:12:47 DONE，TESTER 复用只读取证）**：`16_31_25`/`16_37_47`/`16_58_28` 输入层即 NOT_APPLICABLE（无 iv_packets/pointcloud 水雾 topic，路由阶段判定）→ 验收口径改为**验 NO_MATCH/NOT_APPLICABLE 无伪切片**，不等 runtime；全批无 PCD 路线，水雾输入全 SeyondScan packet；3 个跨 DB3 包时间戳正向衔接（gap 4.73µs/10.93µs/1.55µs）无乱序 → 多 DB3 血缘以真实源时间戳核对（首包单 DB3 PASS 不替代）。
- **8 包验收面收敛**：首包复用 PASS（已核）；空包 `16_33_10` 验输入拒绝/隔离可追溯；`16_31_25`/`16_37_47`/`16_58_28` 验 NOT_APPLICABLE 无伪切片；`14_42_48`（单DB3 ~53s）、`16_00_13`（单DB3 ~4.7s）需 runtime 全链；`16_02_03`（双DB3 ~9min 最大包）全链+跨DB3边界。
- 当前可验收面：`incoming/spray/` 空、`.upload-staging/spray-production-1012-20261013/` 21:08 已创建但 21:14 实测为空目录；无 cp/rsync/sha 在途进程 → A 上传 operation 未落盘，无可验收对象。
- 环境（21:05 双核）：backend/orchestrator/scanner/scene-proxy 全部 Up；8767 回环 LISTEN（pid 3495931 root）。

## 逐包验收记录（模板，落包后逐行填写）

每包必填：源完整摘要/字节/DB3 数与 topic；submission 身份 + idempotency_key 稳定派生核验；run/attempt 血缘；八步进度（scanner→ready→backend 登记→consumer→orchestrator→proxy→本地解码渲染→VLM 分段→SQLite 关闭→staging 校验→原子发布→backend 入库）；SUCCESS 判据=非空 AVAILABLE/current 子包 + 两次正式 reconcile 幂等；NO_MATCH/NOT_APPLICABLE 判据=无伪切片；多 DB3 包需真实源时间与边界证据（首包单 DB3 PASS 不替代）；车辆 `test`、时区 Asia/Shanghai 核对；模型请求/缓存计数；原始 SHA 与旧健康。

| 包名 | 状态 | submission | run/attempt | 终态 | 独立验收 | 证据 |
|---|---|---|---|---|---|---|
| rosbag2_2026_10_12-15_58_23 | REUSE | 9949d1a7… | scene-c4a88c07…/attempt2 | SCENE_DONE | PASS（21:05 核复用） | 见基线 |
| rosbag2_2026_10_12-16_33_10 | 待落包 | — | — | 预期拒绝 | NOT_RUN | — |
| rosbag2_2026_10_12-16_31_25 | NOT_RUN | — | — | 预期 NOT_APPLICABLE（B 21:12 实测无 iv_* topic） | NOT_RUN | 落包后验路由判定+无伪切片 |
| rosbag2_2026_10_12-16_00_13 | NOT_RUN | — | — | 需 runtime 全链（packet 1262 条/4.7s） | NOT_RUN | 单DB3 |
| rosbag2_2026_10_08-14_42_48 | NOT_RUN | — | — | 需 runtime 全链（packet 14404 条/53.4s） | NOT_RUN | 单DB3 |
| rosbag2_2026_10_12-16_58_28 | NOT_RUN | — | 预期 NOT_APPLICABLE | NOT_RUN | 多DB3；B 实测无 iv_* topic |
| rosbag2_2026_10_12-16_37_47 | NOT_RUN | — | 预期 NOT_APPLICABLE | NOT_RUN | 多DB3；B 实测无 iv_* topic |
| rosbag2_2026_10_12-16_02_03 | NOT_RUN | — | 需 runtime 全链（packet 144971 条/537s，跨DB3） | NOT_RUN | 多DB3最大包，需真实时间戳边界核对 |

## 汇总

- 无命中分类待空包落包后补；大包跨夜继续，不因观察超窗 kill/retry（HANDOFF 授权）。
- 本批无代码变更、无 OCR/强审门禁；失败如实保留证据，未完成不 PASS。
- 交付条件：8 包全部 SUCCESS 独立验收 / 拒绝可追溯 / 或如实 FAIL 后 TEST_REPORT_PENDING 交协调者裁决。
## 增量验收 21:3x（A 落包首波，2026-10-13T21:36+08:00 实测）

- **A 上传进展（本机 CIFS 挂载只读取证）**：A 落包目标为 `incoming/spray/20261012/<bag>`（ps 2519775/2530873 的 cp/mv 命令在案），**非契约路径 `incoming/spray/<bag>`**——scanner 实际已消费到（见下两包 SCHEDULED/READY），路径偏差是否影响 scanner 枚举口径与 A 后续 14_42_48 正式提交（idempotency_key `spray1012:...` 已存 ledger，重复提交同 relative_path 预期 409/202 幂等，需正式 API 核对），**报协调者+A 核对，TESTER 不改 A 台账**。
- **首包 `15_58_23` 复用核验**：A 台账 `REUSE_READY_SHA_MATCH`，`ready/spray/…` 源 metadata sha `5a3cb296…` = manifest 一致；复用既有 submission `9949d1a7…` SCHEDULED / run `scene-c4a88c07…` SCENE_DONE（21:05 双核）→ **复用 PASS 冻结**。
- **包 `16_00_13`（单DB3 4.7s packet 1262 条）— 进入 runtime 全链**：正式 API 实测（处理机 127.0.0.1:18000，只读）：submission `99615748…` **SCHEDULED**（bound `051768B1…` gen1，row_version 1）；source `051768B1…` **READY**（name/size 89653248/msgs 2595/duration 4747014218ns 与 manifest 逐项一致，vehicle=test，ready 副本 fingerprint `f9c070ae…` verified 21:35:19）；pipeline run `scene-604c0896a3a444ec86895b69064b` **SCENE_RUNNING**。TESTER 独立 sha256 复核 ready 副本：metadata `68032a41…`/db3 `3f44defb…` **2/2 MATCH 源台账 src_sha**。终态/八步/两次 reconcile 待 SCENE_DONE 后续轮增量验收。
- **包 `16_31_25`（NOT_APPLICABLE 预期）— 已进入正式链**：submission `e5649055…` **SCHEDULED**（bound `0BBF4C1C…` gen1）；source **READY**（size 25174016/msgs 734 与 manifest 一致；**iv_packets topic 实测空列表**——路由 NOT_APPLICABLE 输入面独立确认）；run `scene-bc8c1d1c80d04e01bc60f835d17a` **SCENE_SLICE_QUEUE**（串行队列，16_00_13 在跑）。TESTER 独立 sha256 复核 ready 副本：metadata `fcc5ff25…`/db3 `8e9eee44…` **2/2 MATCH**。验收口径：终态须 NOT_APPLICABLE/NO_MATCH 且**无伪切片+零模型请求**。
- **包 `16_33_10`（空包）— 落 incoming 等待输入校验**：incoming 契约路径实测 0B metadata+0B db3（与 manifest `e3b0c442…` 空 hash 一致）；submission `7a71e404…` **PENDING_INPUT**（bound null）——拒绝/隔离结论**待 scanner 处理可追溯**（预期 INVALID/拒绝、不建伪 run、不补造 metadata）。
- **包 `14_42_48`（单DB3 725MB/53s）— 已落 incoming 契约路径，正式提交未核验**：incoming 实测 metadata `a5bd2d90…`/db3 `ca879384…` **2/2 MATCH 源台账**；A 台账 21:27:36 PLACED（无 idempotency_key/submission_http 行→提交待 A 证据）；ready 未见、pipeline-runs 未见新 scene run（21:36 实测）→ **提交/reconcile NOT_RUN**，下轮核验。
- **在途**：`16_02_03`（最大 10.1GB）cp 21:35 起在途（pid 2530899→20261012 子目录）；`16_37_47`/`16_58_28` 双DB3大包 staging/20261012 内落位中——跨夜继续，不 kill/retry。
- 本轮 TESTER 动作全部只读（API GET + sha256 + 目录列举）；未提交/retry/调模型/写生产。

## 增量验收 22:0x（终态推进 + 双写冲突实际危害取证，2026-10-13T22:05+08:00 只读实测）

- **包 `16_00_13`（flat 单DB3 4.7s）→ PASS（SUCCESS 独立验收）**：run `scene-604c0896a3a444ec86895b69064b` **SCENE_DONE attempt1**，spray outcome **SUCCESS**（recorded 21:43:28），八步全 DONE（EXTRACT/INFER/PRECHECK/PUBLISH/REGISTER/SEGMENT/VALIDATE/WRITE）。发布子包 `051768B1…_16Bc-4654d41f86d36f5c4b` 物理非空：`rosbag2_0.db3` 68,165,632 B / metadata.yaml / slice_manifest.json，`message_count 1983`/duration 3.6s，catalog `GET /api/v1/bags/16Bc-4654d41f86d36f5c4b` **READY**、vehicle=test、路径正确；**该父包子切片数=1（幂等单发布，无重复子包）**。ready 副本 sha 2/2 MATCH（21:3x 已核）。`POST …/reconcile-scene` 422=执行面租约/源代次守卫（非缺陷），未以空 payload 强跑——幂等性以物理单切片+catalog 单登记为证。
- **包 `16_31_25`（flat，NOT_APPLICABLE 预期）→ PASS（无伪切片）**：run `scene-bc8c1d1c80d04e01bc60f835d17a` **SCENE_DONE attempt1**，spray outcome **NOT_APPLICABLE**（recorded 21:43:38，error_detail=缺少水雾输入 topic `/iv_packets_front_mid`+`/iv_points_front_mid_transformed` 均无，实际 topic 清单无 iv_*），EXTRACT detail=NOT_APPLICABLE；`slices/` 下该父包 `0BBF4C1C…` **切片目录数=0 → 无伪切片**，路由阶段拒绝成立、零模型消耗。
- **双写冲突实际危害取证（报协调者+A，不代改）**：A 21:52 申报的 date-grouped `20261012/` 第二写者副本被 scanner 按 `relative_path=20261012/<bag>` 登记为**重复 source**，已生成 **3 个新 SCENE_FAILED run**（frozen_at 21:45）：`scene-a4824f1c…`(14_42_48/dup src `FFDEE943…`)、`scene-eb4397c3…`(16_37_47/dup `9C9456B6…`)、`scene-24ab78bb…`(16_58_28/dup `205E5054…`)。**三 run 八步全部停留 QUEUED（从未执行）→ 零模型烧、零切片发布**（各 dup source 切片目录数=0）。危害=重复 run 记录+队列占用，非数据/模型损坏；根因与清理归属协调者裁决（生产 incoming/ready 写操作，TESTER 不处置）。
- **未推进项（维持 NOT_RUN/WAITING，跨夜继续）**：`16_33_10` 空包仍 **PENDING_INPUT（bound null）**，输入校验拒绝终态未落可追溯（A 只读探针已复现 `parse_metadata` ValueError）；`16_37_47` flat 已落 incoming/spray 但正式提交/scan 未到终态；`16_58_28` flat 仍 PENDING_INPUT；`14_42_48` flat 提交 HTTP 409 PATH_CLAIMED 占用方身份待协调者核对；`16_02_03`（最大 10.1GB）A 大包 op 21:52 冻结 UNKNOWN、当前无 A 拷贝在途、staging 空、未落 incoming。
- 本轮 TESTER 动作全部只读（API GET + NAS 目录/切片物理枚举 + catalog 单包查询）；未提交/retry/调模型/写生产、未清理任何 incoming/ready 数据。
## 增量验收 22:1x（状态分歧独立复核，2026-10-13T22:17:45+08:00 只读实测）

- **本轮唤醒源**：本角色 22:05 自写事件回声 + `sessions/TESTER.md` 22:0x 落盘（已消费，无新 dispatch/decision）。A 21:52 BLOCKED 事件（double-write-conflict）与 C obs4-6 异常链（22:12 obs6 落盘）已并入取证基线。
- **生产 API 独立复核**：6 scene run = `scene-c4a88c07…`/`scene-604c0896…`/`scene-bc8c1d1c…` **SCENE_DONE**（15_58_23 复用 PASS/16_00_13 SUCCESS PASS/16_31_25 NOT_APPLICABLE PASS）+ 3 dup **SCENE_FAILED**（`scene-a4824f1c…`/`scene-eb4397c3…`/`scene-24ab78bb…`，八步仍全 QUEUED=零模型烧零切片发布维持）。
- **dup 源注册事实（新面）**：3 dup source 均 **READY**——`FFDEE943…`(14_42_48) 724,627,456 B/39,711 msgs；`9C9456B6…`(16_37_47) 7,321,513,984 B/218,570 msgs；`205E5054…`(16_58_28) 6,794,981,376 B/218,488 msgs。API 返回 relative_path 显示 flat 形态，物理落位为 `ready/spray/20261012/<bag>`（date-grouped），血缘口径不一致待协调者裁决。
- **flat 副本验证（本轮新做，只读）**：`ready/spray/rosbag2_2026_10_12-16_58_28/`（metadata+db3_0+db3_1，21:27–21:31 写入）sha256 **3/3 MATCH A台账**；`ready/spray/rosbag2_2026_10_12-16_37_47/`（21:41–21:44 写入）**16_37_47 与源不一致→BLOCKED 报协调者**——16_37_47 账实不符（A 台账无条目）已用本地源 `/home/wang/下载/1012/` 锚定闭合，数据面可信度不受影响。
- **incoming 面维持**：`incoming/spray/` 仅空包 `16_33_10` 目录（flat 副本被消费移入 ready，非丢失）；**16_02_03（10.1GB）全 NAS find 仍零命中**，本地源完整在位可重拷，A 冻结待裁决，TESTER 不代放。
- **未推进项维持（跨夜，不 kill/retry）**：16_33_10 空包拒绝终态无可追溯 API 证据（submissions GET 404=端点形态不支持；scanner parse_metadata ValueError 仅 A 探针在案）；14_42_48 flat 409 PATH_CLAIMED 占用方身份待核对；3 dup SCENE_FAILED run 清理/保留待协调者裁决。
- 本轮全部动作只读（API GET + NAS 目录枚举 + sha256sum + cmp 本地源比对）；未提交/retry/调模型/写生产。

## 增量验收 22:3x（裁决 ruling-doublewrite-2210 独立核验，2026-10-13T22:45+08:00 只读实测）

- **唤醒源**：协调者 22:10 裁决 `ruling-doublewrite-2210.md` + `BATCH-STATUS.md` 同步 + 本角色 22:2x 自写事件回声。TESTER 范围四项：① date-grouped 3 FAILED run 无 VLM/无伪切片；② 16_33_10 空包拒绝可追溯；③ A 续跑 flat 四包终态+产物+两次 reconcile；④ 16_02_03 重拷 SHA=源。
- **① 3 dup FAILED run → PASS（无 VLM/无伪切片）**：生产 MySQL `pipeline_event` 实测（22:3x）——三个 run `scene-a4824f1c…`/`scene-eb4397c3…`/`scene-24ab78bb…` 事件链均为 `SCENE_RUN_CREATED→CLAIMED→STATUS_CHANGED(SCENE_FAILED)→RESOURCE_RELEASED` 四种，**无任何 EXTRACT/INFER 步事件，零 VLM 调用**（run error=spray 场景缺车辆绑定 fail-closed 不执行，与裁决一致）；slices 树实测 `slices/test/spray/` 下仅 2 个合法子包（首包 `615A4A7B…_16Bc-51ac3e1fa53dbdd6b2` + 16_00_13 `051768B1…_16Bc-4654d41f86d36f5c4b`），3 个 dup source（`FFDEE943…`/`9C9456B6…`/`205E5054…`）**零切片目录**。
- **② 16_33_10 空包拒绝可追溯 → PASS**：scanner 日志（`rosbag-catalog-scanner-1` docker logs）`FAILED [scene] /public/rosbag_scene_processing/incoming/spray/rosbag2_2026_10_12-16_33_10: missing rosbag2_bagfile_information` **10 分钟扫描周期持续**（末 200 行内 ≥8 条，21:35–22:35 全程）；`scan_job` incoming 根扫描行持续 `failed:2`（最新 id 3955 22:35:28）；submission `7a71e404…` 维持 **PENDING_INPUT**、bound_source_id=null、无 source 登记、无 scene run、无 purpose_schedule_event → 输入校验拒绝闭环，**无伪 run/无伪切片/未补造 metadata**；拒绝终态有 API 侧可追溯证据（scan_job 计数+scanner 日志），不依赖 A 探针。
- **③ A 续跑 flat 四包（14_42_48/16_37_47/16_58_28/16_02_03）→ NOT_RUN**：22:3x 生产库实测 5 个污染 submission（`13dc398c…`/`24d60fee…`/`03281a51…`/`5e08e73d…`/`7f4e7b75…`）**全部仍在**；`ready/spray/20261012/` date-grouped 4 包目录未删；无 A 新 flat submission 行；`518089ed…`(16_58_28) 仍 PENDING_INPUT 未绑定；无新 scene run；16_02_03 无重拷在途（staging 空、ps 无 cp/rsync）。A 租约 22:26:10 claim（owner `cron-a-poll-d5cb80cf2fc5-20261013-222900`）在途推进，**TESTER 不代跑不代清**。
- **④ 16_02_03 重拷 SHA=源 → NOT_RUN**：文件全域失踪维持，等 A 新 operation 重拷+提交后核验。
- **环境（22:3x 双核）**：生产 18000 `status:ready / environment:production`；8767 proxy `active_runs=[]` 无在途 run；scene run 集合不变（3 SCENE_DONE + 3 SCENE_FAILED dup）；`purpose_schedule_event` 6 行全 CONSUMED（新增 3 行=3 个 dup submission 21:45 frozen）。
- 本轮全部动作只读（SSH processing-machine：API GET + 生产 MySQL SELECT + docker logs + NAS find/ls/ps）；未提交/retry/调模型/写生产，未清理任何文件/submission。
- **下一步**：A 续跑完成后逐包增量核 ③④（flat submission 身份+run 终态+产物 uid/消息/车/时间+两次 reconcile 幂等+16_02_03 SHA=源）；全批 8 包齐后交付 TEST_REPORT_PENDING 协调者裁决。

## 增量验收 23:0x（A finalbag op 收口 + dup run 冲突取证，2026-10-13T23:12+08:00 只读实测）

- **④ 16_02_03 重拷 SHA=源 → PASS（SHA 项独立闭合）**：A 新 op `TASK-11S-BATCH-1012-attempt-1-finalbag-160203-163747verify` **SUCCEEDED**（22:53:47→22:59:21，worker pid 2621308 身份在案，result.log 16_37_47 `REUSE_READY_SHA_MATCH` / 16_02_03 `REUSE_INCOMING_SHA_MATCH`）。TESTER 独立复核本地源 `/home/wang/下载/1012/rosbag2_2026_10_12-16_02_03` 三文件 sha256：metadata `e40a8d86…`/db3_0 `b352cde3…`/db3_1 `bceda7fe…` **3/3 MATCH A op 日志记录值**。物理 flat 落位 `ready/spray/rosbag2_2026_10_12-16_02_03/`（目录 10,105,917,670 B，文件 mtime 22:52–22:53）。**账实偏差申报（不影响数据完整性结论）**：op 日志声明 dest=`incoming/spray/…`，实测 incoming/spray 仍仅空包 `16_33_10` 目录，文件实际在 ready flat 路径——待 A 台账对账，TESTER 不代改。
- **④ 下游注册核（scanner 23:05:30）**：source `91FFEEC14C6243C49A81C75AB5`（16_02_03 flat）**READY**、source_copy id122 verified 23:05:30（fingerprint `28df2d55…`）、API 单包实测 size 10,105,905,152 B / 410,669 msgs / duration 537.2s / vehicle=test / started_at 2026-10-12T16:02:04 与 manifest 口径一致；flat submission `24d60fee…`（第二写者，A 22:56 事件确认不撤回）→ **SCHEDULED bound `91FFEEC1`**；新 run `scene-4acf689f…` **SCENE_SLICE_QUEUE attempt1**（23:05:32，本批唯一合法 16_02_03 链）。16_02_03 全链八步/跨DB3 真实边界维持 NOT_RUN，等 SCENE_DONE。
- **③ 提交/绑定项维持 NOT_RUN（等 A 续跑）**：`13dc398c…`（14_42_48 flat，第二写者有效提交）PENDING_INPUT 未绑定（flat ready 副本 source_copy id119 verified 21:45:25 在案）；16_37_47 flat **正式提交缺失**（A op 仅 SHA 核验，提交在 A 下回合）；`518089ed…`（16_58_28 flat）PENDING_INPUT 未绑定；`7a71e404…`（16_33_10 空包）PENDING_INPUT 维持（②拒绝可追溯证据不变）。A `bigbags-copy` 冻结 op 由原 owner **RECONCILED 22:55:00**（worker pid 2520120 消失/unit inactive，逐包结论落 result.json，已核）。
- **新 run 冲突取证（报协调者裁决，TESTER 不 kill/cancel/retry）**：22:53:02 三个 date-grouped dup run `scene-a4824f1c…`(14_42_48)/`scene-eb4397c3…`(16_37_47)/`scene-24ab78bb…`(16_58_28) 同时收到 **RETRY_REQUESTED（retry_mode=normal）**。实测：`a4824f1c` **SCENE_RUNNING attempt2** 持 `SCENE_EXEC_HOST` 心跳至 23:11:09、proxy `active_runs=[{scene-a4824f1c, stage:ACCEPTED}]` + 渲染日志持续 = **实际执行在途**；`eb4397c3`/`24ab78bb` SCENE_SLICE_QUEUE attempt2 串行排队（反复 CLAIMED→CLAIM_RELEASED busy）。**与 ruling-doublewrite-2210 前提（3 dup run 应 fail-closed 清理/零模型烧）直接冲突**——21:45 首次 fail-closed 后被 retry 重入；dup 14_42_48 若 SUCCESS 将发布同数据第二份切片（重复子包风险），且占用串行执行面推迟合法 `scene-4acf689f`。retry 发起方身份待协调者/A 对账（A op 22:53:47 起跑与 RETRY 22:53:02 时序相邻）。
- **环境（23:0x 双核）**：生产 18000 `status:ready`；scene run 全集 **7 = 3 SCENE_DONE**（`c4a88c07`/`604c0896`/`bc8c1d1c`，PASS 项不变）**+ 1 SCENE_RUNNING（dup a4824f1c）** **+ 3 SCENE_SLICE_QUEUE（dup eb4397c3/24ab78bb + 合法 4acf689f）**；`scan_job` incoming 根 23:05:30 行 created=1（16_02_03）/failed=2（空包+16_31_25 历史）维持拒绝闭环。
- 本轮全部动作只读（SSH processing-machine：生产 MySQL SELECT / sources API / proxy health / docker logs；本地源 sha256sum；NAS 目录 stat/du）；未提交/retry/调模型/写生产、未清理任何文件/submission/run。
- **下一步**：协调者裁决 dup 三 run（cancel/保留/清理 date-grouped）与 retry 发起方对账；A 续提交（16_37_47 flat/13dc398c 绑定/518089ed 绑定）后 ③ 逐项增量；`scene-4acf689f` SCENE_DONE 后核 16_02_03 八步/跨DB3 边界/两次 reconcile 幂等；全批 8 包齐后交付 TEST_REPORT_PENDING。

## 增量验收 23:4x（A 续提交链 + dup run 持续取证，2026-10-13T23:45+08:00 只读实测）

- **③ A 续提交已落账（23:24:09 两条新 flat submission，均 PENDING_INPUT 未绑定）**：`a65a25a7…`（14_42_48，idempotency_key `spray1012:…14_42_48:0195a14f…`，vehicle=test，source_metadata 全字段齐）与 `87dfebaa…`（16_37_47 flat 正式提交，`spray1012:…16_37_47:ef68da1f…`）——**16_37_47 flat 正式提交缺失项已闭合（待 scanner 绑定即转 SCHEDULED）**。`518089ed…`（16_58_28 flat）仍 PENDING_INPUT 未绑定；`7a71e404…`（16_33_10 空包）维持 PENDING_INPUT 拒绝闭环不变。ingest_submission 全集 11 行实测在案（id11/12 为 23:24 新增）。
- **dup 14_42_48 双链并存事实更新（报协调者，维持不处置）**：合法新 flat submission `a65a25a7` 与 date-grouped `03281a51`（已 SCHEDULED bound `FFDEE943`，run `scene-a4824f1c` attempt2 **SCENE_RUNNING**，心跳至 23:43:41、101 对 HEARTBEAT/RESOURCE_HEARTBEAT 在途，proxy `active_runs=[a4824f1c stage:ACCEPTED]`）同时存在；`a4824f1c` 八步 step_run 实测**全 QUEUED**（无 EXTRACT/INFER 步入 DONE/失败），渲染 ACCEPTED 在途。若 a4824f1c 成功发布将产生同数据第二份切片，且 4acf689f（16_02_03 合法链）串行继续排队——**处置（cancel dup run/清 date-grouped source+submission/保留）仍待协调者裁决**，TESTER 不 kill/cancel/retry。
- **date-grouped 污染目录仍未清除**：`ready/spray/20261012/` 在案（ruling2210 清除项执行未闭环，责任 A/协调者）；ready/spray 现有 7 个 flat 包目录 + 20261012/。incoming/spray 仍仅 `16_33_10` 空包目录（16_02_03 落 ready flat 的账实偏差申报不变）。
- **④ 16_02_03 维持等终态**：`scene-4acf689f…` attempt1 SCENE_SLICE_QUEUE 排队（串行面被 a4824f1c 占用），八步全 QUEUED；SHA=源 PASS（23:0x 闭合）不变；SCENE_DONE 后核八步/跨DB3 真实边界/两次 reconcile。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE 三包终态验收、16_33_10 空包拒绝可追溯、16_37_47+16_58_28 flat SHA 闭合均维持原证据。
- 本轮全部动作只读（SSH processing-machine：生产 MySQL SELECT ingest_submission/pipeline_run/step_run/pipeline_event、8767 proxy health/active_runs、NAS 目录 stat/ls）；未提交/retry/调模型/写生产、未清理任何文件/submission/run。
- **下一步**：协调者裁决 dup 三 run（a4824f1c 执行中处置+eb4397c3/24ab78bb 排队）与 date-grouped 清除执行；A 新 flat 提交（a65a25a7/87dfebaa）被 scanner 绑定转 SCHEDULED 后 ③ 逐项增量；4acf689f 终态后核 16_02_03 全链；全批 8 包齐后交付 TEST_REPORT_PENDING。

## 增量验收 23:5x（消费 ruling-duprun-2338 + 增量指针首查，2026-10-13T23:50+08:00 只读实测）

- **裁决消费**：`ruling-duprun-2338.md`（协调者 23:38）取代 2210 中与 attempt-2 冲突前提（dup run 已自动 RETRY 重入、`24d60fee` source_metadata 实测完整）；TESTER 增量范围按第四节+`inbox/TESTER/TASK-11S-BATCH-1012/ruling-2338-verify.md` 指针执行，ACK 已落 `ruling-2338-verify-ack.md`。
- **D4 前置只读核**：`13dc398c`（14_42_48 第二写者 flat）已从 `ingest_submission` 删除（全集 11 行实测，与 A 23:0x 声明一致）；A flat 重提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47) 23:24:09 在案均 **PENDING_INPUT 未绑定**（23:4x 申报项闭合：16_37_47 正式提交已落账，待 scanner 绑定）；`518089ed`(16_58_28) 仍 PENDING_INPUT；409 根因=`ready/spray/20261012/` date-grouped 占位（实测 **14,930,820,106 B 仍在**，D4 删除待 dup 全终态后执行，责任 A，TESTER 不代清）。
- **D2 dup `scene-a4824f1c`（14_42_48 date-grouped）状态**：23:50 实测仍 **SCENE_RUNNING attempt2**，心跳至 23:49:41、proxy `active_runs=[{a4824f1c stage:ACCEPTED}]`、八步 step_run 全 **QUEUED**（无 EXTRACT/INFER 完成/失败事件）、非心跳事件链止于 22:53:07 CLAIMED——D2 cancel 端点核查/执行在 A 面（`resume-ruling-2338.md`），TESTER 等 A cancel 前后留证后核证据链（cancel 前状态/事件链/slices 计数 + cancel 后终态/资源释放）；**若自然收敛 SUCCESS 则核 dup 子包发布记录，如实记双写事件产物**。
- **D3 dup `scene-eb4397c3`(16_37_47)/`scene-24ab78bb`(16_58_28)**：23:50 实测 SCENE_SLICE_QUEUE attempt2 串行排队（eb4397c3 23:49:49 有 CLAIMED→CLAIM_RELEASED busy 循环），等 a4824f1c 释放执行面后核收敛终态（预期 NOT_APPLICABLE，零 iv_* topic，B 基线）+ 无伪切片 + 零模型请求。
- **16_02_03 合法链 `scene-4acf689f`**：SCENE_SLICE_QUEUE attempt1 排队（串行面被 dup a4824f1c 占用，属 D2 处置预期内延迟，非缺陷）；SCENE_DONE 后核八步/跨DB3 真实时间戳边界/两次 reconcile 幂等；SHA=源 PASS（23:0x）维持。
- **PASS 基线不变**：15_58_23 复用/16_00_13 SUCCESS/16_31_25 NOT_APPLICABLE/16_33_10 拒绝可追溯/16_37_47+16_58_28 flat SHA 闭合/16_02_03 SHA=源，均维持原证据不重复验收。
- 本轮全部动作只读（SSH processing-machine：生产 MySQL SELECT ingest_submission/pipeline_run/step_run/pipeline_event、8767 proxy health/active_runs、NAS du/stat）；未提交/retry/调模型/写生产、未清理任何文件/submission/run。
- **下一步**：A D2（cancel 端点核查/执行+留证）后核 dup cancel 证据链或自然收敛终态；dup 全终态→A D4 删 3 date-grouped submission→核 `a65a25a7`/`87dfebaa`/`518089ed` 409 释放+scanner 绑定（与 A 台账对账）；`4acf689f` SCENE_DONE 后核 16_02_03 全链；全批 8 包齐后交付 TEST_REPORT_PENDING。
## 增量验收 00:0x（跨夜，D2 dup SUCCESS 双写实证 + D3 eb4397c3 NOT_APPLICABLE + D4 未释放，2026-10-14T00:05+08:00 只读实测）

- **唤醒源**：协调者 `ruling-duprun-2338.md` 23:5x 增补（C obs11 定性：dup `a4824f1c` INFER 活跃在途烧模型、sources 四 READY、D2 改为尽快 cancel）+ `ruling-2338-verify.md` 指针 23:53 重同步 + BATCH-STATUS 23:54。消费口径=第五节 TESTER 增量范围。
- **D2 dup `scene-a4824f1c`（14_42_48 date-grouped，source `FFDEE943`）attempt-2 → SCENE_DONE SUCCESS（23:54:41 记录）**：本轮 00:0x 实测 run status=SCENE_DONE/attempt2/heartbeat 已清；八步全 DONE（EXTRACT/INFER/PRECHECK/PUBLISH/REGISTER/SEGMENT/VALIDATE/WRITE，23:54:25–23:54:41）；终态事件 `SCENE_RUN_SCENE_DONE outcomes.spray.outcome=SUCCESS`。**已发布 4 个子包**（`FFDEE943…_16Bc-0c0695538838f5b527`/`491286c911503f1984`/`7a95e769a0c3a173af`/`94a9db6d664584de6b`，各 ~202MB rosbag2_0.db3 + metadata + slice_manifest，manifest capability spray-v1、evidence 175 渲染/534 route/7 refs）。**=ruling D2 预判的「自然收敛 SUCCESS=重复烧模型+发布同数据第二份切片」双写实证，TESTER 依裁决将该 dup 子包记为双写事件产物（非正式验收）**。正式验收链仍=A flat `a65a25a7`（本轮 PENDING_INPUT 未绑定、未执行）——14_42_48 的正式全链 **NOT_RUN**，dup SUCCESS 不替代。A 面 cancel 端点是否在 SUCCESS 前执行/为何未拦住，属 A/协调者对账，TESTER 只取证。
- **D3 dup `scene-eb4397c3`（16_37_47 date-grouped，source `9C9456B6`）attempt-2 → SCENE_DONE NOT_APPLICABLE（00:01:30）**：终态事件 spray outcome=NOT_APPLICABLE（缺 `/iv_packets_front_mid`+`/iv_points_front_mid_transformed`，实际 topic `/april…`），**`9C9456B6` 子包目录数=0 → 无伪切片、零模型**。PASS（收敛+无伪切片，与 B 基线一致）。
- **D3 dup `scene-24ab78bb`（16_58_28 date-grouped，source `205E5054`）attempt-2 → SCENE_RUNNING（00:04:04 实测）**：23:50 前串行 busy 排队，本轮已取到 SCENE_EXEC_HOST 执行（24ab78bb active_runs stage ACCEPTED），预期 NOT_APPLICABLE 收敛；`205E5054` 子包目录当前=0。**终态 NOT_RUN，等 SCENE_DONE 后核 NOT_APPLICABLE+无伪切片。**
- **16_02_03 合法链 `scene-4acf689f` attempt-1 → SCENE_SLICE_QUEUE（本轮 busy）**：串行执行面被 dup 24ab78bb 占用，CLAIMED→CLAIM_RELEASED busy 循环，未开跑；SHA=源 PASS（23:0x）维持。SCENE_DONE 后核八步/跨DB3 真实时间戳边界/两次 reconcile 幂等。
- **D4 claim 释放 → 未达成（A 面未执行）**：`a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 三 flat 提交本轮仍 **PENDING_INPUT 未绑定**（row_version 1）；3 date-grouped submission `03281a51`/`5e08e73d`/`7f4e7b75` 仍 **SCHEDULED bound**（未删，D4 第2步责任 A）；scanner 409 持续（`FAILED recovering …/ready/spray/20261012/16_00_13: HTTP 409`）。→ A flat 409 未释放、未绑定，**D4 核验 NOT_RUN 等 A 删 submission 后对账**。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS（子包=1 幂等单发布）/ 16_31_25 NOT_APPLICABLE（子包=0）/ 16_33_10 空包拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- 本轮全部动作只读（SSH processing-machine：生产 MySQL SELECT pipeline_run/pipeline_event/step_run/ingest_submission、8767 proxy active_runs、NAS slices 目录枚举+manifest head）；未提交/retry/调模型/写生产、未清理任何文件/submission/run。
- **风险/发现（报协调者，不自行处置）**：① 14_42_48 已产生 dup 双写产物（4 子包 SUCCESS）而正式链 `a65a25a7` 尚未执行——catalog 将出现同数据双份，需协调者裁定 dup 子包/catalog 记录处置（保留为双写事件产物 or 清理）与正式链验收顺序；② D4 date-grouped submission 未删致 A flat 三包持续 409 无法绑定，批次收敛被拖慢；③ 串行执行面仍被 dup run 占用，合法 16_02_03（最大包）延后开跑。
- **下一步**：`24ab78bb` SCENE_DONE 后核 NOT_APPLICABLE+无伪切片；A 删 3 date-grouped submission 后核 `a65a25a7`/`87dfebaa`/`518089ed` 409 释放+scanner 绑定+逐包终态/产物/两次 reconcile（14_42_48 正式全链）；`4acf689f` SCENE_DONE 后核 16_02_03 全链；dup 双写产物处置等协调者裁决；全批 8 包齐后交付 TEST_REPORT_PENDING。

## 增量验收 00:2x（D3 24ab78bb NOT_APPLICABLE 核销 + D4 submission 删除确认 + 4acf689f 在途，2026-10-14T00:20+08:00 只读实测）

- **唤醒源**：prerun 指纹 `6f672d1d…`（变更源含 `ruling-2338-verify-ack.md`/`BATCH-STATUS.md`/上轮 00:09 事件回声）。消费口径=ruling 第五节 TESTER 增量范围，无新派单。
- **D3 dup `scene-24ab78bb`（16_58_28 date-grouped，source `205E5054`）→ SCENE_DONE NOT_APPLICABLE（00:07:46 记录）**：终态事件 spray outcome=NOT_APPLICABLE（error_detail=缺 `/iv_packets_front_mid`/`/iv_points_front_mid_transformed`，实际 topic 为 apriltag/bev/perception 系）；八步 attempt2 全 DONE（00:07:46 一分钟内收口，零模型请求）；`RESOURCE_RELEASED SCENE_EXEC_HOST`（00:07:46）；NAS 实测 `205E5054` 正式树子包=0 → **无伪切片，PASS**（与 B 基线一致）。D3 两 dup（eb4397c3 上轮 PASS + 24ab78bb 本轮 PASS）**全部收敛核销**。
- **D4 第2步（删 3 date-grouped submission）已执行确认**：`ingest_submission` 全集实测 **8 行**（id 1/2/3/4/5/7/11/12），`03281a51`/`5e08e73d`/`7f4e7b75` 三行已不存在——A 已删（删除时点介于上轮 00:0x 与本轮 00:20 之间，A 台账对账属 A 面，TESTER 只核在/不在）。
- **D4 第3步（409 释放/flat 绑定）未达成**：`a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 三 flat 提交仍 **PENDING_INPUT**（row_version 1、source_id 空、bound 路径空）；scanner 日志持续 `FAILED recovering …/ready/spray/20261012/rosbag2_2026_10_12-16_00_13: HTTP 409`（最近 25m 多条）。根因仍指 `ready/spray/20261012/` date-grouped NAS 目录 **14,930,820,106 B 实测仍在**（D4 第4步删除未执行，责任 A；submission 删除单独不足以释放该 409 路径——待 A 下轮验证口径，TESTER 不代清）。
- **16_02_03 合法链 `scene-4acf689f`（D1 保留链）→ SCENE_RUNNING（00:07:56 取执行面后开跑）**：orchestrator 日志实测其 busy 循环止于 00:07:5x `dispatched`；heartbeat 持续至 **00:20:27**（30s 节奏正常）；八步 step_run 仍全 **QUEUED**（EXTRACT 未开跑事件，跨 DB3 大包 10GB 前置解析/EXTRACT 静默段）。**未判定卡死**（心跳+ACCEPTED 在途），下轮核步骤推进；SHA=源 PASS（23:0x）维持。
- **D2 dup 双写产物取证更新（现场口径修正）**：`.staging/scene-a4824f1c…/attempt-2` 实测已为**空目录（0 B）**（PUBLISH 原子移走后的残留壳）；真正第二份切片产物=正式树 `slices/test/spray/FFDEE943…_16Bc-*` **4 子包**（本轮 du 实测 202.8/202.8/202.1/201.6 MB）+ `051768B1`=1/`615A4A7B`=1（PASS 基线包）。**「保留现场」要求实际指向正式树 4 子包目录**（staging 壳无数据价值）——处置（保留/清理）仍等协调者裁决，TESTER 不删不并。
- **环境**：生产 18000 正常；8767 proxy `active_runs=[{scene-4acf689f, stage:ACCEPTED}]`；MySQL 容器 Up 5 days healthy；ready/spray 现有 8 flat 包目录+20261012/（date-grouped 残留）。
- 本轮全部动作只读（SSH processing-machine：生产 MySQL SELECT、8767/18000 只读探测、orchestrator/scanner/proxy docker logs、NAS du/ls/find）；未提交/retry/调模型/写生产、未清理任何文件/submission/run。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 空包拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **下一步**：下轮核 `4acf689f` 八步推进（EXTRACT 开跑/跨 DB3 边界）；A D4 第3/4步（删 `ready/spray/20261012/` NAS + flat 三提交绑定）后核 409 释放 + 逐包终态/产物/两次 reconcile（14_42_48 正式全链）；dup FFDEE943 4 子包处置等协调者裁决；全批 8 包齐后交付 TEST_REPORT_PENDING。


## 增量验收 00:3x（D4 submission 删除独立复核 + 4acf689f 在途 + scanner 409 口径更新，2026-10-14T00:33+08:00 只读实测）

- **唤醒源**：prerun 指纹 `9877395e…`（变更源=上轮 00:24 事件回声 + `BATCH-STATUS.md` 00:28 同步 + `sessions/TESTER.md`）；消费口径=ruling 第五节 TESTER 增量范围，无新派单。
- **16_02_03 合法链 `scene-4acf689f`（D1 保留链）→ SCENE_RUNNING attempt1（00:33 复核）**：pipeline_run updated_at 00:33:28（DB 时钟，心跳持续刷新）；orchestrator 日志 `dispatched Scene pipeline scene-4acf689f…` 后 12min 窗口**零 busy 循环**（执行面独占在跑）；八步 step_run attempt1 **仍全 QUEUED（started_at=NULL）**——00:07:56 取 SCENE_EXEC_HOST 后约 25min 静默段，跨 DB3 大包 10GB 前置解析/EXTRACT 未开跑，**未判卡死**（心跳+proxy `active_runs` 为 4acf689f/ACCEPTED 在案），下轮核 EXTRACT started_at 落值。SHA=源 PASS（23:0x）维持。
- **D4 第2步（3 date-grouped submission 删除）独立复核 → 确认**：`ingest_submission` 00:33 实测 8 行（`24d60fee`/`9949d1a7`/`99615748`/`e5649055` SCHEDULED + `a65a25a7`/`87dfebaa`/`518089ed`/`7a71e404` PENDING_INPUT），`03281a51`/`5e08e73d`/`7f4e7b75` 不在——与 A 00:17:59 删除声明一致。
- **D4 第3步（409 释放/flat 绑定）→ 口径更新，未达成**：flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 00:33 仍 **PENDING_INPUT 未绑定**；scanner 日志 00:25 起 12min 窗口 **409 recovering 行消失**（上轮 00:20 前持续），`scan_job` id3977（00:25:34）/3975（00:15:33）均 **SUCCESS failed=2**（=空包 16_33_10 `missing rosbag2_bagfile_information` + 1 历史项，与 22:3x 拒绝口径同族）；flat 绑定仍未发生，**409 根因是否随 submission+NAS 删除释放，待 A 绑定回执/下轮 scanner 绑定行核实**（TESTER 不代绑）。
- **D4 第4步（NAS `ready/spray/20261012/` 删除）独立复核 → 完成确认**：00:33 NAS 实测 `ready/spray/` 仅 7 个 flat 包目录（14_42_48/15_58_23/16_00_13/16_02_03/16_31_25/16_37_47/16_58_28），date-grouped `20261012/` **不在**——A 00:20:59 删除声明与账实一致（原件移 `.upload-staging/d4-dategrouped-delete-20261014/` 属 A 台账面）。
- **dup 双写产物现场维持（不删不并，处置等协调者裁决）**：`slices/test/spray/` 00:33 实测 6 目录=`FFDEE943…_16Bc-*` **×4**（dup `a4824f1c` SUCCESS 双写产物，~202MB×4）+ `051768B1…×1`（16_00_13 PASS 基线）+ `615A4A7B…×1`（首包 PASS 基线）；`.staging/scene-a4824f1c…` 壳目录已清（00:2x 在案），保留现场=正式树 4 子包目录。
- **scene run 全集（00:33 API+DB 双核一致）7 = 6 SCENE_DONE + 1 SCENE_RUNNING**：`c4a88c07`(15_58_23 复用 PASS)/`604c0896`(16_00_13 SUCCESS PASS)/`bc8c1d1c`(16_31_25 NOT_APPLICABLE PASS)/`a4824f1c`(dup SUCCESS 双写产物)/`eb4397c3`(dup NOT_APPLICABLE PASS)/`24ab78bb`(dup NOT_APPLICABLE PASS) + `4acf689f`(16_02_03 合法链 RUNNING)。
- 本轮全部动作只读（SSH processing-machine：生产 MySQL SELECT、8767 proxy health、scanner/orchestrator docker logs、NAS ls/du）；未提交/retry/调模型/写生产、未清理任何文件/submission/run。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **下一步**：下轮核 `4acf689f` EXTRACT/八步推进（started_at 落值）+跨 DB3 真实时间戳边界；A flat 三提交绑定回执后核 SCHEDULED/终态/产物/两次 reconcile（14_42_48 正式全链）；dup FFDEE943 4 子包处置等协调者裁决；全批 8 包齐后交付 TEST_REPORT_PENDING。

## 增量验收 00:4x（4acf689f 在途 45min 静默段核实 + D4 等 A 绑定 + dup 裁决登记，2026-10-14T00:52+08:00 只读实测）

- **唤醒源**：prerun 指纹 `37d3a698…`（变更源=上轮 00:36 事件回声 + `BATCH-STATUS.md` + 新裁决 `ruling-dup-slices-0038.md` + `sessions/TESTER.md`）；消费口径=ruling 第五节 TESTER 增量范围 + dup 裁决 TESTER 责任项（登记+核账口径），无新派单。
- **裁决 `ruling-dup-slices-0038` 消费（00:39 协调者）**：dup FFDEE943×4 子包=不删不并、不计入验收交付物，TEST_REPORT 以「双写事件产物」一节如实登记；正式 `a65a25a7` run 验收时把「发布幂等如何处置已存在的同名 source 切片」并入两次 reconcile 核账口径，如实记录不预判。本回执已按此口径登记现场（下项），**正式 run 未绑定未执行，核账面 NOT_RUN 待 `a65a25a7` 绑定后执行**。
- **dup 双写事件产物现场登记（裁决要求项①）**：`scene-a4824f1c` attempt-2（源自已删 submission `13dc398c`，22:53:02 外部人工 RETRY 重入）23:54:41 SCENE_DONE SUCCESS，发布 `slices/test/spray/FFDEE943…_16Bc-{0c0695538838f5b527/491286c911503f1984/7a95e769a0c3a173af/94a9db6d664584de6b}` 4 子包各 ~202MB（00:42 NAS 实测目录 mtime 23:54 在案）；与 14_42_48 正式 source 同源性=按内容哈希派生同一 source `FFDEE943`（裁决口径）；`.staging/scene-a4824f1c…` 壳已清；现场保留不删不并。
- **16_02_03 合法链 `scene-4acf689f` → SCENE_RUNNING attempt1，00:46:29 heartbeat 活跃，45min 静默段在算**：pipeline_run 00:46 实测 heartbeat_at/updated_at=00:46:29；八步 attempt1 **仍全 QUEUED（started_at=NULL）**；proxy worker `scene_host_proxy.py`（pid 3495931，04:30 存活）00:52 实测 **10.97GiB RAM / 2.54% CPU**=10GB 大包前置解析/EXTRACT 在算，**非卡死**（上轮 00:33 判未卡死口径维持，本轮补进程级在算证据）；orchestrator 日志 `dispatched` 行 UTC 16:07:56（=北京 00:07:56）后零 busy 循环=执行面独占在跑。SHA=源 PASS（23:0x）维持。
- **D4 第3步（flat 三提交绑定）→ 未达成，等 A**：`ingest_submission` 00:46 实测 8 行不变（`24d60fee`/`9949d1a7`/`99615748`/`e5649055` SCHEDULED + `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28)/`7a71e404`(空包) PENDING_INPUT）；**409 已实证消失**：scanner 日志末 409 行=UTC 16:15:33（=北京 00:15:33，指向已删 `ready/spray/20261012/` 路径），其后零 409；`scan_job` id3978–3981（00:25–00:45 四轮）全 **SUCCESS failed:2**（=16_33_10 空包 missing rosbag2_bagfile_information 同族+1 历史）——409 面随 D4 第4步 NAS 删除释放，**但 scanner 尚未对 flat 三包产生绑定行**，绑定推进责任 A，TESTER 不代绑；14_42_48 正式全链维持 NOT_RUN。
- **环境**：生产 18000 scene 队列 API 7 run 与 DB 一致（6 SCENE_DONE + 4acf689f SCENE_RUNNING）；proxy health ok `active_runs=[4acf689f ACCEPTED]`；NAS `ready/spray/` 7 flat 包目录、date-grouped 不在（D4 第4步维持确认）；load 1.26 回落；scene 串行单执行面正常。
- 本轮全部动作只读（SSH processing-machine：生产 MySQL SELECT ingest_submission/pipeline_run/step_run/pipeline_event/scan_job、docker logs/stats/top、8767/18000 只读 API、NAS ls）；未提交/retry/调模型/写生产、未清理任何文件/submission/run。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **下一步**：下轮核 `4acf689f` EXTRACT started_at 落值/八步推进 + SCENE_DONE 后跨 DB3 真实时间戳边界/产物/两次 reconcile（16_02_03 正式全链）；A flat 三提交 scanner 绑定行出现后核 SCHEDULED/终态/产物（14_42_48 正式全链，reconcile 核账并入 dup 同名 source 切片处置证据，按 0038 裁决口径如实记录）；全批 8 包齐后交付 TEST_REPORT_PENDING（含「双写事件产物」一节）。

## 增量验收 01:0x（4acf689f 推进在算 19GiB + D4 等 A flat 绑定 + 409 零出现，2026-10-14T01:05+08:00 只读实测）

- **唤醒源**：prerun 指纹 `948923d8…`（变更源=上轮 00:54 事件回声 + `ruling-2338-verify.md` 00:39 增补回声 + `BATCH-STATUS.md` 00:39 同步 + `ruling-dup-slices-0038.md` 回声 + sessions）；均已消费，**无新派单/新 decision**，消费口径=ruling 第五节 TESTER 增量范围 + 0038 裁决 TESTER 责任项（登记已完成于 00:4x 段）。
- **16_02_03 合法链 `scene-4acf689f` → SCENE_RUNNING attempt1，13min 增量对比确认推进在算**：pipeline_run 01:04 实测 SCENE_RUNNING/attempt1/heartbeat_at=updated_at=**01:04:00**（持续刷新）；八步 attempt1 **仍全 QUEUED（started_at=NULL）**——自 00:07:56 取执行面后约 57min 前置静默段；**proxy worker（`rosbag-scene-proxy` 容器）01:05 docker stats 实测 19.47GiB RAM/24.57% CPU**（00:52 为 10.97GiB/2.54%）→ 内存 13min 增长 ~8.5GiB，=10GB 跨 DB3 大包前置解析/EXTRACT 在算推进，**非卡死**（00:4x 进程级在算证据的增量延续）；orchestrator 日志 dispatched 后零 busy 循环=执行面独占在跑；proxy `active_runs=[{4acf689f stage:ACCEPTED}]`。SHA=源 PASS（23:0x）维持。
- **D4 第3步（flat 三提交绑定）→ 继续未达成，等 A**：`ingest_submission` 01:04 实测 8 行不变（`9949d1a7`/`e5649055`/`99615748`/`24d60fee` SCHEDULED + `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28)/`7a71e404`(空包) PENDING_INPUT，source_id 全空）；**scanner 409 近 40min 实测零出现**（`docker logs -t --since 40m | grep 409`=空；末次 409 行=北京 00:15:33 指向已删 `ready/spray/20261012/` 路径，00:4x 口径维持）；`scan_job` id3979–3983（00:35–00:55 三轮 incoming）全 **SUCCESS failed:2**（=16_33_10 空包 `missing rosbag2_bagfile_information` 同族+1 历史）——409 面持续释放，**但 scanner 尚未对 flat 三包产生绑定行/提交行**，绑定推进责任 A，TESTER 不代绑；**14_42_48 正式全链维持 NOT_RUN**（`a65a25a7` 未绑定未执行；reconcile 核账并入 dup 同名 source 切片处置证据按 0038 裁决口径待正式 run 终态后执行）。
- **dup 双写产物现场维持（不删不并，0038 裁决）**：`slices/test/spray/` 01:05 实测 6 目录=`FFDEE943…_16Bc-*` **×4**（dup `a4824f1c` SUCCESS 双写产物，已登记于 00:4x 段）+ `051768B1…×1`（16_00_13 PASS 基线）+ `615A4A7B…×1`（首包 PASS 基线）；`ready/spray/` 7 flat 包目录、date-grouped `20261012/` 不在（D4 第4步维持确认）。
- **scene run 全集（01:04 DB 实测）7 = 6 SCENE_DONE + 1 SCENE_RUNNING**：`c4a88c07`(20:24:05)/`604c0896`(21:43:29)/`bc8c1d1c`(21:43:39)/`a4824f1c`(23:54:41)/`eb4397c3`(00:01:30)/`24ab78bb`(00:07:46) 全 DONE + `4acf689f` RUNNING；与上轮 API+DB 双核一致。
- 本轮全部动作只读（SSH processing-machine：生产 MySQL SELECT ingest_submission/pipeline_run/step_run/pipeline_event/scan_job、scanner/orchestrator docker logs、docker stats、8767 proxy health、NAS ls）；未提交/retry/调模型/写生产、未清理任何文件/submission/run。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **下一步**：下轮核 `4acf689f` 八步推进（EXTRACT started_at 落值预期临近）+ SCENE_DONE 后跨 DB3 真实时间戳边界/产物/两次 reconcile（16_02_03 正式全链）；A flat 三提交 scanner 绑定行出现后核 14_42_48 正式全链（reconcile 核账并入 dup 同名 source 切片处置证据，0038 口径）；全批 8 包齐后交付 TEST_REPORT_PENDING（含「双写事件产物」一节）。
## 增量验收 01:1x（4acf689f 71min 前置段推进在算 + D4 等 A flat 绑定 + 空包拒绝持续可追溯，2026-10-14T01:19+08:00 只读实测）

- **唤醒源**：prerun 指纹 `f89a51ab...`（变更源=上轮 01:11 自写事件 `6cd0009d...` + `sessions/TESTER.md` 回声，均已在 01:0x 段消费，**无新派单/新 decision**）；消费口径=ruling 第五节 TESTER 增量范围。
- **16_02_03 合法链 `scene-4acf689f` -> SCENE_RUNNING attempt1，71min 前置段推进在算**：01:18:33 实测 heartbeat_at=updated_at=01:18:33（30s 周期持续刷新，RESOURCE_HEARTBEAT SCENE_EXEC_HOST 在案）；八步 attempt1 **仍全 QUEUED（started_at=NULL）**；proxy 容器 01:19 docker stats 实测 **17.5GiB RAM / 386.59% CPU**（01:05 为 19.47GiB/24.57%）-> CPU 多核高负载爆发=10GB 跨 DB3 大包前置解析/EXTRACT 活跃在算，**非卡死**；8767 proxy health ok `active_runs=[4acf689f stage:ACCEPTED pid:1]`。SHA=源 PASS（23:0x）维持。
- **D4 第3步（flat 三提交绑定）-> 继续未达成，等 A**：`ingest_submission` 01:19 实测 8 行不变（`9949d1a7`(->615A4A7B)/`e5649055`(->0BBF4C1C)/`99615748`(->051768B1)/`24d60fee`(->91FFEEC1) SCHEDULED + `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28)/`7a71e404`(16_33_10 空包) PENDING_INPUT，source_id 全空）；**scanner 无真 409 行**（--since 30m grep "409|PATH_CLAIMED" 唯一命中=UTC 17:15:38.886140944Z 时间戳微秒数字串伪匹配，非 409 事件；真 409 末次仍=北京 00:15:33 指向已删 date-grouped 路径，00:4x 口径维持）；`scan_job` id3982-3987（00:55-01:15 三轮）scene 根全 **SUCCESS failed:2**（=16_33_10 空包 `missing rosbag2_bagfile_information` 持续拒绝同族+1 历史）——**空包拒绝 01:15:38 仍在持续可追溯**（10min 周期）；flat 三包绑定行仍未产生，绑定推进责任 A，TESTER 不代绑；**14_42_48 正式全链维持 NOT_RUN**。
- **scene run 全集（01:19 DB 实测）7 = 6 SCENE_DONE + 1 SCENE_RUNNING**：`c4a88c07`(20:24:05)/`604c0896`(21:43:29)/`bc8c1d1c`(21:43:39)/`a4824f1c`(23:54:41)/`eb4397c3`(00:01:30)/`24ab78bb`(00:07:46) + `4acf689f`(RUNNING)；与 01:04 双核一致，无新 run。
- **dup 双写产物现场维持（不删不并，0038 裁决）**：`slices/test/spray/` 01:19 find 实测 6 目录=`FFDEE943..._16Bc-*` x4（dup `a4824f1c` 双写产物）+`051768B1...x1`（16_00_13 PASS 基线）+`615A4A7B...x1`（首包 PASS 基线）；`ready/spray/` 7 flat 包目录、date-grouped 不在；`incoming/spray/` 仅空包 16_33_10。
- 本轮全部动作只读（SSH processing-machine：backend 容器内 pymysql SELECT pipeline_run/step_run/ingest_submission/pipeline_event/scan_job、8767 只读 API、docker logs/stats、NAS ls/find）；未提交/retry/调模型/写生产、未清理任何文件/submission/run。backend 容器 /tmp 残留 1 份本角色只读探针 `t0114b2.py`（容器内 rm 权限不足，宿主机 /tmp 无残留），不影响验收。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **下一步**：下轮核 `4acf689f` 八步推进（PRECHECK/EXTRACT started_at 落值预期临近）+ SCENE_DONE 后跨 DB3 真实时间戳边界/产物/两次 reconcile（16_02_03 正式全链）；A flat 三提交 scanner 绑定行出现后核 14_42_48 正式全链（reconcile 核账并入 dup 同名 source 切片处置证据，0038 口径）；全批 8 包齐后交付 TEST_REPORT_PENDING（含「双写事件产物」一节）。
## 增量验收 01:2x（4acf689f ~80min 前置段持续在算 + flat 三提交仍等 A 绑定 + 空包拒绝持续，2026-10-14 01:28+08:00 只读实测）

- **唤醒源**：prerun 指纹 `fb875e67…`（变更源=上轮 01:22 自写事件 `6dd6319f…` + `sessions/TESTER.md` 回声，均已在 01:1x 段消费口径内，**无新派单/新 decision**）；消费口径=ruling 第五节 TESTER 增量范围。
- **16_02_03 合法链 `scene-4acf689f` → SCENE_RUNNING attempt1，~80min 前置段持续在算**：01:27:06 实测 pipeline_run updated_at=heartbeat 持续刷新；八步 attempt1 **仍全 QUEUED（started_at=NULL）**；proxy 容器 01:27 docker stats 实测 **18.5GiB RAM / 341.87% CPU**（01:19 为 17.5GiB/386.59%、01:05 为 19.47GiB/24.57%）→ 多核高负载维持=10GB 跨 DB3 大包前置解析/EXTRACT 活跃在算，**非卡死**；8767 proxy health ok `active_runs=[4acf689f stage:ACCEPTED pid:1]`。SHA=源 PASS（23:0x）维持。
- **D4 第3步（flat 三提交绑定）→ 继续未达成，等 A**：`ingest_submission` 01:27 实测 8 行不变（`9949d1a7`→`615A4A7B`/`e5649055`→`0BBF4C1C`/`99615748`→`051768B1`/`24d60fee`→`91FFEEC1` SCHEDULED + `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28)/`7a71e404`(空包) PENDING_INPUT，source_id 全空）；scanner 12min 窗口无 409 行（唯一 FAILED=16_33_10 空包 `missing rosbag2_bagfile_information` 10min 周期持续）；`scan_job` id3989（01:25:39）incoming 根 **SUCCESS failed:2** 维持拒绝口径——**空包拒绝 01:25:39 持续可追溯**；flat 三包绑定行仍未产生，绑定推进责任 A，TESTER 不代绑；**14_42_48 正式全链维持 NOT_RUN**。
- **scene run 全集（01:27 DB 实测）7 = 6 SCENE_DONE + 1 SCENE_RUNNING**：`c4a88c07`/`604c0896`/`bc8c1d1c`/`a4824f1c`/`eb4397c3`/`24ab78bb` 全 DONE + `4acf689f` RUNNING；与 01:19 一致，无新 run。
- **dup 双写产物现场维持（不删不并，0038 裁决）**：`slices/test/spray/` 01:27 ls 实测 6 目录=`FFDEE943…_16Bc-*` ×4（dup 双写产物，已登记）+ `051768B1…×1`（16_00_13 PASS 基线）+ `615A4A7B…×1`（首包 PASS 基线）；`ready/spray/` 7 flat 包目录、date-grouped 不在；`incoming/spray/` 仅空包 16_33_10。
- 本轮全部动作只读（SSH processing-machine：backend 容器内 pymysql SELECT pipeline_run/step_run/pipeline_event/ingest_submission/scan_job、8767 只读 API、docker stats/logs、NAS ls）；未提交/retry/调模型/写生产、未清理任何文件/submission/run。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **下一步**：下轮核 `4acf689f` 八步推进（PRECHECK/EXTRACT started_at 落值）+ SCENE_DONE 后跨 DB3 真实时间戳边界/产物/两次 reconcile（16_02_03 正式全链）；A flat 三提交 scanner 绑定行出现后核 14_42_48 正式全链（0038 口径）；全批 8 包齐后交付 TEST_REPORT_PENDING（含「双写事件产物」一节）。

## 增量验收 01:01:3x（4acf689f 前置段 CPU 骤降 341%→0.5% + flat 三提交仍等 A 绑定 + 空包拒绝持续，2026-10-14 01:41+08:00 只读实测）

- **唤醒源**：prerun 指纹 `4b818d96…`（变更源=上轮 01:28 自写事件 `c7149fdc…` + `sessions/TESTER.md` 回声，均已在 01:2x 段消费，**无新派单/新 decision**）；消费口径=ruling 第五节 TESTER 增量范围。
- **16_02_03 合法链 `scene-4acf689f` → SCENE_RUNNING attempt1，~88min 前置段，CPU 骤降为本轮关键增量**：01:35:38 实测 heartbeat_at=updated_at=01:35:38（持续刷新）；八步 attempt1 **仍全 QUEUED（started_at=NULL）**；proxy worker pid 3495931（elapsed 05:13+）——**docker stats 连续 3 测（间隔 8s，01:36–01:38）CPU=0.45%/0.57%/0.58%，RAM 稳定 20.43GiB/30.78GiB**，对比 01:27 341.87%/18.5GiB、01:19 386.59%/17.5GiB、01:05 24.57%/19.47GiB：**多核高负载前置段已过或进入静默子段，内存高位维持=10GB 跨 DB3 包数据已在内存**；容器日志窗口内反复出现 `OpenGL(4.5)/FEngine created/EGL` 渲染引擎重建行（每次 ~2 行一组，多组）；8767 proxy health ok `active_runs=[4acf689f stage:ACCEPTED pid:1]`。**暂不判卡死**（heartbeat 30s 周期持续）；若下轮八步仍全 QUEUED 且 CPU 维持低位，升级证据链（连续静默段时长+FEngine 重建频率）报协调者定性。SHA=源 PASS（23:0x）维持。
- **D4 第3步（flat 三提交绑定）→ 继续未达成，等 A**：`ingest_submission` 01:35 实测 8 行不变（`9949d1a7`→`615A4A7B`/`e5649055`→`0BBF4C1C`/`99615748`→`051768B1`/`24d60fee`→`91FFEEC1` SCHEDULED + `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28)/`7a71e404`(空包) PENDING_INPUT，source_id 全空）；**14_42_48 正式全链维持 NOT_RUN**。
- **空包拒绝持续可追溯**：`scan_job` id3991（01:35:39）/3989（01:25:39）incoming 根均 **SUCCESS failed:2**（=16_33_10 `missing rosbag2_bagfile_information` 10min 周期持续同族+1 历史）；无 409 新行（00:4x 后口径维持）。
- **scene run 全集（01:35 DB 实测）7 = 6 SCENE_DONE + 1 SCENE_RUNNING**：`c4a88c07`(20:24:05)/`604c0896`(21:43:29)/`bc8c1d1c`(21:43:39)/`a4824f1c`(23:54:41)/`eb4397c3`(00:01:30)/`24ab78bb`(00:07:46) + `4acf689f`(RUNNING)；与 01:27 一致，无新 run。
- **NAS 物理面（01:3x 实测）**：`slices/test/spray/` 6 目录=`FFDEE943…_16Bc-*`×4（dup 双写产物，0038 裁决不删不并）+`051768B1…×1`+`615A4A7B…×1`（PASS 基线）；`ready/spray/` 7 flat 包目录（14_42_48/15_58_23/16_00_13/16_02_03/16_31_25/16_37_47/16_58_28）、date-grouped 不在；`incoming/spray/` 仅空包 16_33_10。宿主机 `/`（NVMe）28% 已用、367G 可用。
- 本轮全部动作只读（backend 容器内 pymysql SELECT pipeline_run/step_run/ingest_submission/scan_job、docker stats×3/top/logs、8767 只读 API、NAS ls、df）；未提交/retry/调模型/写生产、未清理任何文件/submission/run。backend 容器 /tmp 残留本角色只读探针 t0130a1.py/t0130a2.py（容器内 rm 权限不足，宿主机 /tmp 无残留）。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **下一步**：下轮核 4acf689f CPU 回落性质（八步 PRECHECK/EXTRACT started_at 是否落值；持续低位则升级静默段证据链报协调者定性）+ SCENE_DONE 后跨 DB3 真实时间戳边界/产物/两次 reconcile（16_02_03 正式全链）；A flat 三提交 scanner 绑定行出现后核 14_42_48 正式全链（0038 口径）；全批 8 包齐后交付 TEST_REPORT_PENDING（含「双写事件产物」一节）。

## 增量验收 01:4x（4acf689f 静默段定性证据链升级：进程级零上下文切换增量 + flat 三提交仍等 A 绑定，2026-10-14 01:52+08:00 只读实测）

- **唤醒源**：prerun 指纹 `61fe8ce6…`（变更源=上轮 01:41 自写事件 `tester-t11s-batch-1012-4acf-cpu-drop-…` + `sessions/TESTER.md` 回声，已消费，**无新派单/新 decision**）；消费口径=ruling 第五节 TESTER 增量范围。
- **16_02_03 合法链 `scene-4acf689f` → SCENE_RUNNING attempt1，静默段证据链升级（本轮关键增量）**：01:48:39 DB 实测 heartbeat_at=updated_at=01:48:39 持续刷新；八步 attempt1 **仍全 QUEUED started_at=NULL**（23:05:32 入队至 01:48 约 163min，其中 01:05-01:38 CPU 高/低交替后进入持续低位）。**进程级取证（宿主机 top + /proc 双采样，间隔 10s）**：pid 3495931 %CPU=0.0、RES 17.4g、State S(sleeping)、52 线程全 Ssl；`voluntary_ctxt_switches=55223` 双采样**零增量=worker 完全停转、无 I/O 无计算推进**；对比时间线 01:05 24.57%→01:19 386.59%→01:27 341.87%→01:36-38 0.45/0.57/0.58%→01:49 0.51%。**定性升级**：01:3x 判「前置解析段已过或静默子段，暂不判卡死」；本轮零上下文切换增量证据成立，**静默段已 >20min 且 worker 零推进，heartbeat 由 orchestrator 侧维护不能替代 worker 在算——按 01:3x 预设口径升级报协调者定性（疑似渲染引擎重建后等待条件未满足/卡死），TESTER 不自行 cancel/retry**（生产写边界）。SHA=源 PASS（23:0x）维持；SCENE_DONE 后跨 DB3 边界/产物/两次 reconcile 维持 NOT_RUN。
- **D4 第3步（flat 三提交绑定）→ 继续未达成，等 A**：`ingest_submission` 01:48 实测 8 行不变（`9949d1a7`→`615A4A7B`/`e5649055`→`0BBF4C1C`/`99615748`→`051768B1`/`24d60fee`→`91FFEEC1` SCHEDULED + `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28)/`7a71e404`(空包) PENDING_INPUT source_id 全空）；**14_42_48 正式全链维持 NOT_RUN**。
- **空包拒绝持续可追溯**：`scan_job` id3993（01:45:40）/3991（01:35:39）incoming 根均 **SUCCESS failed:2**（=16_33_10 `missing rosbag2_bagfile_information` 10min 周期持续同族）；无 409 新行（00:4x 后口径维持）。
- **scene run 全集（01:48 DB 实测）7 = 6 SCENE_DONE + 1 SCENE_RUNNING**：`c4a88c07`(20:24:05)/`604c0896`(21:43:29)/`bc8c1d1c`(21:43:39)/`a4824f1c`(23:54:41)/`eb4397c3`(00:01:30)/`24ab78bb`(00:07:46) + `4acf689f`(RUNNING heartbeat 01:48:39)；与 01:35 一致，无新 run。
- **NAS 物理面（01:48 实测）**：`slices/test/spray/` 6 目录=`FFDEE943…_16Bc-*`×4（dup 双写产物，0038 裁决不删不并）+`051768B1…`+`615A4A7B…`（PASS 基线）；`ready/spray/` 7 flat 包目录、date-grouped 不在；`incoming/spray/` 仅空包 16_33_10。
- **环境（01:4x 双核）**：18000 `status:ready environment:production`；8767 `active_runs=[scene-4acf689f stage:ACCEPTED]`；docker stats 各容器低负载（backend 0.08%、proxy 0.51%/20.44GiB）。
- 本轮全部动作只读（backend 容器内 pymysql SELECT pipeline_run/step_run/ingest_submission/scan_job、docker stats/top、8767 只读 API、NAS ls、/proc 状态与 voluntary_ctxt_switches 双采样）；未提交/retry/调模型/写生产、未清理任何文件/submission/run。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **风险报协调者（不自行处置）**：4acf689f worker 零推进静默段 >20min 需定性；若卡死，16_02_03 为全批唯一剩余 runtime 链，且阻塞执行面导致 A flat 三提交（14_42_48/16_37_47/16_58_28）无法进入 runtime，批次收敛被拖。
- **下一步**：等协调者定性 4acf689f（cancel/retry 由 A/协调者执行）；SCENE_DONE 后跨 DB3 真实时间戳边界/产物/两次 reconcile（16_02_03 正式全链）；A flat 三提交 scanner 绑定行出现后核 14_42_48 正式全链（0038 口径）；全批 8 包齐后交付 TEST_REPORT_PENDING（含「双写事件产物」一节）。

## 增量验收 02:0x（4acf689f 静默段证据链修正：CPU 噪声甄别 + 上下文切换低速增长，2026-10-14 02:01+08:00 只读实测）

- **唤醒源**：prerun 指纹 `7c2b9d29…`（变更源=上轮 01:52 自写事件 `tester-t11s-batch-1012-4acf-stall-escalate-…` + `sessions/TESTER.md` 回声，均已消费，**无新派单/新 decision**）；消费口径=ruling 第五节 TESTER 增量范围。
- **16_02_03 合法链 `scene-4acf689f` → SCENE_RUNNING attempt1，静默段证据链增量修正（本轮关键）**：02:00:10 DB 实测 heartbeat_at=updated_at 持续刷新（30s 节奏）；八步 attempt1 **仍全 QUEUED started_at=NULL**（23:05:32 入队至 02:00 约 175min）。**CPU 回升甄别**：02:00:26 docker stats 5.70%（上轮 01:49 为 0.51%）——经 /proc/3495931 10s 双采样甄别=**短窗口采样噪声**（voluntary_ctxt_switches 增量仅 20、top -bn1 实测 %CPU=0.0/RES 17.4g/State S、52 线程全 Ssl），worker **未恢复实质在算**。**01:4x『零推进』口径修正**：voluntary_ctxt_switches 01:49 55223 → 02:01 56536，12min **+1313（~110/min 低速增长）=worker 存在低频事件循环/等待活动，非完全停转**；定性升级维持（01:36-02:01 约 25min 零实质推进、八步零 started_at 落值），**按预设口径报协调者定性（疑似渲染引擎重建后等待条件未满足/卡死或极慢推进），TESTER 不自行 cancel/retry**（生产写边界）。SHA=源 PASS（23:0x）维持；SCENE_DONE 后跨 DB3 边界/产物/两次 reconcile 维持 NOT_RUN。
- **D4 第3步（flat 三提交绑定）→ 继续未达成，等 A**：`ingest_submission` 02:00 实测 8 行不变（`9949d1a7`→`615A4A7B`/`e5649055`→`0BBF4C1C`/`99615748`→`051768B1`/`24d60fee`→`91FFEEC1` SCHEDULED + `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28)/`7a71e404`(空包) PENDING_INPUT source_id 全空）；**14_42_48 正式全链维持 NOT_RUN**。
- **空包拒绝持续可追溯**：`scan_job` id3995（01:55:40）/3993（01:45:40）incoming 根均 **SUCCESS failed:2**（=16_33_10 `missing rosbag2_bagfile_information` 10min 周期持续同族）；无 409 新行（00:4x 后口径维持）。
- **scene run 全集（02:00 DB 实测）7 = 6 SCENE_DONE + 1 SCENE_RUNNING**：`c4a88c07`(20:24:05)/`604c0896`(21:43:29)/`bc8c1d1c`(21:43:39)/`a4824f1c`(23:54:41)/`eb4397c3`(00:01:30)/`24ab78bb`(00:07:46) + `4acf689f`(RUNNING heartbeat 02:00:10)；与 01:48 一致，无新 run。
- 本轮全部动作只读（backend 容器内 pymysql SELECT pipeline_run/step_run/ingest_submission/scan_job/pipeline_event、/proc 双采样+top、docker stats、ssh）；未提交/retry/调模型/写生产、未清理任何文件/submission/run。容器 /tmp 残留本角色只读探针 t0155.py/t0155c.py/t0155b.py（容器内 rm 权限不足，宿主机 /tmp 副本同轮可清），不影响验收。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **风险报协调者（不自行处置）**：4acf689f 静默段证据链修正后定性不变——~25min 零实质推进（低速事件循环 ~110 ctxsw/min，八步零开跑）；16_02_03 为全批唯一剩余 runtime 链且阻塞串行执行面，A flat 三提交（14_42_48/16_37_47/16_58_28）无法进入 runtime，批次收敛被拖；处置（cancel/retry/继续观察时限）等协调者裁决。
- **下一步**：等协调者定性 4acf689f 后按裁决核处置证据链（cancel 前后状态/事件/资源释放，或 retry 后新 attempt 八步推进）；SCENE_DONE 后跨 DB3 真实时间戳边界/产物/两次 reconcile（16_02_03 正式全链）；A flat 三提交 scanner 绑定行出现后核 14_42_48 正式全链（0038 口径）；全批 8 包齐后交付 TEST_REPORT_PENDING（含「双写事件产物」一节）。

## 增量验收 02:1x（4acf689f 定性证据分歧上报：DB 八步零推进 vs C obs22 进程层 INFER 段在算，2026-10-14 02:07+08:00 只读实测）

- **唤醒源**：prerun 指纹 `f12e29cb…`（变更源=上轮 02:03 自写事件 `tester-t11s-batch-1012-4acf-stall-slow-activity-…` + `sessions/TESTER.md` 回声，均已消费；另消费 C obs22 事件 `c-t11s-batch-1012-obs22-infer-phase-active-20261014`（02:01））；**无新派单/新 decision**。
- **16_02_03 合法链 `scene-4acf689f` → SCENE_RUNNING attempt1（02:07 DB 实测）**：heartbeat_at=02:07:40（30s 节奏）、lease_expires_at=02:09:40 活跃续租；八步 attempt1 **仍全 QUEUED started_at=NULL**（23:05:32 入队至 02:07 约 185min）。/proc/3495931 12s 双采样 voluntary_ctxt_switches 57347→57372（+25，~125/min，与 02:0x 的 ~110/min 同口径低速事件循环）、nonvoluntary 210 不变；docker stats proxy cpu=1.27%/mem=20.84GiB。
- **C obs22（02:01）交叉新证据消费 → 定性证据分歧（本轮关键）**：C 处理机只读实测 ① work 树 EXTRACT 产物冻结（jpg 1781/pcd 5373 双采样 90s 零新增、末件 frame_001787 mtime 17:30:53Z）=**EXTRACT 完成口径成立**；② 容器 /proc/net/tcp + 宿主 ss 双核 **VLM 192.168.2.45:8002 ESTAB 活跃通道**；③ RSS 15.8GB→18.2GB 持续增长 → C 判『EXTRACT 已完成、run 大概率处于 INFER/后续段计算，**在算未卡死**』。本角色 DB 层口径（八步 checkpoint 零 started_at、~185min 未开跑）与 C 进程/work 树层口径**存在证据分歧**——可能为 INFER 段长时计算但 step_run 状态边界写滞后，也可能为 checkpoint 停滞而推理通道空挂；**按协议报协调者统一裁决定性（含『卡死/极慢/正常 INFER』三选），TESTER 不自行 cancel/retry**（生产写边界）。
- **D4 第3步（flat 三提交绑定）→ 继续未达成，等 A**：`ingest_submission` 02:07 实测 8 行不变（`a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28)/`7a71e404`(空包) PENDING_INPUT source_id 全空 + 4 SCHEDULED 绑定不变）；**14_42_48 正式全链维持 NOT_RUN**。
- **空包拒绝持续可追溯**：`scan_job` id3997（02:05:40）/3995（01:55:40）incoming 根均 **SUCCESS failed:2**（10min 周期持续同族）；无 409 新行。
- **scene run 全集（02:07 DB 实测）7 = 6 SCENE_DONE + 1 SCENE_RUNNING**，与 02:00 一致无新 run；8767 `active_runs=[4acf689f ACCEPTED pid:1]`。
- 本轮全部动作只读（ssh 处理机：mysql 容器 SELECT pipeline_run/step_run/ingest_submission/scan_job/pipeline_event、/proc 双采样、docker stats、8767 health）；未提交/retry/调模型/写生产。scratch 探针 t0205*.py 已清理。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **下一步**：等协调者统一裁决 4acf689f 定性分歧后按裁决核处置证据链；SCENE_DONE 后跨 DB3 真实时间戳边界/产物/两次 reconcile（16_02_03 正式全链）；A flat 三提交 scanner 绑定行出现后核 14_42_48 正式全链（0038 口径）；全批 8 包齐后交付 TEST_REPORT_PENDING（含「双写事件产物」一节）。

## 增量验收 02:2x（4acf689f 静默段持续 ~2.5h+、ctxsw 低速同口径，等协调者定性裁决，2026-10-14 02:23+08:00 只读实测）

- **唤醒源**：prerun 指纹 `6615a9cb…`（变更源=上轮 02:11 自写事件 `7bd8e2c4…` + `sessions/TESTER.md` 回声，均已核读，**无新派单/新 decision**）；消费口径=ruling 第五节 TESTER 增量范围。
- **16_02_03 合法链 `scene-4acf689f` → SCENE_RUNNING attempt1（02:23 DB 实测）**：heartbeat_at=updated_at=02:23:41 持续刷新；八步 attempt1 **仍全 QUEUED started_at=NULL**（23:05:32 入队至 02:23 约 198min，静默段自 01:36 起已 ~50min）。**进程级同口径复采**：`/proc/3495931/status` voluntary_ctxt_switches 60130→60155（12s **+25，~125/min**，与 02:1x 的 57347→57372 同口径）、nonvoluntary 221 不变、top %CPU=0.0/RES 17.4g/State S；docker stats proxy cpu=0.90%/mem=20.84GiB——**低速事件循环持续、无实质推进**；定性分歧（DB 八步零推进 vs C obs22 进程层 INFER 段在算）维持报协调者裁决，TESTER 不自行 cancel/retry（生产写边界）。
- **D4 第3步（flat 三提交绑定）→ 继续未达成，等 A**：`ingest_submission` 02:2x 实测 8 行不变（`9949d1a7`→`615A4A7B`/`e5649055`→`0BBF4C1C`/`99615748`→`051768B1`/`24d60fee`→`91FFEEC1` SCHEDULED + `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28)/`7a71e404`(空包) PENDING_INPUT source_id 全空）；**14_42_48 正式全链维持 NOT_RUN**。
- **空包拒绝持续可追溯**：`scan_job` id3999（02:15:41）/3997（02:05:40）incoming 根均 **SUCCESS failed:2**（10min 周期持续同族）；无 409 新行。
- **scene run 全集（02:23 DB 实测）7 = 6 SCENE_DONE + 1 SCENE_RUNNING**，与 02:07 一致无新 run；8767 `active_runs=[4acf689f ACCEPTED pid:1]`。
- 本轮全部动作只读（ssh 处理机：mysql 容器 SELECT pipeline_run/step_run/ingest_submission/scan_job/pipeline_event、/proc/3495931/status 双采样、top、docker stats、8767 只读 API）；未提交/retry/调模型/写生产。scratch 探针 `tester_021x2_prod.py`/`tester_021x2_ctx.py` 在宿主机保留供复核。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **下一步**：等协调者统一裁决 4acf689f 定性分歧（静默段 ~2.5h+ 持续）及处置；SCENE_DONE 后跨 DB3 真实时间戳边界/产物/两次 reconcile（16_02_03 正式全链）；A flat 三提交绑定行出现后核 14_42_48 正式全链（0038 口径）；全批 8 包齐后交付 TEST_REPORT_PENDING（含「双写事件产物」一节）。

## 纠偏 02:3x（消费协调者 ruling-4acf-infer-active-0218：4acf689f 定性=INFER 模型推理活跃非卡死，本角色 stall-escalate 撤案，2026-10-14 02:3x+08:00）

- **裁决消费（本轮唯一外部新输入）**：协调者 02:1x 独立核实（VLM 36.152.27.114 日志 Running 3-4 reqs/Waiting 0+POST 200 连发+prefix cache ~95%、proxy 容器 /proc/1/net/tcp 持 192.168.2.45:8002 ESTABLISHED、work 树 jpg 1781/pcd 5373 冻结=EXTRACT 完成、lease 随 heartbeat 前移 error 空、CPU 低=远端内存受限推理）定性 4acf689f=**INFER 阶段远端模型推理活跃，非卡死**。本角色 01:4x/01:52『静默段零推进/卡死嫌疑』stall-escalate 与 02:03/02:11『DB vs 进程层证据分歧』口径**一并撤销**——协调者裁定属**阶段边界写口径**：八步 DB 状态在阶段完成/complete-scene 时翻转（PRECHECK 已 DONE），逐帧模型调用发生在 INFER 进程段不落逐步 DB 行，『~198min 无 started_at』不构成卡死证据；01:52 宿主 ss 空输出系观测盲区（连接在容器命名空间内）。**上段 02:2x 中『维持报协调者定性』为裁决前口径，本段注记过期**。
- **DB 侧 02:23 实测与裁决一致**：`scene-4acf689f` SCENE_RUNNING attempt1、heartbeat_at=02:23:41 持续刷新、八步全 QUEUED=**模型段完成信号未到**（非静默段）；ctxsw 60130→60155（12s +25）=I/O 编排低速活动，与『宿主仅编排、推理在远端』口径吻合。
- **新核销口径（按裁决执行）**：改核模型段完成信号=checkpoint 翻 EXTRACT/DONE、八步 DB 推进、SCENE_DONE 三选一；**不再升级 CPU 静默项**。升级条件仅=heartbeat 连续 4 败 / run 翻 FAILED / VLM Waiting 持续>0 且 proxy 无 ESTABLISHED / 八步翻 FAILED 错误面。不 kill/cancel/retry（跨夜既定口径维持）。
- **批次面不变**：flat 三提交（`a65a25a7`/`87dfebaa`/`518089ed`）+空包 `7a71e404` 仍 PENDING_INPUT source_id 全空（串行阻塞等 4acf689f 终态后 D4③ 推进，BATCH-STATUS 口径）；14_42_48 正式全链维持 NOT_RUN；空包拒绝周期持续（scan_job 3999 failed:2）；scene run 7=6DONE+1RUNNING；PASS 基线不变。
- 本轮动作：读裁决与 BATCH-STATUS（只读）+ 落本纠偏段；claim→event→release 闭环（token 不出脚本）。
- **下一步**：下轮按新口径等模型段完成信号（预计模型段持续数小时，跨夜继续观察）；SCENE_DONE 后核跨 DB3 真实时间戳边界/产物/两次 reconcile（16_02_03 正式全链）；A flat 绑定行出现后核 14_42_48 正式全链（0038 口径）；全批 8 包齐后交付 TEST_REPORT_PENDING（含「双写事件产物」一节）。

## 增量验收 02:4x（按 ruling 新口径核 4acf689f：INFER 持续活跃、无完成信号、升级条件逐项未命中，2026-10-14 02:43+08:00 只读实测）

- **唤醒源**：prerun 指纹 `451c015c…`（变更源=上轮 02:3x 自写事件 `29895cf6…`/`ecaaaf04…` + `sessions/TESTER.md` 回声，均已核读，**无新派单/新 decision**）；消费口径=ruling-4acf-infer-active-0218 第五节。
- **16_02_03 合法链 `scene-4acf689f` → SCENE_RUNNING attempt1，02:43:42 heartbeat 持续刷新；八步仍全 QUEUED started_at=NULL**（23:05:32 入队至 02:43 约 218min）=模型段完成信号未到，与裁决『阶段边界写口径』一致。
- **升级条件逐项核（本轮关键，全未命中）**：① heartbeat 正常无连败；② run 未翻 FAILED、八步无 FAILED 错误面；③ VLM 36.152.27.114 `/tmp/vllm_qwen38.log` 02:43:05–02:43:55 六行实测 **Running 3-4 reqs / Waiting 0-1 reqs 瞬态**（02:43:15、02:43:25 各 Waiting 1 后回落 0，非持续）、prefix cache hit ~95%、GPU KV 6.5-8.4%；④ proxy 容器 `/proc/net/tcp` 持 `1F42`(:8002) 端口 **3 条记录=ESTAB 通道在**；⑤ 进程同口径 ctxsw 61876→61901（12s +25，~125/min 编排低速）、RSS 18.2GB、proxy cpu=0.25%/mem=21.08GiB——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- **D4 第3步（flat 三提交绑定）→ 继续未达成，等 A**：`ingest_submission` 02:4x 实测 8 行不变（`9949d1a7`→`615A4A7B`/`e5649055`→`0BBF4C1C`/`99615748`→`051768B1`/`24d60fee`→`91FFEEC1` SCHEDULED + `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28)/`7a71e404`(空包) PENDING_INPUT source_id 全空，串行阻塞等 4acf689f 终态 D4③）；**14_42_48 正式全链维持 NOT_RUN**。
- **空包拒绝持续可追溯**：`scan_job` id4003（02:35:41）/4001（02:25:41）incoming 根均 **SUCCESS failed:2**（10min 周期持续同族）；无 409 新行。
- **scene run 全集（02:43 DB 实测）7 = 6 SCENE_DONE + 1 SCENE_RUNNING**，与 02:23 一致无新 run；8767 `active_runs=[4acf689f ACCEPTED pid:1]`。
- 本轮全部动作只读（ssh 处理机 mysql 容器 SELECT×5 表、/proc 双采样、docker stats/exec grep、VLM 日志 tail、8767 只读 API）；未提交/retry/调模型/写生产。scratch 探针 `tester_024x_prod.py`/`t024x3_check.py` 宿主机保留供复核。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **下一步**：按新口径继续等模型段完成信号（预计持续数小时，跨夜继续观察）；SCENE_DONE 后核跨 DB3 真实时间戳边界/产物/两次 reconcile（16_02_03 正式全链）；A flat 三提交绑定行出现后核 14_42_48 正式全链（0038 口径）；全批 8 包齐后交付 TEST_REPORT_PENDING（含「双写事件产物」一节）。

## 增量验收 02:5x（ruling 新口径续核 4acf689f：INFER 持续活跃、完成信号未到、升级条件逐项未命中，2026-10-14 02:53+08:00 只读实测）

- **唤醒源**：prerun 指纹 `2675746b…`（变更源=上轮 02:46:37 自写事件 `95cd853b…` + `sessions/TESTER.md` 回声，均已核读，**无新派单/新 decision**）；消费口径=ruling-4acf-infer-active-0218 第五节。
- **16_02_03 合法链 `scene-4acf689f` → SCENE_RUNNING attempt1（02:52:13 DB 实测）**：heartbeat_at=updated_at=02:52:13 30s 节奏持续刷新；八步 attempt1 仍全 QUEUED started_at=NULL（模型段完成信号未到）。
- **升级条件逐项核（本轮关键，全未命中）**：① heartbeat 正常无连败；② run 未翻 FAILED、八步无 FAILED 错误面；③ VLM 36.152.27.114 `/tmp/vllm_qwen38.log` 02:51:35–02:52:25 六行实测 **Running 3-4 reqs / Waiting 0 reqs**、prefix cache 95.1%、MM cache 83.3%、GPU KV 4.7-5.6%；④ proxy 容器 `/proc/net/tcp` 持 `1F42`(:8002) 目标 `2D02A8C0`(192.168.2.45) **1 条 ESTAB + 1 条 CLOSE_WAIT**（与 02:4x 同口径，通道在）；⑤ worker pid 3495931 `State S / VmRSS 18213940kB 不变`、`voluntary_ctxt_switches=62953` 较 02:4x 61901 持续递增（事件循环活动）；docker stats proxy cpu=0.53%/mem=21.29GiB——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- **D4 第3步（flat 三提交绑定）→ 继续未达成，等 A**：`ingest_submission` 02:5x 实测 8 行不变（`9949d1a7`→`615A4A7B`/`e5649055`→`0BBF4C1C`/`99615748`→`051768B1`/`24d60fee`→`91FFEEC1` SCHEDULED + `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28)/`7a71e404`(空包) PENDING_INPUT source_id 全空，串行阻塞等 4acf689f 终态 D4③）；**14_42_48 正式全链维持 NOT_RUN**。
- **空包拒绝持续可追溯**：`scan_job` id4005（02:45:41）/4003（02:35:41）incoming 根均 **SUCCESS failed:2**（10min 周期持续同族）；无 409 新行。
- **scene run 全集（02:52 DB 实测）7 = 6 SCENE_DONE + 1 SCENE_RUNNING**，与 02:43 一致无新 run；8767 `active_runs=[4acf689f ACCEPTED pid:1]`。
- 本轮全部动作只读（ssh 处理机 mysql 容器 SELECT×5 表、/proc 采样、docker stats/exec grep、VLM 日志、8767 只读 API）；未提交/retry/调模型/写生产。scratch 探针 `tester_024x_prod.py`/`t0252x2_check.py`/`t0252x3_ctx.py` 宿主机保留供复核。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **下一步**：按新口径继续等模型段完成信号（预计持续数小时，跨夜继续观察）；SCENE_DONE 后核跨 DB3 真实时间戳边界/产物/两次 reconcile（16_02_03 正式全链）；A flat 绑定行出现后核 14_42_48 正式全链（0038 口径）；全批 8 包齐后 TEST_REPORT_PENDING（含「双写事件产物」一节）。

## 增量验收 03:0x（按 ruling 新口径核 4acf689f：INFER 持续活跃、无完成信号、升级条件逐项未命中，2026-10-14 03:02+08:00 只读实测）

- **唤醒源**：prerun 指纹 `88b5055d…`（变更源=上轮 02:53:53 自写事件 `95cd853b…` + `sessions/TESTER.md` 回声，均已核读，**无新派单/新 decision**）；消费口径=ruling-4acf-infer-active-0218 第五节。
- **16_02_03 合法链 `scene-4acf689f` → SCENE_RUNNING attempt1，03:02:44 heartbeat 持续刷新（30s 节奏）；八步仍全 QUEUED started_at=NULL**（23:05:32 入队至 03:02 约 237min）=模型段完成信号未到，与裁决『阶段边界写口径』一致。
- **升级条件逐项核（本轮关键，全未命中）**：① heartbeat 正常无连败；② run 未翻 FAILED、八步无 FAILED 错误面；③ VLM `/tmp/vllm_qwen38.log` 03:02:35–03:03:25 六行实测 **Running 1-4 reqs / Waiting 恒 0**、prefix cache hit 95.0%、MM 83.8%、GPU KV 1.7-7.0%、POST 200 连发；④ proxy 容器 `/proc/net/tcp` 持 `1F42`(:8002) 端口 **3 条记录=ESTAB 通道在**；⑤ 进程 VmRSS 18213940kB/State S 同口径、proxy cpu=1.25%/mem=21.29GiB——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- **D4 第3步（flat 三提交绑定）→ 继续未达成，等 A**：`ingest_submission` 03:0x 实测 8 行不变（`9949d1a7`→`615A4A7B`/`e5649055`→`0BBF4C1C`/`99615748`→`051768B1`/`24d60fee`→`91FFEEC1` SCHEDULED + `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28)/`7a71e404`(空包) PENDING_INPUT source_id 全空，串行阻塞等 4acf689f 终态 D4③）；**14_42_48 正式全链维持 NOT_RUN**。
- **空包拒绝持续可追溯**：`scan_job` id4007（02:55:42）/4005（02:45:41）incoming 根均 **SUCCESS failed:2**（10min 周期持续同族）；无 409 新行。
- **scene run 全集（03:02 DB 实测）7 = 6 SCENE_DONE + 1 SCENE_RUNNING**，与 02:53 一致无新 run；8767 `active_runs=[4acf689f ACCEPTED pid:1]`。
- 本轮全部动作只读（ssh 处理机 mysql 容器 SELECT×5 表、/proc 采样、docker stats/exec grep、VLM 日志、8767 只读 API）；未提交/retry/调模型/写生产。探针 `tester_030x_check.py`/复用 `tester_024x_prod.py` 宿主机保留供复核。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **下一步**：按新口径继续等模型段完成信号（预计持续数小时，跨夜继续观察）；SCENE_DONE 后核跨 DB3 真实时间戳边界/产物/两次 reconcile（16_02_03 正式全链）；A flat 三提交绑定行出现后核 14_42_48 正式全链（0038 口径）；全批 8 包齐后交付 TEST_REPORT_PENDING（含「双写事件产物」一节）。

## 增量验收 03:1x（按 ruling 新口径核 4acf689f：INFER 持续活跃、无完成信号、升级条件逐项未命中，2026-10-14 03:14+08:00 只读实测）

- **唤醒源**：prerun 指纹 `836dea26…`（变更源=上轮 03:05 自写事件 `e6101308…` + `sessions/TESTER.md` 回声，均已核读，**无新派单/新 decision**）；消费口径=ruling-4acf-infer-active-0218 第五节。
- **16_02_03 合法链 `scene-4acf689f` → SCENE_RUNNING attempt1，03:14:14 heartbeat 持续刷新（30s 节奏）；八步仍全 QUEUED started_at=NULL**（23:05:32 入队至 03:14 约 248min）=模型段完成信号未到，与裁决『阶段边界写口径』一致。
- **升级条件逐项核（本轮关键，全未命中）**：① heartbeat 正常无连败；② run 未翻 FAILED、八步无 FAILED 错误面；③ VLM `/tmp/vllm_qwen38.log` 03:12:35–03:13:25 六行实测 **Running 2-3 reqs / Waiting 0-1 瞬态后回落 0**、prefix cache 94.5-94.6%、MM 84.5%、GPU KV 3.3-5.0%、POST 200 连发；④ proxy 容器 `/proc/net/tcp` 持 `1F42`(:8002) 端口 **3 条记录=ESTAB 通道在**；⑤ 进程 3495931（本轮核实=容器内 `scene_host_proxy.py` 宿主映射）`/status` **voluntary_ctxt_switches 66119→66143（12s +24，~120/min 持续递增）**、nonvoluntary 235 不变、VmRSS 18213940kB/State S、docker stats proxy cpu=0.86%/mem=21.29GiB——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- **探针修正注记**：本轮初测 `/proc/3495931/stat` 仅 52 字段（`s[72]` 越界），volcsw 正确读法=`/proc/3495931/status` 具名 `voluntary_ctxt_switches` 字段（与历史 02:5x 62953 同口径，本轮 66119 持续递增）——**历史 ctxsw 数据有效，非误读**。
- **D4 第3步（flat 三提交绑定）→ 继续未达成，等 A**：`ingest_submission` 03:1x 实测 8 行不变（`9949d1a7`→`615A4A7B`/`e5649055`→`0BBF4C1C`/`99615748`→`051768B1`/`24d60fee`→`91FFEEC1` SCHEDULED + `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28)/`7a71e404`(空包16_33_10) PENDING_INPUT source_id 全空，串行阻塞等 4acf689f 终态 D4③）；**14_42_48 正式全链维持 NOT_RUN**。
- **空包拒绝持续可追溯**：`scan_job` id4009（03:05:42）/4007（02:55:42）incoming 根均 **SUCCESS {dirs:3 bags:1 created:0 updated:0 failed:2}**（10min 周期持续同族）；4008/4006 self_built raw_rosbags SUCCESS failed:0；无 409 新行。
- **scene run 全集（03:14 DB 实测）7 = 6 SCENE_DONE + 1 SCENE_RUNNING**，与 03:02 一致无新 run；8767 `active_runs=[scene-4acf689f… pid:1 stage ACCEPTED]`。
- 本轮全部动作只读（ssh 处理机 mysql 容器 SELECT×5 表、/proc/status 双采样、docker stats/top/exec grep、VLM 日志、8767 只读 API）；未提交/retry/调模型/写生产。探针 `tester_031x_check.py`/`_data.py`/`_ctx.py`/`_f73.py`/`_id.py` 宿主机保留供复核。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **下一步**：按新口径继续等模型段完成信号（预计持续数小时，跨夜继续观察）；SCENE_DONE 后核跨 DB3 真实时间戳边界/产物/两次 reconcile（16_02_03 正式全链）；A flat 绑定行出现后核 14_42_48 正式全链（0038 口径）；全批 8 包齐后交付 TEST_REPORT_PENDING（含「双写事件产物」一节）。

## 增量验收 03:3x（按 ruling 新口径核 4acf689f：INFER 持续活跃、无完成信号、升级条件逐项未命中，2026-10-14 03:37+08:00 只读实测）

- **唤醒源**：prerun 指纹 `b4c6c926…`（变更源=上轮 03:24 自写事件 `8d059c8d…` + `sessions/TESTER.md` 回声，均已核读；协调者 03:28 事件 `coord-...0325` 同口径确认全部变更源为自产回声，**无新派单/新 decision**）。
- **16_02_03 合法链 `scene-4acf689f` → SCENE_RUNNING attempt1，03:37:16 heartbeat 持续刷新；八步仍全 QUEUED started_at=NULL**（23:05:32 入队至 03:37 约 272min）=模型段完成信号未到，与裁决『阶段边界写口径』一致。
- **升级条件逐项核（本轮关键，全未命中）**：① heartbeat 正常无连败；② run 未翻 FAILED、八步无 FAILED 错误面；③ VLM `/tmp/vllm_qwen38.log` 03:36:55–03:37:25 四行实测 **Running 3-4 reqs / Waiting 恒 0**、prefix cache 93.6-93.8%、MM 85.7%、GPU KV 0.7-4.0%、POST 200 连发；④ proxy 容器 `/proc/net/tcp` 持 `1F42`(:8002) 端口 **4 条记录=ESTAB 通道在**（上轮 3 条，计数含 CLOSE_WAIT 微差，同口径）；⑤ 进程 3495931 `/status` **voluntary_ctxt_switches 68244→68268（12s +24，~120/min 持续递增）**、nonvoluntary 240 不变、VmRSS 18213940kB/State S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- **D4 第3步（flat 三提交绑定）→ 继续未达成，等 A**：`ingest_submission` 03:3x 实测 8 行不变（`9949d1a7`→`615A4A7B`/`e5649055`→`0BBF4C1C`/`99615748`→`051768B1`/`24d60fee`→`91FFEEC1` SCHEDULED + `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28)/`7a71e404`(空包16_33_10) PENDING_INPUT source_id 全空，串行阻塞等 4acf689f 终态 D4③）；**14_42_48 正式全链维持 NOT_RUN**。
- **空包拒绝持续可追溯**：`scan_job` id4015（03:35:43）/4013（03:25:42）incoming 根均 **SUCCESS {dirs:3 bags:1 created:0 updated:0 failed:2}**（10min 周期持续同族）；4014/4012 self_built raw_rosbags SUCCESS failed:0；无 409 新行。
- **scene run 全集（03:37 DB 实测）7 = 6 SCENE_DONE + 1 SCENE_RUNNING**，与 03:14 一致无新 run；8767 `active_runs=[scene-4acf689f… pid:1 stage ACCEPTED]`。
- 本轮全部动作只读（ssh 处理机 mysql 容器 SELECT×5 表、/proc/status 双采样、docker exec grep、VLM 日志、8767 只读 API）；未提交/retry/调模型/写生产。探针 `tester_0329_check.py`（scratch）宿主机保留供复核。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **下一步**：按新口径继续等模型段完成信号（预计持续数小时，跨夜继续观察）；SCENE_DONE 后核跨 DB3 真实时间戳边界/产物/两次 reconcile（16_02_03 正式全链）；A flat 绑定行出现后核 14_42_48 正式全链（0038 口径）；全批 8 包齐后交付 TEST_REPORT_PENDING（含「双写事件产物」一节）。

## 增量验收 03:4x（按 ruling 新口径核 4acf689f：INFER 持续活跃、无完成信号、升级条件逐项未命中，2026-10-14 03:46+08:00 只读实测）

- **唤醒源**：prerun 指纹 `946291a0…`（变更源=上轮 03:40 自写事件 `90503441…` + `sessions/TESTER.md` 回声，均已核读；用户恢复入口指令已按既有 attempt-1 派单+ruling-4acf 口径接续，**无新派单/新 decision**）。
- **16_02_03 合法链 `scene-4acf689f` → SCENE_RUNNING attempt1，03:45:16 heartbeat 持续刷新；八步仍全 QUEUED started_at=NULL**（23:05:32 入队至 03:45 约 281min）=模型段完成信号未到，与裁决『阶段边界写口径』一致。
- **升级条件逐项核（本轮关键，全未命中）**：① heartbeat 正常无连败；② run 未翻 FAILED、八步无 FAILED 错误面；③ VLM `/tmp/vllm_qwen38.log` 03:45:35–03:45:55 实测 **Running 2-3 reqs / Waiting 0-1 瞬态**、prefix cache 93.7%、MM 86.0%、GPU KV 3.2-3.8%、POST 200 连发；④ proxy 容器 `/proc/net/tcp` 持 `1F42`(:8002) **4 条记录=ESTAB 通道在**（与上轮同口径）；⑤ 进程 3495931 `voluntary_ctxt_switches 69270→69295（12s +25，~125/min 持续递增）`、nonvoluntary 244 不变、VmRSS 18213940kB/State S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- **D4 第3步（flat 三提交绑定）→ 继续未达成，等 A**：`ingest_submission` 03:4x 实测 8 行不变（`9949d1a7`→`615A4A7B`/`e5649055`→`0BBF4C1C`/`99615748`→`051768B1`/`24d60fee`→`91FFEEC1` SCHEDULED + `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28)/`7a71e404`(空包16_33_10) PENDING_INPUT source_id 全空，串行阻塞等 4acf689f 终态 D4③）；**14_42_48 正式全链维持 NOT_RUN**。
- **空包拒绝持续可追溯**：`scan_job` id4017（03:45:43）/4015（03:35:43）incoming 根均 **SUCCESS {dirs:3 bags:1 failed:2}**（10min 周期持续同族）；4016/4014 self_built raw_rosbags SUCCESS failed:0；无 409 新行。
- **scene run 全集（03:45 DB 实测）7 = 6 SCENE_DONE + 1 SCENE_RUNNING**，与 03:37 一致无新 run；8767 `health=ok active_runs=[scene-4acf689f… stage ACCEPTED pid:1]`。
- 本轮全部动作只读（ssh 处理机 mysql 容器 SELECT×5 表、/proc/status 双采样、docker exec grep、VLM 日志、8767 只读 API）；未提交/retry/调模型/写生产。探针 `tester_034x_check.py`（scratch，复用 0329 模板）宿主机保留供复核。
- **PASS 基线不变**：15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，均维持原证据不重复验收。
- **下一步**：按新口径继续等模型段完成信号（预计持续数小时，跨夜继续观察）；SCENE_DONE 后核跨 DB3 真实时间戳边界/产物/两次 reconcile（16_02_03 正式全链）；A flat 三提交绑定行出现后核 14_42_48 正式全链（0038 口径）；全批 8 包齐后交付 TEST_REPORT_PENDING（含「双写事件产物」一节）。

### 03:5x 静默期增量只读巡检（03:51 实测）

- 命令：`python3 ~/.hermes/cache/scratch/tester_035x_check.py`（ssh processing-machine 只读：mysql 容器 SELECT×5 表、/proc/status 双采样 12s、8767 health、VLM 日志 tail），exit 0。
- 断言/结果：
  - `pipeline_run` scene-4acf689f SCENE_RUNNING attempt1 heartbeat 03:51:47（30s 节奏）✅ 在算
  - `step_run` 八步全 QUEUED started_at=NULL（23:05:32 入队至 03:51 ~287min）✅ 与上轮一致
  - `ingest_submission` 8 行不变，flat 三提交 PENDING_INPUT source_id=NULL ✅ 等 A D4③
  - `scan_job` 4017/4015/4013 incoming SUCCESS {dirs:3 bags:1 failed:2} ✅ 空包 16_33_10 拒绝持续
  - 8767 health ok active_runs=[4acf689f ACCEPTED] ✅
  - proxy 3495931 volcsw 70008→70032（12s +24）、RSS 18213940kB、State S ✅ 进程推进中
  - VLM 03:51:36–56 Running 4/Waiting 0-2、prefix 93.4-93.5%、KV 4.5-6.1%、POST /v1/chat/completions 200 连发 ✅ 远端推理活跃
- 结论：无升级条件命中，维持只读等待；14_42_48 正式全链 NOT_RUN；PASS 基线不变。

### 03:57 静默期增量只读巡检（03:55 实测）

- 命令：`python3 ~/.hermes/cache/scratch/tester_0357_check.py`（ssh processing-machine 只读：mysql 容器 SELECT×5 表、/proc/status 双采样 12s、8767 health、VLM 日志 tail），exit 0。
- 断言/结果：
  - `pipeline_run` scene-4acf689f SCENE_RUNNING attempt1 heartbeat 03:55:17（30s 节奏）✅ 在算
  - `step_run` 八步全 QUEUED started_at=NULL（23:05:32 入队至 03:55 ~292min）✅ 与上轮一致
  - `ingest_submission` 8 行不变，flat 三提交（a65a25a7/87dfebaa/518089ed）PENDING_INPUT source_id=NULL ✅ 等 A D4③
  - `scan_job` 4017/4015/4013 incoming SUCCESS {dirs:3 bags:1 failed:2} ✅ 空包 16_33_10 拒绝持续
  - 8767 health ok active_runs=[4acf689f ACCEPTED] ✅
  - proxy 3495931 volcsw 70475→70501（12s +26）、nvolcsw 249、RSS 18213940kB、State S ✅ 进程推进中
  - VLM 03:55:36–46 Running 1-3/Waiting 0、prefix 93.4-93.5%、KV 2.7-4.7%、MM 86.3%、POST /v1/chat/completions 200 连发 ✅ 远端推理活跃
- 副本核对：`inbox/sessions/TESTER.md` 落后 canonical（缺 03:5x 段，03:47 vs 03:53），本轮随写同步一致。
- 结论：无升级条件命中，维持只读等待；14_42_48 正式全链 NOT_RUN；PASS 基线不变。

### 04:0x 静默期增量只读巡检（04:01 实测）

- 命令：`python3 ~/.hermes/cache/scratch/tester_040x_check.py`（ssh processing-machine 只读：mysql 容器 SELECT×5 表、/proc/status 双采样 12s、8767 health、VLM 日志 tail），exit 0。
- 断言/结果：
  - `pipeline_run` scene-4acf689f SCENE_RUNNING attempt1 heartbeat 04:01:17（30s 节奏，入队 23:05:32 起 ~297min）✅ 在算
  - `step_run` 八步全 QUEUED started_at=NULL ✅ 与上轮一致，完成信号未到
  - `ingest_submission` 8 行不变，flat 三提交（a65a25a7/87dfebaa/518089ed）PENDING_INPUT source_id=NULL ✅ 等 A D4③
  - `scan_job` 4019（03:55:43）/4017/4015 incoming SUCCESS {dirs:3 bags:1 failed:2} ✅ 空包 16_33_10 拒绝 10min 周期持续
  - 8767 health ok active_runs=[4acf689f ACCEPTED] ✅
  - proxy 3495931 volcsw 71217→71241（12s +24）、nvolcsw 251、RSS 18213940kB、State S ✅ 进程推进中
  - VLM 04:01:36–56 Running 4/Waiting 1 瞬态后回落 0、prefix 92.9%、KV 4.0-5.4%、MM 86.3%、POST 200 连发 ✅ 远端推理活跃
- 结论：无升级条件命中（Waiting 为 10s 级瞬态且 POST 200 连发、ctxsw 持续递增），维持只读等待；14_42_48 正式全链 NOT_RUN；PASS 基线不变。

### 04:07 静默期增量只读巡检（04:07 实测）

- 命令：`python3 ~/.hermes/cache/scratch/tester_040x_check.py`（复用上轮探针，ssh processing-machine 只读：mysql 容器 SELECT×5 表、/proc/status 双采样 12s、8767 health、VLM 日志 tail），exit 0。
- 断言/结果：
  - `pipeline_run` scene-4acf689f SCENE_RUNNING attempt1 heartbeat 04:06:48（30s 节奏，23:05:32 入队起 ~301min）✅ 在算
  - `step_run` 八步全 QUEUED started_at=NULL ✅ 与上轮一致，模型段完成信号未到
  - `ingest_submission` 8 行不变，flat 三提交（a65a25a7/87dfebaa/518089ed）PENDING_INPUT source_id=NULL ✅ 等 A D4③
  - `scan_job` 4021（04:05:44）/4019/4017 incoming SUCCESS {dirs:3 bags:1 failed:2} ✅ 空包 16_33_10 拒绝 10min 周期持续；self_built 4020 零变化
  - 8767 health ok active_runs=[4acf689f ACCEPTED] ✅
  - proxy 3495931 volcsw 71849→71873（12s +24）、nvolcsw 253→254、RSS 18213940kB、State S ✅ 进程推进中（与 04:01/03:5x 同口径）
  - VLM 04:06:56–04:07:06 Running 3-4/Waiting 0、prefix 93.1-93.2%、MM 86.3%、KV 3.5-5.1%、POST /v1/chat/completions 200 连发 ✅ 远端推理活跃
- 升级条件逐项核全未命中（heartbeat 正常/run 未 FAILED/VLM Waiting 恒 0/POST 200 连发）→ **维持不 kill/cancel/retry**。
- scene run 全集 7 不变（6 SCENE_DONE + 4acf689f RUNNING），无新 run；PASS 基线不变；14_42_48 正式全链 NOT_RUN。

### 04:1x 静默期增量只读巡检（04:15 实测）

- 命令：`python3 ~/.hermes/cache/scratch/tester_040x_check.py`（ssh processing-machine 只读：mysql 容器 SELECT×5 表、/proc/status 双采样 12s、8767 health、VLM 日志 tail），exit 0。
- 断言/结果：
  - `pipeline_run` scene-4acf689f SCENE_RUNNING attempt1 heartbeat 04:15:18（30s 节奏，入队 23:05:32 起 ~310min）✅ 在算
  - `step_run` 八步全 QUEUED started_at=NULL ✅ 与上轮一致，完成信号未到
  - `ingest_submission` 8 行不变，flat 三提交（a65a25a7/87dfebaa/518089ed）PENDING_INPUT source_id=NULL ✅ 等 A D4③
  - `scan_job` 4021（04:05:44）incoming SUCCESS {dirs:3 bags:1 failed:2} ✅ 空包 16_33_10 拒绝 10min 周期持续
  - 8767 health ok active_runs=[4acf689f ACCEPTED] ✅
  - proxy 3495931 volcsw 72874→72898（12s +24）、nvolcsw 257、RSS 18213940kB、State S ✅ 进程推进中
  - VLM 04:15:16–36 Running 3-1/Waiting 恒 0、prefix 93.2-93.3%、KV 2.1-4.1%、MM 86.8%、POST 200 连发 ✅ 远端推理活跃
- 结论：无升级条件命中（heartbeat 正常/Waiting 恒 0/ctxsw 持续递增），维持只读等待；14_42_48 正式全链 NOT_RUN；PASS 基线不变。

### 04:2x 静默期增量只读巡检（04:21 实测）

- 命令：`python3 ~/.hermes/cache/scratch/tester_0420_check.py`（ssh processing-machine 只读：mysql 容器 SELECT×5 表、/proc/status 双采样 12s、8767 health、VLM 日志 tail），exit 0。
- 断言/结果：
  - `pipeline_run` scene-4acf689f SCENE_RUNNING attempt1 heartbeat 04:21:19（30s 节奏，入队 ~316min）✅ 在算
  - `step_run` 八步全 QUEUED started_at=NULL ✅ 与上轮一致，完成信号未到
  - `ingest_submission` 8 行不变，flat 三提交（a65a25a7/87dfebaa/518089ed）PENDING_INPUT source_id=NULL ✅ 等 A D4③
  - `scan_job` 4023（04:15:44）incoming SUCCESS {dirs:3 bags:1 failed:2} ✅ 空包 16_33_10 拒绝 10min 周期持续
  - 8767 health ok active_runs=[4acf689f ACCEPTED] ✅
  - proxy 3495931 volcsw 73620→73644（12s +24）、nvolcsw 258、RSS 18213940kB、State S ✅ 进程推进中
  - VLM 04:21:06–46 Running 3-2/Waiting 恒 0、prefix 92.8%、KV 2.3-3.6%、MM 87.0%、POST 200 连发 ✅ 远端推理活跃
- 结论：无升级条件命中（heartbeat 正常/Waiting 恒 0/ctxsw 持续递增），维持只读等待；14_42_48 正式全链 NOT_RUN；PASS 基线不变。

### 04:29 静默期增量只读巡检（04:26 实测）

- 命令：`python3 ~/.hermes/cache/scratch/tester_0420_check.py`（ssh processing-machine 只读：mysql 容器 SELECT×5 表、/proc/status 双采样 12s、8767 health、VLM 日志 tail），exit 0。
- 断言/结果：
  - `pipeline_run` scene-4acf689f SCENE_RUNNING attempt1 heartbeat 04:26:19（30s 节奏，入队 ~322min）✅ 在算
  - `step_run` 八步全 QUEUED started_at=NULL ✅ 与上轮一致，完成信号未到
  - `ingest_submission` 8 行不变，flat 三提交（a65a25a7/87dfebaa/518089ed）PENDING_INPUT source_id=NULL ✅ 等 A D4③
  - `scan_job` 4025（04:25:45）新周期 incoming SUCCESS {dirs:3 bags:1 failed:2} ✅ 空包 16_33_10 拒绝 10min 周期持续
  - 8767 health ok active_runs=[4acf689f ACCEPTED] ✅
  - proxy 3495931 volcsw 74172→74196（12s +24）、nvolcsw 259、RSS 18213940kB、State S ✅ 进程推进中
  - VLM 04:25:46–04:26:16 Running 2-4/Waiting 恒 0、prefix 93.1-93.2%、KV 3.3-5.8%、MM 87.0%、POST 200 连发 ✅ 远端推理活跃
- 结论：无升级条件命中（heartbeat 正常/Waiting 恒 0/ctxsw 持续递增），维持只读等待；14_42_48 正式全链 NOT_RUN；PASS 基线不变。

### 04:3x 静默期增量只读巡检（04:30 实测）

- 命令：`python3 ~/.hermes/cache/scratch/tester_0420_check.py`（ssh processing-machine 只读：mysql 容器 SELECT×5 表、/proc/status 双采样 12s、8767 health、VLM 日志 tail），exit 0。
- 断言/结果：
  - `pipeline_run` scene-4acf689f SCENE_RUNNING attempt1 heartbeat 04:30:49（30s 节奏，入队 ~326min）✅ 在算
  - `step_run` 八步全 QUEUED started_at=NULL ✅ 与上轮一致，完成信号未到
  - `ingest_submission` 8 行不变，flat 三提交（a65a25a7/87dfebaa/518089ed）PENDING_INPUT source_id=NULL ✅ 等 A D4③
  - `scan_job` 4025 后无新周期（4025 为最新，10min 周期未到点），incoming SUCCESS failed:2 空包拒绝可追溯 ✅
  - 8767 health ok active_runs=[4acf689f ACCEPTED] ✅
  - proxy 3495931 volcsw 74759→74790（12s +31）、nvolcsw 259、RSS 18213940kB、State S ✅ 进程推进中（docker top 本容器无输出，按 /proc 具名口径）
  - VLM 04:30:46–04:31:06 Running 2-3/Waiting 恒 0、prefix 93.0%、KV 2.5-5.2%、MM 87.1%、POST 200 连发 ✅ 远端推理活跃
- 结论：无升级条件命中（heartbeat 正常/Waiting 恒 0/ctxsw 持续递增），维持只读等待；14_42_48 正式全链 NOT_RUN；PASS 基线不变。

### 04:4x 静默期增量只读巡检（04:36-04:37 实测）

- 命令：`python3 ~/.hermes/cache/scratch/tester_043x_check.py`（ssh processing-machine 只读：mysql 容器 SELECT×5 表、8767 health、VLM 日志 tail），exit 0；探针本轮 ctxsw 段字符串拼接 bug 误报，改用 ssh 直接 `/proc/3495931/status` 双采样（12s）补证。
- 断言/结果：
  - `pipeline_run` scene-4acf689f SCENE_RUNNING attempt1 heartbeat 04:36:50（30s 节奏，入队 ~332min）✅ 在算
  - `step_run` 八步全 QUEUED started_at=NULL ✅ 与上轮一致，完成信号未到
  - `ingest_submission` 8 行不变，flat 三提交（a65a25a7/87dfebaa/518089ed）PENDING_INPUT source_id=NULL ✅ 等 A D4③
  - `scan_job` 4027（04:35:45）incoming SUCCESS {dirs:3 bags:1 failed:2} 新周期到点 ✅ 空包拒绝可追溯
  - 8767 health ok active_runs=[4acf689f ACCEPTED] ✅
  - proxy 3495931 volcsw 75517→75541（12s +24）、nvolcsw 259、RSS 18213940kB、State S ✅ 较 04:30 的 74759 持续递增，进程推进中
  - VLM 04:36:26–04:36:56 Running 2-3/Waiting 恒 0、prefix 93.4%、KV 3.8-5.7%、MM 87.1%、POST 200 连发 ✅ 远端推理活跃
- 结论：无升级条件命中（heartbeat 正常/Waiting 恒 0/ctxsw 持续递增），维持不 kill/cancel/retry 只读等待；14_42_48 正式全链 NOT_RUN；PASS 基线不变。

### 04:5x 静默期增量只读巡检（04:47 实测）

- 命令：`python3 ~/.hermes/cache/scratch/tester_043x_check.py`（ssh processing-machine 只读：mysql 容器 SELECT×5 表、8767 health、VLM 日志 tail）+ ssh 直接 `/proc/3495931/status` 双采样（12s）补证；探针 ctxsw 段沿用 04:4x 已知字符串拼接 bug，以 /proc 直接采样为准。
- 断言/结果：
  - `pipeline_run` scene-4acf689f SCENE_RUNNING attempt1 heartbeat 04:46:50（30s 节奏，入队 ~342min）✅ 在算
  - `step_run` 八步全 QUEUED started_at=NULL ✅ 与上轮一致，模型段完成信号未到
  - `ingest_submission` 8 行不变，flat 三提交（a65a25a7/87dfebaa/518089ed）PENDING_INPUT source_id=NULL ✅ 等 A D4③，14_42_48 正式全链 NOT_RUN
  - `scan_job` 4029（04:45:45）incoming SUCCESS {dirs:3 bags:1 failed:2} 新周期到点 ✅ 空包拒绝持续可追溯
  - 8767 health ok active_runs=[4acf689f ACCEPTED] ✅
  - proxy 3495931 volcsw 76734→76758（12s +24）、nvolcsw 264、RSS 18213940kB、State S ✅ 较 04:36 的 75541 持续递增，进程推进中
  - VLM 04:46:46–04:46:56 Running 2-3、Waiting 1 瞬态（10s 级回落）、prefix 91.9-92.0%、KV 4.5-6.2%、MM 87.1%、POST 200 连发 ✅ 远端推理活跃
- 结论：无升级条件命中（heartbeat 正常/Waiting 瞬态/ctxsw 持续递增），维持不 kill/cancel/retry 只读等待；PASS 基线不变。

### 05:5x 静默期增量只读巡检（04:57 实测）

- 命令：`python3 ~/.hermes/cache/scratch/tester_055x_check.py`（ssh processing-machine 只读：mysql 容器 SELECT×5 表、8767 health、VLM 日志 tail）+ 远端 `/proc/3495931/status` 双采样（12s，本轮修复 04:3x 探针字符串拼接 bug，直接 /proc 采样）；ctxsw 数值以本轮直采为准。
- 断言/结果：
  - `pipeline_run` scene-4acf689f SCENE_RUNNING attempt1 heartbeat 04:56:51（30s 节奏，23:05:32 入队至 04:57 约 352min）✅ 在算
  - `step_run` 八步全 QUEUED started_at=NULL ✅ 与 04:47 一致，模型段完成信号未到
  - `ingest_submission` 8 行不变，flat 三提交（a65a25a7/87dfebaa/518089ed）PENDING_INPUT source_id=NULL ✅ 等 A D4③，14_42_48 正式全链 NOT_RUN
  - `scan_job` 4031（04:55:45）incoming SUCCESS {dirs:3 bags:1 failed:2} 新周期到点 ✅ 空包拒绝持续可追溯；self_built 4030 8 目录 failed:0
  - 8767 health ok active_runs=[4acf689f ACCEPTED] ✅
  - proxy 3495931 volcsw 77961→77985（12s +24）、nvolcsw 265→266、RSS 18213940kB、State S ✅ 较 04:47 的 76758 持续递增，进程推进中
  - VLM 04:57:06–04:57:26 Running 4、Waiting 1→0 瞬态、prefix 91.9%、KV 4.1-5.3%、MM 87.1%、prompt 吞吐 845-1602 tok/s、POST 200 连发 ✅ 远端推理活跃
- 结论：无升级条件命中（heartbeat 正常/Waiting 瞬态回落/ctxsw 持续递增/吞吐健康），维持不 kill/cancel/retry 只读等待；PASS 基线不变。

### 05:0x 静默期增量只读巡检（05:07 实测，无实质变化）

- 命令：`python3 ~/.hermes/cache/scratch/tester_055x_check.py`（ssh processing-machine 只读：mysql 容器 SELECT×5 表、8767 health、/proc 双采样、VLM 日志 tail），exit 0。
- 断言/结果：
  - `pipeline_run` scene-4acf689f SCENE_RUNNING attempt1 heartbeat 05:06:52（30s 节奏，23:05:32 入队至 05:07 约 362min）✅ 无 FAILED
  - `step_run` 八步全 QUEUED started_at=NULL ✅ 与上轮一致，完成信号未到
  - **升级条件逐项未命中**：VLM 05:06:56-05:07:16 Running 3-4 reqs/Waiting 0、prefix 91.9%、KV 4.8-5.7%、prompt 298-1030 tok/s、POST 200 连发；proxy 3495931 volcsw 79150→79174（12s +24 持续递增）、nvolcsw 268 不变、RSS 18213940kB S——**INFER 远端推理持续活跃，按裁决口径不 kill/cancel/retry**
  - `ingest_submission` 8 行 05:07 实测不变，flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id 空等 A D4③；**14_42_48 正式全链维持 NOT_RUN**
  - `scan_job` 4033（05:05:46）/4031（04:55:45）incoming SUCCESS failed:2=空包 16_33_10 拒绝 10min 周期持续可追溯；无 409 新行
  - scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]
  - 本轮全部动作只读；未提交/retry/调模型/写生产
- PASS 基线不变（15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，24ab78bb dup NOT_APPLICABLE 无伪切片）。

### 05:09 静默期增量只读巡检（05:11 实测，无实质变化）

- 命令：`python3 ~/.hermes/cache/scratch/tester_0509_check.py`（ssh processing-machine 只读：mysql 容器 SELECT×5 表、8767 health、/proc 双采样、VLM 日志 tail），exit 0。
- 断言/结果：
  - `pipeline_run` scene-4acf689f SCENE_RUNNING attempt1 heartbeat 05:11:22（30s 节奏，23:05:32 入队至 05:11 约 370min）✅ 无 FAILED
  - `step_run` 八步全 QUEUED started_at=NULL ✅ 与上轮一致，完成信号未到
  - **升级条件逐项未命中**：VLM 05:11:26-05:11:56 Running 3-4/Waiting 0、prefix 91.7%、KV 1.9-6.1%、MM 87.3%、prompt 258-1434 tok/s、POST 200 连发；proxy 3495931 volcsw 79700→79724（12s +24 持续递增）、nvolcsw 270 不变、RSS 18213948kB S——**INFER 远端推理持续活跃，按裁决口径不 kill/cancel/retry**
  - `ingest_submission` 8 行 05:11 实测不变，flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id 空等 A D4③；**14_42_48 正式全链维持 NOT_RUN**
  - `scan_job` 4033（05:05:46）仍为最新（10min 周期未到点）SUCCESS failed:2 空包拒绝可追溯
  - scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]
  - 本轮全部动作只读；未提交/retry/调模型/写生产
- PASS 基线不变（15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，24ab78bb dup NOT_APPLICABLE 无伪切片）。

### 05:2x 静默期增量只读巡检（05:21 实测，无实质变化）

- `scene-4acf689f`（16_02_03 合法链）05:21:22 SCENE_RUNNING attempt1、heartbeat 05:21:22 30s 节奏刷新、八步仍全 QUEUED started_at=NULL（入队 ~380min）=模型段完成信号未到；**升级条件逐项未命中**——run 未 FAILED/VLM 05:20:56-05:21:26 Running 2-3、Waiting 0、prefix 91.4%、KV 2.4-5.1%、MM 87.6%、prompt 0-384 tok/s、POST 200 连发、proxy 3495931 volcsw 80861→80885（12s +24 持续递增）nvolcsw 272 微增 RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- `ingest_submission` 8 行不变（2026-10-13 21:23–23:24 各 updated_at），flat 三提交 `a65a25a7`/`87dfebaa`/`518089ed` 仍 PENDING_INPUT source_id 空等 A D4③，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4035（05:15:46）新周期 incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝持续可追溯；scene run 7=6DONE+1RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED]。
- 本轮全部动作只读（ssh 处理机 mysql 容器 SELECT×5 表、/proc/status 双采样、8767 health、VLM 日志），未提交/retry/调模型/写生产；探针 `tester_0520_check.py`/`tester_0520_out.txt`（scratch）保留供复核。
- PASS 基线不变（15_58_23 复用/16_00_13 SUCCESS/16_31_25 NOT_APPLICABLE/16_33_10 拒绝可追溯/16_37_47+16_58_28 flat SHA/16_02_03 SHA=源）。
### 05:2x 静默期增量只读巡检（05:26 实测，无实质变化）

- 命令：`python3 ~/.hermes/cache/scratch/tester_0530_check.py`（ssh processing-machine 只读：mysql 容器 SELECT×5 表、8767 health、/proc 双采样、VLM 日志 tail），exit 0。
- 断言/结果：
  - `pipeline_run` scene-4acf689f SCENE_RUNNING attempt1 heartbeat 05:26:23（30s 节奏，23:05:32 入队至 05:26 约 381min）✅ 无 FAILED
  - `step_run` 八步全 QUEUED started_at=NULL ✅ 与上轮一致，模型段完成信号未到
  - **升级条件逐项未命中**：VLM 05:26:17-05:26:47 Running 1-4、Waiting 0、prefix 91.4-91.5%、KV 0.8-5.5%、MM 87.7-87.8%、prompt 213-1293 tok/s、POST 200 连发；proxy 3495931 volcsw 81493→81517（12s +24 持续递增）、nvolcsw 274、RSS 18213948kB S——**INFER 远端推理持续活跃，按裁决口径不 kill/cancel/retry**
  - `ingest_submission` 8 行不变，flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id 空等 A D4③；**14_42_48 正式全链维持 NOT_RUN**
  - `scan_job` 4037（05:25:47）新周期 incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝 10min 周期持续可追溯；无 409 新行
  - scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]
  - 本轮全部动作只读；未提交/retry/调模型/写生产
- PASS 基线不变（15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，24ab78bb dup NOT_APPLICABLE 无伪切片）。

### 05:3x 静默期增量只读巡检（05:36 实测，无实质变化）

- 命令：`python3 ~/.hermes/cache/scratch/tester_0535_check.py`（ssh processing-machine 只读：mysql 容器 SELECT×5 表、8767 health、/proc 双采样、VLM 日志 tail），exit 0。
- 断言/结果：
  - `pipeline_run` scene-4acf689f SCENE_RUNNING attempt1 heartbeat 05:35:53（30s 节奏，23:05:32 入队至 05:36 约 390min）✅ 无 FAILED
  - `step_run` 八步全 QUEUED started_at=NULL ✅ 与上轮一致，模型段完成信号未到
  - **升级条件逐项未命中**：VLM 05:36:07-05:36:37 Running 2-4、Waiting 0、prefix 91.4%、KV 3.0-5.2%、MM 88.2-88.3%、prompt 66-1847 tok/s、POST 200 连发；proxy 3495931 volcsw 82677→82701（12s +24 持续递增）、nvolcsw 274 不变、RSS 18213948kB S——**INFER 远端推理持续活跃，按裁决口径不 kill/cancel/retry**
  - `ingest_submission` 8 行不变，flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id 空等 A D4③；**14_42_48 正式全链维持 NOT_RUN**
  - `scan_job` 4039（05:35:47）新周期 incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝 10min 周期持续可追溯，无 409 新行
  - scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]
  - 本轮全部动作只读；未提交/retry/调模型/写生产
- PASS 基线不变（15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，24ab78bb dup NOT_APPLICABLE 无伪切片）。

### 2026-10-14 05:4x 增量巡检（只读，探针 `tester_0540_check.py` exit 0）

- `scene-4acf689f`（16_02_03 合法链）SCENE_RUNNING attempt1，heartbeat 05:40:54 30s 节奏；八步全 QUEUED started_at=NULL（~395min）。
- 升级条件逐项未命中：VLM 05:40:47–05:41:27 Running 0-2（05:41:17 起瞬态 0/KV 0.0%）但 POST 200 持续连发（05:41:27 仍收 POST 200）→ 请求流未断，非推理终止；prefix 91.1-91.2%；proxy 3495931 volcsw 83264→83293（12s +29 持续递增）nvolcsw 274 不变 RSS 18213948kB S。**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id 空等 A D4③，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 无 4040 新行（4039 05:35:47 最后），空包拒绝可追溯；scene run 7=6DONE+1RUNNING；8767 health=ok。
- PASS 基线不变（15_58_23/16_00_13/16_31_25/16_33_10 拒绝/16_02_03 在算/双 dup NOT_APPLICABLE）。事件 `tester-t11s-batch-1012-0541-infer-continue-quiet-20261014`。

### 2026-10-14 05:4x 增量巡检（只读，05:46 实测，探针 `tester_0540_check.py` 复用 exit 0）

- `scene-4acf689f`（16_02_03 合法链）SCENE_RUNNING attempt1，heartbeat 05:45:54 30s 节奏；八步全 QUEUED started_at=NULL（~401min）。
- 升级条件逐项未命中：VLM 05:45:17–05:45:47 Running 2-3、Waiting 0、prefix 90.8-91.0%、KV 2.1-3.8%、MM 88.6%、prompt 752-1118 tok/s、POST 200 持续连发；proxy 3495931 volcsw 83807→83831（12s +24 持续递增）、nvolcsw 276 微增、RSS 18213948kB S。**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id 空等 A D4③，**14_42_48 正式全链维持 NOT_RUN**；`ingest_submission` 8 行不变；`scan_job` 4039（05:35:47）仍为最新（10min 周期未到 05:45:47 触发线，无 4040 新行），空包拒绝可追溯；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读；未提交/retry/调模型/写生产。
- PASS 基线不变（15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源，24ab78bb dup NOT_APPLICABLE 无伪切片）。

### 2026-10-14 05:5x 增量巡检（只读，05:51 实测，探针 `tester_0550_check.py` exit 0）

- `scene-4acf689f`（16_02_03 合法链）SCENE_RUNNING attempt1，heartbeat 05:51:24 30s 节奏刷新；八步全 QUEUED started_at=NULL（约406min）。
- 升级条件逐项未命中：VLM 05:51:17-05:51:47 Running 3-4、Waiting 0、prefix 92.1%、KV 3.3-5.2%、MM 88.6%、prompt 332-1020 tok/s、POST 200 持续连发；proxy 3495931 volcsw 84609 到 84633（12s +24 持续递增）、nvolcsw 279 不变、RSS 18213948kB S。**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id 空等 A D4第三步（ingest_submission 8 行不变），**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4041/4040（05:45:47）新周期 incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读（处理机 mysql 容器 SELECT×5、docker top、远端 /proc/status 双采样、8767 health、VLM 日志）；未提交/retry/调模型/写生产。
- PASS 基线不变（15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源；24ab78bb dup NOT_APPLICABLE 无伪切片）。

### 2026-10-14 06:0x 增量巡检（只读，06:02 实测，探针 `tester_0600_check.py`+`tester_0600_ctx.py` exit 0）

- `scene-4acf689f`（16_02_03 合法链）SCENE_RUNNING attempt1，heartbeat 06:01:55 30s 节奏刷新；八步全 QUEUED started_at=NULL（约417min）。
- 升级条件逐项未命中：VLM 06:01:27-06:01:57 Running 2-3、Waiting 0、prefix 92.2%、KV 2.2-3.9%、MM 88.6%、prompt 0-2167 tok/s、POST 200 持续连发；proxy 3495931 volcsw 85868→85893（12s +25 持续递增）、nvolcsw 283、RSS 18213948kB S。**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL 等 A D4 第三步（ingest_submission 8 行不变），**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4043/4042（05:55:47-48）新周期 incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED]。
- 本轮全部动作只读（处理机 mysql 容器 SELECT×5、docker top、远端 /proc/status 直接 grep 双采样、8767 health、VLM 日志）；未提交/retry/调模型/写生产。
- PASS 基线不变（15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 拒绝 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源在算；24ab78bb/eb4397c3/a4824f1c dup 均 SCENE_DONE 终态无伪切片）。事件 `tester-t11s-batch-1012-0603-infer-continue-quiet-20261014`。

### 2026-10-14 06:12 +08:00 静默期增量只读巡检（06:1x，prerun 指纹 2bf5d8f2…）

- 状态：**无实质变化**。`scene-4acf689f`(16_02_03 合法链) SCENE_RUNNING attempt1，heartbeat 06:11:26、八步全 QUEUED started_at=NULL（约427min）。
- 升级条件逐项未命中：VLM 06:11:27-06:11:47 Running 4 reqs / Waiting 0-1 瞬态、prefix 92.1%、KV 3.9-5.1%、MM 88.7%、prompt 108-1576 tok/s、POST 200 连发；proxy 3495931 volcsw 87015->87043（12s +28 持续递增）、nvolcsw 284 不变、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4045/4044（06:05:48）新周期 incoming SUCCESS failed:2 空包拒绝持续；scene run 全集 7=6DONE+1RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED]。
- 全部动作只读（探针 `tester_0610_check.py` exit 0 + ctx 双采样），未提交/retry/调模型/写生产。PASS 基线不变。事件 `tester-t11s-batch-1012-0612-infer-continue-quiet-20261014`。

### 2026-10-14 06:17 +08:00 静默期增量只读巡检（prerun 指纹 71f47aa5…）

- 状态：**无实质变化**。`scene-4acf689f`(16_02_03 合法链) SCENE_RUNNING attempt1，heartbeat 06:16:26、八步全 QUEUED started_at=NULL（约432min）。
- 升级条件逐项未命中：VLM 06:15:57-06:16:27 Running 2-4 reqs / Waiting 0、KV 1.4-4.6%、prefix 92.3%、MM 88.9%、prompt 830-1044 tok/s、POST 200 连发；proxy 3495931 volcsw 87576->87600（12s +24 持续递增）、nvolcsw 285、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4047/4046（06:15:48）新周期 incoming SUCCESS failed:2 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6DONE+1RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED]。
- 全部动作只读（探针 `tester_0610_check.py` exit 0，ctxsw 段 docker top pid 解析失败为已知问题，改由 `tester_0600_ctx.py` /proc 直接双采样补证 exit 0），未提交/retry/调模型/写生产。PASS 基线不变。事件 `tester-t11s-batch-1012-0617-infer-continue-quiet-20261014`。

### 2026-10-14 06:2x 静默期增量只读巡检（06:21 实测，prerun 指纹 ed7c73de…）

- 状态：**无实质变化**。`scene-4acf689f`(16_02_03 合法链) SCENE_RUNNING attempt1，heartbeat 06:21:26 30s 节奏刷新、八步全 QUEUED started_at=NULL（约436min）。
- 升级条件逐项未命中：VLM 06:21:17-06:21:37 Running 2-4 reqs / Waiting 0（06:21:27 一行 Waiting 2 为 10s 级瞬态，下一行回落 0）、prefix 92.4-92.5%、KV 2.6-6.0%、MM 88.9%、prompt 5898 tok/s 峰值、POST 200 连发；proxy 3495931 volcsw 88190->88215（12s +25 持续递增）、nvolcsw 288 不变、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4047/4046（06:15:48）incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读（探针 `tester_0610_check.py` exit 0，ctxsw 段 docker top pid 解析失败为已知问题，改 `tester_0600_ctx.py` /proc 直接双采样 exit 0），未提交/retry/调模型/写生产。PASS 基线不变。事件 `tester-t11s-batch-1012-062x-infer-continue-quiet-20261014`。

## 2026-10-14 06:27 静默期巡检（prerun 指纹 e8c17161…）
- scene-4acf689f（16_02_03 合法链）06:25:44 实测 SCENE_RUNNING attempt1 heartbeat 06:25:27 30s 节奏、八步全 QUEUED started_at=NULL（约440min）=模型段完成信号未到。
- 升级条件逐项未命中：VLM 06:25:17-06:25:47 Running 1-2 reqs / Waiting 0、prefix 92.5-92.6%、KV 1.3-2.8%、MM 88.9%、POST 200 连发；proxy 3495931 volcsw 88727->88750（12s +23 持续递增）、nvolcsw 289、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4047/4046（06:15:48）incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读（探针 `tester_0625_check.py` exit 0，ctxsw 段 docker top pid 解析失败为已知问题，改 `tester_0625_ctx.py` ps 定位 + /proc 直接双采样 exit 0），未提交/retry/调模型/写生产。PASS 基线不变。事件 `tester-t11s-batch-1012-0627-infer-continue-quiet-20261014`。

## 2026-10-14 06:3x 静默期巡检（prerun 指纹 8ec7c326…）
- scene-4acf689f（16_02_03 合法链）06:36:16 实测 SCENE_RUNNING attempt1 heartbeat 06:35:57 30s 节奏、八步全 QUEUED started_at=NULL（约450min）=模型段完成信号未到。
- 升级条件逐项未命中：VLM 06:35:57-06:36:27 Running 2-3 reqs / Waiting 0、prefix 92.4%、KV 2.4-4.3%、MM 88.6%、POST 200 连发；proxy 3495931 volcsw 89946->89970（12s +24 持续递增）、nvolcsw 292、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4051/4050（06:35:49）新周期 incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读（探针 `tester_0635_check.py` exit 0，ps 定位 pid + /proc/status 直接双采样），未提交/retry/调模型/写生产。PASS 基线不变。事件 `tester-t11s-batch-1012-0636-infer-continue-quiet-20261014`。

## 2026-10-14 06:4x 静默期巡检（prerun 指纹 daa95223…）
- scene-4acf689f（16_02_03 合法链）06:40:52 实测 SCENE_RUNNING attempt1 heartbeat 06:40:28 30s 节奏、八步全 QUEUED started_at=NULL（约455min）=模型段完成信号未到。
- 升级条件逐项未命中：VLM 06:40:37-06:40:57 Running 3-4 reqs / Waiting 0、prefix 92.2%、KV 7.3-7.7%、MM 88.6%、POST 200 连发；proxy 3495931 volcsw 90502->90526（12s +24 持续递增）、nvolcsw 294、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4051/4050（06:35:49）后无新周期，incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读（探针 `tester_0639_check.py` exit 0，ps 定位 pid + /proc/status 直接双采样），未提交/retry/调模型/写生产。PASS 基线不变。事件 `tester-t11s-batch-1012-0641-infer-continue-quiet-20261014`。

### 2026-10-14 06:4x 静默期增量只读巡检（06:46 实测，prerun 指纹 ac8eb056…）

- 状态：**无实质变化**。`scene-4acf689f`(16_02_03 合法链) SCENE_RUNNING attempt1，heartbeat 06:45:58 30s 节奏、八步全 QUEUED started_at=NULL（约461min）=模型段完成信号未到。
- 升级条件逐项未命中：VLM 06:45:57-06:46:17 Running 3 reqs / Waiting 0、prefix 92.3-92.4%、KV 2.8-3.6%、MM 88.6%、prompt 284-2642 tok/s、POST 200 连发；proxy 3495931 volcsw 91147->91171（12s +24 持续递增）、nvolcsw 297、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4053/4052（06:45:49）新周期 incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读（探针 `tester_0639_check.py` 复用 exit 0，06:46:10 实测），未提交/retry/调模型/写生产。PASS 基线不变。事件 `tester-t11s-batch-1012-0647-infer-continue-quiet-20261014`。

## 2026-10-14 06:5x 静默期巡检（prerun 指纹 19eb713e…）
- scene-4acf689f（16_02_03 合法链）06:50:28 实测 SCENE_RUNNING attempt1 heartbeat 06:50:28 30s 节奏、八步全 QUEUED started_at=NULL（约470min）=模型段完成信号未到。
- 升级条件逐项未命中：VLM 06:50:27-06:50:57 Running 1-3 reqs / Waiting 0、prefix 92.4%、KV 1.1-3.4%、MM 88.6%、POST 200 连发；proxy 3495931 volcsw 91722->91746（12s +24 持续递增）、nvolcsw 298、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4053/4052（06:45:49）仍最新 incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读（探针 `tester_065x_check.py` exit 0，ps 定位 pid + /proc/status 直接双采样），未提交/retry/调模型/写生产。PASS 基线不变。事件 `tester-t11s-batch-1012-0650-infer-continue-quiet-20261014`。

## 2026-10-14 06:5x 静默期巡检（prerun 指纹 795a1a22…）
- scene-4acf689f（16_02_03 合法链）06:55:29 实测 SCENE_RUNNING attempt1 heartbeat 06:55:29 30s 节奏、八步全 QUEUED started_at=NULL（约475min）=模型段完成信号未到。
- 升级条件逐项未命中：VLM 06:55:07-06:55:37 Running 2-3 reqs / Waiting 0、prefix 92.2%、KV 2.5-3.5%、MM 88.6%、POST 200 连发；proxy 3495931 volcsw 92293->92319（12s +26 持续递增）、nvolcsw 298、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4053/4052（06:45:49）仍最新 incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读（探针 `tester_065x_check.py` 复用 exit 0，06:55:31 实测），未提交/retry/调模型/写生产。PASS 基线不变。事件 `tester-t11s-batch-1012-0655-infer-continue-quiet-20261014`。

## 2026-10-14 07:0x 静默期巡检（prerun 指纹 f0bd62a2…）
- scene-4acf689f（16_02_03 合法链）07:00:59 实测 SCENE_RUNNING attempt1 heartbeat 07:00:59 30s 节奏、八步全 QUEUED started_at=NULL（约480min）=模型段完成信号未到。
- 升级条件逐项未命中：VLM 07:00:58-07:01:18 Running 3-4 reqs / Waiting 0、prefix 92.1%、KV 5.7-6.0%、MM 88.6%、POST 200 连发；proxy 3495931 volcsw 92978->93002（12s +24 持续递增）、nvolcsw 300、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4055/4054（06:55:49）incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读（探针 `tester_070x_check.py` exit 0，07:01:12 实测），未提交/retry/调模型/写生产。PASS 基线不变。事件 `tester-t11s-batch-1012-0701-infer-continue-quiet-20261014`。

## 2026-10-14 07:07 静默期巡检（prerun 指纹 804d58e4…）
- scene-4acf689f（16_02_03 合法链）07:06:19 实测 SCENE_RUNNING attempt1 heartbeat 07:05:59 30s 节奏、八步全 QUEUED started_at=NULL（约485min）=模型段完成信号未到。
- 升级条件逐项未命中：VLM 07:06:08-07:06:28 Running 3-4 reqs / Waiting 0、prefix 92.0-92.1%、KV 6.4-7.8%、MM 88.6%、POST 200 连发；proxy 3495931 volcsw 93605->93631（12s +26 持续递增）、nvolcsw 301、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4057/4056（07:05:49）新周期 incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读（探针 `tester_070x_check.py` 复用 exit 0，07:06:19 实测），未提交/retry/调模型/写生产。PASS 基线不变。事件 `tester-t11s-batch-1012-0707-infer-continue-quiet-20261014`。

## 2026-10-14 07:15 静默期增量（prerun 指纹 d307a312…，探针 tester_070x_check.py 复用 exit 0）

- scene-4acf689f（16_02_03 合法链）07:15:38 实测 SCENE_RUNNING attempt1 heartbeat 07:15:30 30s 节奏、八步全 QUEUED started_at=NULL（约495min）=模型段完成信号未到。
- 升级条件逐项未命中：VLM 07:15:08-07:15:48 Running 0-2 reqs / Waiting 0、prefix 92.2、KV 0-2.9、MM 88.6、POST 200 连发；proxy 3495931 volcsw 94740->94764（12s +24 持续递增）、nvolcsw 301->303、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4057/4056（07:05:49）仍为最新 incoming SUCCESS dirs:3 bags:1 failed:2 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读，未提交/retry/调模型/写生产。PASS 基线不变。事件 `tester-t11s-batch-1012-0715-infer-continue-quiet-20261014`。


## 2026-10-14 07:2x 静默期增量只读巡检（07:26 实测，prerun 指纹 19e2899d…，探针 tester_0725_check.py 复用 exit 0）

- scene-4acf689f（16_02_03 合法链）07:26:01 实测 SCENE_RUNNING attempt1 heartbeat 07:26:01 30s 节奏、八步全 QUEUED started_at=NULL（约505min）=模型段完成信号未到。
- 升级条件逐项未命中：VLM 07:25:48-07:26:08 Running 1-2 reqs / Waiting 0、prefix 92.5、KV 0.9-2.4、MM 88.7、prompt 332-1036 tok/s、POST 200 连发；proxy 3495931 volcsw 95995->96019（12s +24 持续递增）、nvolcsw 305 不变、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4061/4060（07:25:50）新周期 incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读，未提交/retry/调模型/写生产。PASS 基线不变。事件 `tester-t11s-batch-1012-0728-infer-continue-quiet-20261014`。


## 2026-10-14 07:3x 静默期增量只读巡检（07:32 实测，prerun 指纹 ec8ee0cb…，探针 tester_0725_check.py 复用 exit 0）

- scene-4acf689f（16_02_03 合法链）07:32:31 实测 SCENE_RUNNING attempt1 heartbeat 07:32:31 30s 节奏、八步全 QUEUED started_at=NULL（约510min）=模型段完成信号未到。
- 升级条件逐项未命中：VLM 07:32:28-07:32:48 Running 2-3 reqs / Waiting 0、prefix 92.3-92.4、KV 4.2-6.3、MM 88.7、prompt 114-1131 tok/s、gen 77-174 tok/s、POST 200 连发；proxy 3495931 volcsw 96792->96816（12s +24 持续递增）、nvolcsw 309、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4061/4060（07:25:50）仍最新（07:35 周期未到点）incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读，未提交/retry/调模型/写生产。PASS 基线不变。事件 `tester-t11s-batch-1012-0732-infer-continue-quiet-20261014`。

## 增量验收 07:40（4acf689f 模型段持续在算，只读无实质变化，2026-10-14T07:40:52+08:00）

- **唤醒源**：prerun 指纹 `2d3e0ed7…`（变更源=上轮 07:32 自写事件 `tester-t11s-batch-1012-0732-infer-continue-quiet-20261014` 的 canonical 落盘 + sessions 回声），非新派单/新 decision。
- **关键实测（07:40:52）**：`scene-4acf689f`(16_02_03 合法链) SCENE_RUNNING attempt1，heartbeat **07:40:32** 30s 节奏刷新、八步仍全 **QUEUED** started_at=NULL（模型段 ~520min）；**升级条件逐项未命中**——VLM 07:40:38-07:40:58 Running 3 reqs / Waiting 0、prefix 92.9、KV 3.7-4.1、MM 88.7、prompt 622-1879 tok/s、gen 33-174 tok/s、POST 200 连发、proxy 3495931 volcsw 97798->97822（12s +24 持续递增）、nvolcsw 312、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 **PENDING_INPUT** source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4063/4062（07:35:50）新周期 incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读（探针 `tester_0725_check.py` 复用 exit 0；SSH 生产 MySQL SELECT×5 表、8767 只读探测、/proc/status 双采样、VLM 日志 tail）；未提交/retry/调模型/写生产。
- **PASS 基线不变**（15_58_23 复用 / 16_00_13 SUCCESS / 16_31_25 NOT_APPLICABLE / 16_33_10 空包拒绝可追溯 / 16_37_47+16_58_28 flat SHA 闭合 / 16_02_03 SHA=源）。
- **下一步**：等 4acf689f 模型段完成信号（checkpoint 翻 EXTRACT/DONE 或八步 DB 推进或 SCENE_DONE，跨夜继续）；A flat 三提交绑定行出现后核 14_42_48 正式全链（0038 口径）；全批 8 包齐后 TEST_REPORT_PENDING。


## 2026-10-14 07:5x 静默期增量只读巡检（07:51:28 实测，prerun 指纹 4dc91230…，探针 tester_0750_check.py exit 0）

- scene-4acf689f（16_02_03 合法链）07:51:02 实测 SCENE_RUNNING attempt1 heartbeat 30s 节奏、八步全 QUEUED started_at=NULL（约530min）=模型段完成信号未到。
- 升级条件逐项未命中：proxy 3495931 volcsw 99097->99121（12s +24 持续递增，较 07:40 的 97798 同节奏）、nvolcsw 317、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**（VLM 日志 tail 本轮空输出，维持 heartbeat+ctxsw 双锚定口径）。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4065/4064（07:45:51）新周期 incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读，未提交/retry/调模型/写生产。PASS 基线不变。事件 `tester-t11s-batch-1012-0750-infer-continue-quiet-20261014`。

## 2026-10-14 07:5x 静默期增量只读巡检（07:56:01 实测，prerun 指纹 f1429af1…，探针 tester_0755_check.py exit 0）

- scene-4acf689f（16_02_03 合法链）07:56:01 实测 SCENE_RUNNING attempt1 heartbeat 07:55:32 30s 节奏、八步全 QUEUED started_at=NULL（约540min）=模型段完成信号未到。
- 升级条件逐项未命中：VLM 07:55:58-07:56:08 Running 2 reqs / Waiting 0、prefix 93.2、KV 3.2-3.3、MM 88.8、prompt 222-401 tok/s、gen 134-177 tok/s、POST 200 连发；proxy 3495931 volcsw 99639->99663（12s +24 持续递增，较 07:51 的 99097 同节奏）、nvolcsw 320、RSS 18213948kB S——**INFER 远端推理持续活跃，不 kill/cancel/retry**。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，**14_42_48 正式全链维持 NOT_RUN**；`scan_job` 4067/4066（07:55:51）新周期 incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]。
- 本轮全部动作只读，未提交/retry/调模型/写生产。PASS 基线不变。事件 `tester-t11s-batch-1012-0755-infer-continue-quiet-20261014`。

## 2026-10-14 08:00 增量巡检（静默期结束首轮，prerun 指纹 659cbb95…）

- 探针 `tester_0800_check.py` exit 0（08:01:12 实测，全部只读）。
- `scene-4acf689f` SCENE_RUNNING attempt1：heartbeat 08:01:03（30s 节奏正常）、八步全 QUEUED started_at=NULL（~550min）。
- 升级条件逐项未命中：VLM 08:00:58-08:01:18 Running 3-4 / Waiting 0、prefix 93.1、KV 4.1-4.9、MM 88.9、prompt 86-1078 tok/s、gen 117-195 tok/s、POST 200 连发；proxy 3495931 同 pid volcsw 100273->100297（12s +24 持续递增）、nvolcsw 322、RSS 18144036kB S。**结论：INFER 远端推理持续活跃，不 kill/cancel/retry。**
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步；**14_42_48 正式全链维持 NOT_RUN**。
- `scan_job` 4067/4066（07:55:51-52）仍最新：incoming SUCCESS {dirs:3 bags:1 failed:2} 空包拒绝可追溯、self_built 8dirs 全绿；下一周期（4068/4069）未触发。
- scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health=ok active_runs=[4acf689f ACCEPTED pid:1]；PASS 基线不变。
- 未提交/retry/调模型/写生产。

## 2026-10-14 08:0x 增量巡检（prerun 指纹 38338fd2…，单脚本 claim→巡检→落盘→release→ack 闭环）

- 2026-10-14 08:07:38 +0800 实测：`scene-4acf689f` heartbeat 2026-10-14 08:07:33、八步 QUEUED 8/8；proxy 3495931 volcsw 101056->101080（+24/12s）（+24/12s）、nvolcsw 326——INFER 持续活跃，不 kill/cancel/retry。
- flat 三提交 3/3 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变），14_42_48 正式全链 NOT_RUN；scan 最新周期 4069	/public/rosbag_scene_processing/incoming	SUCCESS	{"directories": 3, "bags": 1, "created": 0, "updated": 0, "failed": 2, "root_id": "scene"}	2026-10-14 08:05:52；8767 health ok；PASS 基线不变。
- VLM tail：(APIServer pid=17395) INFO 10-14 08:07:18 [loggers.py:273] Engine 000: Avg prompt throughput: 845.2 tokens/s, Avg generation throughput: 85.1 tokens/s, Running: 3 reqs, Waiting: 0 reqs, GPU KV cache usage: 6.1%, Prefix cache hit rate: 93.3%, MM cache hit rate: 88.9% | (APIServer pid=17395) INFO:     127.0.0.1:49032 - "POST /v1/chat/completions HTTP/1.1" 200 OK | (APIServer pid=17395) INFO:     127
- 全部只读（探针段单脚本内执行 exit 0），未提交/retry/调模型/写生产。

## 2026-10-14 08:1x 增量巡检（prerun 指纹 65db1358…，单脚本 claim→巡检→落盘→release→ack 闭环）

- 2026-10-14 08:17:12 +0800 实测：`scene-4acf689f` heartbeat 2026-10-14 08:17:04、八步 QUEUED 8/8；proxy 3495931 volcsw 102221->332（12s）、nvolcsw 332——INFER 持续活跃，不 kill/cancel/retry。
- flat 三提交 3/3 PENDING_INPUT source_id=NULL（ingest_submission 9 行），14_42_48 正式全链 NOT_RUN；scan 最新周期 4071	/public/rosbag_scene_processing/incoming	SUCCESS	{"directories": 3, "bags": 1, "created": 0, "updated": 0, "failed": 2, "root_id": "scene"}	2026-10-14 08:15:53；8767 health ok；PASS 基线不变。
- VLM tail：(APIServer pid=17395) INFO:     127.0.0.1:58570 - "GET /v1/models HTTP/1.1" 200 OK | (APIServer pid=17395) INFO:     127.0.0.1:58584 - "POST /v1/chat/completions HTTP/1.1" 200 OK | (APIServer pid=17395) INFO 10-14 08:16:48 [loggers.py:273] Engine 000: Avg prompt throughput: 81.9 tokens/s, Avg generation throughput: 186.5 tokens/s, Running: 2 reqs, Waiting: 0 reqs, GPU KV cache usage: 4.0%, Prefix 
- 全部只读（探针段单脚本内执行），未提交/retry/调模型/写生产。

## 2026-10-14 08:2x 增量巡检（prerun 指纹 fcb8bd08…，单脚本 claim→巡检→落盘→release→ack 闭环）

- 2026-10-14 08:23:06 +0800 实测：`scene-4acf689f` heartbeat 2026-10-14 08:23:04、八步 QUEUED 8/8；proxy 3495931 volcsw 102937->102961（12s +24）、nvolcsw 334 不变——INFER 持续活跃，不 kill/cancel/retry。（注：初稿 regex 误取 nvolcsw 为 t12 值，已核 /proc 原始采样修正）
- flat 三提交 3/3 PENDING_INPUT source_id=NULL（ingest_submission 9 行），14_42_48 正式全链 NOT_RUN；scan 最新周期 4071	/public/rosbag_scene_processing/incoming	SUCCESS	{"directories": 3, "bags": 1, "created": 0, "updated": 0, "failed": 2, "root_id": "scene"}	2026-10-14 08:15:53；8767 health ok；PASS 基线不变。
- VLM tail：(APIServer pid=17395) INFO:     127.0.0.1:58000 - "POST /v1/chat/completions HTTP/1.1" 200 OK | (APIServer pid=17395) INFO:     127.0.0.1:58014 - "GET /v1/models HTTP/1.1" 200 OK | (APIServer pid=17395) INFO 10-14 08:22:48 [loggers.py:273] Engine 000: Avg prompt throughput: 87.9 tokens/s, Avg generation throughput: 146.2 tokens/s, Running: 4 reqs, Waiting: 0 reqs, GPU KV cache usage: 8.0%, Prefix 
- 全部只读（探针段单脚本内执行），未提交/retry/调模型/写生产。

## 2026-10-14 08:3x 增量巡检（prerun 指纹 cdff09ab…，单脚本 claim→巡检→落盘→release→ack 闭环）

- 2026-10-14 08:34:36 +0800 实测：`scene-4acf689f` heartbeat 2026-10-14 08:34:35、八步 QUEUED 8/8；proxy 3495931 volcsw 104326->104350（12s）、nvolcsw 342——INFER 持续活跃，不 kill/cancel/retry。
- flat 三提交 3/3 PENDING_INPUT source_id=NULL（ingest_submission 9 行），14_42_48 正式全链 NOT_RUN；scan 最新周期 4073	/public/rosbag_scene_processing/incoming	SUCCESS	{"directories": 3, "bags": 1, "created": 0, "updated": 0, "failed": 2, "root_id": "scene"}	2026-10-14 08:25:54；8767 health ok；PASS 基线不变。
- VLM tail：(APIServer pid=17395) INFO 10-14 08:33:48 [loggers.py:273] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 142.1 tokens/s, Running: 2 reqs, Waiting: 0 reqs, GPU KV cache usage: 2.9%, Prefix cache hit rate: 93.3%, MM cache hit rate: 89.0% | (APIServer pid=17395) INFO:     127.0.0.1:35166 - "GET /v1/models HTTP/1.1" 200 OK | (APIServer pid=17395) INFO 10-14 08:33:58 [logg
- 全部只读（探针段单脚本内执行），未提交/retry/调模型/写生产。

## 2026-10-14 08:4x 增量巡检（prerun 指纹 02913eed…，单脚本 claim→巡检→落盘→release→ack 闭环）

- 2026-10-14 08:43:25 +0800 实测：`scene-4acf689f` heartbeat 2026-10-14 08:43:06、八步 QUEUED 8/8；proxy 3495931 volcsw 105393->105417（12s）、nvolcsw 344——INFER 持续活跃，不 kill/cancel/retry。
- flat 三提交 3/3 PENDING_INPUT source_id=NULL（ingest_submission 9 行），14_42_48 正式全链 NOT_RUN；scan 最新周期 4075	/public/rosbag_scene_processing/incoming	SUCCESS	{"directories": 3, "bags": 1, "created": 0, "updated": 0, "failed": 2, "root_id": "scene"}	2026-10-14 08:3；8767 health ok；PASS 基线不变。
- VLM tail：(APIServer pid=17395) INFO:     127.0.0.1:43164 - "POST /v1/chat/completions HTTP/1.1" 200 OK | (APIServer pid=17395) INFO 10-14 08:42:48 [loggers.py:273] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 109.8 tokens/s, Running: 2 reqs, Waiting: 0 reqs, GPU KV cache usage: 2.9%, Prefix cache hit rate: 93.1%, MM cache hit rate: 89.1% | (APIServer pid=17395) INFO:     127.
- 全部只读（探针段单脚本内执行），未提交/retry/调模型/写生产。

## 2026-10-14 08:5x 增量巡检（prerun 指纹 979c9ac0…，单脚本 claim→巡检→落盘→release→ack 闭环）

- 2026-10-14 08:47:51 +0800 实测：`scene-4acf689f` heartbeat 2026-10-14 08:47:36、八步 QUEUED 8/8；proxy 3495931 volcsw 105929->105953（12s）、nvolcsw 344——INFER 持续活跃，不 kill/cancel/retry。
- flat 三提交 3/3 PENDING_INPUT source_id=NULL（ingest_submission 9 行），14_42_48 正式全链 NOT_RUN；scan 最新周期 4077	/public/rosbag_scene_processing/incoming	SUCCESS	{"directories": 3, "bags": 1, "created": 0, "updated": 0, "failed": 2, "root_id": "scene"}	2026-10-14 08:4；8767 health ok；PASS 基线不变。
- VLM tail：(APIServer pid=17395) INFO 10-14 08:47:18 [loggers.py:273] Engine 000: Avg prompt throughput: 839.4 tokens/s, Avg generation throughput: 179.2 tokens/s, Running: 4 reqs, Waiting: 0 reqs, GPU KV cache usage: 7.9%, Prefix cache hit rate: 92.9%, MM cache hit rate: 89.1% | (APIServer pid=17395) INFO 10-14 08:47:28 [loggers.py:273] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation through
- 全部只读（探针段单脚本内执行），未提交/retry/调模型/写生产。

## 2026-10-14 08:5x 增量巡检（prerun 指纹 c538809f…，单脚本 claim→巡检→落盘→release→ack 闭环）

- 2026-10-14 08:55:50 +0800 实测：`scene-4acf689f` heartbeat 2026-10-14 08:55:36、八步 QUEUED 8/8；proxy 3495931 volcsw 106901->106925（12s +24）、nvolcsw 347、RSS 18137684kB S——INFER 持续活跃，不 kill/cancel/retry。
- flat 三提交 3/3 PENDING_INPUT source_id=NULL（ingest_submission 9 行），14_42_48 正式全链 NOT_RUN；scan 最新周期 4077	/public/rosbag_scene_processing/incoming	SUCCESS	{"directories": 3, "bags": 1, "created": 0, "updated": 0, "failed": 2, "root_id": "scene"}	2026-10-14 08:45:55；8767 health ok（active_runs=[4acf689f ACCEPTED pid:1]）；PASS 基线不变。
- VLM tail：(APIServer pid=17395) INFO 10-14 08:55:38 [loggers.py:273] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 76.5 tokens/s, Running: 2 reqs, Waiting: 0 reqs, GPU KV cache usage: 2.6%, Prefix cache hit rate: 92.8%, MM cache hit rate: 89.0% | (APIServer pid=17395) INFO 10-14 08:55:48 [loggers.py:273] Engine 000: Avg prompt throughput: 1152.9 tokens/s, Avg generation throughput: 111.4 tokens/s, Running: 2 reqs, Waiting: 0 reqs, GPU KV cache usage: 2.7% | (APIServer pid=17395) INFO: 127.0.0.1:34628 - "POST /v1/chat/completions HTTP/1.1" 200 OK
- 全部只读（探针 tester_0850_check.py 单脚本执行 exit 0），未提交/retry/调模型/写生产。

## 2026-10-14 09:0x 增量巡检（prerun 指纹 8f69f291…，单脚本 claim→巡检→落盘→release→ack 闭环）

- 用户恢复交接核读：原角色机制/5分钟 poll 恢复，Codex 临时接管已释放；attempt-1 ACK 口径不变（3c9c496 固定、只读验收）。
- 2026-10-14 09:03:37 +0800 实测：`scene-4acf689f` heartbeat 2026-10-14 09:03:37、八步 QUEUED 8/8；proxy 3495931 volcsw 107844->107868（12s）、nvolcsw 349——INFER 持续活跃，不 kill/cancel/retry。
- flat 三提交 3/3 PENDING_INPUT source_id=NULL（ingest_submission 9 行），14_42_48 正式全链 NOT_RUN；scan 最新周期 4079	/public/rosbag_scene_processing/incoming	SUCCESS	{"directories": 3, "bags": 1, "created": 0, "updated": 0, "failed": 2, "root_id": "scene"}	2026-10-14 08:5；8767 health ok；PASS 基线不变。
- VLM tail：(APIServer pid=17395) INFO 10-14 09:03:09 [loggers.py:273] Engine 000: Avg prompt throughput: 1241.4 tokens/s, Avg generation throughput: 85.4 tokens/s, Running: 4 reqs, Waiting: 0 reqs, GPU KV cache usage: 6.2%, Prefix cache hit rate: 92.7%, MM cache hit rate: 89.0% | (APIServer pid=17395) INFO:     127.0.0.1:50058 - "POST /v1/chat/completions HTTP/1.1" 200 OK | (APIServer pid=17395) INFO 10-14 0
- 全部只读（探针段单脚本内执行），未提交/retry/调模型/写生产。

## 2026-10-14 09:1x 增量巡检（prerun 指纹 fc52683c…，单脚本 claim→巡检→落盘→release→ack 闭环）

- 2026-10-14 09:13:25 +0800 实测：`scene-4acf689f` heartbeat 2026-10-14 09:13:08、八步 QUEUED 8/8；proxy 3495931 volcsw 109041->109065（12s）、nvolcsw 354——INFER 持续活跃，不 kill/cancel/retry。
- flat 三提交 3/3 PENDING_INPUT source_id=NULL（ingest_submission 9 行），14_42_48 正式全链 NOT_RUN；scan 最新周期 4081	/public/rosbag_scene_processing/incoming	SUCCESS	{"directories": 3, "bags": 1, "created": 0, "updated": 0, "failed": 2, "root_id": "scene"}	2026-10-14 09:0；8767 health ok；PASS 基线不变。
- VLM tail：(APIServer pid=17395) INFO:     127.0.0.1:40284 - "POST /v1/chat/completions HTTP/1.1" 200 OK | (APIServer pid=17395) INFO 10-14 09:12:59 [loggers.py:273] Engine 000: Avg prompt throughput: 1746.4 tokens/s, Avg generation throughput: 37.9 tokens/s, Running: 3 reqs, Waiting: 0 reqs, GPU KV cache usage: 4.7%, Prefix cache hit rate: 92.7%, MM cache hit rate: 89.0% | (APIServer pid=17395) INFO 10-14 0
- 全部只读（探针段单脚本内执行），未提交/retry/调模型/写生产。

## 2026-10-14 09:1x 增量巡检（prerun 指纹 cfc3f098…，09:19:53 轮，单脚本 claim→巡检→落盘→release→ack 闭环）

- 2026-10-14 09:22:13 +0800 实测：`scene-4acf689f` heartbeat 2026-10-14 09:22:08、八步 QUEUED 8/8；proxy 3495931 volcsw 110108->110132（12s）、nvolcsw 359——INFER 持续活跃，不 kill/cancel/retry。
- flat 三提交 3/3 PENDING_INPUT source_id=NULL（ingest_submission 9 行），14_42_48 正式全链 NOT_RUN；scan 最新周期 4083	/public/rosbag_scene_processing/incoming	SUCCESS	{"directories": 3, "bags": 1, "created": 0, "updated": 0, "failed": 2, "root_id": "scene"}	2026-10-14 09:1；8767 health ok；PASS 基线不变。
- VLM tail：(APIServer pid=17395) INFO:     127.0.0.1:35122 - "POST /v1/chat/completions HTTP/1.1" 200 OK | (APIServer pid=17395) INFO:     127.0.0.1:41214 - "POST /v1/chat/completions HTTP/1.1" 200 OK | (APIServer pid=17395) INFO:     127.0.0.1:41226 - "POST /v1/chat/completions HTTP/1.1" 200 OK | (APIServer pid=17395) INFO:     127.0.0.1:41238 - "POST /v1/chat/completions HTTP/1.1" 200 OK | (APIServer pid=1
- 全部只读（探针段单脚本内执行），未提交/retry/调模型/写生产。

## 2026-10-14 09:2x 增量巡检（prerun 指纹 b0846f09…，单脚本 claim→巡检→renew→release 闭环）

- 2026-10-14 09:29:38 +0800 实测：`scene-4acf689f` heartbeat 09:29:39、八步 QUEUED 8/8；VLM 09:29:19-09:29:49 Running 2-4 reqs / Waiting 0、prefix 92.5、KV 3.4-7.2、MM 88.8、POST 200 连发；proxy 3495931 volcsw 111007->111031（12s +24）、nvolcsw 359、RSS 18084436kB S——INFER 持续活跃，不 kill/cancel/retry。
- flat 三提交 3/3 PENDING_INPUT source_id=NULL，14_42_48 正式全链 NOT_RUN；scan 最新周期 4085	/public/rosbag_scene_processing/incoming	SUCCESS	{"directories": 3, "bags": 1, "created": 0, "updated": 0, "failed": 2, "root_id": "scene"}	2026-10-14 09:25:57（self_built 4084 全绿）；8767 health ok（active_runs=[4acf689f ACCEPTED pid:1]）；PASS 基线不变。
- 全部只读（探针 tester_0925_run.py 单脚本执行 exit 0），未提交/retry/调模型/写生产。

## 2026-10-14 09:3x 增量巡检（prerun 指纹 586cfb2d…，单脚本 claim→巡检→renew→release 闭环）

- 2026-10-14 09:38:17 +0800 实测：`scene-4acf689f` heartbeat 09:38:09、八步 QUEUED 8/8 started_at=NULL（入队 ~633min）；VLM 09:37:59-09:38:29 Running 3-4 reqs / Waiting 1-2 瞬态（10s 级回落）、prefix 90.9-92.1%、KV 3.9-7.0%、MM 88.8、POST 200 连发；proxy 3495931 volcsw 112067->112091（12s +24）、nvolcsw 362 不变、RSS 18084332kB S——INFER 持续活跃，升级条件逐项未命中，不 kill/cancel/retry。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 3/3 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，14_42_48 正式全链 NOT_RUN；scan 最新周期 4087	/public/rosbag_scene_processing/incoming	SUCCESS	{"directories": 3, "bags": 1, "created": 0, "updated": 0, "failed": 2, "root_id": "scene"}	09:35:57（空包 16_33_10 拒绝 10min 周期持续，self_built 4086 8dirs 全绿）；scene run 全集 7=6 SCENE_DONE+1 SCENE_RUNNING 无新 run；8767 health ok（active_runs=[4acf689f ACCEPTED pid:1]）；PASS 基线不变。
- 唤醒源=上轮 09:30:10 自写事件 canonical 落盘 + `inbox/PROTOCOL.md` 09:34:47 同步（已核读，无 TESTER 新指令）+ sessions 回声，无新派单/新 decision。
- 全部只读（探针 tester_0935_run.py 单脚本执行 exit 0），未提交/retry/调模型/写生产。事件 `tester-t11s-batch-1012-0938-infer-continue-20261014`。

## 2026-10-14 09:4x 增量巡检（prerun 指纹 b8858110…，单脚本 claim→巡检→renew→release 闭环）

- 2026-10-14 09:48:16 +0800 实测：`scene-4acf689f` heartbeat 09:48:10、八步 QUEUED 8/8 started_at=NULL（入队 ~643min）；VLM 09:48:09-09:48:29 Running 3-4 reqs / Waiting 0-1 瞬态、prefix 91.2、KV 3.6-5.6、MM 88.8、prompt 424-1785 tok/s、gen 59-212 tok/s、POST 200 连发；proxy 3495931 volcsw 113275->113299（12s +24 持续递增）、nvolcsw 368 不变、RSS 18084332kB S——INFER 远端推理持续活跃，升级条件逐项未命中，不 kill/cancel/retry。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 3/3 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，14_42_48 正式全链维持 NOT_RUN；scan 4089 incoming SUCCESS {directories:3 bags:1 failed:2} 09:45:58 周期持续空包 16_33_10 拒绝可追溯、self_built 4088 8dirs 全绿；scene run 全集 7=6SCENE_DONE+1SCENE_RUNNING 无新 run；8767 health ok active_runs=[4acf689f ACCEPTED pid:1]；PASS 基线不变。
- 全部只读（探针 tester_0944_run.py 单脚本执行 exit 0），未提交/retry/调模型/写生产。

## 2026-10-14 09:5x 增量巡检（prerun 指纹 73fdcbd3…，单脚本 claim→巡检→renew→release 闭环）

- 2026-10-14 09:57:40 +0800 实测：`scene-4acf689f` heartbeat 09:57:40、八步 QUEUED 8/8 started_at=NULL（入队 ~653min）；VLM 09:56:59-09:57:19 Running 3-4 reqs / Waiting 0-1 瞬态、prefix 91.3-91.5、KV 3.8-6.0、MM 88.8、prompt 578-1383 tok/s、gen 91-208 tok/s、POST 200 连发；proxy 3495931 volcsw 114343->114367（12s +24 持续递增）、nvolcsw 369 不变、RSS 18084292kB S——INFER 远端推理持续活跃，升级条件逐项未命中，不 kill/cancel/retry。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 3/3 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，14_42_48 正式全链维持 NOT_RUN；scan 4091 incoming SUCCESS {directories:3 bags:1 failed:2} 09:55:59 周期持续空包 16_33_10 拒绝可追溯、self_built 4090 8dirs 全绿；scene run 全集 7=6SCENE_DONE+1SCENE_RUNNING 无新 run；8767 health ok active_runs=[4acf689f ACCEPTED pid:1]；PASS 基线不变。
- 全部只读（探针 tester_0954_run.py 单脚本执行 exit 0，lease 释放后 cat 为空），未提交/retry/调模型/写生产。

## 2026-10-14 10:1x 增量巡检（prerun 指纹 ed030147…，单脚本 claim→巡检→renew→release 闭环）

- 2026-10-14 10:18:19 +0800 实测：`scene-4acf689f` heartbeat 10:18:12、八步 QUEUED 8/8 started_at=NULL（入队 ~673min）；VLM 10:18:09-10:18:39 Running 4 reqs / Waiting 3→1 瞬态回落、prefix 95.4、KV 7.4-17.3、MM 88.6、prompt 214-874 tok/s、gen 59-150 tok/s、POST 200 连发；proxy 3495931 volcsw 116912->116936（12s +24 持续递增）、nvolcsw 376 不变、RSS 18084292kB S——INFER 远端推理持续活跃，升级条件逐项未命中，不 kill/cancel/retry。
- flat 三提交 `a65a25a7`(14_42_48)/`87dfebaa`(16_37_47)/`518089ed`(16_58_28) 3/3 仍 PENDING_INPUT source_id=NULL（ingest_submission 8 行不变）等 A D4 第三步，14_42_48 正式全链维持 NOT_RUN；scan 4095 incoming SUCCESS {directories:3 bags:1 failed:2} 10:16:00 周期持续空包 16_33_10 拒绝可追溯、self_built 4094 8dirs 全绿；scene run 全集 7=6SCENE_DONE+1SCENE_RUNNING 无新 run；8767 health ok active_runs=[4acf689f ACCEPTED pid:1]；PASS 基线不变。
- 唤醒源说明：prerun 变更源 `inbox/PROTOCOL.md` mtime 10:15:17 刷新，内容核对=20:58:48 恢复决定历史行（本批唯一任务 TASK-11S-BATCH-1012、UI 仍暂停），非新 TESTER 指令。
- 全部只读（探针 tester_1014_run.py 单脚本执行 exit 0，lease 释放），未提交/retry/调模型/写生产。

## 2026-10-14 10:2x–12:0x 增量验收（prerun 指纹 1942a42a…，消费 Codex 直接修复回执 10:23，复用 run 面独立取证）

- **唤醒源=实质新输入（非自写回声）**：`codex-repair-receipt-20261014.md`（10:23，协调者/Codex 面）——三份 flat 提交经正式 Backend API 恢复源登记+用途事件消费，**复用既有终态 run（created_runs=0/reused_runs=3）**：`a65a25a7`(14_42_48)→`scene-a4824f1c`(SUCCESS)、`87dfebaa`(16_37_47)→`scene-eb4397c3`(NOT_APPLICABLE)、`518089ed`(16_58_28)→`scene-24ab78bb`(NOT_APPLICABLE)；`4acf689f` 八步补报真实阶段（PRECHECK/EXTRACT=DONE、INFER=RUNNING）。TESTER 本轮独立核该复用结果及既有产物。
- **① 绑定面 DB 独立核对（10:32/10:35，处理机 MySQL 只读）**：flat 三提交 3/3 **SCHEDULED**（updated 10:23:08/09）、source_id 落值 `FFDEE943…`/`9C9456B6…`/`205E5054…`；`purpose_schedule_event` id 8/9/10 **CONSUMED**（10:23:08/09，gen1，capability/config hash 与 run 冻结配置一致）；`ingest_submission` 8 行不变、**无新 scene run（全集 7）**=复用口径实证；`a65a25a7` 行 idempotency_key=`spray1012:rosbag2_2026_10_08-14_42_48:0195a14f…`（稳定派生格式在案）、source_metadata vehicle_code=test、bound ready 路径 flat。**血缘注记（如实记录）**：被复用 run `a4824f1c` 行内 submission_id 仍指向已删 date-grouped `03281a51`，正式提交 `a65a25a7` 经 source 绑定+用途事件消费关联同一 run，非新 attempt。
- **② 14_42_48（`a65a25a7`→复用 run `scene-a4824f1c` attempt2，SUCCESS）→ 独立 PASS（复用产物验收，0038 口径并入）**：八步 attempt2 全 DONE（23:54:25/41）；outcome SUCCESS recorded 23:54:41；父包 `FFDEE943…` bag_record **READY**（39711 msgs、started_at 2026-10-08 14:42:49、vehicle_id=1=test、row_version=2）；**4 子包 READY/AVAILABLE**（`16Bc-0c0695…`/`16Bc-94a9db…`/`16Bc-491286…`/`16Bc-7a95e7…`，各 11165/11146/11175/11154 msgs×15.0s 窗口=15000000000ns、db3 各 ~202MB 物理非空）；**真实时间戳边界**：4 切片 14:42:52.007→14:43:43.007（2026-10-08，源采集窗内、`slice_manifest.json` expected_slice_keys 4/4 全覆盖、mapping_basis=bag_storage_ns、source_fingerprint `fa86215e…` 与 flat source_copy 一致、gen1、outcome SUCCESS）；ready 源 SHA 今晨复核 metadata `a5bd2d90…`=manifest、db3 `ca879384…`=21:3x 源台账；catalog `GET /api/v1/bags/<4子包>` 全部 READY。**两次正式 reconcile**（`POST …/reconcile-scene`，payload scene_code=spray/gen1/publish_root=slices）：**200 @11:18:58（reconciled+registered，available_children=4）** 与 **200 @11:28:58**，两次后 DB 行零变化（row_version=1/updated_at=23:54:41 四子包+父包不变、无重复子包）=**幂等确认**。**双写事件产物登记（0038 裁决口径）**：FFDEE943×4 切片=22:53 dup RETRY 事件产物，现经正式 `a65a25a7` 绑定复用核销，如实登记不计新交付物。
- **③ 16_37_47/16_58_28（`87dfebaa`/`518089ed`→复用 run `eb4397c3`/`24ab78bb`，NOT_APPLICABLE）→ 独立 PASS（NOT_APPLICABLE 分支）**：run 终态 NOT_APPLICABLE recorded 00:01:30/00:07:46、缺 iv_* topic 口径与 B 21:12 一致；**正式 reconcile 各 2 次=409 INCOMPLETE「发布根下无本 run 切片的 manifest 记录」（11:36/11:47 实测）**=无伪切片发布面正式确认；物理面 `slices/test/spray/` 6 目录=2 PASS 基线+4 FFDEE943，**无 `9C9456B6…`/`205E5054…` 目录**；16_58_28 ready SHA 今晨 3/3 逐字节=本地源（`935220dc…`/`26971938…`/`55ff5e55…`）；16_37_47 维持 22:2x 逐字节 IDENTICAL 源结论（复用）。
- **④ 16_02_03（`4acf689f`）维持 IN_PROGRESS，全链 NOT_RUN**：12:05:17 heartbeat、INFER=RUNNING（10:26:00 补报后）、SCENE_RUNNING attempt1；VLM Running 4 reqs/Waiting 2-4 瞬态、prefix 95.4、KV 10-21%、MM 88.5、POST 200 连发；proxy 3495931 volcsw 118594→119017（多轮 +24/12s 持续递增）、nvolcsw 380 不变、RSS 18084028kB S——**INFER 远端推理持续活跃，升级条件逐项未命中，不 kill/cancel/retry**；ready 三方 SHA 今晨复核 3/3=源台账（`e40a8d86…`/`b352cde3…`/`bceda7fe…`）；SCENE_DONE 后核八步/跨 DB3 真实边界/两次 reconcile。
- **⑤ 环境面**：scan 4115（11:56:09）incoming SUCCESS {dirs:3 bags:1 failed:2} 空包 16_33_10 拒绝 10min 周期持续可追溯、self_built 4114 8dirs 全绿；8767 health ok active_runs=[4acf689f ACCEPTED pid:1]；16_33_10 拒绝闭环维持 PASS。
- **⑥ 观察项（报协调者，不自行处置，非阻塞）**：`a4824f1c` reconcile 在两次 200 之外的 3 次尝试 500（`pymysql 1205 Lock wait timeout`，11:28:22/11:45:38/12:00:18），阻塞持有者无法经 app 账号定位（information_schema.innodb_trx 需 PROCESS 权限被拒）；processlist 见 backend 池连接 93257 在 `SELECT pipeline_run…` 长时间 statistics 态。不影响本次两次正式 reconcile 200 幂等结论；是否属在途 4acf689f 心跳/租约写者同池锁竞争建议协调者归因（可并入 10:17 登记的缺陷候选面，不新开任务）。
- 本轮动作边界：只读 DB/物理 SHA/catalog GET + **两次正式 reconcile-scene POST（`a4824f1c`）与两次 409 确认 POST（`eb4397c3`/`24ab78bb`）**——reconcile 为派单 AC 要求的正式验收动作（非提交/非 retry/非调模型/非业务写，幂等 no-op 实证）；其余不提交/不 retry/不调模型/不写生产；探针 `tester_1014_run.py`（10:3x 复用）+处理机远端 reconcile 日志 `/tmp/tester_recon_*.log`。claim→renew→release 租约闭环 exit 0。
- **批次进度：8 包 7 包终态独立验收齐（15_58_23 复用 PASS / 16_33_10 拒绝 PASS / 16_31_25 NOT_APPLICABLE PASS / 16_00_13 SUCCESS PASS / 14_42_48 SUCCESS PASS(复用+2×reconcile 幂等) / 16_37_47、16_58_28 NOT_APPLICABLE PASS(409 无伪切片)）；16_02_03 在途**。TEST_REPORT_PENDING 待 4acf689f SCENE_DONE 后全批收口。

### 收尾增补核销（`post-release-closeout-20261014.md` 10:49:02 + `ruling-104x-codex-binding-verify.md` 10:4x 并入卡，逐条闭环，12:3x 实测）

- **C1 绑定身份一致 → 实证**：三 submission SCHEDULED/gen1，bound source 指向各自 **flat ready 源**（source_copy id 119/121/120，路径 `ready/spray/<bag>` flat 形态，fingerprint verified，与 21:45 date-grouped 代次 id 116-118 区分）；`a65a25a7` 行 source_metadata 完整（vehicle_code=test/batch/sensor_profile）、bound_ready_path flat。
- **C2 复用不新建 → 实证**：run 全集 7、attempt 不变、无第 8 run；`eb4397c3`/`24ab78bb`/`a4824f1c` 10:23 后 backend 日志**仅本角色 reconcile 409 行，零模型请求/零新 slice 烧**（slices 树 12:3x 无新增目录）；14_42_48 复用后 FFDEE943×4 切片未产生第二份。
- **C3 outcome 一致/无伪切片 → 实证**：a4824f1c=SUCCESS（23:54:41）、eb4397c3/24ab78bb=NOT_APPLICABLE（00:01:30/00:07:46，缺 iv_* 口径与 B 21:12 一致）；NOT_APPLICABLE 两包 reconcile 各 2 次 409 INCOMPLETE + 物理无目录=无伪切片双证。
- **C4 事件/幂等 → 实证**：purpose_schedule_event id 8/9/10 CONSUMED；`a4824f1c` 两次正式 reconcile 200 后 DB 零变化；Codex 409 首载拒绝留痕在 `binding-repair.jsonl`（未写入未重试执行）。
- **C5 大包补报未改 checkpoint/未重启 → 实证**：`attempt-1/checkpoint.json` 无 10:20 后 mtime 变化（EXTRACT 产物冻结维持 jpg 1781/pcd 5373）；proxy pid **3495931 起于 2026-10-13 20:22:38 连续运行 15h53m**；八步 PRECHECK/EXTRACT=DONE、INFER=RUNNING（10:26:00）、余 QUEUED，不再称八步全排队。
- **C6 隔离分支未污染生产 → 口径**：生产栈维持 `3c9c496`（closeout 明令不改代码/不迁移部署/不提交新模型任务；本轮未见部署动作，backend/proxy 版本面未变）；Codex「c5d98d0 45 项定向测试 PASS、仅测试无业务变更、OCR NOT_EVALUATED 零调用」属 Codex 面**不重复跑、不冒称**。
- **12S-D 缺证矩阵（closeout 口径列示，不预标）**：已证=test 受控车辆真实采集链（8 包真实 SHA/真实时间戳/真实 VLM 推理/真实 NAS 发布）；缺证=①真阴性对照（有人工标签的水雾阴性样本）②真实运营车辆（`test` 非实车）③16_02_03 跨 DB3 真实边界（大包在途未终态）——**缺 topic 不当阴性结论、test 不当实车结论**，外部输入到位后另补，不用批次完成冒充全部验收完成。
- **收口判定**：本增补卡范围 7/7 核销闭合；TESTER 槽释放（本轮 claim→release 闭环）；大包终态后补 16_02_03 全链（八步/跨 DB3 真实边界/两次 reconcile）+ 全批 TEST_REPORT_PENDING（含双写事件产物一节+1205 观察项+12S-D 矩阵）。

## 17:45 取消面只读巡检（17:31-17:45 实测，消费 BATCH-STATUS 17:20 协调者 obs）

- **状态**：大包 `scene-4acf689f`（16_02_03 正式链）run 行 **SCENE_CANCELLING** attempt1，heartbeat 停 16:21:55、lease_expires 16:23:55、error 空；八步 DB 无推进（PRECHECK/EXTRACT=DONE、INFER=RUNNING 10:26:00 补报口径、PUBLISH 等 5 步 QUEUED）。
- **proxy 代次**：处理机 `scene_host_proxy` 进程 **start 2026-10-14 15:57:51**（容器 rosbag-scene-proxy Up 2h），与协调者登记的 15:57:45 kernel OOM-kill 旧代次（C obs77）时间线吻合；旧代次 pid 3495931 已不存在。新代次**未认领在途 run**：8767 health `active_runs=[]`；`.staging/scene-4acf689f…/attempt-1` 目录存在但内容空。
- **模型侧**：VLM 36.152.27.114 17:38:24-17:39:14 六点采样仍 Running 4 reqs / Waiting 7-10、POST 200 持续；proxy 进程内到 8002 连接面因 /proc 网络命名空间受限不可观测（观测盲区，不据此下结论）——**模型在出活但调用方归属未核实**，待 C/协调者下轮只读核实（候选：旧代次被 kill 前在途请求收尾 / 其他调用方），非 TESTER 处置面。
- **flat 三提交**：`a65a25a7`/`87dfebaa`/`518089ed` 维持 SCHEDULED + source 绑定（10:23:08/09 后零变化）；今晨已独立 PASS 的 14_42_48 复用产物、两次 reconcile 幂等、NOT_APPLICABLE 双包 409 无伪切片结论**不受影响**。
- **TESTER 面**：按协调者口径切换为二选一等待——收敛 SCENE_CANCELLED → 转取消终态登记（核账点：中断步 INFER/零 PUBLISH 产物/无第 8 run/无重烧模型）；回 SCENE_RUNNING → 恢复原跨夜观察口径。期间不 kill/不 retry/不重烧模型；TEST_REPORT_PENDING 维持。本轮全部动作只读（探针 `tester_172x_check.py`/`tester_173x_cancel_check*.py`，处理机 MySQL 只读 + NAS + docker + VLM 日志），未提交/未 retry/未调模型/未写生产。
- **下一步**：下轮核实 4acf689f 收敛方向与 VLM 调用方归属；16D 线不变（A 叶返修+单文件增量 OCR、B 叶 OCR 16:45 起跑在途、固定集成 SHA 联合验收待三叶接受）。