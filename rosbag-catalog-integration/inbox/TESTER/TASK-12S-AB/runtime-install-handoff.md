# 环境 owner 补充交接：真实验证环境就绪

2026-10-13 15:12 +08:00。本通知是环境证据交接，不更新已派测试快照，不把开发或环境自测写成独立验收 PASS；协调者入口见 [runtime-ready](../../coordinator/SPRAY-1900-20261013/runtime-ready.md)。

两机器 `rosbag-spray-runtime:20261013` 已完成真实解码、软件渲染与模型多图接口验证。按 [运行方法](../../../../../analysis/spray-runtime-install-20261013/runtime/README.md) 只读挂载正式候选代码及原包，输出写私有 work；宿主机 Conda 缺 Open3D，应使用 Docker。无须重复安装、重建或重复环境模型探针；需要正式业务模型验收时仍按原资源许可执行。

- 小包 1184 条 packet 消息、44 个帧结束标志、44 个 PCD；两机器抽样 JPEG 摘要一致。
- 53秒包 14404 条 packet 消息、534 个帧结束标志、534 个 PCD；实测抽样图 298956 bytes / 2224192 bytes，前者会被500KiB规则过滤，可用于 S1 与 S9 的真实返修复验。
- 两机器各一次真实8图请求 HTTP200、输出“异常”；这不是人工真值或正常/SIM分支验收。完整识别、切片、入库和恢复测试应使用协调者更新后的受审固定快照。

完整证据见 [安装报告](../../../../../analysis/spray-runtime-install-20261013/REPORT.md)。
