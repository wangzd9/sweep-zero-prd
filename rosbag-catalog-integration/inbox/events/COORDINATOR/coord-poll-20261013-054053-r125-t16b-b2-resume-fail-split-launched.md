# coord-poll-20261013-054053-r125-t16b-b2-resume-fail-split-launched
- role: COORDINATOR
- poll: 14ae4556629a r125
- checked_at: 2026-10-13T05:35:53+08:00
- task: TASK-16B
- attempt: 1（OCR 批次 resume 链收口 + 拆组重试）
- status: T16B_B2_SPLIT_RETRY_INFLIGHT
- summary: 16B resume 链 05:36:15 全收口——b1-orchestrator resume 235dac12 rc=0（3 findings 全 CONFIRMED，r123 已裁决）；b2-proxy resume e2b8a607 rc=1（新 session 10b08d5e，LLM 队列超时再复现，无已审成果）→ r118 落账政策第 1 次拆组：proxy 968 行 fresh 起跑 --max-tokens 20000，detached pid 1266766 05:40:34 持 ocr.lock，硬截止窗 06:00-06:20；再 rc=1 挂 NEEDS_REVIEW 冻结 16B 合入门禁（16A 不受牵连）。
- evidence: ~/.hermes/cache/scratch/t16_ocr/t16b_resume_progress.txt; t16_ocr/resume_b2-proxy.log; t16_ocr/b2_split_progress.txt; reviews/TASK-16/16A-16B-ocr-batches.md r125 段
- next: r126 核 b2 拆组收口 → rc=0 派 16B 合并返修单 / rc=1 挂 NEEDS_REVIEW + 16A 增量 OCR 接锁
