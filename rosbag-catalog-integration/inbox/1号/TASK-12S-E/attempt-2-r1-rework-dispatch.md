# TASK-12S-E attempt-2 最小返修派单 R1（协调者，2026-10-15 08:52 +08:00）

- **状态**：DISPATCHED。owner=执行者 A（原任务最小返修，OCR 纠正级）。
- **起因**：retry1 OCR 裁决更正版（`reviews/TASK-12S-E/ocr-run-20261014-retry1/ocr-verdict.md`，08:52）——首发"零 findings"误判已撤销，E 接受登记随之撤销。逐条编号 **E-R1～E-R8** 全在更正版裁决内，按该文件为准。
- **base**：`b39a3ec`（attempt-1 冻结 head，wt-01-t12se@`a/task-12s-e-auto-bind`）续 commit；**不得回退/改写 attempt-1 已交付行为**，只修下述点位。

## 返修范围（仅以下，不扩需求）

1. **E-R1（HIGH）`pending_binding.py:216`**：对账绑定行 `bound_ready_path` 重复拼接物理段（`ready_root` 绝对根 + storage 相对 `bag.relative_path`）。修为真实物理路径口径（建议 `f"{settings.nas_storage_root.rstrip('/')}/{bag.relative_path.lstrip('/')}"`，与 `upsert_bag` 落库相对段一致）。
2. **E-R2（MEDIUM）`pending_binding.py:215`**：`bound_incoming_path` 丢失 `incoming_prefix` 段。`prefix` 非空时拼回：`f"{incoming_root}/{prefix}/{sub.relative_path}"`。
3. **E-R3（MEDIUM）`pending_binding.py:212` 附近**：对账绑定漏持久化 `bound_purposes_json`。与主路径 ingest_service.py:1187 同口径 `json.dumps(sorted({e.purpose for e in events}), ensure_ascii=False)`，保证恢复登记回显一致。
4. **E-R4（MEDIUM）`pending_binding.py:162-165 + 181-183`**：防御分支注释声称的 root_id 身份防线在该分支为空操作（`derive_root_id_for_ready` 返回 None）。更正注释；裸短段候选命中绑定时要求根身份可推导（`derive_root_id_for_ready(ready_root)` 非 None 或与 snapshot_root 一致）再放行，否则记 `ROOT_MISMATCH` 不绑。
5. **E-R5（LOW）`pending_binding.py:99-101`**：PENDING_INPUT 选取加 `order_by(IngestSubmission.created_at)` FIFO 确定性。
6. **E-R6（LOW）`scene_schedule_consumer.py:383-384`**：poll docstring"03B outbox 未合入时无副作用"已过时——对账在每次 consume 调用执行，outbox 空不意味无副作用。更正措辞；同批顺手合并双分支全零 stats 字面量（漂移项，非独立门禁）。
7. **E-R7（HIGH）`source_service.py:207-216`**：`incoming_roots` 是绝对配置根，`r.relative_path` 是 storage 相对段，tier-2 incoming 侧检测恒空、移动恢复在真实数据上失效。**比对前把 incoming 根归一到 storage 相对形式**（`root.rstrip('/').removeprefix(storage_root).lstrip('/')`）。⚠️ 既有夹具 `tests/test_pipeline_api.py:177` 以异常口径行 `relative_path="/test/incoming/bag-moved"`（storage-qualified，非 `upsert_bag` 产物）侥幸通过——**返修必须把该夹具改为真实口径 `incoming/bag-moved`**，防止修复被旧夹具反向绑架；同时补一条 `upsert_bag` 正常登记路径的移动恢复用例。
8. **E-R8（MEDIUM）`source_service.py:199-206`**：409 栅栏先于 tier-2 身份评估触发。先计算 `incoming_side` 与 `registered_under_ready`，`len(incoming_side)==1 and registered_under_ready` 时豁免 409 走移动恢复分支（与 E-R7 归一口径联动）；补豁免/非豁免两路用例（切片兄弟行存在时应恢复不应 409；不满足移动恢复条件时仍 409）。

## 用例与验证要求

- 新增/修改断言覆盖：对账行三字段（`bound_incoming_path`/`bound_ready_path`/`bound_purposes_json`）真实物理口径；移动恢复真实夹具（E-R7）；409 豁免两路（E-R8）；FIFO 选取；防御分支不静默套配。
- 本地隔离验证：真 MySQL 8.4.11 独立探针库（用完即毁），SQLite 绿不算数；全量回归不新增失败（4 个 devflow/web 基线既有失败在案）。
- VLM/模型调用=0；不碰 1012 大包取消链、生产库/处理机/NAS 生产路径、16C 已合入面。

## 交付

- 冻结 head + 回执 `inbox/1号/TASK-12S-E/receipts/attempt-2.md`（逐条 E-R 编号对照修复 commit 行号、用例数、隔离库证据、自毁归零）。
- 门禁：协调者机械核验 → OCR 唯一入口对 attempt-2 commit 增量审查（新交付身份）→ TESTER 对修复点增量复验（重点 E-R7 真实口径夹具、E-R1~R3 字段断言、E-R8 两路）→ 接受。
- ACK 时限：30 分钟内落盘 `attempt-2-ack.md`。