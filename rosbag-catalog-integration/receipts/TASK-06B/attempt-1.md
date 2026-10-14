# TASK-06B 回执（attempt-1）

- owner：2号会话（前端功能开发群）
- status：REVIEW_PENDING
- 需求版本：rosbag-catalog-integration v0.3.2
- 接口版本：scene-capability/v1（04A 终版）、06A 数据层契约（e92ef17 合入 8bd5618）
- 集成 base：main 8bd5618（含 06A 终版 / 05 四 commit / 03B a8fac99）
- 工作树：/home/wang/.local/state/rosbag-scene/wt-04a，分支 scene/task-06b（自 8bd5618 新开）
- output_commit：76d2958（7 文件，纯 06B scope；.venv 软链未入 commit）
- 已授权阶段：P0 本地（无生产、无处理机操作）
- 恢复说明：本 attempt 开发期间会话中断一次，resume 后核对全部在途改动保留、
  补齐收尾（ruff 格式化+1 处自动修）、验证全绿后提交。无 checkout/reset。

## 交付内容

- `app/api/scene_results.py`（新增）：执行面 3 路由
  - POST /api/v1/scene-analysis-runs/{id}/results — 分批幂等登记
  - POST /api/v1/scene-analysis-runs/{id}/complete-scene — 完整性门禁+文件证据+换版+运行终态
  - POST /api/v1/scene-analysis-runs/{id}/reconcile-scene — 发布后登记故障补偿
- `app/schemas/scene_result.py`（新增）：3 个请求 DTO（manifest JSON 64KiB 限额、
  child_bag_uids 形状校验、publish_root/vehicle_key 受控字段）
- `app/services/scene_result_report_service.py`（新增，559 行）：身份校验 + 登记 +
  完整性门禁 + 换版 + 运行终态 + reconcile 恢复
- `app/services/scene_publish_service.py`（新增，245 行）：staging 写出 +
  storage_offset 推导 + 原子发布（跨文件系统阻断、冲突禁止覆盖、slice manifest）
- `app/api/__init__.py`（+2 行）：scene_results.router 接线（按派单申报，
  协调者合入时确认——DESIGN §11.3 共享入口）
- `app/services/scene_slice_service.py`（+2/-1）：05 文件最小兼容修——
  finish_scene_run 的 error_message 写 None 撞 NOT NULL 列（05 模型默认 ""），
  改 `or ""`。**越出 06B 允许文件清单的一处，见"越界申报"节。**
- `tests/test_scene_result_report.py`（新增，962 行，24 项）：真实文件链
  （tests/scene_fixture 确定性 CompressedImage bag + 04B CDR 封装格式），
  不用自洽 fixture 冒充真实格式

## 06A 契约输入落地（逐条）

1. **完整性门禁**：`_check_integrity` 做 `expected_segment_count ==
   registered_segment_count` 等值比较（同基数=manifest 全部区间含 flat）；
   可发布子集走 `list_segments(publish_only=True, limit=200)` 与 manifest
   `expected_slice_keys` 核对，truncated 时拒绝（不混入段数基数）。
2. **换版**：complete 走 06A `switch_current`（409 有界重放语义）；
   新版失败（FAILED）保旧 current 不动（test_failed_keeps_old_current）；
   NO_MATCH 切空当前结果（test_no_match_completes_empty_current）；
   晚到旧版不倒退（test_late_old_version_no_rollback）。
3. **storage_offset_ns**：`derive_storage_offset(manifest, source_bag_dir)` 从
   manifest 证据推导——header 域映射 basis 且首帧 offset 恒定时推导常数；
   mixed/非常数/损坏帧/缺相机 topic → 返回 None 并**阻塞发布**（4 项测试）。
   失败语义：发布前阻断，不发布不登记，reconcile 可重试。
4. **PENDING 不展示**：results 登记后 availability=PENDING 回显；
   complete 才 `_mark_children_available` 切 AVAILABLE；
   06A 检索默认 slices 视图仅 AVAILABLE（既有行为）。

## 验收标准覆盖（AC 对照）

| AC | 实现 | 测试 |
|---|---|---|
| 真实租约/源代次验证 | `require_valid_task_lease`（05 通道，只消费不改 05 枚举）+ `parent.source_generation` 比对 + source fence | test_identity_gates（无效 lease 409/代次不匹配 409/fence 阻断） |
| 重复单子包幂等 | 06A IntegrityError 兜底重放 200 语义 + idempotency_key 重放 | test_report_replay_same_manifest_without_key、test_publish_moves_..._reuses_on_replay |
| 发布后登记故障补偿 | reconcile-scene：按发布目录 per-slice manifest 对账补登记/推进可用，无租约字段 | test_reconcile_backfills_after_publish_without_report、test_reconcile_semantics |
| 晚到旧版不倒退 | switch_current (created_at,id) 有界守卫 | test_late_old_version_no_rollback |
| 新版失败保旧/无命中切空 | complete 仅 SUCCESS/NO_MATCH 换版；FAILED 保旧 | test_failed_keeps_old_current、test_no_match_completes_empty_current |
| PENDING 不展示可用 | 登记 PENDING、complete 才 AVAILABLE；检索默认过滤 | test_full_report_publish_complete_flow |
| 文件非空/可打开/时间证据+登记完成才可用 | `_verify_published_files`：db3 可打开、非空、topic/消息数、CDR 抽验、时间范围 | test_complete_blocked_when_file_missing |
| 不复制父/子文件、原子发布 | staging 同文件系统 os.rename；跨文件系统显式阻断 | test_cross_filesystem_blocked、test_publish_conflict_forbids_overwrite |

## 越界申报（需协调者裁决）

- `app/services/scene_slice_service.py`（05 文件）改了 1 行：
  finish_scene_run 写 `error_message=None` 与模型 NOT NULL 列（默认 ""）冲突，
  complete-scene 走 finish_scene_run 时无原因路径会 500。最小修复 `or ""`，
  不改 05 任何枚举/状态机/租约语义。若协调者认为应回派 1号修，本行可独立 revert
  （76d2958 内 hunk 明确）。
- `app/api/__init__.py` 路由接线：按派单"commit 里带上入口改动，回执申报"执行。
- 05 占位行升级（`_link_av_row`）：事件消费路径 05 不预分配版本行，05 显式 API
  路径预分配占位行——06B 首次回报时把占位行升级为内容身份（同 run 一行，
  不另建），保证换版排序按 05 提交时点。此行为 05/06A/06B 三方交汇点，
  协调者验收时请重点核。

## 验证（worktree，.venv 软链主仓；真实退出码）

| 命令 | 结果 |
|---|---|
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q tests/test_scene_result_report.py` | 24 passed（exit 0） |
| 同上 + tests/test_scene_result_storage.py（06A 回归） | 49 passed（exit 0） |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q`（全量） | 776 passed, 10 skipped, 3 failed（exit 1，3 个全部 tests/test_devflow.py 沙箱用例，worktree `.git` 文件非目录环境差异，与 06A/05 同因；main 基线 8bd5618 同 3 failed） |
| `.venv/bin/ruff check app scripts tests` | All checks passed（exit 0） |
| `.venv/bin/ruff format --check app scripts tests` | 全 formatted（exit 0） |
| `python3 -m compileall -q app scripts` | exit 0 |
| `git diff --check` | 无空白错误 |
| `git diff --name-only 8bd5618..HEAD` | 7 文件，零 .venv/环境产物 |

## 未执行项（如实）

- **OCR：未自跑**——按派单由协调者代跑（flock inbox/ocr.lock）。
  请代跑 `ocr review -c 76d2958 --audience agent`（7 文件，单批安全）。
- MySQL 隔离库 DML 实测：未执行——本任务零 DDL（publish/report 全部走既有表
  DML + 06A 的 guarded UPDATE 语义，两后端同义）；reconcile 的 os.rename 路径
  语义与 MySQL 无关（文件系统层）。SQLite 测试即真实执行环境。
- local_stack.sh test / 处理机/生产：未执行——P0 本地授权，无路由页面改动
  （3 个新 POST 路由为执行面专用，无前端依赖）。
- TASK-08 联调（重启/并发/故障注入端到端）：未执行——聚合任务范围，
  06B 只交付单模块闭环。

## 建议可解锁

- TASK-08（父 06 聚合后，03/04/05 已 DONE）

---

## 返修段（attempt-1-rework，2026-10-10 08:55，status REVIEW_PENDING）

- base：main **3b78736**（cherry-pick 76d2958 → 6e6bb73，自动合并 05 error_message 行无冲突）
- output_commit：**6b21c91**（单文件 tests/test_scene_result_report.py，+11/-5）
- worktree：/home/wang/.local/state/rosbag-scene/wt-04a，分支 scene/task-06b-rework
- 根因确认（返修单第 2 条）：05 强模型 #7 持久身份键（scene_identity_key 终态不释放，同身份全局只建一个 run）使
  test_late_old_version_no_rollback / test_failed_keeps_old_current 的"同 source 同场景第二次建 run"
  命中 run1 终态身份被幂等复用——是测试假设过期，非 05 返修 bug。已按最小改法修复：
  1. `_create_run` 增加可选 `reanalysis_id` 透传（schema 已支持，app/schemas/requests.py:114）；
  2. 两个失败用例的 run2 创建带独立 reanalysis_id（语义=重新分析产生新版本，与用例意图一致）；
  3. 已 grep 全部 `_create_run` 调用点：其余 12 个用例均同 uid 只建一次 run，不受影响，无连带修改；
  4. 未改 05 服务代码（持久身份键为已裁决契约）。
- 验证（真实退出码）：

| 命令 | 结果 |
|---|---|
| 返修前基线复现（6e6bb73 上） | 定向 2 failed, 22 passed（与协调者 08:49 实测一致） |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q tests/test_scene_result_report.py tests/test_scene_result_storage.py` | **49 passed**（exit 0） |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q`（全量） | **804 passed, 10 skipped, 3 failed**（exit 1，3 个全部 tests/test_devflow.py 沙箱环境性，同基线） |
| `.venv/bin/ruff check app scripts tests` | All checks passed（exit 0） |
| `.venv/bin/ruff format --check app scripts tests` | 202 files already formatted（exit 0） |
| `git diff --name-only 3b78736..HEAD` | 7 文件全在 06B scope，零 .venv/环境产物 |

- OCR：未自跑，请协调者对 **6b21c91** 串行代跑（flock inbox/ocr.lock）。
- 合入范围：main 3b78736 之上的 6e6bb73 + 6b21c91 两个 commit（76d2958 已被 d849c54 回退，本次为重新交付）。