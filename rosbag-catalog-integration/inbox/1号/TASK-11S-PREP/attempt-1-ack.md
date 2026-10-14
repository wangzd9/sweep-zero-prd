# ACK：TASK-11S-PREP attempt-1 水雾生产首包发布准备（执行者 A，2026-10-13 15:0x）

- **派单**：`inbox/1号/TASK-11S-PREP/attempt-1-dispatch.md`（协调者 r159，2026-10-13 14:5x，消费 SPRAY-1900 notice 调度调整 #3）
- **task/attempt**：TASK-11S 发布准备子项 / attempt-1
- **owner**：执行者 A（1号）
- **base**：main `0e9a2df`（纯文档 tip，最后业务基线 `6fb42c4`；派单指定口径，fetch 后实测 origin/main=`0e9a2df`，祖先链含 `6fb42c4`）
- **分支/worktree**：新建 `a/task-11s-prep` @ `wt-01-t11sp`（/home/wang/.local/state/rosbag-scene/wt-01-t11sp，HEAD `0e9a2df8` 双核一致）；不触碰 12S-A 冻结 worktree `wt-01-t12sa`、16C/16B/16A 各域
- **时间**：2026-10-13 15:0x +08:00
- **状态**：ACKED → RUNNING（生产只读预核 / 隔离迁移实验 / 车辆登记入口核对 / 首包路径面 / 维护窗口清单 → 交付 `deploy/scene/*` 冻结 commit + 回执 `receipts/TASK-11S-PREP/attempt-1.md`，**17:15 前**）
- **硬边界确认**：零生产写入/零部署执行/零服务重启/零迁移生产库（生产面全只读，SSH 无免密 sudo 只用 docker/只读命令）；不碰 `app/scene/spray/*`（B 返修在途）、`scripts/scene_host_{proxy,orchestrator}.py` 本体（C 域，模板只引用不复制）、16C 冻结面；不建 cron/长驻进程，隔离 mysql:8.4 容器用完即毁申报 0 残留；本单完成≠授权发布（11S 本体 G1–G6 门禁与用户 17:30 放行面不变）
- **在途申报**：12S-A attempt-1 交付冻结 `77c395b` REVIEW_PENDING 在 OCR 排队，与本单 worktree/文件域零交集，不重复自测不移动该 HEAD