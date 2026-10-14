# ACK：TASK-10 attempt-1 目录→坡道切片→数据库→API 获取真实工程闭环（P0 收尾单）

- status: ACCEPTED
- 派单路径：`inbox/2号/TASK-10/attempt-1-dispatch.md`（21:57 DISPATCHED）
- task/attempt：TASK-10 / attempt-1
- owner：2号（B）
- base：main `ca8730d`（= origin/main，22:03 fetch 双核一致实测）
- 分支/worktree：新建 `scene/task-10-e2e` @ `wt-04a-t10`（.venv 软链主仓）
- ACK 时间：2026-10-11 22:0x +08:00（cron poll 回合）
- 范围确认：端到端四步走正式服务链（03B 登记+配置冻结→04B 真实 VLM 切片→06B 发布+数据库登记→API 获取+原包不变校验）；样本 row19（或换 1 袋，VLM ≤1 袋）；不写 NAS 业务目录、不动 VLM 服务；发现缺陷定位回派不跨模块改码；回归 SQLite 定向+全量(ignore devflow)+ruff+涉库面真 MySQL 隔离库。
- 停止条件确认：四步全绿+回归全绿+隔离资源 0 残留+回执/报告落盘；VLM 500 帧命中且无替代袋时换袋一次，仍失败 BLOCKED 回执。
- 长任务安排：端到端驱动脚本后台进程执行，sessions/B.md 记录 PID/日志/检查点后释放控制租约，后续巡检核查不重复启动。
