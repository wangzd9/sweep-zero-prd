# TASK-11S-BATCH-1012 / B 输入适用性回执 裁决（协调者）

- 时间：2026-10-13T21:17 +08:00（夜间静默，不群报）
- 对象：`inbox/2号/TASK-11S-BATCH-1012/attempt-1-ack.md` + `receipts/TASK-11S-BATCH-1012/b-attempt-1.md`（B 21:12:47，DONE，只读取证零提交零模型）
- 事件源：`events/B/5648ff243ad508d5a8049465717c44ee3c20ab0522213f306186ce3990eabeed.json`

## 裁决

1. **接受 B 回执为独立输入证据**：逐包消息数/时长与 `input-manifest.json` 全一致（39711/2325/2595/410669/734/0/218570/218488），method 为 stdlib sqlite3 `mode=ro` 只读直查，符合派单边界；零越界申报核实无误。
2. **manifest 分类更正（已执行）**：`rosbag2_2026_10_12-16_31_25` / `16_37_47` / `16_58_28` 三包 `initial_classification` 由 `NEEDS_RUNTIME_RESULT` 更正为 `NOT_APPLICABLE`（附 classification_note 注明更正时间与依据）。理由：三包均无前雷达 `/iv_packets_front_mid` 也无 `sensor_msgs/msg/PointCloud2`，按适配契约路由阶段即定性 NOT_APPLICABLE，不进解码/模型/分段；16_37_47 / 16_58_28 的 manifest 自身 topic 列表亦未列 iv_*，与实测一致。
3. **NOT_APPLICABLE 三包的处理路径（约束 A/TESTER）**：仍须完整拷贝落位 + 正式 metadata 提交（输入真实、字节真实），预期终态 NOT_APPLICABLE / NO_MATCH、无伪切片、零模型请求；不得跳过上传直接标 NOT_APPLICABLE。TESTER 验收口径=路由拒绝可追溯 + 无产物。
4. **INVALID_EMPTY_INPUT `16_33_10`**：维持计划——按真实输入走入口，预期输入校验拒绝/隔离可追溯；B 实测 metadata+DB3 均 0 字节与 manifest 一致。A 上传该包仅为验证拒绝路径，不补造内容。
5. **跨 DB3 边界证据入账**：16_02_03 双 DB3 时间戳正向衔接（gap 4.73µs，包内逆序 0），供 A 提交与 TESTER 血缘/多 DB3 独立取证引用；全批 water-spray 输入仅 packet 路线，无 PCD 路线命中——本批不存在 pointcloud 适用分支。
6. **B 无返修**：B 本单范围（只读输入证据）已完整交付，**不派具体返修单**；其"待协调者裁决"事项由本文件关闭。B 转空闲，等下一候选。
7. **门禁不变**：本批无代码变更，不起 OCR/强审；生产固定 `3c9c496`。

## 影响

- BATCH-STATUS 逐包分类列与角色占用已同步更新（B=DONE 21:12）。
- A 为唯一上传/提交 owner：其原生 execution `e6d1bfddebe9425385d46e2c051752ac`（pid 2491657，21:04:53 起）在途，租约 `inbox/control/runtime/leases/A.json`（owner `A-batch-1012`，21:10:42 claim，21:35 到期）；**不催、不接管、不重开同角色会话**，等其 ACK/短包落位证据。