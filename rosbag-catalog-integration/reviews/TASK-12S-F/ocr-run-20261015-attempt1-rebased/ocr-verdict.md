# TASK-12S-F rebased OCR 初审失败裁决（协调者，2026-10-15 15:0x +08:00）

## 运行身份

- run `1fe96fde76d64a138ca3791ff8ecea19`，目录 `reviews/TASK-12S-F/ocr-run-20261015-attempt1-rebased`
- 范围：base `1e9c7de`（E attempt-2 冻结 head）→ head `96afc43`（B rebase 后 F 冻结 head）
- review_identity `4b1b109f03d0f2815530ddc5dbd75e8028785103482c8c8cbc24a54eae0da3c0`，retry_depth=0，逐文件 7 批（b01 起）
- 前身：`ef462fc8`（`b39a3ec→8c8bf2f`，合批 b01 4 文件，13:03:31 撞 3900s 单批硬截止失败，0/4 完成）

## 终态与根因（本轮独立核，非复述）

- **state=HARD_DEADLINE**（`updated_at 2026-10-15T06:19:08.87Z`=14:19:08 CST；14:40 脚本扫描进入 pending 唤醒本轮）。
- b01（`app/services/ingest_service.py`，+179 行，单文件批）`started_at 05:14:07Z` → `ended_at 06:19:08Z`，**duration 3901.49s，rc=1**，撞外层单批 3900s 硬截止。
- b01-diagnosis：`coverage_complete=false`、`selected=0/completed=0`、`terminal_state=null`、`batch_identity_matches=false`、21 responses/438962 prompt tokens、最后事件 `llm_request 06:13:05Z`——**0/1 完成，未产生任何 findings 结论**。
- b02–b07 未起跑（逐批停链），`gate_decision=NOT_EVALUATED`。
- systemd unit `coordinator-ocr-1fe96fde…service` 已不存在（list-unit-files 无残留）；双锁 `inbox/ocr.lock` + `/home/wang/.local/state/ocr-runtime/ocr.lock` fuser 均无持有者。
- **根因=远端 vllm 单 engine capacity 排队**：本轮实测 `192.168.2.45:8002` `num_requests_running=4 / waiting=10（reason=capacity）`，单批 3900s 硬截止窗内未完成。与前两次同根（`ef462fc8` b01 13:03 撞截止时 running=4/waiting=6；E 初审 `617b9375` 撞截止时 vllm 槽争抢）。

## 裁决

1. **不判通过、不写零 findings**：coverage_complete=false、0 完成、rc=1 为进程层失败，F 接受门禁 OCR 面**维持关闭**。旧 ef462fc8、本 1fe96fde 均不产生"已通过"结论。
2. **本轮不发起补审**：补审四条件不满足——端点不空闲（running=4/waiting=10 capacity 排队），根因未消除前补审必再撞截止。
3. **补审路径（留待端点空窗）**：同身份 retry_depth 0→1 唯一额度，经唯一入口 `ocr_runtime.py prepare --reuse-run <本 run> --retry-reason ...`；须在 base/head、全体入选、背景、规则、配置身份一致且 vllm 队列空窗（running=0/waiting=0）时提交，最多一次，再失败 RETRY_LIMIT 升级。不得换 task 名/另建目录/改超时绕过。
4. **不阻塞独立线**：F 面代码已冻结（96afc43），B 无在途开发；TESTER F 面真 MySQL/并发/迁移探针仍可待 OCR 裁决后再派（探针不依赖 OCR 结果，但按接受门禁顺序仍先 OCR 裁决）。E 已接受（12:28）不受影响；E+F 强审批次包 MERGE_INTO 仍待 F 收口后生成。

## 证据

- `reviews/TASK-12S-F/ocr-run-20261015-attempt1-rebased/state.json`（HARD_DEADLINE 终态）
- `reviews/TASK-12S-F/ocr-run-20261015-attempt1-rebased/b01-diagnosis.json`（coverage_complete=false）
- `reviews/TASK-12S-F/ocr-run-20261015-attempt1-rebased/b01.log`（background 3999 chars 超推荐 2000 提示，非失败主因）
- `ocr_runtime.py results --run ...`（evidence_state=INSUFFICIENT_EVIDENCE，b01 SESSION_TERMINAL_REQUIRED，b02-b07 STATE_BATCH_MISSING_OR_DUPLICATE）
