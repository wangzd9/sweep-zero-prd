# TASK-12S-F attempt-1 全量 app 交付审查背景（协调者，2026-10-15 13:0x +08:00，身份更正版）

## 需求与版本
- 需求：REQ-21（无效输入持久拒绝与受控恢复，AC-21）；契约版本=V04_CLOSEOUT 水雾收尾计划（TODO §11）+ 原 08:38 派单 + 补充 S1（08:52，冻结 base 后移至 E attempt-2 冻结 head）。
- 交付身份：base `1e9c7de`（TASK-12S-E attempt-2 冻结 head，已接受 12:28）→ head `96afc43`（分支 `b/task-12s-f-input-reject`，worktree `wt-04a-t12sf`，2 commit：`9ef9785` 全量实现 + `96afc43` 4×E501 折行）。F app+alembic 面相对旧 base `b39a3ec` **逐字节不变**（diff sha `86897504adbc8548` 双方一致，rebase 为纯 base 平移）。
- 本 run 审查 7 app 文件（tests 默认排除），逐文件一批（7 批），避免多文件合批在 VLM 争抢下超 3900s 单批硬截止。

## 前序失败说明（身份层，非代码）
- 前 run `ef462fc8`（范围 `b39a3ec→8c8bf2f`，4 文件合 b01）b01 于 13:03:31 撞 3900s 单批硬截止（rc=1、`context canceled`、coverage_complete=false、0/4 文件完成、36 次 LLM 往返停在 file_read）——起跑时 VLM 负载高（running=4/waiting=6）。**零 findings 产出、零覆盖**，不产生任何"已通过"结论，仅登记为进程层失败。本次为重新 prepare 的正确批次设计（逐文件），非对同一失败批次换参续跑；身份已随 rebase 变更（base→1e9c7de），属新审查身份，retry_depth=0。

## 本次实现面（允许行为，逐文件）
1. `app/models.py`：IngestSubmission 新增 `rejection_reason_code` String(32) nullable（index=True 自动名索引）/ `rejection_evidence_json` Text nullable 无 server_default / `stable_reject_rounds` Integer nullable；INPUT_REJECTED 终态语义注释。
2. `app/services/ingest_service.py`：`report_input_rejected`（受控根校验 409 越界；按 path_claim 定位唯一活动行：PENDING 复用 / 已拒绝幂等再确认不推代次 / 无行建系统拒绝行 scanner-reject；置 INPUT_REJECTED + 审计块）；`resume_input_rejected`（乐观锁 row_version：旧代次 409 ROW_VERSION_CONFLICT / 非拒绝态 409 SUBMISSION_NOT_REJECTED / 缺行 404；成功回 PENDING_INPUT、清稳定计数、保留拒绝历史、幂等键重放）；`_submission_response` 增 rejection 字段 + resume_hint。
3. `app/api/ingest_submissions.py`：`POST /reject-input`（Scanner 内部上报，原始 body 限额复用 _raw_body + 幂等依赖）；`POST /{id}/resume-input`（ResumeInputRequest DTO extra=forbid）。
4. `app/scanner/metadata.py`：`classify_bag_input` 三分量（parsed / reason_code / detail）：BAD_METADATA / UNSUPPORTED_STORAGE / EMPTY_BAG / MISSING_DB3 稳定机器码 + 512 截断详情；`validate_bag_input` 保持原 raise 语义（既有调用方零改动）。
5. `app/scanner/runner.py`：稳定确认后（先落稳定证据再分类）无效输入不 raise：拒绝快照=mtime:file_count:total_bytes（**不含**递增 stable_rounds，保"相同快照抑制"口径）；相同快照已报→抑制不刷重复拒绝；Backend 上报不可达→计 failed 不写拒绝标记（下轮重试）；原包不 move 不删。
6. `app/scanner/backend.py`：`report_input_rejected` 上报封装（/reject-input，timeout 60）。
7. `alembic/versions/20261014_01_ingest_rejected.py`：单头迁移（down_revision=20261013_01_scene_intake）三列 + 逐对象 gate（空库 create_all 已含新列时跳过 add，防 big-bang 重放 duplicate column）；downgrade 逆删。

## 不变量（任何文件均须保持）
1. **逻辑隔离**：pending_binding 对账只扫 PENDING_INPUT——INPUT_REJECTED 行零事件零 run，不产生 source/run/模型请求；既有 AVAILABLE/DERIVED 记录零触碰（与 12S-E E-R 面文件不相交：本 run 不审 `pending_binding.py`/`source_service.py`/`scene_schedule_consumer.py`）。
2. **原包不可变**：拒绝输入留 incoming 受控位置，不 move 不删（扫描面红线）。
3. **稳定快照抑制**：拒绝证据快照不含递增计数，相同快照重复上报抑制；内容变化重新计稳定可再报。
4. **resume 代次一致**：row_version 乐观锁，旧代次/非拒绝态/已绑定拒绝一律 409 不覆盖；幂等键重放不二次副作用。
5. **受控根边界**：incoming_path 越出声明 root 受控 scan 根 → 409，拒绝登记不越权写任意路径。
6. **上报不可达不假称**：Backend 不可达计 failed 不写拒绝标记（下轮重试），不产生"已登记"假终态。
7. **迁移安全**：单头、nullable 列、无 TEXT server_default、索引 String(32) 窄列（避开 1101/1071 已知 MySQL 8.4 形态）；空库 create_all 共存 gate。
8. **不烧模型**：scanner→backend 纯 HTTP 上报，VLM/模型调用 0；不改算法/生产面。

## 测试证据（开发自测 + 协调者独立复核）
- 开发自测：`tests/test_ingest_input_rejected.py` 14 passed；组合回归 91 passed；全量 1204 passed / 5 failed（归属核实均非本任务）；rebase 后 B 复验 14 passed + E 面回归抽查 55 passed。
- 协调者独立复核（R1 阶段 11:2x）：`6798059→8c8bf2f` 单文件折行 +20/−4、ruff 10 文件 All checks passed、定向 14 passed rc=0、`alembic heads` 单头 `20261014_01_ingest_rejected`、工作树干净。
- 开发如实未执行（留待交付冻结/TESTER 口径，非本次 OCR 范围）：真 MySQL 8.4.11 隔离库 `alembic upgrade head` + DML 探针；真并发乐观锁双会话竞争（SQLite 静默忽略行锁）；Scanner 真实 NAS 双轮稳定 E2E。

## 待核实风险（审查重点关注）
- `report_input_rejected` path_claim 定位"唯一活动行"的并发/时序窗口（两 scanner 实例同时上报同 path）是否仍保持"复用/幂等/建行"三分支无重复副作用。
- `resume_input_rejected` 清稳定计数与保留拒绝历史的边界：多次拒绝-恢复代次递增下 row_version 与幂等键组合是否可绕过 409 栅栏。
- `classify_bag_input` 512 截断详情与 `validate_bag_input` 原 raise 语义共存：既有调用方（非 scanner 路径）行为是否零变化。
- 迁移 gate 的"空库 create_all 已含新列时跳过 add"分支在大库重放/混合形态下是否可能静默漏列。
- runner 稳定快照口径（mtime:file_count:total_bytes）对同字节内容 mtime 变化的输入：是否误判"内容变化"重复拒绝。