# 回执：TASK-16B attempt-2-r2（强审 SR-16B-R1 5 项阻塞最小返修）

- status: REVIEW_PENDING
- 交付时间：2026-10-13 16:2x +08:00
- owner：C（3号，16B 原 owner）｜attempt：attempt-2-r2
- base：`40ab818`（attempt-2-r1 交付冻结，机械核验全绿+增量 OCR 0 findings 在案）
- head：`e152465`（`c/task-16b-scene-host-proxy` @ `wt-03b-t16b`，base 上单 commit）
- diff 范围：`git diff --stat 40ab818..e152465` = 2 文件 +506/-43，**零越界**（只动 `scripts/scene_host_proxy.py` + `tests/test_scene_host_proxy.py`，不碰 orchestrator/fake_vlm/app 面/迁移/12S-C 文件）

## 一、逐项修复（R1-01~05，均按强审 result.md 最小修复边界）

### R1-01 [高] H1 单写者——已终态 run 不得重执行
- 修复：`resolve_spec` 在 attempt 对账后新增 run 状态对账——`run.status ∈ _TERMINAL_RUN_STATUSES` → `SpecError("run 已终态…重复 /run 不重执行")`，走既有 RESOLVING 失败收尾（台账清除/ACTIVE 释放/`_confirm_terminal` 判定「已达其他终态」不再重报 SCENE_FAILED）。
- 不扩面：`try_reserve` 释放后读空→409 面未动（强审已核无独立反例）。
- 注入证据：`test_r1_01_late_duplicate_run_after_release_not_rerun`——正常全链 202→收敛（模型 INFER 步 post 计数基线）→ Backend run 置 SCENE_DONE → 迟到重复 /run 拿 202（缺陷触发路径）→ 终态对账拒绝：`/steps/INFER` post 数不变（**无第二次模型执行**）、SCENE_FAILED post=0、台账清、ACTIVE 释放；释放边界后再重放一次仍不重执行。

### R1-02 [高] H2 终态必达——失败终态写入对账补报
- 修复：`_report_steps` 新增 `reconcile_terminal`（终态 post 返回 None 时按本 attempt 对账读 run_detail：DB 已=target → 确认不重复 post；DB 非 target 且状态机允许 → 重试 post 一次，仍失败留痕不无限重试）；DONE/FAILED 两分支接入。RUNNING 前置 post 失败同样经 `ensure_running` 对账（未确认不冒进终态）。`_report_step_single`（REGISTER 补报）同口径加对账段。
- 注入证据（两分支）：
  - 分支一「已提交但响应丢失」：`test_r1_02_step_terminal_lost_response_converges`——step_fail[DONE] committed=True（DB 已落 DONE、HTTP 500）→ 对账确认、DONE post 恰好 1 次、DB 收敛 DONE。
  - 分支二「未提交」：`test_r1_02_step_terminal_uncommitted_converges`——step_fail[RUNNING]/[DONE] committed=False（HTTP 500、DB 不落）→ RUNNING 对账重试落地（post 2 次有界）、DONE 对账补报（post 2 次有界）、DB 收敛 DONE。

### R1-03 [高] H4 失败恢复——先对账再清恢复台账
- 修复：新增 `_confirm_terminal`（对账读 run 状态：=target → 确认；∈其他终态 → 确认不覆盖；可读非终态 → 按原身份重试 post 一次再对账；读失败=状态不确定 → False）；`_finish_failure` 改为 **confirmed 才 `clear_recovery_state`**，未确认保留台账留痕（重启 `recover_pending_runs` 按原身份重新对账续收尾）；ACTIVE 恒释放。
- 注入证据（两分支）：
  - 上报未提交：`test_r1_03_finish_failure_uncommitted_keeps_recovery`——status_fail[SCENE_FAILED] committed=False（503、DB 仍 SCENE_RUNNING）→ **台账保留**（`state_path exists`）、ACTIVE 清、DB 未动。
  - 已提交但响应丢失：`test_r1_03_finish_failure_lost_response_confirms_and_clears`——committed=True（500、DB 已落 SCENE_FAILED）→ 对账确认、SCENE_FAILED post 恰好 1 次、**台账清除**、ACTIVE 清。
  - 其他终态不覆盖：`test_r1_03_confirm_terminal_other_terminal_no_dup_post`——run 已 CANCELLED → `_confirm_terminal` 返回 True 且 **/status post=0**。

### R1-04 [中] H4 收尾恒执行——unlink 异常不中断
- 修复：`clear_recovery_state` 捕获 `OSError`（非 FileNotFoundError）→ 留痕（含「ledger kept as restore evidence」）不外抛；`_finish_failure` 的 `ACTIVE.remove` 在清理异常下仍执行（调用顺序：confirm→release→clear(吞错)→remove）。except 范围未扩（强审已认可 `except Exception` 面不碰）。
- 注入证据：`test_r1_04_unlink_error_keeps_ledger_and_releases_active`——monkeypatch `Path.unlink` 抛 `PermissionError` → `_finish_failure` 正常返回：ACTIVE 不残留、台账原位保留（恢复依据）。

### R1-05 [中] H6 台账耐久——replace 后 fsync 父目录
- 修复：`_write_json_atomic` 在 `os.replace` 后 `os.open(parent, O_RDONLY)` + `fsync(dfd)` + close；docstring 明确掉电语义限于受支持文件系统（ext4/xfs 等 POSIX 持久化语义）。同 PID tmp 名冲突面未扩（强审未立阻塞项）。
- 注入证据：`test_write_json_atomic_fsyncs_before_replace`（增强）——记录 os.open/fsync/replace 序列，断言调用顺序 `file_fsync → replace → dir_fsync`，内容正确、tmp 无残件。

## 二、测试基建变更（声明：测试文件内，非业务面）

`FakeBackend` 由静态假后端升级为**有状态**假后端（R1-01~03 注入必需：终态对账/步骤收敛需要 Backend 侧状态真实推进）：
- step 迁移跟踪：`_FAKE_STEP_TRANS` 与 `app/domain/transitions.py` STEP_TRANSITIONS 同口径（QUEUED→{RUNNING,SKIPPED,CANCELLED}、RUNNING→{DONE,FAILED,CANCELLED}、终态空集）；非法迁移 409。
- run status 终态写：`/status` POST 落 `self.status`，`/complete-scene` 置 SCENE_DONE。
- 注入面：`step_fail`/`status_fail`（`committed`=已提交但响应丢失/未提交，一次性消费）。
- 既有 20 用例零改动语义（唯一适配：`test_recovery_drops_non_running` 的 `fb.run_detail["status"]` 改 `fb.status`，同一语义新字段）。

## 三、自测（真实执行，环境=`wt-03b-t16b`，`.venv/bin/python`，`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`）

| 命令 | 结果 |
|---|---|
| `pytest tests/test_scene_host_proxy.py -q` | **26 passed**（既有 20 零回归 + R1 新注入 6：r1_01 / r1_02×2 / r1_03×3）exit 0 |
| `pytest tests/test_scene_host_proxy.py tests/test_scene_host_orchestrator.py -q` | **39 passed** exit 0 |
| `pytest tests -q --ignore=tests/test_bag_cleanup_mysql.py`（全仓口径） | **889 passed, 3 failed**（`test_devflow.py` 3 例=**base `40ab818` 同口径复现**，临时 worktree 于 base 独立复跑同样 3 failed/21 passed，与本单无关） |
| `ruff check scripts/scene_host_proxy.py tests/test_scene_host_proxy.py` | All checks passed |
| `compileall` 两文件 | OK |
| `git diff --stat 40ab818..e152465` | 2 文件 +506/-43=本回执清单逐文件一致 |

- 未执行项：真实栈/MySQL/模型全链冒烟（16B 交付口径=模块自测+故障注入；real 栈冒烟属 TESTER 收口与 12S-C 接线核验单，禁本单自宣 PASS）；OCR/强审（协调者门禁）。
- 越界申报：无（业务面零改动，测试基建升级已声明）。

## 四、下一步（协调者收口链，按派单三节）
机械核验（base 祖先/diff 逐文件/独立复跑）→ **返修增量 OCR 固定入口** `--from 40ab818 --to e152465`（单业务文件小增量）→ **强审增量复审**（只看 R1-01~05 问题 ID+修复 diff+注入证据，授权期限内 60min 剩 4/5）→ TESTER 收口（r1 口径）→ 合入 main → 16B DONE → 重算 12S-C 依赖。12S-C 前置（`wt-03b-t12sc` @ `92dcb52`）按派单冻结待 16B 接受后续。