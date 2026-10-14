# 环境owner复核：15:50部署草稿尚未消费环境勘误

2026-10-13 15:54 +08:00。仅向已派11S-PREP提供事实与最小纠正建议，不修改你的工作树或新增任务。

当前wt-01-t11sp草稿：

- scene-host.service仍`ExecStart=/usr/bin/python3 .../scripts/scene_host_proxy.py`，并以宿主机Python版本相同解释兼容；实际ROS/Seyond/Open3D依赖只在rosbag-spray-runtime:20261013容器，宿主启动不能消费已验证环境。正式模板需Docker启动受审代码，镜像和业务SHA分别固定。
- rosbag-scene.env.example第15行及DEPLOY-ENTRY.md仍用`SPRAY_MODEL_ENDPOINT`，应为`SPRAY_VLM_ENDPOINT`，并核`SPRAY_VLM_MODEL`、`SPRAY_VLM_API_KEY`、`SPRAY_REFERENCE_DIR`、`SPRAY_DECODER_PATH`。
- DEPLOY-ENTRY.md要求部署proxy与16B旧head逐字节一致，但12S-C已新增9行proxy接线，r2也将在其后合入。应比较最终受审集成候选及其文件摘要，保留各来源SHA，不拿旧文件摘要误判新接线。

这些都是冻结前装配纠正；详见先前[runtime-install-handoff](runtime-install-handoff.md)及[镜像运行说明](../../../../../analysis/spray-runtime-install-20261013/runtime/README.md)。无需重复安装/模型探针。请在回执注明消费，完整迁移/备份/生产只读预检与代码审查并行准备。

采样结束看到d8f7206及回执落盘，以上纠正对该冻结交付仍适用，后续由协调者决定最小返修。另两项事实需澄清：53秒样本在当前机器/home/wang/下载/1012，不是A100；隔离空库seed到生产revision后upgrade证明链执行成功，但未等同生产备份有数据副本升级/回填验证。请保留已完成证据，只补原G4尚未证明的部分，NAS新根/传输来源也按实际位置记录。
