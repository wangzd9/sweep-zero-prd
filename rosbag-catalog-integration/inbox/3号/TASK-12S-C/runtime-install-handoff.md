# 环境 owner 补充交接：正式接线运行入口

2026-10-13 15:12 +08:00。本通知补充已派任务，不改变固定快照及合入门禁。协调者入口见 [runtime-ready](../../coordinator/SPRAY-1900-20261013/runtime-ready.md)。

两机器均已安装并实测通过 `rosbag-spray-runtime:20261013`；正式代理通过该 Docker 镜像执行受审代码，容器内解释器为 `/opt/spray-venv/bin/python`，宿主机 Conda 没有 Open3D。实际模型变量是 `SPRAY_VLM_ENDPOINT`，不能使用 `SPRAY_MODEL_ENDPOINT`。具体挂载、参考图、decoder 和网络要求见 [运行方法](../../../../../analysis/spray-runtime-install-20261013/runtime/README.md)。不要复制代理或重复安装依赖。

现有环境证据只覆盖真实解码、渲染和多图模型接口；业务全链仍消费 B 返修后的固定 SHA。53秒包已实测 14404 条 packet 消息对应 534 帧，第一张抽样渲染图 298956 bytes 会触发500KiB过滤；该样本可复验 S9 血缘和 S1 过滤后的有效图集合，不能绕过返修降低阈值。
