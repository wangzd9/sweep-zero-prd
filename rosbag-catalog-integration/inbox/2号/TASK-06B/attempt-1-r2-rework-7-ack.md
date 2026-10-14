---
task: TASK-06B
item: attempt-1-r2-rework-7
owner: 2号
status: ACCEPTED
ack_by: 执行者B（cron poll）
ack_at: 2026-10-11T11:04:11+08:00
dispatch_path: inbox/2号/TASK-06B/attempt-1-r2-rework-7.md
base: main 4697be0
branch: scene/task-06b-codex-rework7
worktree: /home/wang/.local/state/rosbag-scene/wt-04a-r7
---
# 2号 ACK：codex 第四轮 2 条非阻塞小修（R-03 时钟固定 [low] + 注释精确化 [info]，同单 2 项行级）

已接收并开工。执行者 B 新建本任务专属分支/worktree（`scene/task-06b-codex-rework7` / wt-04a-r7，base main `4697be0`），不占第二任务、不 reset 他人工作；rework-6 交付 `f4cd654` 已在 main 祖先链冻结，本轮在其上游续开。

计划最小行为（逐条对应裁决 `reviews/codex-r7-rework6-20261010-verdict.md`）：
- **[low] R-03 同秒窗口时钟固定**：`tests/test_scene_result_report.py` :993 附近「同秒」重放用例改为固定首放与同秒重放的时钟（patch 服务内 `local_now` 到同一整秒时刻），消除恰逢真实墙钟秒边界时实际跨秒的 flaky 风险；跨秒窗口沿用 :1013 已有的 patch 写法（同秒窗口→显式推进一秒→跨秒窗口），与 R-03 既有零 UPDATE 断言口径对齐。
- **[info] 注释精确化**：rework-6 新增注释「纳秒末 ≥约 1ms 向上取整」改为与实际根因一致的表述（接近秒末时浮点/datetime 舍入已进位、microsecond=0 无法恢复），指向探针实测事实（半秒 5e8 旧实现仍留前秒，进位发生在近秒末舍入而非固定 1ms 阈值）。

验证口径（按派单）：两条用例定向 + SQLite 全量不回归（预期 825 passed / 3 failed = test_devflow 沙箱环境性=main 基线同集 / 10 skipped）+ ruff 绿。交单单 commit（`4697be0` 之上，仅测试文件 2 处，app 服务文件不动）+ 回执 + 群内通报；OCR 不自跑、不自行合入、不自行强复审。