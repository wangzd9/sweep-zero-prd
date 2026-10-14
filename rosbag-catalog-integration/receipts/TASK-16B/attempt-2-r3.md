# 回执：TASK-16B attempt-2-r3（强审 SR-16B-R2 两项残余 CORRECTION 最小关闭）

- status: **REVIEW_PENDING**
- 派单：`inbox/3号/TASK-16B/attempt-2-r3-dispatch.md`（2026-10-13 18:03:29 落盘，当前 Codex 协调者 r17x）
- owner：C
- base：`e152465`（r2 冻结 head，延续 commit）
- 交付 head：**`603e695`**（单 commit，2 文件 +562/-33）
- 分支/worktree：`c/task-16b-scene-host-proxy` @ `wt-03b-t16b`
- 回执时间：2026-10-13 18:4x +08:00

## 一、问题 ID 设计与修复（只 R1-02/R1-03，原 R1-01/04/05 已关闭不重做）

强审 result.md（`reviews/strongmodel/runs/005277e6e60a43308431b5505f0bf6dc/result.md`）全文已读。

### R1-02：步骤回报无确认结果 → 调用方无条件清 recovery（4 反例）

**设计**（不扩面、不加重试层、不模拟后端）：
1. `reconcile_terminal` 返回 `bool`（终态已确认/未确认）：对账读失败=False；转移被拒=False；补报成功或补报后再对账确认=True。
2. `_report_steps` 返回 `unconfirmed: list[dict]`（{step,target,detail}）：DONE/FAILED 步的 `ensure_running` 返回 None（RUNNING 前置对账读失败/迁移未落地）、终态 post+reconcile 均未确认、SKIPPED 未确认——三种未确认全部收集，不再静默吞掉。
3. `_report_step_single`（REGISTER 终态后补报）返回 `bool`：对账读失败=False；补报后重读仍非 DONE=False（r2 此处异常容忍后直接 return=静默未确认）。
4. 收尾按确认结果分治：
   - `_finish_failure(..., unconfirmed=...)`：**先** `save_recovery_state(pending_failure={target:SCENE_FAILED, error, unconfirmed_steps, at})` **再** `_confirm_terminal` 回报；确认→清台账（r2 行为保持），未确认→台账含意图保留。
   - `_finish_success(..., unconfirmed=...)`：七步未确认或 REGISTER 未确认→写 `pending_failure={target:SCENE_DONE,...}` 保留台账；全确认→清台账（原行为）。

**真实 Backend 约束核**（写代码前实测 app 面，非假设）：
- `require_valid_task_lease`（app/domain/security.py:33）：`lease_token_hash` 为空→直接 return。`finish_scene_run`/`publish_run`/`activate_due_auto_retries` 均 `clear_task_lease`→**run 终态切换后步骤写恒过**（complete-scene 清租约后 REGISTER 补报可行=与代码注释"容忍 409"口径一致，409 面来自状态机而非租约）。
- `update_step`（app/services/pipeline_service.py:836）：`attempt != run.attempt → 409`。**auto-retry bump run.attempt 后，旧 attempt 的补报步骤写被守卫拒绝**——closeout 不得模拟支持，按真实约束留痕容忍（fixture 已建等价守卫面验证）。
- REGISTER/complete 调用顺序：成功路径 `_report_steps(terminal_step="REGISTER")`→orchestrator 内 complete-scene（清租约切 SCENE_DONE）→`_report_step_single(REGISTER)` 终态后补报（恒过）→`_finish_success` 按确认结果收尾。

### R1-03：失败收尾意图未持久化 → 重启掉回业务执行（extra_model_invocations=1 反例）

**设计**（区分业务执行恢复 vs 待收尾恢复）：
1. `save_recovery_state(..., pending_failure: dict | None)`：失败收尾意图=原 attempt/目标终态/原因/待补报步骤，**持久化先于回报尝试**（`_finish_failure` 首动作）。
2. 新增 `_recover_closeout(cfg, backend, state)`：只做对账补报收尾——run 详情读失败（Backend 短时不可用）→保留台账等待下轮；非终态→按原身份补报目标终态一次（不无限重试）再对账确认；确认终态后补报 unconfirmed_steps（迁移表口径+attempt 守卫容忍）；**步骤终态未确认也保留台账**（不标成功）；确认才清台账；ACTIVE 恒释放。
3. `recover_pending_runs`：台账含 `pending_failure` 且旧写者已停→认领 RECOVER_CLOSEOUT 起 closeout 线程（不计 recovered 之外的副作用）；**不再进入 execute_run**（模型执行计数新增 0）。无 pending_failure 的既有台账走原业务执行恢复路径（行为不变）。

## 二、自测证据（真实执行，先失败断言→修复到通过）

环境：`wt-03b-t16b` `.venv`（python3.10）、`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`、dev 机。

| 定向断言（新增 7） | 注入 | 关键断言 | 结果 |
|---|---|---|---|
| test_r3_02_done_uncommitted_repost_also_fails_keeps_recovery | DONE 步持久 500 未提交 | unconfirmed 含 INFER/DONE；DB 非 DONE；_finish_success 后台账 pending_failure.target=SCENE_DONE+待补报步骤；ACTIVE 清 | PASS |
| test_r3_02_done_lost_response_persistent_keeps_recovery | DONE 步持久 500 committed（迁移表 QUEUED→DONE 拒落=持续丢响应） | 未确认→台账保留 | PASS |
| test_r3_02_reconcile_get_fails_keeps_recovery_then_closes | 前 2 次 run 详情读 503（初始对账+reconcile 读）+DONE post 500 未提交 | r2 会静默清台账→现报未确认保留；故障解除后 `_recover_closeout` 只补报收敛 INFER=DONE、清台账、/results 零调用（不重执行） | PASS |
| test_r3_03_failure_intent_persisted_then_recover_closeout_no_rerun | SCENE_FAILED 上报 503 未提交+死亡 identity 模拟重启 | pending_failure 意图持久化（target/原因/待补报步）；recover 认领=1；**monkeypatch execute_run 捕获零调用**（r2 反例=重烧模型）；终态补报 SCENE_FAILED 收敛、INFER=FAILED、台账清 | PASS |
| test_r3_03_backend_still_down_keeps_ledger_no_rerun | run 详情读持续 503 | recover 认领后保留台账等待下轮；零 execute_run；不标成功；ACTIVE 恒释放 | PASS |
| test_r3_closeout_register_after_complete_scene | run=SCENE_DONE（complete-scene 后）+REGISTER 步持久 500 未提交 | _report_step_single 返回 False（r2 静默吞）→台账保留；故障解除后 closeout 终态后补报 REGISTER 收敛 DONE、清台账 | PASS |
| test_r3_closeout_attempt_guard_409_tolerated | run 已终态+auto-retry bump attempt=2（fixture attempt 守卫启用） | 旧 attempt INFER 写全 409 零落状态（真实 update_step 守卫面）；必须实际尝试补报（非跳过）；终态确认后清台账、ACTIVE 释放 | PASS |

**修前失败证据（最小）**：
- R1-03 核心反例在 r2 `e152465` 上即强审已复现（`extra_model_invocations=1, recovered=1`，result.md 表）；本轮测试 4 在修复前 assert `pf`（pending_failure 持久化）失败=r2 `_finish_failure` 不写意图，recover 起 execute_run 重烧模型。
- R1-02 测试 1 在修复前 `_finish_success` 无 unconfirmed 参数、无条件 clear=台账不存在，assert 失败。

**回归**（复用 r2 已通过 39 用例及未改模块证据，按派单只跑受影响定向组）：
- `pytest tests/test_scene_host_proxy.py tests/test_scene_host_orchestrator.py -q` → **46 passed**（17.36→43.54s，27 proxy 既有零回归+7 新 r3+12 orchestrator）exit 0
- `ruff check scripts/scene_host_proxy.py tests/test_scene_host_proxy.py` → **All checks passed**（--fix 自动整理 import 顺序后）
- `python -m compileall` 两文件 → OK

**零越界**：`git diff --stat e152465..603e695` = 2 文件 +562/-33，只动 `scripts/scene_host_proxy.py`+`tests/test_scene_host_proxy.py`（派单固定边界）；不碰 orchestrator/fake_vlm/app/迁移/12S-C。

## 三、边界申报（未模拟后端支持，按真实接口能力处理）

1. **auto-retry bump attempt 面**：run 终态 SCENE_FAILED 后若 `_schedule_auto_retry` 生效并 `activate_due_auto_retries` bump `run.attempt`，旧 attempt 的补报步骤写被 `update_step` 409 守卫拒绝（如实留痕，步骤事实保留本地 checkpoint，不模拟支持、不标成功）。closeout 的 run 终态补报本身不受影响（`update_status` 无 attempt 守卫）。fixture 已建等价守卫面（attempt_guard）验证容忍路径。
2. **complete-scene 后租约已清**：REGISTER 补报恒过（真实 `require_valid_task_lease` lease 空口径），非 409 面；原代码注释"容忍 409"保留兼容（状态机拒绝面仍可能）。
3. `pending_failure` 台账的恢复分治只改 `recover_pending_runs` 一条分支（含意图→closeout；不含→原 execute_run 路径逐字节保持），既有恢复测试 3 个零回归。

## 四、未执行项

- 真实栈/MySQL/掉电验证留 TESTER 独立核恢复（派单收口链：协调者增量 OCR+原授权两问题复审→TESTER）。
- 全仓 pytest 未重跑（派单口径：复用 r2 已通过 39 用例及未改模块证据）。

## 五、收口链（等协调者）

机械核验→增量 OCR `--from e152465 --to 603e695`（固定入口，2 文件）→强审增量复审（**只 R1-02/R1-03 两问题 ID**，授权 `6b2d83fb` 剩 4/5，期限 2026-10-14 13:27:15）→TESTER 独立核恢复→合入 16B→**12S-C 依赖重算**（C 前置 `92dcb52` 冻结；r3 合入+12S-B S9 合入后按接线核验单做最终集成候选，C 短接续检查点已落盘：merge r2 零冲突+38 passed，事件 `c-t12sc-finaldep-assembly-checkpoint-20261013`）。

12S-C 保持冻结，不重跑已交付实现。