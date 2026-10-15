# TASK-12S-E attempt-2 R1 增量审查背景（协调者，2026-10-15 09:3x +08:00）

## 需求与版本
- 需求：REQ-20（自动绑定与幂等，AC-20.1/AC-20.2）；契约版本 v0.5（SPRAY-POST-V04 及 TASK-12S-E 派单）。
- attempt-1（范围 `16a154f..b39a3ec`）已经 OCR retry1（run `3480a161`）全批 REVIEW_COMPLETE，更正版裁决见 `reviews/TASK-12S-E/ocr-run-20261014-retry1/ocr-verdict.md`：**11 条 findings（2 HIGH/4 MEDIUM/5 LOW），6 条 CONFIRMED CORRECTION（E-R1~E-R8）**；首发"零 findings"系误判已撤销。

## 本次审查身份
- **新交付身份**：base `b39a3ec` → head `1e9c7de`（分支 `a/task-12s-e-auto-bind`，worktree `wt-01-t12se`，单 commit，5 文件 +363/-31）。
- attempt-2 R1 最小返修，只修 E-R1~E-R8 对应点位与真实口径夹具/用例，不扩需求、不回退 attempt-1 已交付行为。

## 逐点位允许行为（冻结口径，来自更正版裁决）
- **E-R1**（`pending_binding.py` 对账绑定行）：`bound_ready_path` 必须落真实物理路径口径 `f"{storage_root}/{bag.relative_path.lstrip('/')}"`，与 `upsert_bag`（catalog_ingest.py:30）落库相对段一致；不得再用 `ready_root` 重复拼接。
- **E-R2**（同文件）：`bound_incoming_path` 在 profile `incoming_prefix` 非空时拼回前缀段，入口侧含前缀。
- **E-R3**（同文件）：对账绑定必须持久化 `bound_purposes_json`，口径与主路径 ingest_service.py:1187 一致（`json.dumps(sorted({e.purpose for e in events}), ensure_ascii=False)`）。
- **E-R4**（同文件防御分支）：`ready_rel_root is None and not (configured is not None and configured == snapshot_root)` 时记 ROOT_MISMATCH 不绑；注释不得断言不存在的防线。
- **E-R5**（同文件 PENDING_INPUT 选取）：`order_by(IngestSubmission.created_at)` FIFO。
- **E-R6**（`scene_schedule_consumer.py`）：poll docstring 更正——对账每次 consume 执行，outbox 空不意味无副作用；全零 stats 双分支合并为共享字面量（漂移项，非独立门禁）。
- **E-R7**（`source_service.py` tier-2 incoming 侧检测）：incoming 根先归一到 storage 相对形式再比对 `r.relative_path`（`root.removeprefix(storage_root).lstrip('/')`）。
- **E-R8**（`source_service.py` 409 栅栏）：先算 `incoming_side`/`registered_under_ready`；`slice_share and not exact_originals and not (len(incoming_side)==1 and registered_under_ready)` 才 409；切片兄弟行不参与豁免判定（血缘不动）。
- 测试面：6 新增用例（三字段真实物理口径/ROOT_MISMATCH fail-closed/FIFO/移动恢复豁免 200/非豁免仍 409）+ `test_pipeline_api.py:177` 夹具从异常口径改真实 storage 相对段。

## 不变量（任何文件均须保持）
1. 同一 bag 两次登记用途一致（`bound_purposes_json` 回显不漂移）。
2. 父子/同指纹识别不改血缘；切片行不得被 register source 归并或重绑。
3. 移动恢复（incoming→ready）身份：tier-1 精确行 / tier-2 incoming 侧恰 1 行 + 受控 ready 根 才豁免 409。
4. 对账绑定不得静默套配任意根的同名 bag 行（根身份不可推导时 fail-closed）。
5. `consume` 零 outbox 时返回体键集与旧口径兼容（orchestrator 消费方不断键）。
6. 不改模型/迁移/配置/生产面；本单为 3 app 服务 + 2 测试文件。

## 测试证据（开发自测，隔离真 MySQL 8.4.11 探针库，已自毁）
- 目标文件 `test_task12se_auto_bind.py`+`test_pipeline_api.py` **42 passed**。
- 全量回归两核（base `b39a3ec` vs head `1e9c7de`）：38 条既有失败逐条 diff NEW=0/GONE=0，head 多 5 passed=新增用例；零新增失败。
- ruff 5 文件 All checks passed；`git diff --check` rc=0；alembic 单头 `20261013_01_scene_intake`。
- 协调者独立复跑（SQLite 口径）：42 passed；ruff 全绿。真 MySQL 隔离库口径以 TESTER attempt-2 复验为准。

## 待核实风险
- E-R7 归一依赖 `storage_root` 前缀关系；若未来配置出现 incoming 根不在 storage 根下的形态（当前 config 校验禁止），tier-2 判定行为需核。
- E-R8 豁免条件 `len(incoming_side)==1` 的边界：多 incoming 行（如跨 profile 双入口同名）仍 409，确认无合法恢复场景被误伤。
- attempt-1 既有 11 条 findings 中 2 条 LOW 非阻塞改进（全零 stats 双分支、尾换行）：双分支已随 E-R6 合并；其余是否残留由本次 findings 核对。