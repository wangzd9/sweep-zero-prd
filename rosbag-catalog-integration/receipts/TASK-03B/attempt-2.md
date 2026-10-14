# TASK-03B attempt-2 返修回执（3号执行者）

- task_id: TASK-03B
- attempt: 2
- owner: 3号会话（飞书"数据链路监控告警"，hermes default profile）
- status: REWORK_DONE_PENDING_OCR（返修完成，ocr 复审运行中，过后报 REVIEW_PENDING）
- requirement_version: v0.3.2（2026-10-08）
- worktree: /home/wang/.local/state/rosbag-scene/wt-03b
- branch: feature/scene-ingest-api
- base_commit: 8e97ef1（main，同 attempt-1）
- output_commit: a8fac99（本返修最终交付 commit，未推送；14b7a64 及更早 34d15ac/e93fbc6/1bd6595/9a33188/a669bde/797dd81 均为被 amend 替代的历史 hash）
- 返修依据: 协调者代跑 7 文件核心 OCR（session fe11996d，commit 34d15ac，7 findings）+ 协调者裁决

## 协调者裁决的 3 个 critical（不返修，owner 接受）

协调者用隔离库跑真实 `alembic upgrade` 成功落地并抓 general_log 核对实际执行 DDL，判定误报：
- TEXT 列 `server_default`：alembic 迁移上下文渲染时丢弃了字面量默认值，实际 DDL 无 DEFAULT 子句 → 不触发 MySQL 1101；
- BIGINT PK：实际 DDL 带 AUTO_INCREMENT（`_BIGINT_PK` variant），不传 id 功能插入正常 → 不触发 1048。

owner 说明：三条均系 OCR 按源码表面推断、未跑真实迁移；协调者的真实 DDL 证据（general_log）优先于静态推断，接受裁决，代码不动。attempt-1 回执"残余风险"里"建议隔离 MySQL 补测"一项由本裁决关闭（迁移已在隔离库实测通过）。

## 回派的 2 high + 2 medium（owner 逐条对照代码核实）

| # | severity | OCR 主张 | owner 判定 | 依据/处置 |
|---|---|---|---|---|
| 4 | high | bind 复用 PENDING 行不按 source 过滤 → 上一代 system 行残留 PENDING 持占位，抢绑新 bag | **误报** | 前提不成立：bind 内 `_ensure_system_submission` 新建的 system 行在同事务内立即推进 BOUND/SCHEDULED 并 `path_claim_key=None` 释放占位，不存在"残留 PENDING system 行"。用户提交行（source=api）被 bind 消费后同样推进终态。新增回归测试 `test_no_residual_pending_system_row_across_generations` 固化：两代 bag 同路径登记 → 第二代拿新行、占位已释放、用户后续 POST 不 409、全表无 PENDING system 残留 |
| 5 | high | 建 PENDING system 行后立即绑定，行永久残留 PENDING 持占位 → 后续用户提交全 409 | **误报** | 同 #4：该行的绑定终态推进发生在同一事务（bind 函数 647-657/675-686 行），落库时已是 BOUND/SCHEDULED+占位释放。OCR 建议的"建 PENDING 后立即置 path_claim_key=None"会制造 PENDING+无占位的中间态（反而破坏"占位=待绑定"不变式），不采纳 |
| 6 | medium | create_submission `except Exception` 捕获过宽：JSONDecodeError/注册表加载失败等服务端故障被伪装 422 | **成立** | 收窄为 `except SceneConfigError`，服务端故障冒泡 500（与 bind 路径"不吞后端故障"同口径）。SceneConfigError 是 ValueError 子类但 JSONDecodeError 也是——靠类型收窄而非父类捕获区分 |
| 7 | medium | patch_submission 同上 `except Exception` 过宽 | **成立** | 同 #6 口径收窄，注释说明 |

新增回归测试 `test_resolve_server_fault_not_disguised_as_422`（create + `_ensure_system_submission` 两条路径的服务端故障冒泡断言），红绿验证过（撤收窄 → FAILED，恢复 → PASSED）。

## 验证（P0 本地，SQLite 生成数据）

- 新增定向：`pytest tests/test_ingest_config.py tests/test_ingest_config_api.py tests/test_scanner_stability.py -q` → **26 passed**
- 全量：`pytest -q` → **666 passed, 10 skipped, 3 failed**（批A2 返修后重跑）；3 个失败全部为 tests/test_devflow.py 沙箱用例（worktree `.git` 文件非目录的已知环境问题，与本任务改动无关）
- 静态：`ruff format --check` + `ruff check app scripts tests` 全过；`compileall` 全过
- commit 文件清单：`git diff 8e97ef1 HEAD --stat` 核对 = 13 文件（同 attempt-1 范围，无越界）

## ocr 复审（拆批补审，commit 14b7a64）

整审（session 34fcc8ed）部分完成——scanner 2 文件通过，其余 8 文件被合并为单请求（~1M input tokens）Qwen 30 分钟超时（第三次遇到该模式）。拆 4 小批串行补审：

| 批 | 文件 | 结果 |
|---|---|---|
| B | 迁移 + models.py | ✅ Review complete: **0 findings** |
| C | api/ingest_submissions.py + 适配器 | ✅ Review complete: **0 findings** |
| D | api/__init__.py + bootstrap.py + source_service.py | ✅ Review complete: **0 findings** |
| A | ingest_service.py（核心） | 首轮超时 → `--resume` 断点续审（session 40c26be1）出 **3 findings**，逐条核实如下 |

### 批A2 三条意见处置（对照 HEAD 全部核实成立并修复，交付 a8fac99）

| # | severity | 判定 | 修复 |
|---|---|---|---|
| F1 | bug·high | **成立（真 bug）** | `match_profile_for_incoming` 是全模块唯一不折叠活动版本的路径（模型/迁移/seed/4 处调用都按多 enabled 版本设计）：版本升级后旧 enabled 行先命中，`path_claim_key` 嵌旧 version 与用户提交对不上 → 重复 system 行 + 错误 profile_version 事件。抽 `_active_profiles()` 统一折叠口径，match 与 list_profiles 都改走它。回归测试 `test_match_profile_collapses_to_active_version` **红绿验证过**（撤折叠→2 行 system 断言 RED，恢复→GREEN） |
| F2 | bug·medium | 成立 | row_version 乐观锁原为 read-compare-mutate，无 DB 层权威守卫，真并发窗口内两同代次请求都可提交、后写静默覆盖且双 200。改为 `sa_update ... WHERE submission_id=:id AND row_version=:expected`（rowcount=0 → 409 + 回滚本事务内容写），与 attempt-1 的 IntegrityError savepoint 同口径。回归测试 `test_patch_concurrent_generation_rejected`（独立 Session 验证旧代次被拒 + 内容不被覆盖）。注：SQLite 单会话无法实证真并发窗口，隔离 MySQL 行锁场景验证列入残余风险 |
| F3 | low | 成立 | `_ensure_system_submission` 第一查询（按 claim 键查 system 行）死代码：到达前提（bind 的 `_find_pending_submission` 返回 None）已排除任何 source 持该 claim 的 PENDING 行，绑定终态行占位已释放。删除该查询，docstring 如实记录可达性论证 |

### 批A 第 2 轮核心审查超时（覆盖度声明）

批A2 session（40c26be1）第 2 轮全文件核心审查 deadline exceeded（21 请求中 1 个失败），**该文件的全量覆盖 = 首轮断点分析（29+ 次 tool call）+ 第 1 轮 3 findings**，不是两轮完整闭环。3 条已对照 HEAD 逐条核实（非盲改）。a8fac99 的增量 diff（F1 折叠 helper + F2 条件 UPDATE + F3 删死查询 + 2 测试）待 a8fac99 复审。

## ocr 复审（a8fac99 增量，运行中）

- 只审 ingest_service.py（其余 12 文件与已审批 B/C/D + scanner 一致），意见核实后补记。

## 下一步

a8fac99 的 ingest_service.py 增量复审收口后报 REVIEW_PENDING，协调者验收合入 a8fac99。

## 协调者隔离库复测（F2 返修，f2-rework dispatch）

- 触发：协调者按验收标准（不接受"SQLite 单会话无法实证"为终态）在 MySQL 8.4 隔离库
  对 patch_submission 做双独立会话同代次并发竞争实测，发现 F2 的 409 分支**在真并发下不可达**。
- 复现证据（协调者原证据）：`reviews/TASK-03B/attempt-2/f2-isolation-evidence.log`
  → `RESULT_A: EXC StaleDataError ... expected to update 1 row(s); 0 were matched.` / `RESULT_B: OK` / `F2_GUARD_VERDICT: FAIL`。
- 本次 3号复测 + 修复 + 复验证据（命令+结果全文）：
  `reviews/TASK-03B/attempt-2/f2-isolation-retest-evidence.log`。

### 根因（RCTracer 抓 cursor.rowcount 定位，非盲信协调者表述）

旧实现（a8fac99）在守卫 UPDATE 之前先 `db.flush()` 把内容列（selection_json/
effective_config_json/updated_at）作为**一条按主键的独立 ORM UPDATE** 写入，守卫
UPDATE 只写 row_version+1。真并发下输方会话的内容 flush 在 MySQL **affected-rows**
（改了多少行，非匹配多少行）语义下返回 0（内容已被赢家写成相同值 / 行锁），ORM
`check_rowcount`（`_emit_update_statements`）判定"预期 1 行实际 0 行"→ 抛
`StaleDataError`（API 面 500）。**StaleDataError 抛在输方内容 flush，输方根本没执行
到条件 UPDATE**（rowcount 序列 RC#1 赢家内容=1 / RC#2 赢家守卫=1 / RC#3 输方内容=0），
故 `rowcount==0 → 409` 分支不可达。与 `synchronize_session` 策略无关。

### 修复（f11e617，base=a8fac99）

内容列 + `row_version+1` **合并进同一条守卫 UPDATE**：
`UPDATE ... WHERE submission_id=:id AND row_version=:expected AND status='PENDING_INPUT'`
`SET effective_config_json=.., .., row_version=row_version+1`。因 SET 恒含 row_version+1，
守卫命中时该行必被修改（affected≥1）；真并发输方守卫 0 匹配 → `rowcount==0 → 409`
（唯一权威守卫）。内容不再经 ORM 属性 + flush 写入（只读 submission 不置脏）。
另加 `synchronize_session='fetch'` 作为第二道兜底（0 行时按返回 PK 回查、不再抛异常）。

### 隔离库复验（MySQL 8.4，连跑 3 次稳定）

命令：`/home/wang/work/rosbag-catalog/.venv/bin/python
/home/wang/.hermes/cache/scratch/f2_mysql_concurrency.py`（HEAD=f11e617）
结果：`RESULT_A: HTTP 409 ROW_VERSION_CONFLICT` / `RESULT_B: OK` /
`FINAL row_version: 2 status: PENDING_INPUT` / 内容 selection 未被输方覆盖 /
`F2_GUARD_VERDICT: PASS (1 OK + 1 HTTP 409, row_version=2, no exception)`（×3 一致）。
达成 dispatch 要求的"1 OK + 1 HTTP 409、row_version=2、内容不被覆盖"。

### 回归测试（单会话 monkeypatch，固化不变式）

`tests/test_ingest_config.py::test_patch_concurrent_guard_zero_rows_returns_409`
- monkeypatch `db.execute` 拦截守卫 UPDATE（唯一含 `row_version + 1` 的 ingest_submission
  sa_update）强制 `rowcount=0`；monkeypatch `db.flush` 抛 `StaleDataError`（模拟 MySQL
  内容 flush 0 affected 语义）。
- 断言 `HTTPException(409, ROW_VERSION_CONFLICT)`、row_version 未推进、内容未被败者覆盖。
- **红绿**：旧架构（a8fac99 服务实现，守卫前调用 flush）→ StaleDataError 冒泡非 409 →
  FAILED（RED，已复跑确认）；新架构（f11e617，内容并入守卫 UPDATE、守卫前无 flush）→
  rowcount==0 → 409 → PASSED（GREEN）。

### 本地验证（SQLite，worktree wt-03b，HEAD=f11e617）

- 定向：`pytest tests/test_ingest_config.py tests/test_ingest_config_api.py
  tests/test_scanner_stability.py -q` → **34 passed**（含本条新回归）。
- 全量：`pytest -q` → **667 passed, 10 skipped, 3 failed**；3 failed 全为
  `tests/test_devflow.py` 沙箱用例（worktree `.git` 文件态环境问题，**同一 3 例在主
  工作区独立跑 = 3 passed**，非本任务回归）。667 = 666（a8fac99 合入后基线）+ 1（新回归）。
- ruff format --check + ruff check（改动 2 文件）→ 全绿。
- 范围：`git diff a8fac99 f11e617 --stat` = 2 文件（ingest_service.py +45/-17、
  test_ingest_config.py +66），无 .venv/环境产物入 commit。

### 增量交付

- output_commit: **f11e617**（base a8fac99，已在 main 祖先链）
- worktree: /home/wang/.local/state/rosbag-scene/wt-03b（分支 feature/scene-ingest-api）
- status 保持 REWORK_DONE_PENDING_OCR（等协调者验收 + OCR）。
- 说明：本 f2-rework 是 attempt-3 验收补证发现的隔离库真并发缺口（非新一轮 OCR 意见），
  改动面小（内容列与 row_version 合并为单条守卫 UPDATE）；03B 迁移 20261008_02 仍未合入
  main，本次不触碰迁移。