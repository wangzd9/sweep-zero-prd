# TASK-12S-F 派单（协调者，2026-10-15 08:38 +08:00）

- **状态**：DISPATCHED。owner=执行者 B（共写 ingest/API 顺序接 E，E 已接受）。
- **REQ/AC**：REQ-21 / AC-21（INPUT_REJECTED 持久证据与逻辑隔离；补齐后受控 resume 与完整重校验）。
- **设计依据**：需求包内 12S-F 设计节（SPRAY-POST-V04.md §E/F；以该包当前版为准，不得从旧 PRD 推断）。

## base 与 worktree

- base：`b39a3ec`（TASK-12S-E 已接受冻结 head，含 pending_binding.py 与 source_service/scene_schedule_consumer 对账接线；F 与 E 共写 ingest/API，**必须基于 E head 开发**，避免与 E 未合入的公共文件冲突）。
- 工作分支建议 `a/task-12s-f-input-reject`，专属 worktree（wt-02-*，与 B 已释放的 16C-B worktree 不复用）。
- 合入口径：随 12S 父任务集成节奏（E 先、F 后 --no-ff），不单独合 main。

## 交付范围（最小一致改动）

1. 无效/缺失输入在 ingest 入口被**拒绝并持久登记 INPUT_REJECTED**（证据含原因码+原始标识，可追溯、不静默丢弃）。
2. 被拒输入与已登记 bag **逻辑隔离**：不进入绑定对账（E 的 pending_binding 扫描不得拾取）、不烧模型、不影响既有 AVAILABLE/DERIVED 记录。
3. **受控 resume**：材料补齐后按显式恢复动作重走完整校验链（指纹/完整性/身份），恢复成功才转正常登记路径；恢复失败保持 INPUT_REJECTED 并可重复尝试（幂等）。
4. 机械用例：拒绝登记、隔离断言（E 对账扫描跳过）、resume 成功/失败两路、幂等重复尝试。

## 硬边界（零越界清单）

- 不动 16C 界面三功能已合入面（main `16a154f`）；不写生产库/处理机/NAS 生产路径；不碰 1012 大包取消链（等用户通知恢复）。
- 不改 E 已接受的行为语义（只在其接线点旁路拒绝态）。
- VLM/模型调用=0（本任务纯控制面）。
- 本地隔离验证：真 MySQL 8.4.11 独立探针库（用完即毁），SQLite 绿不算数。

## 门禁与回执

- 交付=冻结 head+回执（`receipts/TASK-12S-F/attempt-1.md`：diff 清单、用例数、隔离库证据、自毁归零）→ 协调者机械核验 → OCR 固定入口审查（唯一）→ TESTER 独立验证 → 接受。
- ACK 时限：30 分钟内落盘 `attempt-1-ack.md`（base 可达性+worktree 洁净+边界确认）。