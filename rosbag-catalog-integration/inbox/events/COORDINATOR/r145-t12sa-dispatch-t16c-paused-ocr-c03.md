{
  "event_id": "coord-r145-t12sa-dispatch-t16c-paused-ocr-c03",
  "occurred_at": "2026-10-13T11:37:14+08:00",
  "recorded_at": "2026-10-13T11:37:14+08:00",
  "role": "COORDINATOR",
  "task": "TASK-12S-A",
  "attempt": "1",
  "status": "DISPATCHED",
  "summary": "r145 实质轮（11:25 TODO 变更=16C 用户暂停+§9 v0.5 状态表）：①派单 12S-A attempt-1 给 A（base 6fb42c4，DTO source_metadata scene-input/v1+API+快照独立 hash+scene-spray profile 种子，禁新迁移，AC-18.1/2/3，含真 MySQL 隔离库自测）；②16C 裁决=OCR 链跑完取证、C5/C7 返修单随暂停搁置不派（c03 11:28:51 收口 rc=0 4 findings=C7 medium 时间契约 CORRECTION 候选+3 low）；③16B 第 8 次等待器 11:19:22 重置循环在途（11:18:49 首窗 ABORT 核）；④强审授权 11:33:12 到期（累计 2/5 在途 0，无新增调用）；12S-B 素材 7 图缺失不派、12S-C 维持 WAITING。",
  "evidence": "inbox/1号/TASK-12S-A/attempt-1-dispatch.md; ~/.hermes/cache/scratch/t16c_ocr/t16c_ocr_progress.txt c03 行+t16c_c03.log; strong_review.py status EXPIRED; TODO.md r145 注记",
  "next": "核 A ACK/开工；16C OCR c04-c07 取证；16B 第 8 次收口核 rc；恢复决定等用户"
}
