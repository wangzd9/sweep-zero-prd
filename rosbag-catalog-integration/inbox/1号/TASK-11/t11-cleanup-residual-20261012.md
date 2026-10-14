# TASK-11 残留最小清理（裁决 1 清理链接续，非业务派单）

- task: TASK-11（生产门禁项）/ attempt: 0（观察与清理链接续，不占开发槽）
- base: main `453da0c`（不变）；本单零 app 代码面，只清 T11 测试残留
- 背景（协调者 08:31 轮独立核验）：A 08:27 清理申报 `a-t11-ruling1-stop-clean-done-20261012` 经核 T11 口径全部达成（scene_segment/scene_analysis_version/bag_derivation/bag_scene_label_evidence/ingest_submission/purpose_schedule_event 均 0，incoming 两袋副本 absent，驱动文件已删，ps 无 t11/launcher/real_e2e 存活，无第 9 跑）；**发现 1 处残留缺口**：第 8 跑在 NAS 测试根留下的两个 ready/ 袋目录未清，本地栈 scanner 于 08:30:51 将 slope 袋重新登记为 `bag_record` id=26（uid `021F73162DAE4E3188B10BE7FE`，status READY / source_status READY），bag_record 17→18。
- 动作（最小、严格限 T11 口径）：
  1. 删除 `/mnt/nas_backup/vla_dataset_builder_test/ready/1165414093_slope_20260818_105105_105120/` 与 `/mnt/nas_backup/vla_dataset_builder_test/ready/1165414093_flat_20260818_105143_105201/`（仅这两个第 8 跑袋目录，合计约 516MB；ready/ 目录本身与其余既有袋保留）。
  2. 删除 `bag_record` 中 uid `021F73162DAE4E3188B10BE7FE` 行（id=26）及其关联 `bag_file`/`bag_topic`/`bag_purpose` 行；仅该 uid，前核后验 COUNT。
  3. 复验并写入申报：bag_record 回到 17、该 uid 查无、两个 ready/ 袋目录 absent、scene 派生各表仍 0、ps 无 t11 进程、无新驱动日志。
- 禁止：不重启本地栈容器、不再跑 T11 驱动、不动其余既有开发数据（17 行 bag_record）、不删 NAS 测试根目录结构。
- 停止条件：申报事件落盘后即止，等协调者下轮核。
- 回执/证据路径：event `a-t11-cleanup-residual-done-20261012`（events/A）。
- 派单人：协调者（cron poll 14ae4556629a，2026-10-12 08:4x）。