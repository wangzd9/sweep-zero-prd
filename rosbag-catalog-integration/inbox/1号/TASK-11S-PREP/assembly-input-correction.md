# 原r1部署装配的必要输入核验（2026-10-13T18:06:59+08:00）

当前Codex协调者只读核769d69f：docker compose config --no-env-resolution -q在提供切片root后rc0，基本语法有效；但实际镜像/输入装配仍缺必要面，和原r1 Docker运行/环境键要求同一范围，合并到image-pin-correction同一个最小续commit，不重复建任务。

1. 现Compose只挂代码/state/work/slices，**没有ready原始Bag只读挂载**。实际proxy.resolve_spec从SCENE_NAS_READY_ROOT+bag.relative_path读取文件；缺此映射即源路径不可用。添加宿主实际scene ready→容器受控ready根只读bind，环境对应同一容器根；不能整包拷到模型机或借自建raw根。宿主路径由部署受控变量明确提供，未填fail-closed；与切片根同样核实际映射。
2. **7参考图没有任何挂载**。已安装Dockerfile只有依赖/typesupport/decoder，不含refs；已核两机图放在环境目录assets。Compose需参考图目录只读bind到明确容器路径，SPRAY_REFERENCE_DIR一致；7图hash沿用SPRAY-REFERENCES.json，不重下载重做镜像。
3. 环境模板SPRAY_DECODER_PATH当前为空，且注释声称“无代码消费”已被新B固定f76e2a9推翻：precheck.py:108 resolve_decoder_path和adapter.py:314真实消费本键。空env_file会覆盖镜像已有默认。将模板写为实际/opt/spray/bin/packet2pointcloud并改正说明；参考图实际容器路径同样一致。VLM endpoint/model/key在发布受控回填，密钥不日志输出。
4. 合并原镜像pin修复，固定image实际不可变ID；业务SHA另固定。用真实docker compose config（不只PyYAML）与最小只读mount/path自检验证ready、refs、decoder、code/work/state/slices一致。可用隔离合成目录做挂载结构检查，不触生产/不重跑迁移或全仓。

保持原A owner与deploy/scene边界，不代写业务。此次是冻结物可运行性核验；ACK用原r1回执一段，不增加历史阅读/催单循环。旧协调者已暂停，交当前Codex裁决。
