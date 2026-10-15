# TASK-12S-D1 资料与固定验收清单 attempt-1 回执（执行者C）

状态：REVIEW_PENDING（部分交付：清单骨架与已证用例齐；关键真值/阴性/跨DB3/实车项缺材料，逐项标 BLOCKED，不阻塞 12S-E/F）
- owner=C；task/attempt=TASK-12S-D1 / attempt-1；派单 `inbox/3号/TASK-12S-D1/attempt-1-dispatch.md`（2026-10-14 20:2x）
- 交付时间：2026-10-14 20:40 +08:00（occurred=now）
- base/head：**零代码改动、无分支/worktree**（纯资料/fixture/清单面）；生产业务代码只读观测基准 `3c9c496`
- 环境：处理机 `127.0.0.1:18000`（`/health/ready` 实测 environment=production）、NAS `/mnt/nas_backup/rosbag_scene_processing`、本地文档共享根
- 命令与证据：生产只读取证全部经 ssh 处理机 curl/python 实测（本回执 §5 证据入口）；未执行任何提交/重试/取消/迁移/模型调用/生产写入

## 1. 用例覆盖结论（按派单 AC 逐条）

| 派单要求 | 结论 | 依据 |
|---|---|---|
| ≥1 输入有效已知水雾阳性 | **已齐（受控 test 口径）** | `rosbag2_2026_10_12-15_58_23`：正式 normal retry attempt2 SCENE_DONE SUCCESS（10-13 20:24 实测收口），1 切片 1752 消息/12 topics，原包 SHA 前后不变，TESTER 独立核对 PASS（production-first-bag-20261013.md） |
| ≥1 输入有效真实正常阴性（含水雾 topic、内容无水雾） | **BLOCKED_MATERIAL** | 本批 8 包与既有素材均无「有 `/iv_packets_front_mid` 但内容无水雾」的包（B §6.2 实测定性）；三个 NOT_APPLICABLE 包缺雷达 topic，只算**输入适用性用例**，按派单口径不能算正常阴性 |
| ≥1 目标区间跨两个 DB3 边界的真实多 DB3 包 | **BLOCKED（取消终态，跨边界未证）** | 候选 `rosbag2_2026_10_12-16_02_03`（双 DB3 5.37G+4.74G、537.2s）run `scene-4acf689f` 10-14 17:14:25 取消链收口 INFER=CANCELLED、无已发布切片（checkpoint 实测）；DB3 边界位置未定位、跨边界命中/顺序均未证。1012 不能凭文件数/包名认定跨边界（派单明示） |
| 质量样本符合 15s 窗口/抽样与有效帧约束 | **缺证** | 首包 15_58_23 duration 4.38s、604c0896 4.75s，均短于冻结 15s 分析窗口，只能作短包探针；本批无完整窗口质量证据 |
| ≥1 辆真实车辆父/子继承完整实证 | **PARTIAL（test 车已证，实车缺）** | test 车：child `16Bc-51ac3e1fa53dbdd6b2` 继承 test 车辆绑定、血缘可读、两次 reconcile 幂等（首包验收实测）；**真实采集车=0 辆**，全批 vehicle_code=test 用户指定受控车，MANUAL×3 绑定非自动匹配（B §6.2）→ 实车项 BLOCKED_MATERIAL |
| ≥1 输入适用性（NOT_APPLICABLE）用例 | **已齐 ×3** | `16_31_25`/`16_37_47`/`16_58_28`：缺 `/iv_packets_front_mid` 路由 NOT_APPLICABLE，SCENE_DONE 零模型零伪切片（run 终态实测 + B 只读取证） |
| ≥1 无效输入用例 | **已齐（提交层终态缺）** | `16_33_10` 0B 空包：scanner 拒绝可追溯（TESTER 已核）；submission 层恒 PENDING_INPUT 无提交层终态=12S-F 修复对象，按原状态记录 |
| 业务人工真值区间（storage ns+标注来源） | **BLOCKED_MATERIAL** | 上游未提供任何人工标注；模型 outcome（SUCCESS/NOT_APPLICABLE）按派单口径不能当真值；**不编造准确率** |
| 业务质量接受阈值 | **待业务/算法 owner 书面确认** | 无任何数值在案，记录为待确认项 |
| 冻结有限批次清单 | **已冻结（§4）** | 复用 1012 批 8 包 ~23.4GB 受控材料，只读；不新拷贝/不新提交/不重烧模型 |

## 2. 逐包清单（1012 批 8 包，25119612157 B，vehicle_code=test，profile=scene-spray，timezone=Asia/Shanghai）

来源：`input-manifest.json`（协调者 10-13 冻结）+ 本回执时刻生产只读实测。

1. **rosbag2_2026_10_12-15_58_23**｜57,689,621 B｜DB3×1 顺序 `_0`｜topic：`/iv_packets_front_mid` 1184 + rear_mid 307、cam/label/perception 全套｜duration 4.38s/2325 消息｜metadata sha `5a3cb296…b0064`｜绑定：复用 submission `9949d1a7`/run `scene-c4a88c07` attempt2（REUSE_READY_SHA_MATCH 台账在案）｜**outcome=SUCCESS**（2026-10-13 20:24 SCENE_DONE，八步全 DONE）｜切片 `16Bc-51ac3e1fa53dbdd6b2` AVAILABLE/current、1752 消息、继承 test 车辆｜真值区间=**无（BLOCKED_MATERIAL）**｜用例=阳性（受控 test）+短包探针
2. **rosbag2_2026_10_12-16_00_13**｜89,664,966 B｜DB3×1｜front_mid 1262/rear_mid 330｜duration 4.75s/2595 消息｜sha `68032a41…c79`｜正式 `99615748`/run `scene-604c0896` attempt1｜**outcome=SUCCESS**（10-13 21:43）｜切片 `051768B1_16Bc-4654d41f86d36f5c4b`（NAS 顶层实测在位）｜真值区间=无｜用例=阳性（受控 test）
3. **rosbag2_2026_10_08-14_42_48**｜724,637,738 B｜DB3×1｜front_mid 14404/rear_mid 3732、含 localization/estimate_pose｜duration 53.4s/39711 消息｜sha `a5bd2d90…46dc`｜正式 `a65a25a7`（Codex 10-23 重登记恢复 SCHEDULED gen1，绑定复用 run `scene-a4824f1c`）｜**outcome=SUCCESS**（attempt2 10-13 23:54 自然收敛）｜切片：`FFDEE943×4` 顶层目录中**双写事件产物 4 份**（ruling-dup-slices-0038 保留现场，正式 reconcile 核账并入面）｜真值区间=无｜用例=阳性（受控 test，53s 近完整窗口但无真值）+双写幂等回归
4. **rosbag2_2026_10_12-16_02_03**｜10,105,917,670 B｜**DB3×2** 顺序 `_0`(5.37G)/`_1`(4.74G)｜front_mid 144971/rear_mid 37607、全 topic｜duration 537.2s/410669 消息｜sha `e40a8d86…67ce`｜正式 `24d60fee` SCHEDULED 绑定 source `91FFEEC1`/run `scene-4acf689f`｜**outcome=取消终态**：10-14 17:14:25 INFER=CANCELLED（decoder 收取消信号，409×2 确认；15:57:45 OOM-kill 后断链，ruling-4acf-stuck-cancelling-1840 三方一致）、checkpoint 实测 INFER FAILED/PUBLISH+REGISTER+VALIDATE+WRITE PENDING、**无已发布切片**（slices 顶层无 4acf689f 目录）｜真值区间=无｜用例=**跨 DB3 候选（未证）**+大包取消链取证；DB3 边界消息时间未定位，BLOCKED（取消链/产物完整性归 TESTER 大包验收面，C 不重复）
5. **rosbag2_2026_10_12-16_31_25**｜25,184,760 B｜DB3×1｜**无 iv_packets_***（front/rear 均缺）｜duration 3.58s/734 消息｜sha `fcc5ff25…dda`｜`e5649055`/run `scene-bc8c1d1c`｜**outcome=NOT_APPLICABLE**（10-13 21:43，零模型零伪切片，slices 顶层无 bc8c1d1c 目录实测）｜用例=输入适用性（**不算正常阴性**）
6. **rosbag2_2026_10_12-16_33_10**｜**0 B**（metadata+db3 均 0B，sha `e3b0c442…`=空文件指纹）｜scanner `missing rosbag2_bagfile_information` 持续拒绝可追溯（TESTER 已核）｜submission `7a71e404` 恒 PENDING_INPUT 无提交层终态（12S-F INPUT_REJECTED 修复对象）｜用例=无效输入
7. **rosbag2_2026_10_12-16_37_47**｜7,321,525,005 B｜**DB3×2**｜无 iv_packets_*（manifest topic 表亦无）｜duration 1049.0s/218570 消息｜sha `fdbec007…88b`｜正式 `87dfebaa`/run `scene-eb4397c3` attempt2｜**outcome=NOT_APPLICABLE**（10-14 00:01 零模型零伪切片）｜用例=输入适用性（多 DB3 但无水雾输入，**不能替代跨 DB3 阳性用例**）
8. **rosbag2_2026_10_12-16_58_28**｜6,794,992,397 B｜**DB3×2**｜无 iv_packets_*｜duration 1048.6s/218488 消息｜sha `935220dc…219ae`｜正式 `518089ed`/run `scene-24ab78bb` attempt2｜**outcome=NOT_APPLICABLE**（零模型零伪切片）｜用例=输入适用性

车辆映射：8 包 source 绑定 vehicle_id=1（vehicle_code=test，用户指定受控车）；vehicle_link_status 快照 MATCHED×4（15_58_23/16_00_13/16_02_03/16_31_25）、MANUAL×3（14_42_48/16_37_47/16_58_28，10-23 正式源登记恢复链产物，非自动匹配）、空包 1 无绑定——**真实采集车辆映射=缺**（BLOCKED_MATERIAL）。

## 3. 包外样本清单

见独立文件 `receipts/TASK-12S-D1/attempt-1-samples.md`（机器可读样本表：预期用例/可用性/真值状态/许可/预算归属）。人工标注在包外，本清单不以任何模型输出充当真值。

## 4. 冻结有限批次清单（供 D2 复用，只读）

- 批次：`spray-production-1012-20261013`，8 包 25,119,612,157 B（~23.4GB），生产 NAS incoming/spray 已落位（A 23:0x-00:2x 台账全闭环，date-grouped 污染已清、flat 4/4 SHA MATCH）
- 用途构成：阳性×4（含 1 双写幂等回归）、输入适用性×3、无效输入×1、跨 DB3 候选×1（取消终态未证）、多 DB3 非水雾×2（7/8 号）
- 并发预算：SCENE_EXEC_HOST=1（场景串行单执行机）；VLM 远端 LLM 服务器 max_num_seqs=4（隧道 192.168.2.45:8002）
- 资源余量（本回执时刻证据）：A100 数据盘 free 260,851,949,568 B（4acf PRECHECK checkpoint 证据）；NAS 处理机挂载 ~71% 已用（C obs75 口径，71%/29% 余量）
- 许可：现有受控 test 批用户已授权材料（10-13 批次授权链在案）；**本轮零新拷贝/零新提交/零模型调用/零生产写入**；D2 重跑须另行当次授权（不重烧 4acf 大包、不重启在途批次）
- 覆盖 E/F 修复面：空包（F INPUT_REJECTED）、双写/复用幂等（E 重登记绑定）、取消链滞留（缺陷候选入 16R 盘点口径）

## 5. 证据入口

- manifest/状态表：`inbox/coordinator/SPRAY-BATCH-1012-20261013/{input-manifest.json,BATCH-STATUS.md}`
- 首包独立验收：`reviews/TASK-11S/production-first-bag-20261013.md` + `/home/wang/work/.local/spray-runtime/production-first-bag-3c9c496-verified.json`
- 缺口矩阵（B）：`receipts/TASK-11S-BATCH-1012/b-attempt-1.md` §6.2
- 本回执时刻生产实测：scene run 终态/步骤表（`/tmp/d1_scene_details.json` 处理机侧）、source→bag 映射（`/tmp/d1_srcmap.json`）、4acf checkpoint（`/home/data-process/scene/work/scene-4acf689f…/attempt-1/checkpoint.json`）、NAS slices 顶层目录 listing
- 样本表：`receipts/TASK-12S-D1/attempt-1-samples.md`

## 6. 未执行项 / 越界申报

- 未执行：向用户/上游发消息索取资料（派单禁止）；拷贝生产包；重跑/取消/重启任何 run；写 TODO/HANDOFF/decision；OCR/强审
- 越界：**无**。全部动作=只读取证 + 本角色 receipts/ACK/sessions 写入
- 缺口处置：真值/阴性/跨DB3/实车/阈值五项缺材料，按 BLOCKED_MATERIAL 记录在案，**不编造准确率、不把「有子包」定为质量通过**；任一材料补齐即重算对应用例（派单允许部分交付）