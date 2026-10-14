# TASK-11S-BATCH-1012 / A / attempt-1 — ACK

- 状态：ACKED 开工，owner=A（A-batch-1012），2026-10-13T21:12+08:00。
- 派单：`inbox/1号/TASK-11S-BATCH-1012/attempt-1-dispatch.md`（DISPATCHED 2026-10-13T20:58:48+08:00，用户已明确授权本批生产数据复制及水雾全链）。
- 交接已读：`inbox/coordinator/SPRAY-BATCH-1012-20261013/HANDOFF.md` + `input-manifest.json`（8 包 25119612157 字节 / ~24GB，车辆 test，profile scene-spray，逻辑根 `incoming/spray`，宿主 `/mnt/nas_backup/rosbag_scene_processing/incoming/spray`，staging `/mnt/nas_backup/rosbag_scene_processing/.upload-staging/spray-production-1012-20261013/<bag>`）。
- 生产基线核（只读实测）：backend `127.0.0.1:18000` `{"status":"ready","environment":"production"}`；`GET /api/v1/ingest-profiles` 含 `scene-spray`（intake_root_id=scene）；车辆 `test`（id=1，2 个 Bag 已关联，`/vehicles`）已登记不重复造车；首包 submission `9949d1a7…`=SCHEDULED/bound_source `615A4A7B…`/event CONSUMED，run `scene-c4a88c07…` attempt2 SCENE_DONE（复用，不重提交）。
- 在途身份核：leases 无 A 在途 JSON（本轮 claim `A-batch-1012` token 末4 `29f1`，pid 2499583）；operations 目录不存在（无在途/UNKNOWN 操作）；`incoming/spray/` 空、staging 不存在（TESTER/C 已实测一致）→ **无冲突、无双跑**。
- 本角色范围（唯一上传/正式提交 owner）：原始拷贝→逐文件完整 SHA 核验→staging 原子 rename 入 `incoming/spray`→正式 `POST /api/v1/ingest-submissions`（profile_id=scene-spray、relative_path 相对 spray/、source_metadata 按清单固定）。先短包后长包；首包核 SHA 复用；空包按真实输入验证拒绝入口；大包用 `runtime_tools.py` 固定 operation 跨回合，不占模型回合等传输。
- 写范围：仅本任务 ACK / 上传台账 / receipt / 自身 session / 事件。不写协调者主状态表 BATCH-STATUS、不写 HANDOFF/DESIGN、不领取旧单、不重做旧 16B/S9b/11S-PREP、不改业务代码。
- 幂等键：每包一份正式 submit，idempotency_key 由固定 batch/包名/完整摘要稳定派生，持久存 `receipts/TASK-11S-BATCH-1012/upload-ledger.json`，禁止每回合换 key。
- 本轮动作（夜间静默，照常工作落盘不群报）：首包复用 SHA 核验 → 空包拒绝入口验证 → 短包 16_31_25/16_00_13 拷贝+SHA+提交 → 大包 14_42_48 起首条 frozen operation。
- 冻结快照/边界：生产业务固定 3c9c496；源目录 `/home/wang/下载/1012` 只读；不覆盖已有 incoming/ready/final，不写原包 .done/sidecar，不投旧入口。