# ACK：e2e-reverify-v2（TASK-10 / attempt-2，#3 合入后全链取证）

- status: ACCEPTED
- ACK 时间：2026-10-12 01:57 +08:00（TESTER cron poll 2026-1012-015453）
- 被测快照：main HEAD `453da0c1d88f` = origin/main fetch 双核一致（#1 `277e40f` + #2 `d4719f6` + #3 `453da0c` 均在 main；`git log` 独立核三笔 merge 在位）
- v1 作废确认：attempt-1 被测 `a77aa45` 不含 #3，其 FAIL 证据（defect3 409 / 驱动 :385 NameError）仅作定位材料，v2 结果独立出具
- 驱动核实：`scratch/t10_e2e_reverify.py`（mtime 01:51，协调者已按 #3 申报补 step4 `SlicePublishSpec(actual_start_ns/actual_end_ns)`，:336-342 独立核）；step5 已用 `child_uid` 无 NameError；fresh SQLite（t10-e2e.db 起跑前 unlink）+ 独立 app 实例（主仓 453da0c 代码面，非旧镜像）+ 真实 VLM `192.168.2.45:8002/v1/chat/completions`
- 现场核实：真实袋 row19 `/mnt/nas_backup/data_slice/1165414093/slope/1165414093_slope_20260818_105105_105120` 7 文件在位（只读，前后 hash/mtime 校验对象）；v1 证据已归档 `scratch/t10/v1-attempt-1/`；无 t10/ocr 存活进程、docker 无 tester/t10 残留
- VLM 袋数口径：v2 单袋（row19），累计 v1+v2=2 袋，不超派单上限
- 长验证检查点：驱动后台起跑（pid/日志见 sessions/TESTER.md），日志 `scratch/t10/t10-run.log` + `t10-reverify-driver.out`，证据 `scratch/t10/t10-e2e.json`；巡检只核查不重复启动
- 交付：`test-receipts/TEST-TASK10-e2e-reverify/attempt-2.md`（PASS/FAIL + 全链四步证据 + 原包 ALL_UNCHANGED + VLM 袋数 + 隔离资源 0 残留声明）