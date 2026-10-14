# TASK-12S-A attempt-1 增量 OCR 4 批收口裁决（协调者，AWAITING_DECISION → 裁决）

- 时间：2026-10-13 16:0x +08:00（r165，prerun 指纹 2e34c39f）
- run：固定入口 `ocr_runtime.py`，run_id `8540bf7e`，`reviews/TASK-12S-A/attempt-1/ocr/`
- 范围：base `6fb42c4` → head `77c395b`（12S-A v0.5 原始信息绑定 5 文件 +1272/-32），4 批逐文件

## 收口事实（独立读 bNN.log + bNN-diagnosis.json，非采信服务状态）

| 批 | 文件 | 状态 | findings | coverage | duration |
|---|---|---|---|---|---|
| b01 | `app/api/ingest_submissions.py` | complete rc=0 | **0** | 1/1 | 22m47s |
| b02 | `app/schemas/scene_config.py` | complete rc=0 | **0** | 1/1 | 16m37s |
| b03 | `app/services/bootstrap.py` | complete rc=0 | **0** | 1/1 | 1m24s |
| b04 | `app/services/ingest_service.py` | complete rc=0 | **0**（16:02 收口） | 1/1 | 19m56s |

全部 terminal_state=complete、remaining_paths=[]、llm_errors=[]、batch_identity 匹配。**4 批零 findings，弱 OCR 门禁解除。**

## 跨文件契约与独立测试核

- DTO/API/服务/快照四处车辆绑定契约：`resolve_source_metadata_vehicle`（spray 入口缺/未知 vehicle_code→422 不调度）+ bind 面 `apply_frozen_vehicle`（冻结快照回写、MANUAL 不覆盖、冲突 409）——r165 独立读码核在案（12S-C 裁决 §二.2 同证据）。
- TESTER 14:51 独立验证 PASS 已交付：真 MySQL 8.4 双库迁移往返 3×RC=0 + 零新增 DDL + 坡道默认分库 seed 逐字段一致 + spray 14 项行为全 OK（`test-receipts/TEST-TASK12S-AB/attempt-1.md`）。

## 裁决与合入

- 12S-A **OCR 4 批收口 = 通过（零 findings）**，合入唯一剩余门禁解除。
- **合入已由并行协调者回合执行**：main `6c7d983`（merge `77c395b`，"TASK-12S-A attempt-1 原始信息绑定+车辆绑定+spray profile（OCR 4批零findings+TESTER PASS，19:00首包依赖线）"）。r165 独立核：`77c395b` 祖先关系 OK、merge-tree 零冲突、app diff 与合入 commit 逐字节一致（`git diff 6c7d983..77c395b -- app scripts alembic` = 0 行）。
- **origin 补推核验（r165 执行）**：合入后实测 origin/main 仍 `6fb42c4`（未推）→ `git push origin main` 已补推 `6fb42c4..6c7d983`，推后 `origin/main`=`6c7d983` 双核一致。
- **12S-A 转 DONE**（已合入 main + 协调者验收闭环：OCR 4 批零 findings + TESTER PASS + 机械核验 + 推送核验）。强审口径：DTO/服务接线面已由 TESTER 真 MySQL 独立验证+OCR 全覆盖，12S-C 强审 pack 时将 12S-A 消费面（source_metadata 契约）纳入跨文件疑点面，不单开强审调用。
- 12S-C 消费面重算：12S-C 交付 `92dcb52` 的 12S-A import 面（`77c395b`）现已在 main，接线核验单固定 SHA 不变。