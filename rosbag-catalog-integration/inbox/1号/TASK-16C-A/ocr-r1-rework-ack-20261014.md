# TASK-16C-A OCR 最小返修 ACK（执行者 A）

status: ACKED
- task/attempt: TASK-16C-A / attempt-1 OCR 最小返修（并入 attempt-1 同一冻结链，不新开 attempt）
- owner: 执行者 A（chat `oc_a2b2bc6b8a261371ff713d1b2a2aff6c`，cron-a-poll-d5cb80cf2fc5 逻辑角色）
- 派单路径: `inbox/1号/TASK-16C-A/ocr-r1-rework-dispatch-20261014.md`（协调者 2026-10-14 16:42，REWORK_DISPATCHED）
- 来源裁决: `inbox/coordinator/TASK-16C-A/ocr-merge-ruling-20261014.md`（初 run `7a72eed8` + 唯一入口补审 `0aba25ee` 16:24 收口全覆盖；两条 CONFIRMED 均 low）
- 固定 base: 续 `ff2a0055c75655f2f91f273a80af99633c9fbebf`
- 专属 worktree / 分支: `wt-01-t16ca` / `a/task-16c-a-query-api`（延续本任务分支，同 worktree）
- 范围: 仅 `app/services/bag_search_service.py`（A-OCR-1 删 `data_kind_case()` 死函数 + A-OCR-2 `scene_original` 谓词补 `~_scene_slice_pred()`）
- 在途核对: A 无在途租约（leases 仅协调者自身短巡检，`ocr` 进程为协调者 TASK-16C-B 面非 A）；安全点成立，不抢占不杀进程
- 时间: 2026-10-14 17:15 +08:00（ACK 于开工时写入，返修 commit 17:15 落盘）