# TASK-11S-BATCH-1012 / TESTER / ruling-duprun-2338 增量验收 — ACK

时间：2026-10-13T23:5x+08:00，owner=TESTER。

- **固定快照**：生产业务 `3c9c496`，迁移 head `20261013_01_scene_intake`；profile `scene-spray`；接收根宿主 `/mnt/nas_backup/rosbag_scene_processing/`。
- **增量范围（按 ruling-duprun-2338 第四节 + `ruling-2338-verify.md` 指针）**：
  1. 16_02_03 按 D1 保留链 `scene-4acf689f`（flat `24d60fee` 绑定）：SCENE_DONE 后核八步/跨DB3 真实时间戳边界/两次 reconcile 幂等；SHA=源 23:0x 已 PASS 维持。
  2. A flat 四包逐包终态+产物（14_42_48 以 `a65a25a7` 绑定 run 为准，**不以 dup run 为准**/16_37_47=`87dfebaa`/16_58_28=`518089ed`/16_02_03 见上）。
  3. D2/D3 dup 面：`scene-a4824f1c` cancel 证据或自然收敛终态（SUCCESS=重复烧模型实证则核 dup 子包发布记录记双写事件产物）；`scene-eb4397c3`/`scene-24ab78bb` 收敛 NOT_APPLICABLE+无伪切片+零模型请求。
  4. D4 claim 释放：3 date-grouped submission 删除后 A flat 三提交 409 是否解除、scanner 正常绑定（与 A 台账对账）。
  5. 已 PASS 项（15_58_23 复用/16_00_13 SUCCESS/16_31_25 NOT_APPLICABLE/16_33_10 拒绝可追溯/16_02_03 SHA）维持不重复验收。
- **禁止**：提交/retry/调模型/清理生产数据；发现 A/C 越界只取证报协调者。
- **本轮 23:5x 首查（只读实测）**：`13dc398c` 已不存在于 `ingest_submission`（全集 11 行，与 A 23:0x 删除声明一致）；`scene-a4824f1c` 仍 **SCENE_RUNNING attempt2**（心跳 23:49:41、proxy `active_runs=[a4824f1c ACCEPTED]`、八步 step_run 全 QUEUED、无非心跳事件新增）——D2 cancel 端点核查/执行在 A 面，TESTER 等 A 留证后核 cancel 前后证据链；`scene-eb4397c3`(23:49:49 CLAIMED→排队)/`scene-24ab78bb`/`scene-4acf689f` 均 SCENE_SLICE_QUEUE 串行；`ready/spray/20261012/` 14,930,820,106 B 仍在（D4 NAS 删除待 dup 全终态+submission 删后执行）；空包 `7a71e404` 维持 PENDING_INPUT 拒绝闭环。
- 回执：`test-receipts/TASK-11S-BATCH-1012/attempt-1.md`（追加 23:5x 段）。全批 8 包齐后交付 TEST_REPORT_PENDING。
