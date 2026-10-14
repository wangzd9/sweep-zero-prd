# 水雾识别、切片与入库设计

版本：v0.5 / DESIGN_READY，2026-10-13。覆盖REQ-17/18，优先级与状态见 [TODO §9](../rosbag-catalog-integration/TODO.md#9-v05-水雾优先与生产接入2026-10-13)。根/租约/Backend唯一写库沿用 [DESIGN §7.3](../rosbag-catalog-integration/DESIGN.md#73-v04-场景专用接收执行与界面补齐)，本文件覆盖其中“首期只有坡道”和首包UI必需的本期范围。

## 1. 事实和接入差距

本地catalog main调查为`6fb42c4`：16A已合入并独立验收，场景双根/快照已在代码；注册表只有slope与test-capability，无spray正式适配器。本机代理在16B分支，审查/已裁恢复缺陷仍未收口；16C在途交付被冻结保存，不是水雾发布依赖。旧真实坡道模块/API证据不能作为水雾证据。

参考算法根 `/home/wang/work/ros2_slice`：`src/analysis_spray.py`、`utils/point_to_pdc.py`、`utils/pdc_to_pic.py`、`request/request_spray.py`、`request/request_common.py`，只读复用算法契约，不修改该仓库、不用CSV做平台状态中转。关键已观察风险：

- 原代码把PCD/图片/cache写在原包内，并用“目录非空”判断完成；平台必须改为run/attempt私有work、完整manifest/hash判断缓存，保持NAS原包不可变。
- request返回“异常/正常/未知”，analysis按`result == '是'`判断异常；适配器必须归一化为`spray/normal/unknown`后分段，禁止照搬导致全部NO_MATCH。
- packet转换子进程未检查returncode，渲染无图可能返回空列表；必须检查返回码/实际PCD/有效渲染图/有效判断数，区分解码失败、渲染失败与真实无命中。
- 源time先经本地时间文件名再转毫秒/秒且round会丢精度；平台全程用源DB3存储时间整数纳秒，抽样、排序、窗口、writer和证据都使用同一轴，不借无时区字符串回推。
- 初查旧工作区未找到参考图；按用户指令GitLab master已由197645e快进至`be23177eca685b5f0f75160ca82503beeb63147d`，7个images/refs JPEG均可读取、3840×2160且顺序/hash已冻结，缺图这一**本地**阻塞解除；生产机仍需资产安装校验。此次更新只新增图片，以下算法代码问题仍存在。已有`utils/packet2pointcloud`为x86-64动态链接ELF，仅文件存在不证明生产依赖/型号兼容。

## 2. 能力和输入冻结

新增`scene_code=spray`、`capability_version=spray-v1`、`adapter_key=ros2-spray-v1`，维持scene-capability/v1与通用dispatch/队列/results/complete/reconcile；禁止核心调度硬编码spray分支。descriptor与真实adapter供应者同一owner，源码在但依赖缺失时返回明确unavailable_reason，不宣称enabled即具备可用服务。

输入支持两路线，按服务端sensor profile确定，优先本批实际存在的`/iv_packets_front_mid`（`seyond/msg/SeyondScan`）→已批准packet2pointcloud；替代为`/iv_points_front_mid_transformed`（PointCloud2，x/y/z/intensity）。不把两个topic都列为AND必需，不默默用后雷达。原始包须满足 [原始数据要求](RAW-DATA-REQUIREMENTS.md)，缺topic=NOT_APPLICABLE，存在但不能解码/无有效图=FAILED。

原始packet decoder输出的点云须有可追溯的输入消息ID、DB3文件、存储ns和输出图映射，不能只保留秒级文件名；若旧二进制只能输出截到ms的时间，TASK-12S-B在工作副本/包装层建立确定映射并检验，重复/歧义拒绝，不把ms×1e6冒充源ns。型号/SDK/PointField偏移、padding、row_step、字节序正确性纳入预检，动态依赖只在处理机安装。

首版水雾区间直接定义在**bag storage ns轴**，manifest区间的`mapping_basis`精确填写`bag_storage_ns`，time_mapping证据保持同一口径；writer传offset=0，publish/complete校验同存储轴，不调用坡道header→storage推导来猜偏移。现有`scene_publish_service.derive_storage_offset`已支持该basis并返回0，12S-C优先复用并验证接线，无需为水雾新增offset分支；不能改坡道已有语义。

## 3. 本机预处理与模型契约

PCD解码、图片渲染、时间映射和切包全部在处理机。GPU/CPU离屏渲染必须在该机实测；若EGL不可用，可使用已验证且输出等效的本机软件渲染，不能将渲染迁到A100。模型机只接必要点云图片、固定参考图及参数，共用既有VLM_PERMITS，记录每pass/重试/参考图重复传输的bytes，不只统计目标图。

首版基线保留当前调用的行为并冻结（生产若带宽/空间超预算必须先改版本并取得真实质量证据，不能直接开批）：PCD有序序列跳过前10帧，每3帧取1帧；渲染3840×2160、旋转90度，ROI x=(-2,6)、y=(-3,3)，intensity配色；JPG质量95、原参考过滤阈值500KiB，过滤数量/失败/剩余数必须记录。保留这些规则用于与原算法对照，不能把图片大小当作“没有水雾”；过滤后无足够有效数据是FAILED。帧率/过滤造成的时间空洞和质量风险在单包报告里说明；任何降低尺寸/频率/阈值优化均升预处理版本并复测。

判定复用SPRAY_SYSTEM、SPRAY_PROMPT_V18与SPRAY_PROMPT_SIM双pass规则；pass1明确异常可直接判异常，否则按pass2参考图编号复核；1～4正常、5～7异常。无法解析/未知/HTTP错误有界重试后仍不确定则FAILED，不能用`!=异常`统称正常。模型名/修订、提示词hash、7图有序hash、decoder/render修订、预处理参数、源指纹和帧摘要进入执行证据及缓存身份；改变参考图不复用旧判断。秘密仅经服务端配置引用。

参考图清单严格为以下7个文件，部署路径由服务端`SPRAY_REFERENCE_DIR`受控提供，部署时校验内容摘要和顺序；不把待判定图临时当参考图，也不虚造替代图：

| 编号 | 原文件名 | 类别 |
|---|---|---|
| 1 | 2026_07_29-17_21_13_457-1785316873457.jpg | 正常 |
| 2 | 2026_07_29-17_21_12_257-1785316872257.jpg | 正常 |
| 3 | 2026_07_29-17_21_10_757-1785316870757.jpg | 正常 |
| 4 | 2026_07_01-11_07_37_357-1782875257357.jpg | 正常 |
| 5 | 2026_07_29-17_21_45_257-1785316905257.jpg | 异常 |
| 6 | 2026_07_29-17_20_58_757-1785316858757.jpg | 异常 |
| 7 | 2026_07_29-17_21_52_757-1785316912757.jpg | 异常 |

参考图7张实际总bytes=15190041，Base64合计约20.25MB/每pass，尚不含目标图/JSON/重试；双pass可能至少约40.5MB/帧。用实际解码采样帧数和pass数估算首包请求量/耗时/空间，packet消息数不是点云帧数。发布owner记录可接受预算，超预算阻断生产启用；若需压缩/重采样/服务端已支持的引用复用，先证明与参考基线质量一致、冻结新资产/预处理版本并重测。不能临时改成无参考图请求或另建通用模型缓存平台。

有序SHA-256、逐图bytes及尺寸的永久清单见 [SPRAY-REFERENCES.json](SPRAY-REFERENCES.json)，基线commit为`be23177eca685b5f0f75160ca82503beeb63147d`。部署和缓存校验按此清单，不依赖本机/tmp临时证据。

平台部署预检必须检查文件非空/可解码/hash、converter型号及共享库、ROS类型支持、Open3D/EGL、模型多图接口和工作盘/NAS空间。不允许原模块import产生网络/原包写入或sys.exit结束整个代理；资产缺失返回明确REFERENCE_MISSING。

## 4. 分段、写包和入库

沿用`analysis_ros2`实际调用参数：window_size=15秒、min_abnormal_ratio=0.15、enter=3、exit_=5、前置3秒、重叠>=7秒合并；函数未传参默认0.3不是本轮默认。适配器用整数ns保留相同窗口/去噪语义，参数schema校验密度[0,1]、整数阈值>=1、时长>0，跨字段/源边界先核验。短包可裁剪窗口但不凭空补帧，抽样不足或无法判定不得NO_MATCH。

去噪/窗口内是否“正常”只依据可解析模型结果；目标label=spray可发布，normal不发布，unknown仅作失败证据。SUCCESS有非空可读子包；NO_MATCH是足量有效推理后无目标，保存空分析结果，不创建空子Bag；NOT_APPLICABLE不覆盖既有current；FAILED保持旧current。

沿用八步记录和run/attempt私有目录，WRITE复用通用writer实现、NAS slices同盘staging原子发布、Backend校验并登记Bag/Artifact/区间/血缘/水雾标签，complete后子包AVAILABLE并切当前。发布路径`<vehicle_key>/spray/<parent_uid>_<child_uid>`的vehicle_key由已登记父车辆生成，不能用source_metadata任意拼路径。父包关联的采集水雾意图与子包模型水雾标签分开。

输入元数据扩展：POST/PATCH ingest-submissions新增可选source_metadata（旧profile无需字段）；本轮spray profile要求scene-input/v1中的vehicle_code/collection_timezone/batch_id/sensor_profile。服务端在接受时校验已有Vehicle并解析成稳定vehicle_id；在现有intake_snapshot_json保存有界metadata快照及独立hash，root快照与旧EffectiveConfig/hash不改。绑定时再次验证身份并赋父车辆，再创建调度事件；恢复upsert后重新应用同一冻结绑定，不被现有rustdesk名称匹配清空；不得篡改历史MANUAL车辆。冲突409、新spray提交未知车辆/缺信息422且不创建调度事件；既有待补记录保留，未绑定PATCH后重验，已绑定拒改。记录API/提交审计及row_version，不新增metadata数据库写旁路/CSV队列/第二批次平台。

元数据hash使用校验后的source_metadata规范JSON（键排序、UTF-8、不转义中文、无多余空白）的SHA-256，快照另存解析出的vehicle_id用于绑定。旧入口未传字段按缺省空元数据处理，不重算历史hash。POST幂等比较同时核对原配置/路径身份及元数据hash：同键同payload返回同一提交，同键不同车辆或其他元数据返回409，不悄悄替换；变更必须走未绑定PATCH及row_version，再冻结新快照。12S-A自测和AC-18.2包含这两类重放。

profile新增`scene-spray`、root=scene、incoming_prefix=`spray`、默认纯scene_slice+spray；原scene-isolated坡道profile不改ID/version/default/hash。参数与资产版本由服务端冻结，当前run不随默认值变化。无需16C新集合API：本轮用已有运行详情、results、Bag详情/lineage、文件获取验收，旧页面只做回归烟测；新的查询/页面增量待用户恢复。

## 5. 开发和发布结束条件

TASK-12S-B可用只读本地短包做转换/渲染探针；真实模型请求和写测试NAS由后续执行派单确定许可，不从文档推导付费调用。12S-C最终接线硬依赖16B门禁通过并合入，不能复制未审代理另开旁路。首期SCENE_EXEC_HOST=1，单run模型并发1，实际临时空间覆盖源副本/PCD/图/切片/staging，禁止立即全批处理10GB包。

独立验收绑定固定SHA，覆盖命中/正常/缺topic/空包/缺图/未知模型/中断恢复、storage ns和多DB3、血缘/幂等/current/旧路线回归；需一个授权真实水雾样本及业务确认事件区间。今天上线仅在 [发布清单](SPRAY-RELEASE.md) 所列门禁实际通过时可宣布具备功能，不能靠调整PRD承诺运行成功。
