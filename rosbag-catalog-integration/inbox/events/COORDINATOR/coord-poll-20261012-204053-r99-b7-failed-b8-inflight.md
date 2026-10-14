event_id: coord-poll-20261012-204053-r99-b7-failed-b8-inflight
role: COORDINATOR
task: TASK-07B
attempt: 1
status: OCR_INFLIGHT
time: 2026-10-12T20:47:00+0800
summary: r95 detached 串行 OCR 核账：b7 bag-search.css 第 1 次 FAILED（RC=1，250s，session daa45a1c，usage 109893 tokens/14 工具调用，瞬态故障非 LLM 超时）；b8 bags.html INFLIGHT（20:39 起 node pid 508962，detached 父 pid 464164 存活，flock 持 inbox/ocr.lock）。重试政策更新=b8-b10 后低负载期 b5 --resume 81a66282 与 b7 --resume daa45a1c 各最后一次，再失败挂 NEEDS_REVIEW 冻结 07B 合入门禁，不无限重试。
evidence: scratch/t07b/ocr/remaining_progress.txt; reviews/TASK-07B/attempt-1/ocr-batches.md
next: r100+ 核 b8-b10 收口→低负载期 b5/b7 resume 各最后一次→b3 medium 裁决→强审查 pack（授权 0/5 至 2026-10-13 11:33:12）→合入→TESTER 验证→07B DONE→派 07C