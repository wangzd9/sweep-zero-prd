# S9b 独立机械验证（Codex 委派）

- 结论：**PASS；交主协调者裁决，不代表审查或生产门禁通过。**
- 时间：2026-10-13 18:31–18:33 +08:00。
- 固定代码：`/home/wang/.local/state/rosbag-scene/wt-04a-t12sb`，前后 HEAD 均 `f76e2a9b403577b791ca3688e0da5e574c4c272a`；tracked 工作区干净，仅已有未跟踪 `.venv`。
- 镜像不可变身份：`sha256:e3fe73534ad85e1419c84421ccfce22f00747499acd3b6be88bae5929dffbaef`。本机 Docker、2CPU/6GiB、UID1000、`--network none`，代码与原包只读挂载，产物独立新目录。
- 原包：`/home/wang/下载/1012/rosbag2_2026_10_12-15_58_23`。

## 真实解码与独立映射

探针使用实际 ROS2 `rclpy.serialization.deserialize_message` + `seyond.msg.SeyondScan` 独立解析消息；不调用被测模块的 CDR 帧边界函数来生成预期值。随后调用被测 `decode_packet_route` 与真实 `/opt/spray/bin/packet2pointcloud`。

- 实测 **1184 消息 → 44 is_last_scan 边界 → 44 非空真实 PCD**。
- 所有44帧的 `storage_ns` 与结束消息整数纳秒完全相等，保留非毫秒精度。
- 所有44帧的首/末 DB3、message_id、packet_count、scan_timestamp_f64 与独立 ROS2 反序列化结果逐项一致。
- 最后一完整边界后20条消息按残缺尾部留 `tail_truncated.json`，未冒充帧。
- 原包所有顶层文件 SHA256 前后一致。
- 真实解码耗时 **0.602 秒**；Docker命令 rc=0。

证据：

- 探针：`/home/wang/work/.local/spray-runtime/s9-independent-f76e2a9.py`
- 完整预期/实际映射及前后SHA：`/home/wang/work/.local/spray-runtime/work/s9-independent-f76e2a9/result.json`
- 命令输出：同目录 `docker.log`。

## 定向用例

在同一固定B工作树执行：

`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q tests/test_spray_adapter.py::TestPacketDecode`

结果 **8 passed，0 skipped，0 failed，0.48秒，rc=0**。覆盖子进程不可用/非零、PCD数与scan不一致、scan对齐、无边界拒绝、尾部残缺、跨DB3血缘以及真实小包锚定。日志同证据目录 `unit.log`。

跨DB3单元中的decoder为可控替身；本次真实包只有单DB3，不把该用例冒充真实跨库SDK拼接验证。未运行模型、渲染、全仓或生产写入。未修改业务实现/原包/既有测试，Docker `--rm` 无常驻容器；保留独立验证产物供复核。
