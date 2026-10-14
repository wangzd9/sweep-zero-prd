status: ACCEPTED

# ACK：TASK-09 attempt-1（坡道真实能力与内容核验）

- 派单路径：`inbox/2号/TASK-09/attempt-1-dispatch.md`（2026-10-11 19:55 落盘，20:42 巡检感知）
- task/attempt：TASK-09 / attempt-1
- owner：执行者B（cron `6f7471d8747c`，本轮 poll 会话 `cron-b-poll-6f7471d8747c-20261011-204253`）
- 固定 base：main `0a8ca8ac49b4610580c25b15eb8a3e762ead96d6`（fetch 实测 = origin/main 双核一致，TASK-08 已 DONE 无在途漂移，与派单口径一致）
- 实际分支/worktree：新建 `scene/task-09-slope-real-verify` + 独立 worktree `/home/wang/.local/state/rosbag-scene/wt-04a-t09`（wt-04a 系列冻结交付不动；.venv 软链主仓）
- 协调者前置事实直接引用（不重探）：slope 7 行在位 `/mnt/nas_backup/data_slice/1165414093/slope/`（只读）、flat 16 行阴性对照、VLM `http://192.168.2.45:8002` 模型 ID 须完整路径、Qwen3 思考模式 max_tokens=256 图像请求 content=None 陷阱
- 范围确认：2.1 接线仅动 `app/scene/slope/vlm.py`/`adapter.py` 客户端构造路径（env `SLOPE_VLM_MODEL`、max_tokens≥2048 或 enable_thinking=False，以实测稳定优先，图像 content 非空探针实证）；2.2 真实核验（阳性 2-3 条/阴性 1-2 条/边界故障≥1/时间映射证据）落 `reports/TASK-09/`；2.3 回归（test_scene_* SQLite 定向全绿 + ruff + 06B 35 用例真 MySQL 不破坏）
- 边界确认：NAS 只读、不动 192.168.2.45 服务、VLM 调用量 ≤6 样本抽帧口径、不引入新场景
- ACK 时间：2026-10-11 20:44 +08:00
- 环境预检：ps 无本侧 pytest/scene 在途业务进程（仅 devflow_worker/两个 host_proxy 常驻，与本单无关）；control=ACTIVE、legacy_busy 空