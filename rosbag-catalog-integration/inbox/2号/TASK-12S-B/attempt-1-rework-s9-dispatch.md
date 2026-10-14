# 派单补充：TASK-12S-B attempt-1-rework 追加 S9（真实环境新缺陷，返修面并入）

- status: DISPATCHED
- 派单时间：2026-10-13 14:4x +08:00（协调者，补进 B 正在执行的 r158 返修，不新开 attempt）
- 任务：在 attempt-1-rework（S1-S8+T1-T8）的同一返修冻结里追加修复 **S9**，随 16 条一起交付，不单独成轮。

## S9 [HIGH·CORRECTION] decode.py：packet 消息数 ≠ 点云帧数，现实现拒绝有效包

### 真实环境证据（14:35 前本地独立 ROS2/PCL/Open3D 环境实跑，非推测）
- 样本：`/home/wang/下载/1012/rosbag2_2026_10_12-15_58_23`（只读原包）
- topic `/iv_packets_front_mid`，`seyond/msg/SeyondScan`：**1184 条消息，仅 44 条 `is_last_scan=true`**
- 原始 packet2pointcloud 实际执行 **rc=0，输出 44 个 PCD**；PCD 含有效强度；本机软件 EGL 按原样渲染成功
- 冻结 `f62a29c` 的 `decode.py` 中 **`len(pc_ds) != len(src_msgs)` 对此真实包必成立 → 触发 DECODE_FAILED，拒绝一个完全有效的包**
- 完整原始证据：`/home/wang/work/doc/analysis/spray-runtime-install-20261013/evidence/local-small-v1.json`；规划侧发现全文：`inbox/coordinator/SPRAY-1900-20261013/packet-frame-mapping.md`

### 修复要求
1. **以真实 scan/frame 边界建立可追溯映射**：PCD 帧与参与它的 DB3 message id 一一对应（44 帧 ↔ 1184 消息的分组），映射关系写入渲染/判定日志面（`SPRAY_RENDER_LOG` 或等价物），不得只留内存
2. 解码成功判据从"消息数==帧数"改为"每个 is_last_scan 边界产出 1 帧 PCD"；**缺帧/多余帧才是 DECODE_FAILED**，并给出缺哪些边界的证据
3. packet 路线与 pointcloud 路线的帧对齐口径一致化（pointcloud 路线按消息=帧的前提在本样本下不成立时同样要有映射证据，不得静默 1:1 假设）
4. 回归测试：用 `local-small-v1.json` 中的真实 44/1184 结构构造 fixture（真实边界序列，非自造数字），断言 44 帧全产出、映射表完整、缺 1 帧即 FAILED

### 边界（与 r158 一致，重申）
- 只动 `app/scene/spray/*` + `tests/test_spray_*`；base `f62a29c` 续 commit，不移动冻结审查头
- **禁改**采样策略/参考图/质量阈值/`scene_capabilities.yaml` 坡道面；S9 是解码映射正确性，不是识别口径
- 停止条件不变：17 条（16+S9）各带回归 + spray 定向全绿 + ruff 绿 + 零越界，冻结 head 后交协调者增量 OCR（范围仍 `f62a29c..head`，S9 并入同一增量）

### 回执
ACK 写 `inbox/2号/TASK-12S-B/attempt-1-rework-s9-ack.md`（接受/有异议+理由），交付沿用 `receipts/TASK-12S-B/attempt-1-rework.md` 更新。