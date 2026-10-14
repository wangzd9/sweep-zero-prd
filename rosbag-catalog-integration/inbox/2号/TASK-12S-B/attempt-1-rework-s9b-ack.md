# ACK：TASK-12S-B attempt-1-rework 追加 S9（帧映射契约）

- status: ACKED
- ACK 时间：2026-10-13 16:0x +08:00（2号会话，前端功能开发群）
- 派单口径：`attempt-1-rework-s9b-dispatch.md`（r163），两份 S9 单（r159 addendum 标 SUPERSEDED + r160 dispatch）以本单口径合并执行
- 工作树：`wt-04a-t12sb`（HEAD=0320a8e 冻结干净，base f62a29c），.venv 软链主仓
- 范围确认：只动 `app/scene/spray/*` 与 `tests/test_spray_*`；不改 pointcloud 路线语义/采样/阈值/参考图；续 `0320a8e` commit 冻结 `s9_head`
- 收口链：交付 → 协调者机械核验 → 增量 OCR 覆盖 f62a29c..s9_head（16 条+S9 同一次审）→ TESTER 增量复验 → 合入
- 镜像 `rosbag-spray-runtime:20261013` 已就位可实跑真实小包 1184→44
- 时间压力已知：19:00 受控生产首包排程依赖 12S-B 合入，争取 16:30 前交付