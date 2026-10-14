# OCR 批次账：TASK-08 c3-lineage（c3-1）

## R1-r1

| 字段 | 内容 |
|---|---|
| batch_id | R1-r1 |
| task / attempt | C3-lineage / c3-1 |
| base / head | f9bafb0 / f656507（固定快照） |
| 入选文件 | `tests/test_scene_slice_lineage.py`（+14/-4）— default_path 排除，**0 app 侧入选** |
| 排除依据 | `ocr review` default_path 排除 tests/*（纯测试交付，独立验证=协调者 SQLite 复跑 + 1号真 MySQL 隔离库证据） |
| run_id / session | ocr session `df3efba6-d894-453e-9223-cf81d4e87767` |
| 时间 | 起跑/收口 2026-10-11 17:01（约 0s，0 入选跳过） |
| process | 协调者 cron 后台 terminal `proc_49620a4ca5bd` pid 2454065，持 `inbox/ocr.lock` 稳定 inode，收口已释放 |
| status | COMPLETED（Review skipped: no items selected — 与 I1-r1/R8-r1/R9-r1 纯测试交付先例同口径，非故障） |
| findings | 0 |
| verified_decision | 纯测试 0 入选=预期；合入门禁放行 |
| result | log `~/.hermes/cache/scratch/c31-ocr-r1.log` |