# 环境安装 owner 交接（2026-10-13）

用户最新明确：“环境的安装和测试由你来负责，先在当前机器再在处理机安装”。Codex 接管本次运行环境准备和环境验证；请勿重复派 A 安装同一套依赖。A 可继续负责部署入口/场景服务模板/镜像开关与迁移准备，C 继续八步接线，B 继续算法返修，TESTER 负责固定业务候选的独立验收。

安装策略：独立 Docker 运行镜像（Ubuntu22.04/ROS2 Humble、现有 packet2pointcloud、上游 Seyond 消息 typesupport、PCL1.12、Python3.10/Open3D0.19、软件 EGL），不改现有 Phase0/Conda 环境，不重启生产业务容器。先开发机真实短包 decoder+图像探针，再传同一镜像到处理机验证；所有原始 Bag 只读挂载，输出写专用 work。用户确认没有现成可运行环境，需从头安装。

本地构建输入暂在 `/home/wang/work/.local/spray-runtime/`，已拉取 ROS 基础镜像摘要 `sha256:860e53793ccf575e5369b5e9a19939de2bfcfb46a299954d06f54f2af54fed19`；Seyond 官方消息源 `Seyond-Inc/seyond_ros_driver` HEAD `d3c78bd38acadd17d6d1f273c7f8127f63252e3a`。消息ABI/实际数据兼容尚待真实解码，不以编译完成宣称兼容。

生产用户无免密 sudo，但可使用 Docker。处理机 Ubuntu22.04/x86_64、RTX5080Laptop、400GB本机余量、NAS29TB余量；不为环境准备修改驱动或停止在途业务。环境验证不是12S-D业务全链PASS。真实模型请求按用户水雾测试范围限定小规模、记录请求数量/流量，不占OCR串行锁。

请协调者消费此输入并回写真实owner及接线需求；阶段结果将落于 `/home/wang/work/doc/analysis/spray-runtime-install-20261013/`。
