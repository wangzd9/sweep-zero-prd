> **2026-10-14当前恢复覆盖**：用户明确恢复UI及OCR遗留，先读 [inbox/control/V04-UI-RESUME-20261014.md](/home/wang/work/doc/prd/rosbag-catalog-integration/inbox/control/V04-UI-RESUME-20261014.md)。本文件旧“UI不恢复/暂停”为历史，不再阻止新16C-A/B/C与16D准备；原收尾在途安全点接续，不抢占，TODO §8为唯一状态。当前main调查63bfcf8、生产3c9c496；seed bd0db1d未接受。

# 水雾上线后的原任务收尾接续

刷新时间：2026-10-14T10:49:02+08:00。用户原文：“对协调者、执行者、测试者的状态等进行刷新，现在水雾已经上了生产，需要他们继续去进行原来的收尾工作了”。本卡恢复原收尾，沿用既有 REQ/AC、角色单写、测试和审查流程，不自动开放 PAUSED/DEFERRED。

## 当前事实与优先级

- 生产业务 `3c9c496` 已上线，main 记录 `63bfcf8`；受控车辆 `test` 首包已 PASS。TASK-16B/12S-A/B/C/11S-PREP 已接受，不重做开发、迁移、部署或首包模型。
- 10:23 正式 API 已恢复三提交：`a65a25a7 → scene-a4824f1c` SUCCESS；`87dfebaa → scene-eb4397c3` NOT_APPLICABLE；`518089ed → scene-24ab78bb` NOT_APPLICABLE。均 SCHEDULED/gen1，事件 CONSUMED，created_runs=0/reused_runs=3/errors=[]，仍7 run且attempt不变。10:37只读审计再次确认。A 10:29 已只读核实身份，待协调者核回执。
- `scene-4acf689f9a6a473da1fa2f2efc70` 仍 attempt1 SCENE_RUNNING；PRECHECK/EXTRACT DONE、INFER RUNNING，余QUEUED。不能再称八步全排队。完成帧数/ETA未知，不为观察超窗重启/重烧模型。
- 空包 `16_33_10` 已被 scanner 拒绝且可追溯，但 submission 仍 PENDING_INPUT，无source/run；保护有效不等于提交层终态已收口。
- 本次首要：三复用结果独立验收、批次台账一致、异常追溯、原功能健康、12S-D缺证矩阵；这些可独立于大包推进。大包终态后再补真实跨DB3和全批收口。

## 角色接续

- COORDINATOR：本卡为当前调度入口。先核角色实际 owner/新回执，刷新 BATCH-STATUS 过时等待语句与 TODO/HANDOFF/开发日志，接受三包恢复事实并审核独立验收；停止 A 重登记旧单。按原 REQ/AC 盘点未完成叶任务，能独立推进则细化派单，不让大包绑住全部角色。各角色下方增补卡待其自行 ACK，不能代写 sessions 或虚报已响应。
- A/B/C/TESTER：读本角色 `post-release-closeout-20261014.md` 增补，沿用原 TASK-11S-BATCH-1012 attempt-1，旧 ACK 不重复领取；对新增接续写本角色 ACK/检查点，交付后释放槽。
- 需新代码的既有接收缺陷（父子共享快指纹误拒绝、空包提交长期 PENDING_INPUT）由协调者对照原 AC 分类、固定 base/owner/最小范围再派；本次角色刷新不直接实施，也不把已恢复生产重复部署作为前置。
- 隔离分支 `fix/spray-progress-20261014` 的 `c5d98d0` 测试 + `8be8ac1` 文档可核接收；45项测试已PASS，无业务修改。OCR prepare 为 NO_REVIEWABLE_FILES_OR_DUPLICATES/NOT_EVALUATED，零模型调用，不冒称 OCR PASS。主仓用户脏改动保留，未经核验不覆盖 HANDOFF。

## 保持的范围与停止点

- UI TASK-16C/16D 和其他 DEFERRED 任务仍暂停；本轮“原来的收尾”不等于恢复所有后续需求。
- 大包算法优化由 `/home/wang/work/ros2_slice` 负责人先交付。平台逐帧落盘/流式进度/参考图复用/并发/模型参数优化当前均不开发不部署；收到交付后再据固定接口/样本适配。旧“新进度仍开发中”描述已被用户后续暂缓指令覆盖。
- 旧强审 grant REVOKED，不续用、不自动付费调用。后续必要代码变更按唯一 OCR 入口及适用测试/按需强审规则；已接受代码不重烧，上次 OCR 例外不永久延续。
- 原5分钟错峰巡检、独立observer、协调者20分钟/08点报告、个人11/15/18及21–08静默保持。已有在途角色只排 pending，在安全点接续，不杀、不清锁、不重复启动。
- 7个有效输入逐一终态/独立验收和1个无效输入拒绝追溯齐全才允许全批DONE；12S-D真阴性、真实采集车等外部缺证单独保留，不用批次完成冒充全部验收完成。

证据：`doc/analysis/spray-batch-progress-20261014/REPORT.md`、binding-repair.jsonl、live-step-repair.json、production-snapshot.json及批次 codex-repair-receipt-20261014.md。角色/定时实际状态见 `inbox/coordinator/POST-SPRAY-CLOSEOUT-20261014/role-audit.json`，不能把已配置说成已ACK。
