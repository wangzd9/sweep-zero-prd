# 环境安装完成：两机器PASS，供A/C/TESTER接线

2026-10-13 15:02 +08:00。环境owner Codex已完成用户指定的先当前机器、再处理机安装及实际测试。

- 镜像 `rosbag-spray-runtime:20261013` 已在两机器安装。环境根：本机 `/home/wang/work/.local/spray-runtime`；处理机 `/home/data-process/spray-runtime/20261013`。
- 原packet二进制动态依赖已齐，ROS2/Seyond消息typesupport完整反序列化兼容；Open3D0.19软件EGL渲染真实点云成功。小包1184消息→44帧；本机53秒包14404消息→534帧，原包摘要均不变。
- 两机器小包两张3840×2160 JPEG SHA-256完全一致，镜像RootFS/Config一致；两机器各1次真实V18多图请求HTTP200，54.34秒/39.95秒，均明确“异常”。无重试，pass2因pass1异常未触发，非质量/正常分支验收。
- 处理机安装后检查rc=0，旧Compose容器未重启、Backend/Web ready、旧代理active；本次未启动常驻场景业务服务或迁移/登记生产库。
- **A派单装配勘误**：Python `/opt/spray-venv/bin/python` 只在镜像内；宿主机原Conda仍缺Open3D。service必须通过该镜像运行受审代理。环境变量实际为 `SPRAY_VLM_ENDPOINT`，不是派单占位的 `SPRAY_MODEL_ENDPOINT`；应配置完整chat/completions URL及实际 `SPRAY_VLM_MODEL`。环境镜像不含业务代码，业务commit只读挂载并单独冻结。
- **B/TESTER补充S1实测**：53秒包第10帧JPG实际298956 bytes，会触发500KiB删除，已裁S1需要在真实样本复验。S9帧映射已由协调者正式并入返修，不能用全消息数等PCD数或直接删断言。

报告与复现入口：[安装结果](../../../../../analysis/spray-runtime-install-20261013/REPORT.md) / [运行方法](../../../../../analysis/spray-runtime-install-20261013/runtime/README.md)。原始机器比对、模型调用、53秒样本与安装后健康证据全部在报告evidence目录。

请协调者消费并通知A/C/TESTER使用准确镜像执行方式；原任务状态仍单写TODO。环境门禁缺口已解除，正式业务验收/恢复一致性/备份迁移/发布授权门禁维持。
