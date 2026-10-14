status: ACCEPTED

# ACK：TASK-08 attempt-1（模块联调、故障与兼容）

- 派单路径：`inbox/2号/TASK-08/attempt-1-dispatch.md`（2026-10-11 15:24:57 落盘）
- task/attempt：TASK-08 / attempt-1
- owner：执行者B（cron `cron_6f7471d8747c_20261011_152753`，会话 B）
- 固定 base：main `62a85bfb6b3791ebfa706cce0125bb217635126f`（fetch 实测与 origin/main 双核一致）
- I-1 状态核对：`inbox/1号/TASK-05/i1-fixture-uid-dispatch.md` 与 TASK-08 派单同批 15:24:57 落盘，ACK 时（15:31）未合入 main（HEAD 仍 `62a85bf`），1号 `wt-01-i1` 已在该 base 建分支 `scene/task-05-i1-fixture-uid`（空提交基线，未开工交付）→ 按派单口径：本单 base 维持 `62a85bf`，I-1 回归验证项在联调中动态核对——若 I-1 已合入则以合入 commit 为准 rebase 复核 alembic 单头并跑 `tests/test_scene_slice_scheduling.py` 文件级真 MySQL；未合入则在报告中注明。
- 实际分支/worktree：新建 `scene/task-08-integration` + 独立 worktree `/home/wang/.local/state/rosbag-scene/wt-04a-t08`（不动在冻 worktree；wt-04a 系列冻结交付保留）
- ACK 时间：2026-10-11 15:31 +08:00
- 环境预检：本地 mock 栈 `rosbag-catalog-local-*` 在跑（backend/frontend healthy，29h）；真 MySQL 8.4 隔离容器 `r2i6-mysql` 已销毁 0 残留，无冲突资源
- 开工动作：ACK 落盘 → 建 worktree → 全链路联调（local stack + 真 MySQL 8.4 隔离库，用完即毁）→ 故障并发/兼容/小规模检查 → 报告+回执 REVIEW_PENDING；不改业务代码，失败记录回派