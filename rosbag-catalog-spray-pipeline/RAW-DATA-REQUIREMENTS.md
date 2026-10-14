<!-- spray-post-v04-plan-20261014 -->
> **后续质量验收资料（2026-10-14T13:53:01+08:00）**：除日常上传基础资料外，扩量验收需真实车辆映射、有效雷达真阴性、已知水雾区间跨DB3样本及包外人工真值，清单见 [后续计划D1](SPRAY-POST-V04.md#task-12s-d1-资料与固定验收清单)。这不是要求每个日常上传包提前逐帧标注。用途/目标可由指定水雾profile默认冻结，不要求上游重复手填；意图不能代替真值。当前上游首选仍先提交再上传；“先登记后提交自动收敛”和INPUT_REJECTED/resume属E/F待开发目标，尚不能按示例假称已支持。

# 原始数据自动处理交付要求

版本：scene-input/v1，2026-10-13；适用于本轮水雾生产接入。主需求 [PRD](../rosbag-catalog-integration/PRD.md)，实施 [TODO §9](../rosbag-catalog-integration/TODO.md#9-v05-水雾优先与生产接入2026-10-13)，算法 [水雾设计](SPRAY-INTEGRATION.md)。本文件是交付契约，新增元数据接口仍需TASK-12S-A实现，不能把示例直接投递现有严格DTO。

## 1. 数据提供方必须交付什么

“用途”和“场景”是两个字段：`purposes=["scene_slice"]`表示做场景识别/切片；`scenes=[{"scene_code":"spray"}]`表示识别水雾。不能提交`purposes=["水雾"]`或根据目录名猜模型结论。需要同时生产自建数据集时，才显式选择双用途；本轮水雾默认纯场景，不触发Phase0。

| 信息 | 要求和来源 | 缺失或冲突时处理 |
|---|---|---|
| 原始包身份 | 完整ROS2 Bag目录名、相对接收路径、批次ID和幂等键；路径必须落在独立场景incoming。目录名保持原样，不要求改名。 | 路径越界/冲突拒绝；同包重传复用提交，重复不新建运行。 |
| 车辆信息 | 必填`vehicle_code`，每包恰好一辆。数据方提供编号和含义；平台先在既有Vehicle登记对应车辆。VIN、车型、传感器序列号可补充，VIN不能凭空替代系统vehicle_code。多车一批提供逐包映射。 | 无编号、无匹配Vehicle或相互矛盾时保留待补资料，不执行/发布生产水雾；不猜车、不自动建虚假Vehicle。旧自建/历史未知车辆策略不受影响。 |
| 用途和识别目标 | 每包明确`scene_slice`和`spray`，或使用运营已创建且冻结版本的水雾入口默认值。采用`scene-spray` profile、scene根、`spray/`相对前缀；原空前缀场景profile仍保持其坡道默认。 | 无有效配置为CONFIG_REQUIRED；禁用/未知场景明确失败，不回退自建、不自动全场景识别。 |
| 采集时间 | 原始metadata和消息含真实时间；采集说明必填`collection_timezone`（例如Asia/Shanghai）。UTC epoch整数纳秒是机器切片依据，目录中的年月日时分秒只作核对。 | 时间为0、持续时间非法、源文件与metadata明显冲突，预检拒绝；不能给epoch再加8小时。 |
| 文件完整性 | `metadata.yaml`可解析，`storage_identifier=sqlite3`，所有relative_file_paths列出的DB3完整非空；上传结束后size/mtime连续稳定，生产首包有完整文件摘要证据。 | 空/缺/损坏文件不进入识别；继续上传的文件不移动、不切片。MCAP不是本轮正式支持格式。 |
| 水雾雷达输入 | 本批走`/iv_packets_front_mid`，类型`seyond/msg/SeyondScan`，含消息；传感器型号/固件或解码配置引用可由固定入口绑定，必须能与服务端批准的转换器匹配。后雷达不能替代前雷达。 | 缺支持topic为NOT_APPLICABLE，不产生“正常无水雾”结论；消息存在但无法解码是FAILED。 |
| 替代点云输入 | 若交付已转换包：`/iv_points_front_mid_transformed`、`sensor_msgs/msg/PointCloud2`，有效x/y/z及intensity、字段布局与坐标系说明。两种路线由能力声明选择，其一满足即可。 | 无intensity/坐标系不明时不默默换渲染配色；先核验算法兼容或明确不适用/失败。 |
| 采集场景意图 | 可声明“水雾测试”，记录为采集说明；采集人员可提供事件大致区间作为质量验收参考。 | 意图不能写成模型命中标签，不要求上传者提前标注每帧才运行自动链路。 |
| 交付责任信息 | `batch_id`、数据联系人/团队标识、传感器配置引用；定位失败和追溯来源用，不写密码/凭据。 | 生产批次无法追溯则补齐，不从文件名猜责任人。 |

车辆code推荐不超过64字符、使用平台已登记稳定编号。本轮不增加VIN强制校验/车联网查询/车辆主数据治理项目；VIN非必填。没有车辆编号的当前样本仍可用于隔离算法探针，但不能作为车辆血缘齐全的生产首包验收。

## 2. 平台自动生成什么

上传者不用提供数据库bag_uid/source_id、源代次、指纹、run_id、分析版本、slice_key、子包UID、模型标签或产物路径。平台在登记/执行/发布时生成这些字段并关联原包，子包继承已冻结车辆和采集说明。区间时间、模型判断及证据来自执行结果，不信任提交者自报成功。

已按用户授权将ros2_slice快进到GitLab master `be23177`，7张参考图本地校验齐备；处理机安装时须对照相同hash。

模型endpoint/凭据、7张参考图、转换器/SDK、EGL/Open3D依赖、渲染/抽样/规则/模型修订、输出根与资源许可由运维提供，是服务运行要求，不是每个原始Bag需要携带的文件。

## 3. 数据交付示例和提交顺序

原始包外维护一份批次清单，逐包附以下信息；不把此清单塞入不可变Bag，也不修改ROS `metadata.yaml`。JSON仅为目标示例，`VEHICLE_CODE_TO_FILL`须替换为实际已登记车辆，版本与profile须先由平台真实创建并验证。

```json
{
  "profile_id": "scene-spray",
  "relative_path": "20261012/rosbag2_2026_10_12-16_02_03",
  "purposes": ["scene_slice"],
  "scenes": [{"scene_code": "spray", "capability_version": "spray-v1", "parameters": {}}],
  "source_metadata": {
    "schema_version": "scene-input/v1",
    "vehicle_code": "VEHICLE_CODE_TO_FILL",
    "collection_timezone": "Asia/Shanghai",
    "batch_id": "1012",
    "sensor_profile": "seyond-front-mid-approved-v1"
  },
  "idempotency_key": "1012-spray-rosbag2_2026_10_12-16_02_03"
}
```

步骤：登记真实Vehicle与服务端sensor profile→每包提交配置及source_metadata→确认提交被接受→复制整包到`/public/rosbag_scene_processing/incoming/spray/20261012/<bag目录>`→结束上传并等待稳定→Scanner整包移入相同相对路径ready→Backend冻结身份/车辆→自动队列/本机处理→NAS切片及入库→查询run、results和子包manifest/lineage。数据传输仍用NAS工具，配置API不传大文件。

批次默认相同车辆仍须在每包提交中解析成明确值，不能上传后才补车辆。新spray提交缺资料/车辆未知返回422，不产生调度事件；既有PENDING_INPUT待补记录保留，不自动派发。修订只在未绑定阶段，使用row_version和同一提交；绑定后不能把另辆车套给原run。同幂等键的配置/路径/元数据都一致才复用提交，元数据不同返回409，不能借重传改车。source_metadata有界64KiB、API体1MiB，未知字段拒绝；字段级错误码由TASK-12S-A补OpenAPI。

## 4. 当前1012批次只读盘点

目录由用户提供：`/home/wang/下载/1012`。仅检查metadata、文件stat，以及最小包的SQLite topics表；没有解码/推理、修复原包、复制到NAS或对生产库写入。完整摘要/SQLite integrity/模型质量尚未验收。

| Bag时间后缀 | DB3规模 | metadata时长 | 观察结果/首波用途 |
|---|---|---|---|
| 2026_10_08-14_42_48 | 724627456 bytes | 约53.43秒 | 有前雷达SeyondScan；优先候选真实样本，是否含水雾仍待人工说明/实际识别。 |
| 2026_10_12-15_58_23 | 57679872 bytes | 约4.38秒 | 有前雷达；适合小规模解码/渲染探针，短于15秒窗口，不单独证明完整场景质量。 |
| 2026_10_12-16_00_13 | 89653248 bytes | 约4.75秒 | 有前雷达；同上。 |
| 2026_10_12-16_02_03 | 10105905152 bytes | 约537.25秒 | 有前雷达、多DB3；候选完整链路/跨文件验证；不可直接全批并发，需空间与请求预算。 |
| 2026_10_12-16_31_25 | 25174016 bytes | 约3.58秒 | 未见支持雷达topic；候选NOT_APPLICABLE取证。 |
| 2026_10_12-16_33_10 | 0 bytes | 无法解析 | metadata与DB3均空；输入不完整，禁止识别/正常入库。 |
| 2026_10_12-16_37_47 | 7321513984 bytes | 约1049.02秒 | 未见支持雷达topic；不作为可识别水雾样本。 |
| 2026_10_12-16_58_28 | 6794981376 bytes | 约1048.60秒 | 未见支持雷达topic；同上。 |

8个目录均未从包名得到车辆编号，用户确认编号目前没有，需向数据提供方补索取。现有Vehicle模型以vehicle_code/rustdesk_id匹配，不能通过目录`1012`、topic`/vehicle/chassis`或日期推断车辆。盘点证据 `/tmp/rosbag-scene-v05-audit/input-inventory.json`；本机临时证据不是永久原始包归档。
