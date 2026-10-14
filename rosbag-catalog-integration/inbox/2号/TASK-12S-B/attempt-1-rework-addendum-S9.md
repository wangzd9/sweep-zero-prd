# ⚠️ SUPERSEDED（2026-10-13 14:5x 协调者 r159）：本文件与 r160 并行回合的 `attempt-1-rework-s9-dispatch.md` 主题重复，**以 r160 s9-dispatch 为唯一有效派单**（含 B ACK 路径 `attempt-1-rework-s9-ack.md` 口径）。本文件仅作事实补充参考（运行镜像/53s 包 PASS 证据、C 接线影响），不作为派单。

# 返修单补充：S9 帧映射契约（真实环境发现，纳入 attempt-1-rework）

- status: DISPATCHED（补充项，并入本任务 attempt-1-rework 同一冻结 commit，不新开 attempt 号）
- 落盘：2026-10-13 14:5x +08:00（协调者 r159，消费 `inbox/coordinator/SPRAY-1900-20261013/notice.md` + `packet-frame-mapping.md` 14:35）
- owner：B（2号）｜关联：`inbox/2号/TASK-12S-B/attempt-1-rework-dispatch.md`（16 条 S1-S8/T1-T8）

## 事实（独立环境真实解码证据，非推断）

- 14:3x 起本机已建成独立 ROS2 Humble/PCL 1.12/Open3D 0.19 软件 EGL 运行镜像（`rosbag-spray-runtime:20261013`，处理机同镜像 cross-host 验证 PASS）。
- 小包 `rosbag2_2026_10_12-15_58_23` 官方 Seyond typesupport 完整解码：`/iv_packets_front_mid` **1184 条消息，44 条 `is_last_scan=true`**；原始 packet2pointcloud 实跑 rc=0 出 **44 个 PCD**（强度有效）。
- 53s 候选包 `2026_10_08-14_42_48` 同环境实跑 rc=0、渲染 PASS、原包 sha256 不变（`evidence/local-53s-v1.json` status=PASS 14:42）。
- **当前冻结 `f62a29c` 的 `decode.py` `len(pc_ds) != len(src_msgs)` 在真实包上必成立（44≠1184）→ DECODE_FAILED：packet 路线对一切真实有效包不可用**，单测全绿遮不住此项。
- 证据：`/home/wang/work/doc/analysis/spray-runtime-install-20261013/evidence/{local-small-v1.json,local-53s-v1.log,processing-small-v1.json,cross-host-verification.json}`；`scan_ends[]` 含每帧 scan 结束 message_id + storage_ns + packet_count（首帧 message_id=4，packet_count=2）。

## S9 [HIGH·CORRECTION] packet 路线帧映射契约（decode.py，随 S3 守卫同文件）

1. **帧边界**：以 `is_last_scan` scan 结束消息为帧边界建立可追溯映射；每帧记录参与的 DB3 文件、message id 区间与选定源 storage_ns。
2. **源 ns 口径**：每帧源 storage_ns 取该帧 scan 结束消息的 storage_ns（整数 ns 直用，**不得**用 ms 文件名×1e6 伪造）；跨 DB3/乱序时按消息排序后取边界，规则写入 docstring 并有测试锚定。
3. **完整性**：跨 DB3 拼接、重复帧、缺帧、首尾不完整（首个 scan 不完整/尾部无 is_last_scan）必须拒绝并报明确 reason（沿用 DECODE_FAILED/NOT_APPLICABLE 语义），不猜测不静默丢弃。
4. **禁止**：不得只删长度断言糊过去；`len(pc_ds) != len(src_msgs)` 断言本身是错误契约，替换为上述映射校验。
5. **自测**：合成多 DB3/重复/缺帧/首尾不完整矩阵 + 真实小包 1184→44 映射断言（只读 bag，镜像 `rosbag-spray-runtime:20261013` 内 `SPRAY_DECODER_PATH=/opt/spray/bin/packet2pointcloud`）+ 53s 包映射计数申报（帧数/首末 storage_ns，不改原包）。
6. **环境**：镜像已就位（当前机器+处理机，cross-host PASS）；真实 decode/渲染从 NOT_RUN 转为**本单可实跑**，请回执列实际帧数与 reason 分布，不 mock 当 PASS。

## 边界不变

- 仍只动 `app/scene/spray/*` 与 `tests/test_spray_*`；S9 不改 pointcloud 路线语义（其映射按帧文件 1:1 已在原契约，若同环境核对发现偏差一并申报）。
- 交付口径不变：一次冻结 commit（16 条 + S9 共 17 项逐项回执），回执 `receipts/TASK-12S-B/attempt-1-rework.md` 增 S9 段。
- C 已按 `f62a29c` 固定 SHA 做 import 级集成（wt-03b-t12sc base `22ffb71`）；本返修合入后新 head 由协调者发快照更新，C 做受影响接线核验（禁正式联调 PASS 口径不变）。
- TESTER 已获同步通知（`inbox/TESTER/TASK-12S-AB/frame-mapping-contract-note.md`），12S-A/B 冻结验证继续，B 侧终验收按新 head 重快照。

## ACK 口径

- B 已在返修中（14:23 ACK 开工，wt 有未提交改动）：以本文件落盘为 S9 纳入确认，无需重复 ACK；若认为 S9 与 S1-S8 存在实现冲突或需扩边界，回执申报协调者，不单方面扩需求。