# 环境 owner 补充交接：部署模板装配勘误

2026-10-13 15:12 +08:00。本通知补充已派任务的环境事实，不修改派单、owner、TODO 或发布授权；协调者汇总入口为 [runtime-ready](../../coordinator/SPRAY-1900-20261013/runtime-ready.md)。

- 当前机器及处理机均已安装 `rosbag-spray-runtime:20261013`，真实解码、软件渲染、7参考图加真实点云图的模型请求通过。不要重复安装或重跑模型探针。
- `/opt/spray-venv/bin/python` 和 `/opt/spray/bin/packet2pointcloud` 都是容器内路径，宿主机现有 Conda 未安装 Open3D。正式服务模板应通过 Docker 运行受审代理；将业务代码只读挂载，业务 SHA 与镜像内容分别冻结。
- 派单里的 `SPRAY_MODEL_ENDPOINT` 占位有误，实际使用 `SPRAY_VLM_ENDPOINT`，值为完整 chat/completions URL；同时核对 `SPRAY_VLM_MODEL`、`SPRAY_VLM_API_KEY`、`SPRAY_REFERENCE_DIR`、`SPRAY_DECODER_PATH`。密钥仅从受控配置供给，不进入镜像或日志。
- 网络、只读原包、可写 work/state/staging/slices、用户权限和恢复行为按正式代理契约装配。环境探针的 2CPU/6GiB 不是完整流水线资源预算。
- [运行方法](../../../../../analysis/spray-runtime-install-20261013/runtime/README.md) 给出了两机器路径、镜像 entrypoint 和挂载要求；[安装报告](../../../../../analysis/spray-runtime-install-20261013/REPORT.md) 有健康检查及版本证据。环境 PASS 不替代生产备份、完整迁移或业务全链验收。

请在原任务回执中注明已消费本勘误，无需另起任务。
