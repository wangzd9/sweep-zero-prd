# ACK：TASK-12S-C attempt-1 水雾正式接线（前置开发）

- status: ACCEPTED
- 派单：`inbox/3号/TASK-12S-C/attempt-1-dispatch.md`（2026-10-13 14:02 落盘，status=DISPATCHED（前置）；用户群内授权"加速"——C 修完 16B-r1 核验后无缝接本单）
- task/attempt：TASK-12S-C / attempt-1（前置口径：硬依赖未全接受，仅允许先行编码+模块自测，**禁申报正式联调 PASS**）
- owner：C
- base：main 未含 16B-r1（`40ab818` 仍冻结 REVIEW_PENDING，增量 OCR 排队于 12S-B c02 后）→ 按派单 §13:11 口径以 `40ab818` 所在链为消费基线；12S-A 用固定 SHA `77c395b`（wt-01-t12sa）、12S-B 用固定 SHA `f62a29c`（wt-04a-t12sb）做 import 级集成。回执将注明实际消费基线。
- 分支/worktree：新建本任务专属分支 `c/task-12s-c-spray-wiring` + 隔离 worktree `/home/wang/.local/state/rosbag-scene/wt-03b-t12sc`（自消费基线创建）；`wt-03b-t16b` @ `40ab818` 保持冻结只读消费，不改动。
- 读写范围：独占 `scripts/scene_host_{proxy,orchestrator}.py` 水雾派发面 + 必要 `scene_publish_service.py`/`scene_result_report` 接线 + 对应测试（§9.2 文件边界）；不改 16B 代理行为面、不改 12S-A/B 产物、不碰 16C 冻结面/07B 文件、不部署生产、不跑真链全冒烟。
- ACK 时间：2026-10-13 14:1x +08:00
- 停止条件：9.6 卡模块级自测清单全绿（含旧坡道一包恢复回归硬证据）+ 交付显式标"待接线核验" → 冻结 commit + 回执 `receipts/TASK-12S-C/attempt-1.md` REVIEW_PENDING；接口/契约冲突申报协调者，不擅改。