# TASK-11S-BATCH-1012 协调者 ACK（恢复后首回合）

时间：2026-10-13 21:07 +08:00，owner=cron-coordinator-resume-20261013，协调租约 token 末4位 3c94。

- **交接已读**：`inbox/coordinator/SPRAY-BATCH-1012-20261013/HANDOFF.md` + `input-manifest.json`（8包 25119612157 字节 / ~24GB，test 车，scene-spray profile，逻辑根 `incoming/spray`，宿主映射 `/mnt/nas_backup/rosbag_scene_processing/incoming/spray`）。
- **生产基线确认**：业务 3c9c496 已上线，首包 `rosbag2_2026_10_12-15_58_23` run `scene-c4a88c0746e9422ca35136035fe7` attempt2 SCENE_DONE 已独立 PASS（submission `9949d1a7ea4f4feb8284b3cebfd4fab1`），本批复用其证据，不重跑、不重提交。
- **四份派单接受**（2026-10-13T20:58:48+08:00 已落 DISPATCHED，本轮核实内容无误）：
  - A `inbox/1号/TASK-11S-BATCH-1012/attempt-1-dispatch.md`：原始拷贝/完整SHA/幂等正式提交，唯一上传与提交 owner。
  - B `inbox/2号/TASK-11S-BATCH-1012/attempt-1-dispatch.md`：独立输入适用性与算法证据检查，只读。
  - C `inbox/3号/TASK-11S-BATCH-1012/attempt-1-dispatch.md`：生产装配/资源/租约/进度只读观察。
  - TESTER `inbox/TESTER/TASK-11S-BATCH-1012/attempt-1-dispatch.md`：正式全链逐包独立验收。
- **在途身份核**：leases 目录无 COORDINATOR/A/B/C/TESTER 在途 JSON 租约（仅 `C.lock`、`TESTER.lock` 两个 0 字节陈旧稳定锁，非在途持有）；snapshot processes 全 none；OCR 无在途 run；强审授权 REVOKED。**无冲突、无双跑**，四角色可各自 ACK 开工。
- **操作计划**（写入 `BATCH-STATUS.md` 唯一状态表）：
  1. A 先短包（15_58_23 核复用 → 16_31_25 25MB → 空包 16_33_10 验拒绝入口 → 16_00_13 90MB），staging `/mnt/nas_backup/rosbag_scene_processing/.upload-staging/spray-production-1012-20261013/<bag>` 逐文件 SHA 一致后原子 rename 入 `incoming/spray/`；大包 14_42_48 / 16_02_03(10.1GB) / 16_37_47(7.3GB) / 16_58_28(6.8GB) 用 runtime_tools.py 固定 operation 跨回合，不占模型回合等传输。
  2. 每包落位后 A 正式 `POST /api/v1/ingest-submissions`（profile_id=scene-spray，relative_path 相对 spray/，source_metadata 按清单固定）；test 先 GET 核对不重复造车；idempotency_key 由 batch/包名/完整摘要稳定派生并持久保存。
  3. C 只读核 3c9c496 装配/overlay/8767 回环/SCENE_EXEC_HOST 串行，按 run 监测批次进度；B 本机只读核各包 packet/PointCloud2 topic、多DB3边界、空包事实；TESTER 按 attempt 增量独立验收八步/血缘/获取/幂等/源SHA/旧健康。
  4. 大包可跨夜，不因观察超窗 kill/retry；空包按真实输入拒绝/隔离可追溯，不补造 metadata。
- **门禁**：不重启/重部署/迁移/改挂载；旧 16B/S9b/11S-PREP 已接受禁止重做；本批纯数据面无代码变更，无新 OCR、无强审（旧 grant 已撤销不续）；UI 继续暂停。
- **静默**：当前 21:00 起北京时间夜间静默，工作/文档照常，不主动群报；白天 08:20 起 20 分钟报告 + 08:00 夜间汇总。

下一步：A/B/C/TESTER 各自 ACK 后接续；下轮巡检核 A 短包落位与空包拒绝证据。
