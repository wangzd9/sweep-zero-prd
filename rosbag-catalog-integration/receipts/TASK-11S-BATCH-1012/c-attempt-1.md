# TASK-11S-BATCH-1012 / C / attempt-1 回执（持续更新，只读观察面）

owner：C（执行者C，数据链路监控告警群）。范围：生产装配/资源/租约/进度只读观察，不重启/重部署/改挂载/迁移/起新 run/起模型；发现具体生产问题只读取证并报协调者。全程只读，不代写协调主状态。

## 收尾段：post-release-closeout-20261014（2026-10-14 10:56 +08:00，obs75 实测）

实际 source/run/attempt 与发生时间（处理机 10:43-10:52 只读取证）：

- **4acf689f 正式链**：`scene-4acf689f9a6a473da1fa2f2efc70`，source `91FFEEC1…`（16_02_03），submission `24d60fee…`，attempt=1，frozen_at 2026-10-13T23:05:30。8180 实测 **SCENE_RUNNING，正式八步=PRECHECK DONE / EXTRACT DONE / INFER RUNNING / PUBLISH・REGISTER・SEGMENT・VALIDATE・WRITE QUEUED**（口径按收尾卡更新，不再称八步全 QUEUED；obs74 前全 QUEUED → 10:23 回执步骤补报后翻面）。error_message 空、lease_owner=platform-local、lease_expires_at 2026-10-14T10:53:44（10:51 查点 heartbeat 续租活跃，无 4 连败升级条件）。
- **flat 三提交绑定恢复闭环**（obs74 申报项，10:23 Codex 回执后 C 独立复测）：ingest_submission mysql 实测 `a65a25a7`→source `FFDEE943…`、`87dfebaa`→`9C9456B6…`、`518089ed`→`205E5054…`，全部 **SCHEDULED**（updated_at 2026-10-14 10:23:08/09，obs74 实测 PENDING_INPUT/source NULL/updated 停 23:24:09 已解除）；`24d60fee`→91FFEEC1 不变；复用终态 run 对账（a4824f1c SUCCESS / eb4397c3・24ab78bb NOT_APPLICABLE 零模型）归 TESTER 独立验收面，C 不代核。
- **16_33_10 空包**：submission `7a71e404` 实测仍 **PENDING_INPUT / source NULL**（updated 2026-10-13 21:23:36）=输入校验拒绝链正常口径（scanner 持续 `missing rosbag2_bagfile_information` 可追溯）；提交层终态隔离修复在隔离树 `fix/spray-progress-20261014` 未部署，不生效在途属预期，跟踪待部署面。
- **代理进程自身 socket**：8767/health ok，active_runs=[scene-4acf689f ACCEPTED pid1] 唯一在途；proxy 宿主 pid 3495931 LSTART Tue Oct 13 20:22:38 连续未重启、ELAPSED 14:29:10、TIME 01:22:05（自 09:2x 起每轮 +5~12s 持续非零）、RSS 18084068 同量级；VLM 通道容器 `3376cd90f44e` /proc/net/tcp 实测 **1 条 ESTAB** 8602A8C0:BB60→2D02A8C0:1F42（192.168.2.45:8002）。
- **模型活跃直证**：llm-server `/tmp/vllm_qwen38.log` 10:51:10-10:52:00 六点十秒采样 Running 3-4 reqs、Waiting 前四点=1 末两点=0（**非持续>0，不命中升级条件**）、prefix cache 95.6%、MM 88.5%、gen 63.7-187.0 tok/s=INFER 推理活跃续证。
- **完成帧数/ETA**：**未知**——work 树 `checkpoint.json` mtime 2026-10-14 00:23:10.474817688 +0800 未翻、`find -newermt '2026-10-14 10:00'` 零新写；旧代理无逐帧持久计数（缺陷面已记录，修复在隔离树未部署），模型全局 Running/POST 200 不等于该 run 完成帧计数，如实写缺证。
- **磁盘/NAS 与原功能健康**：NAS `//192.168.2.77/public` 98T/70T/29T **71%** 不变、load 4.46/3.84/3.08（较 obs74 1.26 抬升，C 未起任何进程，如实归因 INFER+VLM 活跃段）、incoming/spray 仍仅 `16_33_10` 空包目录、18000 ready=production（前轮口径，本轮未变探）。
- **升级条件核查**：heartbeat 4 连败=否（续租活跃）/run FAILED=否/VLM Waiting 持续>0 且无 ESTAB=否（Waiting 回落 0 且 ESTAB 在途）→ **不命中，大包继续跨跑不 kill/retry**。

C 全程只读命令：ssh `processing-machine` curl 8180/8767、docker exec mysql SELECT（stdin 口径）、docker exec cat /proc/net/tcp、ps/stat/find/df/uptime/ls；ssh `llm-server` 读 vllm log。未 kill/未删/未重启/未 retry/未改任何生产路径。

下一步：① 4acf 模型段完成信号（checkpoint 翻面/INFER→DONE/后续步骤推进/SCENE_DONE）取证申报；② 16_33_10 提交层终态=隔离树修复待部署面跟踪；③ 11:00 时段总结照常，白天状态变化即时通报。