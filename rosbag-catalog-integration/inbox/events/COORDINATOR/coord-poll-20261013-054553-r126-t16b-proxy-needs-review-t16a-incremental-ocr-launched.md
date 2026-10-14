# r126 巡检事件（2026-10-13T05:53:03+08:00）

## 状态变化
1. **16B proxy OCR = NEEDS_REVIEW（合入门禁冻结）**：b2 `scripts/scene_host_proxy.py`（968 行）拆组重试 05:40:34-05:46:11 rc=1（第 3 次外部 LLM 队列超时，session `2abf70dd`，usage 110518 tokens/budget_exceeded=false，vllm running=2/waiting=0 低负载）。r125 既定政策分支触发。
2. **16A 增量 OCR 已起跑**：`run_t16a_incr_ocr.py` detached pid 1284380（05:53:47 START，flock 持 `ocr.lock`），`--from c30f048 --to 3aee4d1` 逐文件 3 批（runner +24 / ingest_service +12 / scene_intake +6），a-runner INFLIGHT。

## 影响
- 16B 合入门禁冻结（proxy OCR NEEDS_REVIEW）；orchestrator H1/M1/M2 返修单暂缓（等 proxy OCR 解除后一次最小返修单派 C）。
- 16A 增量 OCR INFLIGHT（不受 16B 冻结牵连）。
- 07B R3 增量 OCR 排队（等 16A 增量释放 `ocr.lock`）。

## 解除条件
- 16B 冻结解除=proxy OCR 成功收口（低负载期重试或用户裁决部分接受）。
- 16A 增量 OCR 收口=3 批全 rc=0 无 CORRECTION 级。

## 证据
- `~/.hermes/cache/scratch/t16_ocr/b2_split_progress.txt`（05:46:11 DONE rc=1）
- `~/.hermes/cache/scratch/t16_ocr/b2_split.log`（LLM retry 2 of 9 cancelled, budget_exceeded=false）
- `~/.hermes/cache/scratch/t16_ocr/t16a_incr_progress.txt`（05:53:47 START a-runner）
- `inbox/ocr.lock` fuser=pid 1284380
