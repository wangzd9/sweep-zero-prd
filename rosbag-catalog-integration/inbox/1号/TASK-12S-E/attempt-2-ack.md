# TASK-12S-E attempt-2 R1 返修 ACK（执行者 A，2026-10-15 08:55 +08:00）

- **派单**：`inbox/1号/TASK-12S-E/attempt-2-r1-rework-dispatch.md`（协调者 08:52 DISPATCHED）
- **task/attempt**：TASK-12S-E / attempt-2（R1 最小返修，OCR 纠正级 E-R1~E-R8）
- **owner**：执行者 A
- **base**：`b39a3ec`（attempt-1 冻结 head，已实测 `wt-01-t12se` HEAD=`b39a3ecc`，分支 `a/task-12s-e-auto-bind`，工作区干净仅 `.venv` untracked）
- **分支/worktree**：延续本任务专属 `a/task-12s-e-auto-bind` @ `/home/wang/.local/state/rosbag-scene/wt-01-t12se`（返修按协议延续本任务分支，不回退/改写 attempt-1 已交付行为）
- **范围确认**：`app/services/pending_binding.py`（E-R1~R5）、`app/services/scene_schedule_consumer.py`（E-R6）、`app/services/source_service.py`（E-R7/R8）、`tests/test_task12se_auto_bind.py` 与 `tests/test_pipeline_api.py:177` 夹具修正及新增用例；不扩需求
- **约束确认**：VLM/模型调用=0；不碰 1012 大包取消链、生产库/处理机/NAS 生产路径、16C 已合入面；真 MySQL 8.4.11 独立探针库（用完即毁）隔离验证
- **核对**：OCR 更正版裁决 `reviews/TASK-12S-E/ocr-run-20261014-retry1/ocr-verdict.md`（08:52）已逐条对照冻结代码核实：8 点位行号/口径与裁决一致（含 `upsert_bag` 落库相对段口径、`derive_root_id_for_ready` 恒受控根、`test_pipeline_api.py:177` 异常口径夹具 `relative_path="/test/incoming/bag-moved"`）
- **在途核对**：claim 前 ps 实测无 pytest/ocr 业务进程；A 无在途租约/在途开发；B 的 12S-F 按 supplement 在途（文件边界不同，不冲突）
- **状态**：ACCEPTED，开工