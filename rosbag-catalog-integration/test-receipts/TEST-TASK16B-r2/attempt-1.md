# 独立验证报告：TEST-TASK16B-r2 / attempt-1

- 状态：**TEST_REPORT_PENDING**（交协调者裁决；普通测试 PASS ≠ OCR/强审/生产门禁通过）
- 验证时间：2026-10-13T17:55~18:40+08:00
- owner：TESTER
- 被测固定快照：base=`40ab818`，**head=`e1524657bda1f66f03034cb72ef05cd65e0c1dfc`**（`c/task-16b-scene-host-proxy` @ wt-03b-t16b，base 上单 commit）
- 独立隔离环境：新建 `git worktree --detach` `/home/wang/.local/state/rosbag-scene/wt-tester-t16b-r2` @ `e152465`（不移动/不改原开发树；原树 porcelain 仅 `.venv/scratch` 未跟踪，冻结未动）；`.venv` 软链复用
- diff 越界核对：`git diff --stat 40ab818..e152465` = `scripts/scene_host_proxy.py` + `tests/test_scene_host_proxy.py`，共 +506/-43，**零越界**（与回执逐文件一致）

## 一、强审在途结果告知的独立复现（`inbox/TESTER/TASK-16B-r2/strong-result-addendum.md` 18:03:29）

强审 `SR-16B-R2-20261013`（call `005277e6e60a43308431b5505f0bf6dc`，result.md 18:0x）判定 **REWORK_REQUIRED**：R1-01/R1-04/R1-05 已关闭，**R1-02/R1-03 未关闭（各存在阻塞反例）**。按 addendum 要求"保留实际结果并注明反例、最小独立复现可记录 FAIL、不把 r2 模块绿当最终 PASS"，本 TESTER 用真实 `Backend`→`FakeBackend` HTTP 链独立最小复现（脚本 `/home/wang/.hermes/cache/scratch/repro_r2_counterexamples.py`，只读被测代码不改实现）：

| 复现项 | 注入 | 实测结果 | 判定 |
|---|---|---|---|
| R1-02 DONE 分支 | PUBLISH 已落 RUNNING，DONE 写入未提交（500）+ 对账读超时 | 步骤永久卡 `PUBLISH=RUNNING`、run 已 `SCENE_DONE`、**recovery 已被收尾清除** | **FAIL（反例复现）** |
| R1-02 FAILED 分支 | PUBLISH 已落 RUNNING，FAILED 写入未提交（500）+ 对账读超时，run 级 SCENE_FAILED 已提交确认 | 步骤卡 `PUBLISH=RUNNING`、run `SCENE_FAILED`（`run_confirmed=True`）、**recovery 清除** | **FAIL（反例复现）** |
| R1-03 阶段1 | SCENE_FAILED 上报未提交（503） | `_confirm_terminal=False`，台账保留但 **stage=EXECUTING（无失败目标/错误事实）**，run 仍 SCENE_RUNNING | **FAIL（反例复现）** |
| R1-03 阶段2 | 代理重启、Backend 恢复 | `recover_pending_runs` → `recovered=1`、**extra_model_invocations=1**（再次进入模型执行，强审同口径计数） | **FAIL（反例复现）** |

**独立复现 4/4 与强审 result.md 逐项一致**。R1-02/R1-03 在本固定 head `e152465` 上记 **FAIL**（阻塞 16B 合入），已获 r3 返修单（原 C）；R1-01/R1-04/R1-05 维持下方 PASS（模块测试+断言独立核）。**r2 整体：模块测试全绿 ≠ 最终 PASS，合入门禁保持关闭待 r3。**

## 命令 / 退出码（均在 `wt-tester-t16b-r2`，`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python`）

| 命令 | 结果 |
|---|---|
| `pytest tests/test_scene_host_proxy.py -q` | **27 passed** in 17.36s，rc=0 |
| `pytest tests/test_scene_host_proxy.py -v -k r1_` | **7 passed**（r1_01×1 / r1_02×2 / r1_03×3 / r1_04×1），rc=0 |
| `pytest tests/test_scene_host_proxy.py tests/test_scene_host_orchestrator.py -q` | **39 passed** in 28.46s，rc=0 |
| `pytest tests -q --ignore=tests/test_bag_cleanup_mysql.py` | **889 passed, 3 failed**（失败=devflow 3 例，见下） |
| `ruff check scripts/scene_host_proxy.py tests/test_scene_host_proxy.py` | All checks passed，rc=0 |
| `compileall` 两文件 | OK |

**devflow 3 failed 独立归因**：在 base `40ab818` 的独立 worktree `wt-tester-base40ab818` 复跑 `pytest tests/test_devflow.py -q` → **同样 3 failed / 21 passed**（`ValueError` @ scripts/devflow.py:711）。即 base 同口径预存在的环境性失败，**与本 r2 无关，不计为 r2 回归**。

## 逐项独立核（R1-01~05，读注入测试断言+源码，不抄执行者 PASS）

- **R1-01 迟到重复 /run 不二次执行**：`test_r1_01_late_duplicate_run_after_release_not_rerun` PASS。独立核断言：Backend run 置 `SCENE_DONE` 后迟到重复 `/run` 拿 202（缺陷触发路径）→ `len(fb.wrote("/steps/INFER")) == model_calls_1`（**无第二次模型步**）、`/status` 中 `SCENE_FAILED` post=0、台账 `state_path` 不存在、`run_id not in ACTIVE`；释放边界后再重放仍不重执行。源码：`resolve_spec` 对账 `run.status ∈ _TERMINAL_RUN_STATUSES` → `SpecError`。**PASS**
- **R1-02 终态响应丢失/未提交对账**：`test_r1_02_step_terminal_lost_response_converges` + `test_r1_02_step_terminal_uncommitted_converges` 双分支 PASS。独立核：committed=True（DB 已落 DONE、HTTP 500）→ 对账确认 DONE post 恰 1 次、DB 收敛；committed=False（DB 不落）→ RUNNING/DONE 对账补报 post 有界（≤2）、DB 收敛。源码：`_report_steps.reconcile_terminal`（按本 attempt 读 run_detail，=target 不重 post；非 target 且状态机允许重试一次）。**PASS**
- **R1-03 失败台账保留/确认清除/不覆盖他终态**：`test_r1_03_confirm_terminal_other_terminal_no_dup_post` + `test_r1_03_finish_failure_uncommitted_keeps_recovery` + `test_r1_03_finish_failure_lost_response_confirms_and_clears` 三例 PASS。独立核断言：未确认终态 → `state_path.exists()`（**台账保留**）且 `run_id not in ACTIVE` 且 `fb.status==SCENE_RUNNING`（DB 未动）；已提交响应丢失 → 对账确认后 `SCENE_FAILED` post 恰 1 次、台账清除；run 已 CANCELLED → `_confirm_terminal` 返回 True 且 `/status` post=0（不覆盖他终态）。源码：`_confirm_terminal`（先对账再 `clear_recovery_state`），ACTIVE 恒释放。**PASS**
- **R1-04 unlink 异常不中断收尾**：`test_r1_04_unlink_error_keeps_ledger_and_releases_active` PASS。独立核：monkeypatch `Path.unlink` 抛 `PermissionError` → `run_id not in ACTIVE`（**ACTIVE 恒释放**）且 `state_path.exists()`（**台账原位保留作恢复依据**）。源码：`clear_recovery_state` 捕获 `OSError`（非 FileNotFoundError）留痕不外抛。**PASS**
- **R1-05 replace 后父目录 fsync**：`test_write_json_atomic_fsyncs_before_replace`（增强）PASS。独立核：`events == ["file_fsync", "replace", "dir_fsync"]`（**调用顺序正确**）、内容 `{"k":"v"}` 一致、`sub/.*tmp` 无残件。源码：`_write_json_atomic` 在 `os.replace` 后 `os.open(parent,O_RDONLY)`+`fsync(dfd)`。**PASS**

## 结论（修订）

- **R1-01 / R1-04 / R1-05：PASS**（模块测试+注入断言独立核实，与强审关闭判定一致）
- **R1-02 / R1-03：FAIL**（强审反例经本 TESTER 独立最小复现 4/4 确认，见第一节；阻塞 16B 合入）
- **回归：无新增**（scene_host_proxy 27 passed、proxy+orchestrator 39 passed、全仓 889 passed；唯 3 devflow failed 在 base `40ab818` 独立复现同口径，预存在环境性，非 r2 引入）
- **r2 整体判定：REWORK_REQUIRED 独立佐证成立**——模块测试全绿不能替代最终 PASS；原 C 已获 r3 返修单，r3 冻结后 TESTER 另核 R1-02/R1-03 两反例与恢复路径
- **静态：ruff 全绿 + compileall OK**
- **越界：无**（diff 仅 2 文件 +506/-43，与回执一致）

## 未执行项（如实申报，非失败）

- 真实栈 / MySQL / 真实模型全链冒烟：本单口径=模块自测+故障注入，无真实模型调用、无 NAS 发布、无生产写入（派单明确禁止）；real 全链属 12S-C 接线核验单与 TESTER 最终收口，**不等同 12S-D 正式全链**，本单不预宣其 PASS。
- OCR / 强审：协调者门禁，TESTER 不启动。
- S9 新 head 增量复验：S9 冻结 head 未到达，不预跑、不虚报；到达后按其增量单复用 1184/44 探针做受影响矩阵。

## 边界声明

- 代码如有失败返原 C，本 TESTER 未改任何业务实现。
- 本 PASS 为固定快照 `e152465` 的独立模块级验证；**旧 SHA 匹配项按快照复用，未伪装最终 PASS**。
- 交付 TEST_REPORT_PENDING，交协调者裁决合入门禁。

## 清理

- 独立 worktree `wt-tester-t16b-r2`、`wt-tester-base40ab818` 为本轮新建测试资源，验证保留至协调者复核；原开发树 `wt-03b-t16b` @ `e152465` 冻结未动。