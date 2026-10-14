# 派单补充：TASK-12S-B attempt-1-rework 追加 S9（帧映射契约，0320a8e 漏项）

- status: DISPATCHED
- 派单时间：2026-10-13 15:3x +08:00（协调者 r163）
- 背景：B 的冻结 `0320a8e`（15:18）已含 16 条 OCR findings 全修（协调者核验 40 passed+ruff 绿），**但 S9 未含**——`decode.py:270` 仍是 `if len(pc_ds) != len(src_msgs):`，真实包（1184 消息/44 is_last_scan 帧）上必 DECODE_FAILED。原因：S9 双份单（本目录 `attempt-1-rework-s9-dispatch.md` r160 与 `attempt-1-rework-addendum-S9.md` r159，后者标 SUPERSEDED）在 B 执行面未进入 ACK 覆盖。**两份单均以本单口径合并执行，B 无需区分来源**。

## S9 [HIGH·CORRECTION] packet 路线帧映射契约（decode.py，续 `0320a8e` commit）

1. **帧边界**：以 `is_last_scan` scan 结束消息为帧边界建立可追溯映射；每帧记录参与的 DB3 文件、message id 范围
2. **源 ns 口径**：每帧源 storage_ns 取该帧 scan 结束消息的 storage_ns（整数 ns 直用，**不得**用 ms 文件名近似）
3. **完整性**：跨 DB3 拼接、重复帧、缺帧、首尾不完整（首个 scan 不完整/尾部无 is_last_scan）必须明确处理并给证据
4. **禁止**：不得只删长度断言糊过去；`len(pc_ds) != len(src_msgs)` 断言本身是错误契约，替换为上述映射
5. **自测**：合成多 DB3/重复/缺帧/首尾不完整矩阵 + 真实小包 1184→44 映射断言（只读 bag，镜像 `rosbag-spray-runtime:20261013` 已就位可实跑）
6. **边界**：仍只动 `app/scene/spray/*` 与 `tests/test_spray_*`；不改 pointcloud 路线语义（其 1:1 映射已在原契约）；不改采样/阈值/参考图

## 交付
- 在 `0320a8e` 上续 commit 冻结 `s9_head`，回执更新 `receipts/TASK-12S-B/attempt-1-rework.md`（S9 段：映射设计+真实包断言证据+回归表）
- 收口链：协调者机械核验 → 增量 OCR 一次覆盖 `f62a29c..s9_head`（16 条+S9 同一次审，固定入口排队 12S-A OCR 后）→ TESTER 增量复验（S9 真实解码/渲染探针+16 条受影响项，镜像在库实跑）→ 合入
- 时间压力：19:00 受控生产首包排程依赖 12S-B 合入（12S-C 正式接线验收=16B+12S-A+12S-B 全齐）；16:30 前交付最佳
- ACK：`inbox/2号/TASK-12S-B/attempt-1-rework-s9b-ack.md`（30min 内）