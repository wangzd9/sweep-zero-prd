# 生产NAS写锁最小纠错

时间 2026-10-13T20:31:34+08:00。代码3c9c496已合入并推github/main，标准生产入口部署和本地收敛成功。用户允许本次OCR不等待；未伪造审查结论、未永久修改规则。

首包attempt1在CIFS上SQLite创建报database is locked，目标DB3零字节；模型12次完整且原包SHA不变。根因不是模型或水雾参数，是把切片数据库直接写到网络文件系统。

修复：writer先在本地run/attempt私有slice-write写完关闭校验，再复制NAS同盘.staging，逐文件SHA一致才交现有原子发布；复制异常/DB3或metadata损坏明确阻止发布登记，源不变。旧版新增4例全FAIL，修后组合19PASS；35项既有编排/代理也通过。处理机真实CIFS复制/普通mode=ro/同盘rename/Backend容器只读别名64条夹具PASS，无mount变更、无nolock。

正式原run normal retry attempt2已SCENE_DONE，缓存只移交spray_model_results.json，未移交旧checkpoint。当前步骤八项全DONE，最终机械获取/对账验收另存生产报告。工程任务可DONE；受控单包不代表全验收矩阵。证据在 /home/wang/work/.local/spray-runtime/production-*3c9c496*、pytest-local-write-nas-stage-*、nas-sqlite-copy-probe-20261013/，部署快照由官方只读检查和生成器产生。
