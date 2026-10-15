# TASK-12S-F attempt-1 app 面审查背景（协调者 2026-10-15 17:1x +08:00，xcoding 路由版）

## 需求与交付身份
- 需求 REQ-21 / AC-21（无效输入持久拒绝与受控恢复）；契约版本=TODO §11 水雾收尾 + 原 08:38 派单 + 补充 S1（冻结 base 后移至 E attempt-2 head）。
- 交付：base `1e9c7de` → head `96afc43`（worktree `wt-04a-t12sf`，2 commit：`9ef9785` 实现 + `96afc43` 4×E501 折行）；app+alembic 面相对旧 base `b39a3ec` 逐字节不变（diff sha `86897504adbc8548`）。
- 本 run 审 7 个 app 文件，逐文件一批；测试文件默认排除（归 TESTER）。

## 前序失败（端点/负载层，非代码结论）
- 本地 run `1fe96fde` b01 撞 3900s 单批硬截止（起跑时 VLM running=4/waiting=10）；云端 run `77db648b`（sub2api）因端点对非流式请求返回 `text/event-stream` 26s 失败。**两次均零覆盖、零 findings**，不构成通过也不构成对代码的否定结论。本次为换供应商后的新审查身份重提。

## 实现面（允许行为）
1. `app/models.py`：IngestSubmission 新增 `rejection_reason_code`/`rejection_evidence_json`/`stable_reject_rounds`；INPUT_REJECTED 终态语义注释。
2. `app/services/ingest_service.py`：`report_input_rejected`（受控根越界 409；path_claim 三分支=PENDING 复用/已拒绝幂等再确认/建 scanner-reject 行；置终态+审计块）；`resume_input_rejected`（row_version 乐观锁三态 409；成功回 PENDING_INPUT、清稳定计数、保留拒绝历史、幂等键重放）；`_submission_response` 增 rejection 字段与 resume_hint。
3. `app/api/ingest_submissions.py`：`POST /reject-input`（Scanner 内部上报，原始 body 限额复用）与 `POST /{id}/resume-input`（DTO extra=forbid）。
4. `app/scanner/metadata.py`：`classify_bag_input` 稳定机器码 BAD_METADATA/UNSUPPORTED_STORAGE/EMPTY_BAG/MISSING_DB3 + 512 截断详情；`validate_bag_input` 保持原 raise 语义。
5. `app/scanner/runner.py`：稳定确认后无效输入不 raise；拒绝快照=mtime:file_count:total_bytes（**不含** stable_rounds）抑制重复上报；Backend 不可达计 failed 不写拒绝标记；原包不 move 不删。
6. `app/scanner/backend.py`：`report_input_rejected` 上报封装。
7. `alembic/versions/20261014_01_ingest_rejected.py`：单头迁移三列 + 空库 create_all gate，downgrade 逆删。

## 不变量（任何文件须保持）
逻辑隔离（INPUT_REJECTED 零事件零 run）；原包不可变；稳定快照抑制；resume 代次一致（row_version 栅栏）；受控根边界 409；上报不可达不假称已登记；迁移安全（单头/nullable/窄索引 String(32)，避 MySQL 8.4 的 1101/1071）；scanner→backend 纯 HTTP，不烧模型。

## 测试证据
开发自测 14 passed；组合回归 91 passed；全量 1204 passed / 5 failed（归属核实均非本任务）；协调者独立复核：单文件折行 +20/−4、ruff 10 文件全绿、定向 14 passed、`alembic heads` 单头。真 MySQL/并发/NAS E2E 开发如实留待 TESTER。

## 待核实风险
path_claim 定位唯一活动行的并发窗口；resume 与幂等键组合能否绕过 409 栅栏；512 截断与原 raise 语义共存对既有调用方的影响；迁移 gate 在大库重放时是否静默漏列；拒绝快照对同内容 mtime 变化的误判。
