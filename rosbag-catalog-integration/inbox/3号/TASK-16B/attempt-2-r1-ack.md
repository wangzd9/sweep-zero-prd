# ACK：TASK-16B attempt-2-r1

- status: ACCEPTED
- 派单：`inbox/3号/TASK-16B/attempt-2-r1-dispatch.md`（2026-10-13 13:1x 落盘，status=DISPATCHED）
- task/attempt：TASK-16B / attempt-2-r1（一次最小返修，OCR 第9轮 `40e90fea` 7 findings 全 CONFIRMED）
- owner：C（16B 交付 owner）
- base：`0208a73`（16B 冻结 head）续 commit；只动 `scripts/scene_host_proxy.py` + `tests/test_scene_host_proxy.py` 回归
- 分支/worktree：延续本任务分支 `c/task-16b-scene-host-proxy` @ `/home/wang/.local/state/rosbag-scene/wt-03b-t16b`（HEAD=`0208a73` 干净，本轮核实）
- 修复范围：H1 try_reserve 返回值（:903）、H2 终态 post 跳过（cur 刷新，DONE+FAILED 分支）、H4 RESOLVING except 过窄、H5 config_hash 冻结值 fail-fast（entry 不存提交参数，取 fail-fast 下限并在回执说明）、H6 原子写 fsync（:182-186）、L1 _report_step_single steps 按 attempt 过滤
- ACK 时间：2026-10-13 13:2x +08:00
- 停止条件：六处修复+回归全绿（pytest 定向 + ruff + compileall）+ 零越界 diff → 冻结交付，回执 `receipts/TASK-16B/attempt-2-r1.md` REVIEW_PENDING
