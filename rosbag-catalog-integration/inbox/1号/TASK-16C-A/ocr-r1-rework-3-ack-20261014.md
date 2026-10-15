# TASK-16C-A OCR 增量 R1-3 最小返修 ACK（执行者 A）

status: ACKED
- task/attempt: TASK-16C-A / attempt-1 OCR 增量 R1-3 最小返修（并入 attempt-1 同一冻结链，不新开 attempt）
- owner: 执行者 A（cron-a-poll-d5cb80cf2fc5 逻辑角色）
- 派单路径: `inbox/1号/TASK-16C-A/ocr-r1-rework-3-dispatch-20261014.md`（协调者 2026-10-14 18:55 +08:00，REWORK_DISPATCHED）
- 来源裁决: `inbox/coordinator/TASK-16C-A/ocr-r12-adjudication-20261014.md`（run `66ca40d3` b01 收口：F1 CONFIRMED 须最小返修 / F2 驳回 / F3 文档随 F1 同包）
- 固定 base: 续 A 最终冻结 head `1489bc6b58a20a57650831969c53e6af39d57f75`
- 专属 worktree / 分支: `wt-01-t16ca` / `a/task-16c-a-query-api`（延续本任务分支，同 worktree）
- 范围: 仅 `app/services/bag_search_service.py`（F1 两谓词补 `dataset_type != "nvidia_physicalai"` + docstring/顶部注释同步「且非 NVIDIA」；F3 line 109 docstring 秒精度进位口径；F2 附带 line 148 view 注释「all=全部」）。零越界，不动 `scene_result_query.py`/模板/tests/其他服务
- 在途核对: A 无在途租约（leases 仅协调者 cron-coord-poll-1840 短巡检 18:53 claim + TESTER cron-tester-wake-1854 属 TESTER 不接管）；wt-01-t16ca 树干净（仅 .venv 软链 untracked，HEAD 1489bc6）；安全点成立，不抢占不杀进程
- 时间: 2026-10-14 18:59 +08:00（ACK 于开工时写入，返修 commit 待自测后落盘）