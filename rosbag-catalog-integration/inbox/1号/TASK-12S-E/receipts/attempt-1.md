# TASK-12S-E 接收/登记/绑定自动闭环 attempt-1 回执（执行者 A，2026-10-14 23:4x +08:00）

## 交付冻结

- **base**：`16a154fff6f23e20b15498d1285a783713859647`（派单固定开发起点）
- **head（冻结 commit）**：`b39a3ecc76da1f578d32f4e3c88a6ce989cf749d`
- **分支**：`a/task-12s-e-auto-bind`
- **worktree**：`/home/wang/.local/state/rosbag-scene/wt-01-t12se`（.venv 软链主仓，未入库）
- worktree 干净（仅 .venv 未跟踪），未改 seed/旧冻结树/主仓用户脏文件。

## 文件清单（4 个，均在派单独占范围内）

| 文件 | 变更 |
|---|---|
| `app/services/pending_binding.py` | 新增（207 行）：有界后台对账 |
| `app/services/scene_schedule_consumer.py` | `poll_and_consume_purpose_events` 消费前接入对账；零活动返回体与旧口径逐键一致 |
| `app/services/source_service.py` | 快指纹登记三档身份判定（精确/incoming 侧/歧义）替换旧「id 序第一行无条件重绑」 |
| `tests/test_task12se_auto_bind.py` | 新增 12 个机械用例 |

未触及 `app/api/ingest_submissions.py`（接线复用既有 orchestrator 每轮 consume 入口，无新 API 面）；
未碰场景算法/代理/UI/ros2_slice/models/迁移/部署。

## 行为（对应派单契约 1–5）

1. **契约1 时序收敛**：先提交/先登记/并发/登记后崩溃窗口，PENDING_INPUT 提交在
   orchestrator 每轮 `purpose-events/consume` 入口（既有后台有界，未新建常驻进程）
   被对账绑定出用途事件；不等 SCENE_EXEC_HOST 模型槽（对账不查模型负载）。
2. **契约2 准确定位**：后提交按冻结 `intake_snapshot`（root_id/scan_root/ready_root/
   profile_id/profile_version）+ 相对 ready 映射定位原包行：候选为入口相对段、
   ready 根 storage 相对段、ready 根绝对段、prefix 段；命中行还必须落在冻结 ready 根
   **物理相对段**下（跨根同包名 → ROOT_MISMATCH 不绑）；非 basename/快指纹匹配。
3. **契约3 快指纹仅候选索引**：source_service 登记三档——
   - 同快指纹 + 同 relative_path + 非切片（精确原包身份）→ 重登记放行（父子同指纹
     不再误 409，**生产 1012 批首登恢复被拒的根因修复**）；
   - incoming 侧行（受控 scan 根下）+ 本次登记落在受控 ready 根下 → incoming→ready
     移动恢复，归并既有 UID（12S-C 既有语义保留，test_pipeline_api 覆盖）；
   - 同指纹多原包/多 incoming 行 → 409 AMBIGUOUS_SOURCE 可追溯；
   - 无准确身份且同指纹切片存在 → 保留 TASK-02 409（子包走专用派生登记）。
   对账侧命中 SLICE 行 → SLICE_NOT_ORIGINAL 不绑。
4. **契约4 幂等身份**：对账按**本条提交自身**冻结身份出事件（不走
   `bind_ingest_for_registration` 的按 bag 短路——该入口在「旧提交已绑定同原包」时
   会跳过新正式提交，正是生产三包永不收敛的原因）；消费端 `scene_identity_key`
   持久唯一键复用既有 run：不新建 run、不烧模型、不增 attempt、不新增分析版本；
   同身份显式重复提交不新建 run；车辆冲突（冻结 vs 现存 MATCHED 矛盾）→ 既有 409
   fail-closed 按 ERROR:* 隔离不猜车；同入口代次漂移 → GENERATION_DRIFT 隔离；
   资料不齐（无快照/CONFIG_REQUIRED/源未 READY/无源）→ 逐条留痕待补，不制造成功绑定。
5. **契约5 有界对账**：单次 limit=50、单条独立事务（故障只回滚本条下轮重试）；
   时限沿用既有扫描/消费节奏；开关 `PENDING_BINDING_RECONCILE`（默认 1，显式 0 回旧行为）。

## 自测证据（环境：worktree `.venv`（Python 3.10），SQLite 隔离库，mock 执行模式，不烧模型）

| 命令 | 结果 |
|---|---|
| `.venv/bin/python -m pytest tests/test_task12se_auto_bind.py -q` | **12 passed**（2.2s） |
| `.venv/bin/python -m pytest tests/test_task12se_auto_bind.py tests/test_pipeline_api.py tests/test_source_register_purpose.py tests/test_ingest_config.py tests/test_scene_slice_scheduling.py tests/test_t10def1_source_ready.py tests/test_scene_intake_isolation.py tests/test_scene_spray_intake.py -q` | **154 passed** |
| `.venv/bin/python -m pytest tests/ -q`（全量） | **1186 passed, 10 skipped, 4 failed**；4 失败（test_devflow×3、test_web×1）**已用临时 worktree 在 base 16a154f 原样复现为既有失败**，与本交付无关（devflow 沙箱路径与 web 查询口径，均未在派单范围文件内） |
| `.venv/bin/python -m ruff check <4 个变更文件>` | **All checks passed** |
| `git diff --check` | 通过（无空白错误） |

关键断言（不只看 HTTP 200）：
- 主事故场景（先登记 consume 建 run → 源 READY 后建正式提交）：对账绑定后消费
  `created_runs=0 / reused_runs>=1`，单份 SCENE_SLICE run，attempt 不变；
- 重复 consume：run 计数/attempt/事件行数零增长，对账不再绑定；
- 父子同快指纹重登记 200 且归并同一 UID；切片路径/歧义 409 带可追溯原因；
- 跨根 ROOT_MISMATCH、车辆冲突 ERROR:*、代次漂移 GENERATION_DRIFT 均不绑定；
- 开关 0 时 consume 返回体无 `pending_reconciled` 键；零活动时无 PENDING 的
  consume 返回体与旧口径逐键相等（既有 test_scene_slice_scheduling 严格断言不破坏）。

## 未执行项 / 交接

- **未做**：独立验证（TESTER）、OCR（协调者唯一 ocr_runtime 入口）、适用强审、
  合入 main、生产部署——均按门禁由协调者/测试者执行，本回执不替代。
- **真实样本复核建议（TESTER）**：机械用例为 SQLite + 自构造源；建议按派单自测段
  在 MySQL 隔离库对 base SHA 重放两种先后 + 交错并发 + commit 丢失窗口（对账
  幂等由 scene_identity_key 持久唯一键承载，SQLite 与 MySQL 该约束同构）；
  生产 1012 三包已按既有证据复用（REPORT.md binding-repair），无需重烧。
- 越界申报：无。文件冲突：无（独占范围 4 文件）。
- 租约：控制租约已随 ACK 阶段释放；本轮短租约（owner cron-a-poll-d5cb80cf2fc5-
  20261014-202716）在写回执后释放。

## 恢复材料

- 本文件 + `attempt-1-ack.md` + 事件
  `A:a-task12se-attempt1-ack-running-20261014` /
  `A:a-task12se-attempt1-selftest-running-20261014`；
- 分支/commit 在 worktree 内持久保留，返修延续 `a/task-12s-e-auto-bind`。

状态：**REVIEW_PENDING**（交付冻结，等待协调者派独立验证/OCR）。