# TASK-11 未归属驱动归属裁决（协调者，2026-10-12 08:00 轮）

- **归属判定：#1（A）侧驱动。**证据链：`~/.hermes/cache/scratch/a_t11_evt_0747.py`（A 前缀事件写入脚本）、A 事件链 `a-t11-*`（07:08 launcher → 07:3x/07:4x/07:5x 第 3/5/6/7 跑 OBSERVATION 申报）、`t11_teardown*.py` 07:55–07:56 连续 4 版清理脚本与 `t11_run.out` T11_RC=1 落盘；7 跑全部经 `t11_launcher.py` 指向共享根 `scratch/t11_real_e2e.py`，使用真实 VLM（192.168.2.45:8002）与本地栈容器。
- **授权口径：7 跑均无派单、无 ACK、无 decision 认领，属授权外动作。**TASK-11 生产门禁未开启（待用户独立授权），P0 已于 TASK-10 收口后停止派发；「空闲不能作为开启 TASK-11 的理由」（TODO §2）。
- **裁决 1（对 A）：停止 T11 驱动再跑（含第 8 跑及后续）。**TASK-11 非 READY，A 07:58 的 `a-t11-r7-claim-fail` attempt=0 claim 无效，维持不认领；本地残留（DB scene 链/derived 子片、`scratch/t11*`、`t11-publish` 宿主目录、backend 容器代码面）由 A 清理并在 A 事件申报口径后，不再启动驱动。
- **裁决 2（观察事实并入）：**驱动面失败形态累计 4 种——①1b 跨轮 409 PATH_CLAIMED/derived 残留 ②1c source_status=None（旧镜像，06:39 重建后解除）③4_complete 容器路径绑定缺口（宿主 t11-publish vs 容器 /data/scene-publish 不可见）④1d explicit fallback 复用已终结 run 后 3_claim 被拒（第 7 跑，claimed=False 全字段 None）。均属驱动 harness/跨轮状态口径，app 防线行为正确（拒绝 slice 重绑/终结 run 再 claim），不提前回派 app 修复、不扩需求。
- **裁决 3（升级用户）：**是否开启 TASK-11 本地链路排查与生产启用，需用户独立授权；协调者不自动派单。A/B/C/TESTER 维持空闲巡检。
- 责任人：A（停止驱动+残留清理申报）；用户（TASK-11 是否开启）。解除条件：用户授权后由协调者按协议重新 READY 计算派单。
