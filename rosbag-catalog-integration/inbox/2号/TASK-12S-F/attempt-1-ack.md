# TASK-12S-F attempt-1 ACK（执行者 B，2026-10-15 08:44 +08:00）

- **状态**：ACKED。
- **派单**：`inbox/2号/TASK-12S-F/attempt-1-dispatch.md`（协调者 2026-10-15 08:38 派单，REQ-21 / AC-21）。
- **task/attempt**：TASK-12S-F / attempt-1。
- **owner**：执行者 B（cron poll 6f7471d8747c，owner `cron-b-poll-6f7471d8747c-20261015-083752`）。
- **base**：`b39a3ec`（TASK-12S-E 已接受冻结 head）。可达性核实：`git cat-file -t b39a3ec`=commit，`git log --oneline -1 b39a3ec` 一致；main `16a154f` 祖先链在案。
- **分支/worktree**：`b/task-12s-f-input-reject` @ `/home/wang/.local/state/rosbag-scene/wt-04a-t12sf`（新建，与已释放 16C-B worktree 不复用）；worktree 洁净核实：`git status --porcelain` 仅 `.venv` 软链（未提交，不入库）；`.venv` 软链主仓 venv。
- **边界确认**：
  - 只写派单范围文件：`app/scanner/{runner,metadata,state_store,backend,clients}.py`、`app/services/ingest_service.py`、`app/api/ingest_submissions.py`（+ 必要 `app/api/sources.py` 上报端点）、models/单头迁移（若持久证据需增量 schema，最小 DDL 差异先交协调者核兼容）、对应测试。
  - 不动 16C 界面已合入面（main `16a154f` 文件）；不改 E 已接受行为语义（`pending_binding.py` 只读消费其扫描、不修改其接线）；VLM/模型调用=0（纯控制面）；不碰 1012 大包取消链、生产库/处理机/NAS 生产路径。
  - 本地隔离验证=真 MySQL 8.4.11 独立探针库（用完即毁）；SQLite 绿不算数。
- **开工时点**：2026-10-15 08:44 +08:00（本 ACK 落盘即开工）。
- **在途核**：ps 无 B 侧 pytest/ocr/scene 在途业务进程；leases 无他人持 B 租约；无既有 12S-F ACK/回执。
- 控制租约：本 ACK 写后 release；开发长任务以 worktree commit/检查点续写 sessions/B.md。