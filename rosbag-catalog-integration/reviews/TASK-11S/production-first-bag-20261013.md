# 水雾受控生产首包发布结果

生产业务首包于2026-10-13 20:24完成，最终验收于2026-10-13T20:32:37+08:00通过；19:00目标未达。代码main/处理机/本地运行版本3c9c496，Alembic 20261013_01_scene_intake。用户授权Codex直接收尾，并明确本次OCR卡点不等待；该例外未写成OCR通过，也未永久修改规则。

## 实际结果

- 输入rosbag2_2026_10_12-15_58_23，车辆test（用户指定受控车辆），submission 9949d1a7ea4f4feb8284b3cebfd4fab1，source 615A4A7BF5FE4C51B864D01AEA。
- 原run scene-c4a88c0746e9422ca35136035fe7正式normal retry attempt2达到SCENE_DONE，当前八步全部DONE、outcome SUCCESS、无业务错误。
- 44完整PCD→12有效渲染帧；首轮12次真实模型请求形成水雾区间。原包SHA前后不变，尾部20不完整packet不发布。
- 发布1个3.302042339秒切片，1752条消息、12topics；child 16Bc-51ac3e1fa53dbdd6b2，AVAILABLE/current，继承test车辆。实际DB3消息数与API一致、北京时间正确。
- 既有获取入口 http://192.168.2.134:8180/bags/16Bc-51ac3e1fa53dbdd6b2/access.txt 与原包血缘可读；正式reconcile两次幂等，未重复登记。
- 原始目录独立incoming→ready，切片在独立slices，不触发自建流程。Backend健康与/bags、/pipelines、/vehicles保持正常；部署额外核/nvidia/batch。迁移前后旧Bag13/pipeline17/DatasetFrame225798保持，之后仅按实际场景数据增加。
- 同版本本地mock up/test PASS且stale=false。生产常驻rosbag-scene-host.service active/enabled，正式运行环境镜像与业务源码分别固定。

## 真实故障与关闭证据

原attempt1在CIFS NAS直接创建SQLite报database is locked，目标0字节，模型结果完整。3c9c496最小修复为处理机本地写完关闭并校验→复制NAS同盘staging→逐文件摘要相同→原子发布；旧版新增4例全FAIL，修后19例PASS，相关旧编排/代理35例通过。处理机真实CIFS普通mode=ro/同盘rename/Backend只读别名64条夹具验证PASS，未改挂载或绕过锁。

正式retry前仅移交原模型缓存，不复制旧checkpoint。缓存键由适配器重新校验源指纹/规则/参考图/帧序列/参数后复用，模型未因人工重新提交而重烧。旧attempt1失败证据原样保留。

首次attempt2观察脚本把历史attempt1步骤纳入allDONE而误报FAIL；修复机械脚本按当前attempt校验，使用同submission仅续观察并正式reconcile两次，最终PASS。未改业务状态、阈值或历史步骤凑成功。

## 发布保护与范围

- 19:55即时双副本备份rosbag_catalog-20261013-195539.sql.gz，264215530bytes，SHA23bced7249b320ae0d8fd32856cfb12a0b4f04341e6e95579fb480c7fc39605f；gzip/SHA/timer校验通过，完整副本迁移实验16:58成功。旧源码/环境/镜像保留，不生产downgrade。
- 标准--apply --production先关闭场景发布并核旧健康，再重新叠加catalog-scene overlay，重启正式proxy加载固定代码。生产日志production-deploy-3c9c496.log；官方只读检查processing-check-3c9c496.log生成部署快照。
- B OCR全覆盖0findings已接受；旧R3弱OCR真实HARD_DEADLINE，final-r4/r5/r6仅prepared未启动。用户例外只解除本次水雾必要收尾等待，不宣称OCR PASS。强审累计4次、无在途，R4两项已最小修复及独立故障17例关闭，未新增调用。
- 新UI继续暂停。真实采集车映射、真模型阴性、多DB3实采拼接和批量容量仍是后续验证；此次只是用户授权的test阳性首包受控上线。12S-D/12S完整矩阵保持PARTIAL，11S受控首包DONE。

## 证据入口

主证据 /home/wang/work/.local/spray-runtime/production-first-bag-3c9c496-verified.json；旧失败production-first-bag-8e538bb.json及脚本误报production-first-bag-3c9c496.json保留。独立机械报告位于专项test-receipts；真实NAS探针nas-sqlite-copy-probe-20261013/result.json；本地up/test及生产部署日志同目录。仓库docs/scene-processing-operations.md与既有部署Skill已固化装配及恢复规则。功能日志F-041仅pending，未自行批准或发布。
