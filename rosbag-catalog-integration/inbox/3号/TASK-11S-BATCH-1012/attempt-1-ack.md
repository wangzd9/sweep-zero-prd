# TASK-11S-BATCH-1012 / C / attempt-1 — ACK

状态：ACKED，owner=C，2026-10-13T21:07:41+08:00。

- 派单路径：`inbox/3号/TASK-11S-BATCH-1012/attempt-1-dispatch.md`
- task/attempt：TASK-11S-BATCH-1012 / C / attempt-1
- owner：C（执行者C，数据链路监控告警群）
- base：生产业务固定 `3c9c496`（dev 仓库 HEAD=`63bfcf8` 纯文档领先，`3c9c496` 已在库，与 HANDOFF 基线一致）
- 实际分支/worktree：本单为只读观察，不建代码分支/不动 worktree；冻结交付树 `wt-03b-t16b`/`wt-03b-t12sc` 保持不变
- 范围：生产装配/资源/租约/进度只读观察，按 run 检查，不重启/重部署/改挂载/迁移/起新 run/起模型
- 在途身份核实：claim 前 `inbox/control/runtime/observer/C.json` pending 无 C 业务在途；ps 实测无 C 自发起业务进程；本轮 C 租约 owner `C-cron-poll-20261013-210453-t11sbatch1012-ack`（token 整体 JSON 解析）

## 首轮只读观察基线（2026-10-13T21:07 +08:00）

- 接收入口：`/mnt/nas_backup/rosbag_scene_processing/incoming/spray/` 实测为空目录（0 包）；扫描树外暂存 `.upload-staging/spray-production-1012-20261013/` 尚未创建 → **A（上传/正式提交 owner）尚未落任何 1012 包，本批 run 未启动**。
- 生产业务：`3c9c496` 已上线（HANDOFF 基线）；常驻 rosbag-scene-host/rosbag-scene-proxy 回环 8767 位于处理机，本开发机 systemd 未见该 unit（`rosbag-scene-host.service could not be found`），本宿主无 8765/8766/8767 LISTEN → **生产 scene 链跑在处理机，非本机**，C 按 run 只读核处理机状态（待 A 落包后接续）。
- 本机进程：root `scene_host_proxy.py`(pid 2377013)+`app.orchestrator`(pid 2377038) 存活（本机 Compose 栈），非 C 业务发起、不接管不动；另有 uid10001 `app.orchestrator`(pid 2448204)。
- 租约：本轮仅 C 自身短写租约，claim 前无他角色未到期在途租约需 C 接管；A/B/TESTER 各持自身巡检租约（observer pending 在案），非 C 不抢占。
- 长机械操作：本批上传/处理用 runtime_tools 冻结 spec start/status，C 观察结果/进程身份变化后接续，不阻塞模型会话承载 24GB 传输/推理。

## 停止条件 / 边界

- 不上传、不提交、不改系统配置、不重启/重部署/迁移/起新 run/起模型线；发现具体生产问题只读取证并报协调者，不预设业务修复。
- 只写自身 ACK/session/事件/回执；不写协调主状态、不领旧 16B/12S-C 单（已 DONE）。
- 大包跨夜继续，不因观察超窗 kill/retry；观察预算可延长。

ACK 落盘后 release 本轮租约；后续 5min 脚本巡检按 run/进程身份变化接续。