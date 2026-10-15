# TASK-12S-E attempt-2 增量复验派单（协调者，2026-10-15 10:26 +08:00）

- **状态**：DISPATCHED。owner=TESTER；task/attempt=TASK-12S-E / attempt-2。
- **被测固定快照**：base `b39a3ecc76da1f578d32f4e3c88a6ce989cf749d` → head `1e9c7deff16b532ad7430c5b3639f2e55bb62ec3`（wt-01-t12se，分支 a/task-12s-e-auto-bind）。只测该冻结 head，不追移动分支。
- **前提**：attempt-1 独立验证 PASS（00:43 回执）覆盖 b39a3ec 五面，仍有效；本单只补 **attempt-2 增量面**，不重跑已 PASS 的 attempt-1 全量。
- **OCR 状态**：协调者 attempt-2 增量 OCR run `a9bf637e` 三批 0 findings 收口（裁决 `reviews/TASK-12S-E/ocr-run-20261015-attempt2/ocr-verdict.md`），复验不替代也不被 OCR 替代。

## 增量复验面（真 MySQL 8.4.11 隔离库，用完即毁归零留证）
1. **E-R7 真实口径夹具**：`tests/test_task12se_auto_bind.py:813-860` 新增用例独立复跑；核对源行经 upsert_bag 登记后 `relative_path` 落 storage 相对段（如 `incoming/bag`），incoming 侧检测在**真实口径**下命中（b39a3ec 旧口径恒 False 的缺陷不再复现）。
2. **E-R1~R3 字段断言**：对账绑定成功后读 `IngestSubmission` 行：`bound_ready_path` = `storage_root/bag.relative_path` 真实物理口径（非 ready_root 拼接）、`bound_incoming_path` 含 `profile.incoming_prefix` 段（prefix 空/非空两用例）、`bound_purposes_json` 持久化且与主路径 ingest_service 口径一致（同一 bag 两次登记用途回显一致不变式）。
3. **E-R8 两路**：①豁免路=incoming 侧恰 1 原包行+本次注册落受控 ready 根+同指纹切片兄弟行 → 不 409 走移动恢复；②非豁免路=同指纹切片兄弟但 incoming 侧 0 行或多行 → 仍 409。切片兄弟行血缘不动。
4. **E-R4 防御面抽查**（不要求构造生产配置异常，能用夹具模拟即过）：ready 根不在 storage 根下且根身份不可推导 → `ROOT_MISMATCH` 不绑。
5. **回归抽查**：attempt-2 全量基线 A 已自报 38 既有失败两核零新增（head 多 5 passed）；TESTER 独立复跑目标测试文件 + `tests/test_pipeline_api.py` 改动面（E-R6 统计 key），核 `pending_reconciled` 条件键与旧口径兼容（outbox 空时统计集合不意外缩小）。

## 硬边界
- VLM 调用=0；不写生产库/NAS/A100；不碰 1012 大包取消链与 12S-F 开发树；隔离 MySQL 用完即毁。
- 若 E-R8 豁免路在真实 MySQL 下无法用只读夹具构造完整前置（需真实切片产物），按"断点+所需材料"登记，不 mock 冒充 PASS。

## 交付
- 回执 `test-receipts/TASK-12S-E/attempt-2-reverify.md`：5 面逐条结论（PASS/断点+owner）+ 命令/退出码 + 隔离资源归零证据。
- ACK 30min；本单为增量面，预期 1-2h。
- 后续：PASS → 协调者接受 E（head `1e9c7de`）→ 通知 B 12S-F 冻结 base rebase；FAIL → 回派 A 最小返修（新 attempt 链），不放宽 AC。