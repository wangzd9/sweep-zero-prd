# TASK-11S-BATCH-1012 / TESTER / 增量验收指针 — ruling-duprun-2338

状态：DISPATCHED，owner=TESTER，2026-10-13T23:38+08:00。裁决全文 `inbox/coordinator/SPRAY-BATCH-1012-20261013/ruling-duprun-2338.md`（含 23:5x 增补节）第五节 TESTER 增量范围；BATCH-STATUS 已同步。

增量范围（替代 223x 轮「③④ 等 A 提交」口径，按 D 项更新）：

1. **16_02_03（D1 保留链）**：run `scene-4acf689f`（flat `24d60fee` 绑定）SCENE_DONE 后核八步/跨 DB3 真实时间戳边界/两次 reconcile 幂等；SHA=源你 23:0x 已 PASS 维持。
2. **A flat 四包逐包终态**：14_42_48=`a65a25a7` 绑定 run（NEEDS_RUNTIME_RESULT 全链验收，**不以 dup run 为准**）/ 16_37_47=`87dfebaa` / 16_58_28=`518089ed` / 16_02_03 见上；每包产物 uid/消息/车 test/时间/AVAILABLE/current。
3. **D2/D3 dup 面**：`scene-a4824f1c` attempt-2 cancel 证据（cancel 前状态/事件链/slices 计数 + cancel 后终态+资源释放）或自然收敛终态（若 SUCCESS=重复烧模型实证，核 dup 子包发布记录并如实记双写事件产物）；`scene-eb4397c3`/`scene-24ab78bb` attempt-2 收敛 NOT_APPLICABLE + 无伪切片 + 零模型请求。
4. **D4 claim 释放**：3 date-grouped submission 删除后 A flat 三提交 409 是否解除、scanner 正常绑定（与 A 台账对账）。
5. 已 PASS 项（15_58_23 复用/16_00_13 SUCCESS/16_31_25 NOT_APPLICABLE/16_33_10 拒绝可追溯/16_02_03 SHA）维持，不重复验收。

禁止：提交/retry/调模型/清理生产数据；发现 A/C 动作越界只取证报协调者。全批 8 包齐后 TEST_REPORT_PENDING 交协调者，回执 `test-receipts/TASK-11S-BATCH-1012/attempt-1.md`。

## 00:0x 增补（协调者 2026-10-14，消费 C obs12 23:59）

- **第 3 项 D2 分支已定**：`scene-a4824f1c` attempt-2 **23:54:41 自然收敛 SCENE_DONE SUCCESS**（C 实测，cancel 分支作废）。你的动作=核 dup 子包发布记录+`.staging/scene-a4824f1c…` 第二份切片产物**保留现场取证**，如实记双写事件产物（不删不并）；SCENE_EXEC_HOST 已释放（23:54:41 RESOURCE_RELEASED）。
- **`scene-eb4397c3`（16_37_47 dup）23:58 已 SCENE_RUNNING**（心跳 30s 节奏在案），预期 NOT_APPLICABLE 快速拒绝，收敛后核无伪切片+零模型；`scene-24ab78bb` 排队中同口径。
- **D5 归因（供取证参考，不扩你的范围）**：22:53:02 三 RETRY=开发机 192.168.2.132 外部人工 /retry API 三发（retry3.sh+bind_vehicle.sh 自称『运营授权』），肇事身份待用户核实；`bag_record` 三包 vehicle_id=1 MANUAL 为外部操作产物。
- 其余增量范围（第 1/2/4/5 项）不变。

## 00:39 增补（协调者 2026-10-14，dup 切片处置裁决落地）

- 你 00:24 报「dup FFDEE943 4 子包处置仍等协调者裁决」已裁决：`ruling-dup-slices-0038.md`（本目录同级 `SPRAY-BATCH-1012-20261013/`）。**不删不并不新开清理任务**；正式 `a65a25a7` run 终态后，把发布幂等对已存在同名 source 切片的处置并入两次 reconcile 核账口径，如实记录不预判；TEST_REPORT 设「双写事件产物」一节登记（run 归属/发布时间 23:54/来源已删 submission/与正式链 source 同源性/reconcile 处置证据），不计入验收交付物。
- 你 00:33 独立复核 D4 删除面闭合口径协调者已确认并入 BATCH-STATUS；`scene-4acf689f` 八步 attempt1 全 QUEUED、dispatched 后 ~25min 静默段未判卡死，下轮继续核 EXTRACT 推进（跨 DB3 10GB 大包前置段，不超窗 kill/retry）。
- 无新派单；BATCH-STATUS 已同步 00:39 口径。