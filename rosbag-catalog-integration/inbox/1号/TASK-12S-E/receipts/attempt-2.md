# TASK-12S-E attempt-2 R1 返修回执（执行者 A，2026-10-15）

- **状态**：REVIEW_PENDING（等待协调者机械核验 → OCR 唯一入口增量审查 → TESTER 增量复验 → 接受）。
- **base / head**：`b39a3ec` → 冻结 head `1e9c7de`（`1e9c7deff16b532ad7430c5b3639f2e55bb62ec3`），分支 `a/task-12s-e-auto-bind`，worktree `wt-01-t12se`。
- **起因**：OCR retry1 更正版裁决（`reviews/TASK-12S-E/ocr-run-20261014-retry1/ocr-verdict.md`，08:52）——首发"零 findings"误判撤销，E-R1~E-R8 全在更正版内。
- **变更**：5 文件 +363/−31（3 app 服务 + 2 测试）。未回退/改写 attempt-1 已交付行为，仅修下述点位，零越界。
- **VLM/模型调用**：0（mock 执行模式，SCENE_SLICE run 计数承载）。
- **未执行项**：生产库/处理机/NAS 生产路径/1012 大包取消链/16C 已合入面均零触碰（本单为 app 代码+测试面，无生产写）。

## 逐条 E-R 编号对照（修复 commit `1e9c7de`）

| 编号 | 文件 | 修复点位（冻结代码行号） | 行为 | 对应用例 |
|---|---|---|---|---|
| E-R1 (HIGH) | `pending_binding.py` | 对账绑定行 `bound_ready_path`（原 :216） | 改真实物理路径口径：`f"{storage_root}/{bag.relative_path.lstrip('/')}"`，与 `upsert_bag` 落库相对段（catalog_ingest.py:30）一致，消除 ready_root 重复拼接 | `test_reconcile_bound_paths_real_physical_caliber_and_purposes`（断言 `bound_ready_path == SCENE_READY/{PFX}/{bag} == /test/{orig.relative_path}`） |
| E-R2 (MED) | `pending_binding.py` | `bound_incoming_path`（原 :215） | prefix 非空时拼回 `f"{incoming_root}/{prefix}/{sub.relative_path}"`，入口侧含 profile.incoming_prefix 段 | 同上（断言 `bound_incoming_path == SCENE_INCOMING_ROOT/{PFX}/{bag}`） |
| E-R3 (MED) | `pending_binding.py` | 对账绑定漏持久化 `bound_purposes_json`（原 :212 附近） | 与主路径 ingest_service.py:1187 同口径 `json.dumps(sorted({e.purpose for e in events}), ensure_ascii=False)`；恢复登记回显一致 | 同上（断言 `bound_purposes_json==["scene_slice"]` + 再登记回显 `scheduled_purposes==["scene_slice"]`/`self_built False`） |
| E-R4 (MED) | `pending_binding.py` | 防御分支 :162-165 注释 + :181-183 guard | 更正注释（configured=None 时上方核对为空操作）；`ready_rel_root is None and not (configured is not None and configured == snapshot_root)` → 记 `ROOT_MISMATCH` 不绑，裸短段候选不再静默套配任意根同名行 | `test_reconcile_defensive_root_not_configured_fails_closed`（构造 ready 根在受控根外/快照声明 root_id，旧代码静默绑定，新代码 ROOT_MISMATCH 不绑） |
| E-R5 (LOW) | `pending_binding.py` | PENDING_INPUT 选取 :99-101 | 加 `order_by(IngestSubmission.created_at)` FIFO 确定性 | `test_reconcile_fifo_selection_when_over_limit`（4 条 PENDING，最旧可绑行 created_at 回拨最旧，limit=1 必选中行=最旧） |
| E-R6 (LOW) | `scene_schedule_consumer.py` | poll docstring :383-384 + 全零 stats 双分支 :398-411 | 更正 docstring（对账每次 consume 执行，outbox 空不意味无副作用，全零统计仅指消费侧计数）；同批合并双分支全零 stats 字面量为共享 `zero_stats`（漂移项，非独立门禁） | 既有 `test_consume_endpoint_no_pending_returns_legacy_shape` 回归（零活动返回体逐键一致） |
| E-R7 (HIGH) | `source_service.py` | tier-2 incoming 侧检测 :207-216 | 比对前把 incoming 根归一到 storage 相对形式（`root.removeprefix(storage_root).lstrip('/')`），真实 `upsert_bag` 落库相对段口径生效 | `test_register_move_recovery_with_slice_sibling_exempts_409`（源经真实登记落 `scene/incoming/{PFX}/{bag}` 相对段，ready 重登记归并既有 UID）+ 夹具修正 |
| E-R7 夹具 | `test_pipeline_api.py` | :177 | 异常口径行 `relative_path="/test/incoming/bag-moved"`（storage-qualified）改真实口径 `incoming/bag-moved`，防旧夹具反向绑架 | `test_source_registration_reuses_source_id_after_incoming_to_ready_move` |
| E-R8 (MED) | `source_service.py` | 409 栅栏 :199-206 | 先计算 `incoming_side`/`registered_under_ready`，`slice_share and not exact_originals and not (len(incoming_side)==1 and registered_under_ready)` 才 409——移动恢复条件满足时豁免 409 走归并；切片兄弟行不参与豁免判定 | `test_register_move_recovery_with_slice_sibling_exempts_409`（豁免路：有 incoming 行+落受控 ready 根→200 归并）+ `test_register_slice_fingerprint_still_409_without_move_recovery`（非豁免路：无 incoming 行→仍 409） |

## 用例与验证

- **新增用例**：6 条（E-R1/R2/R3 合并 1 条三字段真实物理口径断言；E-R4 1 条；E-R5 1 条；E-R7/R8 豁免 1 条；E-R8 非豁免 1 条）。
- **修改夹具**：`test_pipeline_api.py:177` 异常口径 → 真实 storage 相对段。
- **新增/修改用例数**：6 新增 + 1 夹具修正。

## 隔离验证（真 MySQL 8.4.11 独立探针库，用完即毁）

- **环境**：`docker run --rm mysql:8.4`（镜像 `docker.m.daocloud.io/library/mysql:8.4`，容器内 `SELECT VERSION()`=**8.4.11**），独立库 `t12se_at2_base`/`t12se_at2_head`，127.0.0.1:13306，`DATABASE_URL=mysql+pymysql://root:[REDACTED_PASSWORD]@127.0.0.1:13306/<db>`。
- **目标文件（本变更面）**：`tests/test_task12se_auto_bind.py` + `tests/test_pipeline_api.py` **42 passed**（真 MySQL 8.4.11）。
- **全量回归（两核对照）**：
  - 基线 `b39a3ec` @ `t12se_at2_base`：`32 failed, 1151 passed, 11 skipped, 6 errors`
  - 本 head `1e9c7de` @ `t12se_at2_head`：`32 failed, 1156 passed, 11 skipped, 6 errors`
  - **失败集逐条 diff：NEW=0 / GONE=0（38 条既有失败两核完全一致）**，本 head 多 5 passed=新增 6 用例 − 1 既有（夹具修正后 test_pipeline_api 移动恢复用例仍过）。**零新增失败**。
  - 既有失败面（两核一致，非本单引入）：devflow 3 + web bounded-query + 若干 scene/cleanup/16c MySQL 环境固有失败（独立探针库无完整外部依赖）。
- **SQLite 口径**：目标文件 42 passed（SQLite 隔离库 conftest）；但按派单"SQLite 绿不算数"，以上真 MySQL 为准。
- **ruff**：`ruff check` 本变更 5 文件 **All checks passed**（F541 已修；`test_task16cc_scene_detail.py` 2 条 E501 为基线既有、非本单文件）。
- **git diff --check**：rc=0（无空白错误）。

## 自毁归零证据

- MySQL 探针容器 `docker rm -f a-t12se-attempt2-mysql` 已执行；`docker ps -a --filter name=t12se` 计数=**0**（无残留容器/库）。
- 基线临时 worktree `/tmp/a-t12se-baseline` `git worktree remove --force` 已执行。
- 交付 worktree `wt-01-t12se` `git status` 仅 `.venv`（untracked，软链），跟踪文件零改动=冻结干净。

## 越界申报

- 无。仅改派单枚举的 3 个 app 服务文件 + 2 个测试文件；未动 TODO/HANDOFF/DESIGN/decision/其他角色目录/统一 TIMELINE；未运行 OCR/强审/合入；未碰生产/迁移/算法/在途批次。

## 交付与门禁

- 冻结 head `1e9c7de` 待协调者机械核验 → OCR 唯一入口对 attempt-2 增量审查（新交付身份）→ TESTER 对 E-R7 真实口径夹具/E-R1~R3 字段断言/E-R8 两路增量复验 → 接受。REVIEW_PENDING 不代表通过，未合入 main。