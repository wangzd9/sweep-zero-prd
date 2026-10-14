# 水雾独立验收契约

2026-10-14按业务归属拆分，原AC编号与要求保持。下表是验收契约，不是测试结果；任务结论和待补证据只读 [任务入口](TODO.md)。

| 验收项 | 场景及应有结果 | 最小证据/责任 |
|---|---|---|
| AC-17.1 能力与输入 | spray-v1正常注册且实装；原packet/PointCloud两路线按profile正确选择；缺topic不适用，缺图/坏decoder/渲染无图失败；不写原包、不迁非模型计算到A100。 | descriptor/预检/转换返回码/图证据、进程/原hash；12S-B |
| AC-17.2 识别与分段 | 模型异常/正常/未知归一正确，双pass与7图顺序保留，15秒/0.15/3/5/前置3秒/合并7秒规则和storage整数ns可对照；未知不充当正常。 | 已知标签fixture、真实阳性及阴性、提示词/refs/render/model版本、bytes/pass统计；12S-B |
| AC-17.3 时间与缓存 | 跨DB3、乱序/重复、短包/缺帧正确或明确失败；用源storage ns，不从本地时间文件名猜；缓存/恢复包含参考图及规则版本，取消不继续写。 | 原消息→渲染→区间映射、小包与多DB3边界、缓存失效/取消证据；12S-B |
| AC-17.4 自动入库与恢复 | 专用incoming→正式Scanner/队列/代理→非空可读切片→NAS→results/complete→AVAILABLE/current和水雾标签/车辆/父子血缘→已有API实际获取；重复/断连/发布后失败先对账，无命中不空Bag、失败保旧current。 | 一条全链时间线、UID/manifest/DB/文件摘要和幂等计数、8步、真实错误恢复；12S-C，TESTER独立联合验证 |
| AC-18.1 必要资料 | 新spray入口vehicle_code/时区/批次/sensor profile有效且purpose=scene_slice、scene=spray；不猜车不把意图当命中；无资料/冲突拒绝或待补，不调度生产。 | 缺/未知/冲突/正常提交/多车映射、outbox/run计数；12S-A |
| AC-18.2 冻结与继承 | source_metadata绑定前可受row_version约束修订，绑定后拒改；源/子包车辆一致、恢复不被basename匹配清空；独立hash与旧业务hash不混用；同幂等键同元数据复用，不同元数据409。 | 快照/hash/车辆FK及重放对照、MANUAL冲突、未绑定PATCH和已绑定409；12S-A/C |
| AC-18.3 旧入口兼容 | 旧self_built/NVIDIA/slope无需新增元数据；原profile/version/default/hash保留，scene-spray窄前缀不跨根、不抢坡道空前缀、无spray能力时bootstrap不崩。 | 双根/新旧profile/关闭场景开关回归、既有提交/UID对照；12S-A |
| AC-19.1 固定候选原功能回归 | 16B实际审查与已裁恢复缺陷收口，候选不依赖16C；旧自建/NVIDIA调度/API/页面和坡道成功/恢复无新回归；新根异常不默认Phase0。 | 固定SHA/实际审查及独立回归/既有失败同基线归因；12S-D，协调者审核 |
| AC-19.2 生产准入 | 从实际生产schema至候选全链隔离迁移、备份/恢复策略、7图/解码器/渲染/model多图、NAS/空间/活跃任务/回滚都核实。 | SPRAY-RELEASE G1～G4实物证据和业务质量接受；11S |
| AC-19.3 生产首包及收敛 | 当次发布授权、正式部署参数；关闭部署后旧功能健康，spray受控单包成功，禁用后不串自建；新快照及部署后本地up/test通过。 | G5～G6部署receipt、版本/步骤/文件/API、旧功能烟测及本地收敛；11S |
| AC-20.1 时序与自动绑定 | 先提交、先登记、并发/崩溃重启均自动收敛，不等模型槽 | 严格MySQL固定SHA，source/代次/冻结快照/outbox/run完整身份与时间线；12S-E |
| AC-20.2 准确源与不重复执行 | 父子同快指纹合法原包可重登记；派生子包/歧义源仍拒；重复不增模型、run/attempt/版本 | 同指纹/跨根/车辆fixture、调用计数与旧终态真结果复用分列；12S-E |
| AC-21.1 拒绝与等待分类 | 活跃上传仍PENDING_INPUT；完成/稳定重复确认的坏输入INPUT_REJECTED，断网不伪判损坏 | 空metadata/DB3/缺文件/变化中/网络错误/无submission先发现；持久错误证据、重启及重复扫描不刷任务；12S-F |
| AC-21.2 补齐受控恢复 | 同提交补齐后resume重校验、有效转绑定、仍坏再拒；已绑定/旧row_version拒恢复 | 并发/幂等重放、审计历史/path claim、原SHA、source/run/模型恰好一次；真MySQL兼容迁移/API；12S-F |
| AC-22.1 真阴性与质量 | 支持雷达且有效正常输入NO_MATCH无伪切片；阳性区间按人工真值与冻结业务阈值验误报漏报/边界 | 包外真值/模型和refs版本/区间指标定义；NOT_APPLICABLE、UNKNOWN、test和mock分列；12S-D1/D2 |
| AC-22.2 实车与真实跨DB3血缘 | 真实vehicle_code冻结并继承；已知阳性区间跨DB3，storage ns消息不漏不重/不错时 | 原/子包/版本/标签/获取对照、边界两侧消息、切片打开计数、完整原SHA、两次reconcile；12S-D2 |
| AC-22.3 固定批次与重复恢复 | 有限固定清单各outcome独立追溯，E/F成功/拒绝/恢复路径覆盖，重复不烧模型 | manifest固定数量/字节、逐包结果、调用/耗时/空间/重试、旧功能回归；记录可接受规模与质量范围；12S-D2 |

真实单包从Scanner、队列、正式代理到发布和Backend登记取证，固定SHA与源UID/代次/冻结配置。检查原包摘要、步骤/manifest/父子血缘、实际可读Bag和有效获取路径；API 200或mock不是自动全链验收。

公共执行/旧路线回归引用 [基础验收](../rosbag-catalog-scene-foundation/ACCEPTANCE.md)。生产门禁和已接受受控首包证据按 [发布资料](SPRAY-RELEASE.md)，后续质量补验按 [生产收尾](SPRAY-POST-V04.md)。test、NOT_APPLICABLE、UNKNOWN、mock均不得代替真实车辆或真阴性；业务真值和质量阈值不足明确NOT_RUN/BLOCKED。
