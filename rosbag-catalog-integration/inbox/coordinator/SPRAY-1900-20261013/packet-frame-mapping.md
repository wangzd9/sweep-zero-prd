# 真实环境发现：packet消息数不等于点云帧数，现实现会拒绝有效包

2026-10-13 14:35前后，本地独立ROS2/PCL/Open3D环境已完成真实小包转换/渲染。此项须纳入B当前返修，避免单测全绿但首包失败。

- 样本：`/home/wang/下载/1012/rosbag2_2026_10_12-15_58_23`，只读原包。
- topic `/iv_packets_front_mid`，`seyond/msg/SeyondScan`：1184条消息，44条`is_last_scan=true`（使用官方Seyond消息typesupport及rclpy.deserialize_message完整解码验证，不仅字节位置推断）。
- 原始packet2pointcloud实际执行rc=0，输出44个PCD；PCD含有效强度，本机软件EGL成功按原算法渲染3840×2160、旋转90度的两张JPEG，原包SHA-256一致。
- B冻结`f62a29c`的`decode.py`中`len(pc_ds) != len(src_msgs)`必成立，触发DECODE_FAILED；按全消息序号将44帧匹配1184条packet时间也不成立。
- 正确性要求：以真实scan/frame边界建立可追溯映射，明确每帧参与的DB3/message id及选定的源storage_ns；核跨DB3/重复/缺帧/首尾不完整，不能只删长度断言或用毫秒文件名乘1e6伪造纳秒。`is_last_scan`与44帧计数一致是映射调查入口，仍需核顺序、时间对应与边界，不直接宣布序号映射已通过。

完整原始证据：[local-small-v1.json](../../../../../analysis/spray-runtime-install-20261013/evidence/local-small-v1.json)。运行环境在当前机器通过后，Codex按用户指令负责传同一镜像到处理机验证；不会改业务文件。请协调者裁决后补入B返修范围，并通知C/TESTER消费新的映射契约。
