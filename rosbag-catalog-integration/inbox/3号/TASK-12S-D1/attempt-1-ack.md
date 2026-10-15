# TASK-12S-D1 资料与固定验收清单 attempt-1 — ACK（执行者C）

状态：ACKED，owner=C（执行者3号），2026-10-14 20:33 +08:00（occurred=now）。

- 派单路径：`inbox/3号/TASK-12S-D1/attempt-1-dispatch.md`（协调者 2026-10-14 20:2x +08:00，PENDING 待 ACK，V04_CLOSEOUT 已解除；父 TASK-12S，REQ-22/AC-22，细化 REQ-09/17/18/19）
- task/attempt：TASK-12S-D1 / attempt-1 / owner=C
- base：本单为纯资料/fixture/清单面，**零代码改动，无开发分支/worktree**（不适用代码 base）；生产业务代码只读观测基准 `3c9c496`（main 集成候选 `16a154f` 已收口，均非本单交付面）
- 恢复核实：C 上一任务 TASK-16C-C attempt-1+CC-R1 返修已 DELIVERED_REVIEW_PENDING 并入协调者集成候选 `1d7f15c` 并随父16合入 main `16a154f`（TODO §8.5 2026-10-14 20:05 DONE 口径），槽已释放；16B/11S-BATCH 收尾面已收口（C 侧 obs 交付在案）。本 ACK 为 D1 新单领取，无重复领取
- 可用资料源（已核实在案，本 ACK 时刻只读取证完成）：
  1. 生产 1012 批 manifest：`inbox/coordinator/SPRAY-BATCH-1012-20261013/input-manifest.json`（8 包 25119612157 B，逐包文件/DB3 顺序/topic/消息数/metadata SHA/vehicle_code=test/profile=scene-spray/timezone=Asia/Shanghai）
  2. 批次唯一状态表：`inbox/coordinator/SPRAY-BATCH-1012-20261013/BATCH-STATUS.md`（逐包终态、裁决链、双写现场、16_02_03 取消链 17:14:25）
  3. 受控首包独立验收：`reviews/TASK-11S/production-first-bag-20261013.md`（15_58_23 attempt2 SCENE_DONE SUCCESS、child `16Bc-51ac3e1fa53dbdd6b2` 继承 test 车辆、两次 reconcile 幂等）
  4. 12S-D 缺口清单（B 交付）：`receipts/TASK-11S-BATCH-1012/b-attempt-1.md` §6.2（真阴性/真实车辆/跨DB3/批量容量缺证分列）
  5. 本 ACK 时刻生产只读实测（处理机 `127.0.0.1:18000`，`/health/ready` environment=production）：7 个 scene run 终态/步骤、source→bag 绑定（7 包全 READY/vehicle 字段空=绑定经 source_metadata 链）、`scene-4acf689f` checkpoint（INFER=CANCELLED、无已发布切片）、NAS `slices/test/spray/` 顶层 6 切片目录（FFDEE943×4 双写现场 + 两正式）
- 真值来源：**业务人工真值区间尚不存在**——上游未提供任何水雾阳性/正常区间的人工标注（storage ns 区间+标注来源均缺），模型 outcome 按派单口径不能当真值；该项记 BLOCKED_MATERIAL 不编造
- 许可与资源预算口径：SCENE_EXEC_HOST=1 场景串行；VLM 远端 LLM 服务器 max_num_seqs=4；A100 数据盘余量 260851949568 B（4acf PRECHECK 证据实测）；NAS ~29% 余量（C obs75 71% 已用口径）；1012 批 8 包 ~23.4GB 为已有受控材料，本轮**只读不新拷贝/不新提交/不重烧模型/不重启在途批次**
- 下一步：按派单产出 `receipts/TASK-12S-D1/attempt-1.md`（逐包清单，可部分交付已齐用例）+ 包外样本清单，缺项标 BLOCKED_MATERIAL/BLOCKED_RESOURCE，不阻塞 12S-E/F