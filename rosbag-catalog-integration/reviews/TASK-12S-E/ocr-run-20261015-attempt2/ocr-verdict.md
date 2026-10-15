# TASK-12S-E attempt-2 增量 OCR 收口裁决（协调者，2026-10-15 09:46 收口 / 10:10 裁决落盘）

## 运行身份
- run `a9bf637e`（`reviews/TASK-12S-E/ocr-run-20261015-attempt2`），unit `coordinator-ocr-a9bf637ebaab4808bdd051eef347627f.service`，2026-10-15 09:35:55 经唯一入口 SUBMITTED。
- 冻结快照 base `b39a3ecc76da1f578d32f4e3c88a6ce989cf749d` → head `1e9c7deff16b532ad7430c5b3639f2e55bb62ec3`（A attempt-2 R1，wt-01-t12se，HEAD 实测一致、工作树干净（仅 .venv 未跟踪））。
- 审查范围：app 面 3 文件逐批（b01 `pending_binding.py` / b02 `scene_schedule_consumer.py` / b03 `source_service.py`）；tests 2 文件按本入口默认排除（与 attempt-1/retry1 同口径，测试面由 TESTER 增量复验覆盖）。
- ocr v1.13.0 / provider vllm-local / model qwen3.8-27b-fp8，三批 manifest resolved_base/head 与 exact_range 一致，`batch_identity_matches=true`。

## 收口事实（逐批实读 b0*.log，不只看 diagnosis）
| 批 | 文件 | 状态 | rc | duration | findings（log comments 数组） |
|---|---|---|---|---|---|
| b01 | pending_binding.py | REVIEW_COMPLETE | 0 | 434.4s | **0**（comments 数组空，16 次 LLM 往返 22 次工具调用） |
| b02 | scene_schedule_consumer.py | REVIEW_COMPLETE | 0 | 60.3s | **0**（5 次 LLM 往返） |
| b03 | source_service.py | REVIEW_COMPLETE | 0 | 126.7s | **0**（6 次 LLM 往返） |

- 三批 diagnosis 均 `coverage_complete=true`、`remaining_paths=[]`、`parse_errors=[]`、`llm_errors=[]`、`repeated_tools=[]`；服务 Result=success（09:46:17 退出）。
- findings 计数已按教训逐批实读 `b0*.log` 的 `comments` 数组（retry1 首发误裁根因不复现）：三批均为 0 条，非"diagnosis 无 findings 字段"推断。
- 独立 session 文件事件核（三个 jsonl）：均 `review_item_done`+`session_end` 完整闭合，无 comment 事件。

## 协调者代码面独立核对（零发现交叉验证）
- `pending_binding.py:165-170` 防御分支注释改写与 E-R4 fail-closed 守卫（`ready_rel_root is None and not (configured is not None and configured == snapshot_root)`）在位，语义=裸短段候选命中时根身份不可推导即 ROOT_MISMATCH 不绑，与更正版裁决 E-R4 一致。
- E-R1（`bound_ready_path = f"{storage_root}/{bag.relative_path.lstrip('/')}"` 真实物理口径）、E-R2（`bound_incoming_path` 含 `profile.incoming_prefix` 拼回）、E-R3（`bound_purposes_json` 持久化与 ingest_service 主路径同口径，`import json` 在位）逐点位在位。
- E-R5 FIFO：`order_by(IngestSubmission.created_at).limit(limit)` 在位。
- `scene_schedule_consumer.py` E-R6：zero_stats 单点收敛（两分支共用）+ docstring 口径更正（reconcile 每次 consume 执行，outbox 空不意味无副作用），统计 key 集合与旧口径兼容（仅新增 `pending_reconciled` 条件键）。
- `source_service.py` E-R7（`incoming_roots_rel` 归一到 storage 相对再比对，修真实数据恒 False 缺陷）、E-R8（409 栅栏后移+豁免条件 `len(incoming_side)==1 and registered_under_ready`，切片兄弟行不参与豁免）逐点位在位；`storage_root` 变量在该块 180 行定义在位。
- 无越界文件（diff 仅 5 文件=3 app+2 tests，app 面 3 文件全部在授权范围内）。

## 裁决
- **OCR 门禁：满足**（attempt-2 增量 3/3 全覆盖、0 findings、身份一致）。
- 不构成接受：接受前置=TESTER 对 E-R7 真实口径夹具 / E-R1~R3 字段断言 / E-R8 两路豁免（含非豁免仍 409）增量复验（真 MySQL 隔离库）PASS。
- **强审查判断：MERGE_INTO 12S-E+F 批次包**——E 的绑定语义风险面与 F 的拒绝/恢复链共享 incoming/ready 路径口径不变量，单独起包属重复阅读；待 TESTER E 复验 PASS 后由协调者按 strong-review pack 模板生成单包，在有效授权（grant `9827cf8f…` 2026-10-15 22:24:23 到期、0/5 已用）内经 strong_review.py 起跑，无有效授权时提醒用户手动触发。本裁决不新增需求、不改 E/F 验收口径。