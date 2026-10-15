# TASK-12S-D1 包外样本清单 attempt-1（执行者C，2026-10-14 20:40 +08:00）

机器可读样本表。人工标注在包外：真值区间由业务/算法 owner 书面提供后填入，标注来源列必填；当前全部为「无」。模型 outcome 不是真值（派单口径）。

```yaml
batch: spray-production-1012-20261013
environment: production
vehicle_code: test            # 用户指定受控车；真实采集车映射缺证
profile: scene-spray
sensor_profile: seyond-front-mid-approved-v1
timezone: Asia/Shanghai
license: 10-13 批次用户授权材料；本轮只读，D2 重跑需当次另行授权
budget:
  scene_exec_host: 1          # 场景串行单执行机
  vlm: 远端 LLM max_num_seqs=4（192.168.2.45:8002 隧道）
  a100_free_bytes: 260851949568   # 4acf PRECHECK checkpoint 证据
  nas_free: 约29%（处理机 /mnt/nas_backup 71% 已用口径，C obs75）
samples:
  - bag: rosbag2_2026_10_12-15_58_23
    bytes: 57689621
    db3_order: ["_0"]
    duration_s: 4.38
    valid_spray_input: true
    expected_case: 阳性（受控 test）+ 短包探针
    case_status: READY_PROVEN      # attempt2 SCENE_DONE SUCCESS，TESTER 独立核对 PASS
    truth_interval: 无（BLOCKED_MATERIAL，待业务人工标注 storage ns 区间+来源）
    window_constraint: 4.38s < 15s 分析窗口，完整窗口质量证据缺
    parent_child: child 16Bc-51ac3e1fa53dbdd6b2 继承 test 车辆已证
  - bag: rosbag2_2026_10_12-16_00_13
    bytes: 89664966
    db3_order: ["_0"]
    duration_s: 4.75
    valid_spray_input: true
    expected_case: 阳性（受控 test）
    case_status: READY_PROVEN      # scene-604c0896 SUCCESS 10-13 21:43
    truth_interval: 无（BLOCKED_MATERIAL）
    window_constraint: 短包，完整窗口质量证据缺
    parent_child: 切片 051768B1_16Bc-4654d41f86d36f5c4b 在位（NAS 顶层实测）
  - bag: rosbag2_2026_10_08-14_42_48
    bytes: 724637738
    db3_order: ["_0"]
    duration_s: 53.4
    valid_spray_input: true
    expected_case: 阳性（受控 test）+ 双写幂等回归
    case_status: READY_PROVEN      # scene-a4824f1c attempt2 SUCCESS 10-13 23:54（自然收敛，重复烧模型实证）
    truth_interval: 无（BLOCKED_MATERIAL）
    window_constraint: 53.4s > 15s 窗口，可作完整窗口样本（缺真值）
    parent_child: FFDEE943×4 顶层切片=双写事件产物，ruling-0038 保留现场，正式 reconcile 核账并入面
  - bag: rosbag2_2026_10_12-16_02_03
    bytes: 10105917670
    db3_order: ["_0", "_1"]
    duration_s: 537.2
    valid_spray_input: true
    expected_case: 跨 DB3 阳性候选 + 大包取消链取证
    case_status: BLOCKED            # scene-4acf689f 10-14 17:14:25 INFER=CANCELLED，无已发布切片
    truth_interval: 无（BLOCKED_MATERIAL）
    window_constraint: 满足（537s）
    cross_db3: DB3 边界消息时间未定位；取消链/产物完整性归 TESTER 大包验收面（ruling-1840 口径），C 不重复
  - bag: rosbag2_2026_10_12-16_31_25
    bytes: 25184760
    db3_order: ["_0"]
    duration_s: 3.58
    valid_spray_input: false        # 无 /iv_packets_front_mid（rear 亦缺）
    expected_case: 输入适用性（NOT_APPLICABLE）
    case_status: READY_PROVEN      # scene-bc8c1d1c NOT_APPLICABLE 零模型零伪切片
    truth_interval: 不适用
    note: 按派单口径不能算正常阴性
  - bag: rosbag2_2026_10_12-16_33_10
    bytes: 0
    db3_order: []
    duration_s: null
    valid_spray_input: null
    expected_case: 无效输入
    case_status: READY_PROVEN_REJECT   # scanner missing rosbag2_bagfile_information 拒绝可追溯（TESTER 已核）
    truth_interval: 不适用
    note: submission 恒 PENDING_INPUT 无提交层终态=12S-F INPUT_REJECTED 修复对象
  - bag: rosbag2_2026_10_12-16_37_47
    bytes: 7321525005
    db3_order: ["_0", "_1"]
    duration_s: 1049.0
    valid_spray_input: false
    expected_case: 输入适用性（NOT_APPLICABLE，多 DB3 非水雾）
    case_status: READY_PROVEN      # scene-eb4397c3 attempt2 NOT_APPLICABLE 零模型零伪切片
    truth_interval: 不适用
    note: 不能替代跨 DB3 阳性用例
  - bag: rosbag2_2026_10_12-16_58_28
    bytes: 6794992397
    db3_order: ["_0", "_1"]
    duration_s: 1048.6
    valid_spray_input: false
    expected_case: 输入适用性（NOT_APPLICABLE，多 DB3 非水雾）
    case_status: READY_PROVEN      # scene-24ab78bb attempt2 NOT_APPLICABLE 零模型零伪切片
    truth_interval: 不适用
gaps:
  - item: 输入有效真实正常阴性（含水雾 topic、内容无水雾）
    status: BLOCKED_MATERIAL
    owner: 上游采集/算法提供
  - item: 业务人工真值区间（storage ns+标注来源，全部样本）
    status: BLOCKED_MATERIAL
    owner: 业务/算法 owner 书面确认
  - item: 业务质量接受阈值及适用范围
    status: BLOCKED_MATERIAL      # 无书面数值在案，待确认，不编造
    owner: 业务/算法 owner
  - item: 真实采集车辆映射（非 test）+父/子继承实车实证
    status: BLOCKED_MATERIAL
    owner: 上游/用户指定
  - item: 跨 DB3 阳性命中与顺序验证
    status: BLOCKED               # 唯一候选取消终态；需 D2 当次授权重跑或上游另提供跨边界包
    owner: TESTER D2 + 协调者授权
```