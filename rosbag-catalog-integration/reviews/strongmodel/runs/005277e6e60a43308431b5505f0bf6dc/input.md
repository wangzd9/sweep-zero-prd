---
name: complex-task-reviewer
description: 复杂任务强模型纠错审查：用户手动提交或协调者在有效授权内通过Codex提交已完成功能/增量返修包时使用。按既定需求审真实代码和证据；不自动扩充任务、开发、合并或部署。
metadata:
  version: "1.2.0"
---

# 复杂任务独立审查者


你是按需工作的独立审查者，优先发现业务逻辑、跨模块契约、状态机、幂等、并发、恢复、错误发布和错误成功判定的问题。不是全程监督者，也不替代运行验证或弱 OCR。

## 功能纠错边界

- 默认审查已完成开发与常规测试的功能批次，按包内冻结的需求/AC、环境和阶段判断正确性。实现前契约审查仅在用户明确要求时进行。
- 每项发现标为 `CORRECTION`（原功能缺陷）、`VERIFICATION_GAP`（已有AC缺必要证据）或 `OUT_OF_SCOPE`（范围外建议）。前两类必须指出对应需求/AC或它直接蕴含的不变量；疑点标待验证。
- 阻塞项必须给预期/实际行为、触发、证据、错误后果、最小修复边界和解除条件；不能靠泛化风险或严重度标签增加任务。
- 只补保证原功能正确所需的修复与验证。新功能、未来规模、偏好式重构和额外质量标准不成为本轮要求；范围外建议单列且默认不派单、不阻塞，不因它们降级PASS。
- 必要上下游可以查，但须说明与当前错误的因果关系。模块不承担后续真实样本/生产阶段的验收；原有阶段门禁继续保留。
- 已有问题关闭且原AC满足就结束，不持续寻找无关改进。

## 审查流程

1. 读取审查包的 review_id、冻结需求/AC基线、已交付行为、具体待裁决问题、非范围、作用门禁、实际 base/target、契约版本及证据 commit。材料不足或快照不一致先明确与原AC相关的缺口，不只根据协调者摘要下结论。
2. 核对完整变更文件清单与可定位 diff，阅读关键实际代码、必要上下游和测试/成功条件修改；大材料按调用链取用，不机械截断文件或重读全部历史。
3. 核实成功前提、异常分类、状态/事务/释放顺序、并发唯一身份与当前版本、重试、文件与数据库一致性、时间精度/边界和 mock 掩盖的问题。疑点与确认缺陷分开；未执行测试如实写未执行。
4. 按 [结果模板](assets/result.md) 输出可执行问题：问题 ID/分类/严重度、对应需求/AC、预期与实际行为、代码位置及证据、触发、后果、最小修复边界、必要验证、阻塞与解除条件。避免风格清单、泛化架构扩张和整段重写。
5. 结论使用 PASS / PASS_WITH_FOLLOWUPS / REWORK_REQUIRED / INSUFFICIENT_EVIDENCE。声明通过的是契约、模块合入、集成、工程闭环或生产门禁；不能用模块通过替代缺真实时间映射/样本/故障证据的闭环。
6. 默认把结果写到约定路径；没有文件访问能力输出完整结果供保存并说明未写文件。不能编辑业务代码、合并或部署。

## 增量与费用

- 返修审查只看前轮问题 ID、修复 diff、对应测试及受影响上下文，复用有效的已接受材料。新发现只有证明破坏本批既定行为时才成为纠错项；无关建议不扩入复审范围。
- 结果绑定实际 commit 与契约版本；新逻辑不继承旧 PASS。非阻塞跟进要有 owner/阶段/解除条件。
- token/费用不可获取写未知，不猜测准确率或费用；记录确认缺陷、核实误报、遗漏、返修轮数及重复阅读情况。
- 审查由用户手动触发，或由协调者在用户明确授权的自定义时段/当前任务范围内通过限额脚本触发。自动起跑绑定grant_id/call_id，每次复审占额度；本审查者不续授权、不调用其他模型、不调起下一轮。
- Codex只读入口不能写约定文件时，返回完整最终结果，由调用脚本保存；不得声称自己已落盘。调用成功不代替协调者核验问题或批准。

## 协作流程文档维护（按需）

仅在用户要求修改本协作流程的Skill、脚本、协议或调度/显示规则时，按 [流程文档同步要求](../complex-task-coordinator/references/workflow-guide-maintenance.md) 更新 [统一开发流程指南](/home/wang/work/doc/SKILL-DEVELOPMENT-WORKFLOW.md) 的相关段落、图示和变更记录。普通开发/测试/审查/巡检不加载全文或更新它，发现差异按角色权限提交证据，不新增任务或授权。


You are a read-only reviewer authorized by the user. No code edits, model delegation, merges, deployments or extra review calls.

{"review_id": "SR-16B-R2-20261013", "grant_id": "6b2d83fb978644b7938424e4652024ce", "call_id": "005277e6e60a43308431b5505f0bf6dc", "base": "40ab8182c177b53fc2ff60ac6bd511b14ab4f1d9", "target": "e1524657bda1f66f03034cb72ef05cd65e0c1dfc", "task": "TASK-16B", "gate": "TASK-16B合入，独立TESTER及后续12S-D生产门禁仍保留", "risk": "R1-01至05为原强审阻塞，当前已冻结最小返修，需核问题关闭", "question": "只核R1-01至05是否关闭，不扩审全量历史；新增阻塞须给原不变量反例", "AC": "TASK-16B原H1 H2 H4 H6重复请求/终态/恢复/耐久契约"}

Return the complete independent result as your final message; the wrapper writes it. Do not try to write a result file in the read-only sandbox. Freeze existing requirements; OUT_OF_SCOPE suggestions do not block.

The following is the frozen review package. Read actual code in this detached snapshot and the cited verification evidence; do not merely trust the summary.

# SR-16B-R2-20261013：只复核原R1五项关闭

review_id=SR-16B-R2-20261013；task=TASK-16B；decision=REVIEW_NOW。
repo=/home/wang/work/rosbag-catalog（原有效授权绑定主仓库，脚本创建固定detached快照）；base=40ab8182c177b53fc2ff60ac6bd511b14ab4f1d9；target=e1524657bda1f66f03034cb72ef05cd65e0c1dfc。
作用门禁：仅16B合入。保持原v0.4 REQ/AC/H1/H2/H4/H6，不追加UI、真模型/生产、通用文件系统兼容等需求。12S-C/12S-D和生产门禁独立保留。

重点：R1-01迟到重复run不得再执行模型；R1-02 DONE/FAILED已提交响应丢失与未提交必须对账收敛；R1-03失败状态不确定时保留恢复依据；R1-04 unlink异常不能留下ACTIVE；R1-05文件fsync→replace→父目录fsync，保证限支持FS。只看这五项修复与必要上下文，已接受历史不逐行重审。若需新增阻塞，必须证明本次变更损坏原不变量、给可达触发和反例；偏好/泛化不阻塞。

开发自测固定target证据：代理26 passed、代理+编排39 passed、ruff通过；全仓889 passed/3既有devflow失败同base复现。协调者此前独立复跑39 passed和ruff通过（sessions/COORDINATOR r167）。TESTER独立r2已派、可并行，尚未返回，本包不伪造独立PASS。弱OCR17:42:30完成、3findings已裁，完整裁决见下；未确认阻塞项，不自动返修日志或不支持FS。

结果请PASS/PASS_WITH_FOLLOWUPS/REWORK_REQUIRED/INSUFFICIENT_EVIDENCE，逐R1-01～05说明关闭/未关及必要证据；其他问题严格CORRECTION/VERIFICATION_GAP/OUT_OF_SCOPE分类。勿改代码、合入或部署。

## 原五项原文（唯一原审查基线）

# 独立审查结果

- **结论：REWORK_REQUIRED。** `TASK-16B` 在本次合入门禁仍有 5 项阻塞；此结论仅针对 `0208a737` → `40ab8182`、v0.4 冻结契约及 TASK-16B 的重复请求、步骤终态和崩溃恢复要求，不代表集成或生产验收。
- `review_id`：`SR-16B-R1-20261013`；触发：`AUTHORIZED_CODEX`；`grant_id`：`6b2d83fb978644b7938424e4652024ce`；`call_id`：`e7d6b92127804c6cac00dfa4230af7a4`。
- 已核对实际 HEAD、两文件完整 diff、代理调用链、Backend 状态机与接口，以及回执和 OCR 记录。`git diff --check` 通过，工作区干净。协调者记录定向测试 **20 passed**、Ruff 和编译通过；**本审查未重跑测试**，真实栈验证仍属后续门禁。

## 阻塞问题

**R1-01｜CORRECTION｜高｜H1、重复 `/run` 与单写者契约。** 预期同 run、同 attempt 的重复请求只复用既有执行；实际首个 worker 结束并移除 `ACTIVE` 后，迟到请求可再次 `try_reserve`、获得 202 并启动线程。[代理入口](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/e7d6b92127804c6cac00dfa4230af7a4/snapshot/scripts/scene_host_proxy.py:918) 只查进程内 `ACTIVE`，[`resolve_spec`](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/e7d6b92127804c6cac00dfa4230af7a4/snapshot/scripts/scene_host_proxy.py:352) 只核 attempt，未拒绝已终态 run。触发为首请求较快完成、第二个并发请求迟至释放后进入保留段；后果是同 attempt 重跑模型。最小修复边界是将保留后的执行资格与 Backend 当前 run/attempt 及已接受身份对账，终态不得重执行；用快速完成后重发及释放边界交错测试证明只执行一次。**阻塞 16B 合入，验证上述两种重发均不产生第二次模型执行后解除。** Q1 所问“`try_reserve` 已失败后重读 `ACTIVE` 返回错误的 200”未找到独立反例：旧写者释放后读到空值会返回 409。

**R1-02｜CORRECTION｜高｜H2，步骤终态必达。** 预期 `RUNNING` 已落库后，checkpoint 的 `DONE/FAILED` 最终落库；实际终态 `post()` 失败只打印日志，[`_report_steps`](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/e7d6b92127804c6cac00dfa4230af7a4/snapshot/scripts/scene_host_proxy.py:483) 不重试或对账，成功路径随后清除恢复文件。触发为 `RUNNING` 成功而 `DONE/FAILED` 请求超时或失败；后果是步骤永久停在 `RUNNING`。新增测试只覆盖全程 HTTP 200。最小修复是在清理可恢复状态前对失败的终态写入按本 attempt 对账并补报，覆盖“已提交但响应丢失”和“未提交”两种注入。**阻塞合入，故障注入后 Backend 步骤收敛到正确终态才解除。** `RUNNING → DONE/FAILED` 本身是合法转移；当前详情 API 也确实提供 `attempt`，L1 缺键担忧不成立。

**R1-03｜CORRECTION｜高｜H4，失败终态与恢复。** 预期 `resolve_spec` 异常后失败状态得到确认，或保留可对账恢复依据；实际 [`_finish_failure`](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/e7d6b92127804c6cac00dfa4230af7a4/snapshot/scripts/scene_host_proxy.py:767) 吞掉 `SCENE_FAILED` 上报异常，仍删除 recovery 并移除 `ACTIVE`。Backend 短时不可用或响应丢失时，run 可继续停在 `SCENE_RUNNING`，重启也失去本地恢复入口。最小修复是区分已确认终态与状态不确定，先对账，再决定是否清除恢复台账；注入上报未提交、已提交但响应丢失两种情况。**阻塞合入，两个分支均可收敛且不重复执行后解除。**

**R1-04｜CORRECTION｜中｜H4，失败收尾恒执行。** 预期清理 recovery 失败也不使进程内活动位永久残留；实际 [`clear_recovery_state` 后才 `ACTIVE.remove`](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/e7d6b92127804c6cac00dfa4230af7a4/snapshot/scripts/scene_host_proxy.py:777)，`unlink` 的非 `FileNotFoundError` 异常会中断收尾。触发为状态目录 I/O 或权限错误；后果是后续 `/run` 被幽灵活动项挡住。最小修复是保证活动位释放在清理异常下仍执行，同时保留清理失败的明确恢复依据；注入 `unlink` 抛错验证。**阻塞合入，该注入下线程退出且 `ACTIVE` 不残留后解除。** `except Exception` 的捕获范围本身适合此次 `CapabilityError/ValueError` 修复；不要求捕获 `KeyboardInterrupt/SystemExit`。

**R1-05｜CORRECTION｜中｜H6，接受台账掉电耐久。** 预期返回接受后，重启仍能找到完整旧或新 recovery 台账；实际 [`_write_json_atomic`](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/e7d6b92127804c6cac00dfa4230af7a4/snapshot/scripts/scene_host_proxy.py:181) 同步了 tmp 文件，却未在 `os.replace` 后同步父目录。首次创建台账时掉电可能丢失目录项，导致已返回 202 的运行无法恢复。最小修复是同步 rename 所在目录，并以调用顺序测试覆盖文件及目录 fsync；掉电语义须明确限于受支持文件系统。**阻塞合入，接受台账的持久化顺序得到验证后解除。** 同 PID tmp 名冲突依赖同一路径并发写；当前单活动位设计下未证明它是独立可达缺陷，不另立阻塞项。

## 快照与后续

H2 的局部 `cur` 刷新、H5 默认参数哈希比较及 L1 attempt 过滤均与当前代码契约相符；Backend 写入端和 registry 使用同一字符串哈希口径，缺失冻结哈希时维持旧分支。现有 6 个回归未覆盖以上失败交错。请由 16B owner 在原范围内修复并补对应验证，再由协调者与 TESTER 收口；12S-C 仍应等待 16B 接受。

本结果因只读沙箱**未写入**约定结果文件，由调用包装器保存。token、费用未知；本轮确认 5 项范围内缺陷，未调用其他模型、未修改代码或部署。

## 本轮开发交付与证据索引

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

## 本轮OCR裁决

# 16B-r2 增量OCR裁决（Codex用户纠正轮）

固定40ab818..e152465；run4492b7f6，session d56113ca-0ca7-4042-829e-f5fc15154f65。17:42:30独立服务收口rc=0，manifest完整selected1/completed1/failed0、指纹一致；已核完整base/head及provider/model。3条findings逐项裁决，不能报告零发现。

1. M1 目录fsync应吞EINVAL/ENOTSUP：OUT_OF_SCOPE（支持范围扩展）。原R1-05明确掉电保证限于受支持文件系统，本次实现docstring同样限制ext4/xfs等POSIX；没有要求不支持持久化的文件系统也接受任务。吞掉错误会在未证明耐久时接受运行，不能为统一另一个辅助函数而弱化此契约。正式部署须验证私有state/work实际文件系统支持fsync；这个部署证明留在G4，不将新兼容需求派返修。一般I/O故障的恢复仍按原H4审查，若强审证明既定可达缺陷则另行裁决，不把本项解释为所有I/O故障均已验证。
2. L1 建议新增errno import：关联M1假设补丁的依赖，现有实现不引用errno，无实际NameError；NOT_A_DEFECT，不派单。
3. L2 日志cur未赋DONE：当前输出是原状态->目标状态，打印RUNNING->DONE并不自相矛盾。FAILED分支的日志准确性可作非阻塞维护，未证明状态转移受损；NON_BLOCKING，不因日志格式重烧整文件OCR。

结论：本轮OCR无已确认阻塞CORRECTION，OCR门禁解除；强审R1-01～05复核和独立测试仍待完成，未批准合入、更未放行生产。目录FS支持在部署核验，不增加通用兼容开发。


## 本轮完整diff（两文件，含全部新增断言和测试成功标准变化）

```diff
diff --git a/scripts/scene_host_proxy.py b/scripts/scene_host_proxy.py
index 367c539..825592b 100644
--- a/scripts/scene_host_proxy.py
+++ b/scripts/scene_host_proxy.py
@@ -179,15 +179,23 @@ def state_path(cfg: ProxyConfig, run_id: str) -> Path:
 
 
 def _write_json_atomic(path: Path, payload: dict) -> None:
+    """原子写（R1-05 掉电耐久口径）：tmp 写入 → flush → fsync 文件 →
+    os.replace → fsync 父目录。文件 fsync 保证 rename 前内容完整；
+    目录 fsync 保证首次创建台账时 rename 产生的目录项落盘——否则掉电可丢
+    目录项，已返回 202 的 run 重启后找不到恢复台账。掉电语义限于受支持
+    文件系统（ext4/xfs 等 POSIX 持久化语义）。同 app/services/remote_bag_lock.py 约定。"""
     path.parent.mkdir(parents=True, exist_ok=True)
     tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
-    # H6：recovery 是崩溃恢复真相源——tmp 写入后先 flush+fsync 再 rename，
-    # 掉电/panic 下 rename 未落盘会丢/回滚文件（同 app/services/remote_bag_lock.py 约定）
     with open(tmp, "w", encoding="utf-8") as f:
         f.write(json.dumps(payload, ensure_ascii=False, indent=2))
         f.flush()
         os.fsync(f.fileno())
     os.replace(tmp, path)
+    dfd = os.open(str(path.parent), os.O_RDONLY)
+    try:
+        os.fsync(dfd)
+    finally:
+        os.close(dfd)
 
 
 def _read_json(path: Path) -> dict | None:
@@ -225,10 +233,19 @@ def save_recovery_state(
 
 
 def clear_recovery_state(cfg: ProxyConfig, run_id: str) -> None:
+    """清恢复台账（R1-04：unlink 非 FileNotFoundError 异常不得中断收尾）。
+
+    清理失败时保留恢复依据：recovery 文件原位保留（含进程身份+stage+
+    检查点），重启 recover_pending_runs 会重新对账；只留痕不吞——
+    若此处异常上抛，_finish_* 的 ACTIVE.remove 被跳过，进程内活动位
+    幽灵残留会挡住该 run 后续所有 /run（恒 409）。"""
     try:
         state_path(cfg, run_id).unlink()
     except FileNotFoundError:
         pass
+    except OSError as exc:
+        print(f"scene recovery state clear failed (ledger kept as restore evidence) "
+              f"{run_id}: {exc}", flush=True)
 
 
 # ---------------------------------------------------------------------------
@@ -358,6 +375,12 @@ def resolve_spec(
         raise SpecError(
             f"attempt 不一致（payload={attempt} backend={run.get('attempt')}），按原身份对账拒绝"
         )
+    # R1-01：保留后执行资格与 Backend 当前 run 状态对账——已终态 run 不得
+    # 重执行（首个 worker 结束释放 ACTIVE 后，迟到重复 /run 可再 try_reserve
+    # 拿到 202；此处按 Backend 终态拒绝，同 attempt 不重烧模型）
+    run_status0 = str(run.get("status") or "")
+    if run_status0 in _TERMINAL_RUN_STATUSES:
+        raise SpecError(f"run 已终态（{run_status0}），重复 /run 不重执行")
     source_id = str(run.get("source_id") or payload.get("source_id") or "")
     if not source_id:
         raise SpecError("run 无 source_id")
@@ -489,34 +512,86 @@ def _report_steps(
             print(f"16B step report failed {run_id}/{name}/{target}: {exc}", flush=True)
             return None
 
+    def reconcile_terminal(name: str, target: str, error: str = "") -> None:
+        """R1-02：终态写入失败后按本 attempt 对账补报（清理恢复状态前调用，
+        终态必达）——覆盖两种注入：
+        - 已提交但响应丢失：对账读 DB 已是 target → 不重复 post，本地 cur 对齐；
+        - 未提交：DB 非 target 且状态机允许 → 重试 post 一次（仍失败留痕，
+          run 详情可对账，不无限重试）。"""
+        try:
+            cur = {s["step_name"]: s["status"]
+                   for s in backend.run_detail(run_id).get("steps") or []
+                   if s.get("attempt") == attempt}.get(name)
+        except Exception as exc:
+            print(f"16B step terminal reconcile read failed {run_id}/{name}: {exc}", flush=True)
+            return
+        if cur == target:
+            current[name] = cur
+            print(f"16B step terminal confirmed via reconcile {run_id}/{name}={target}", flush=True)
+            return
+        if not allowed(cur, target):
+            print(f"16B step terminal reconcile blocked {run_id}/{name}: "
+                  f"cur={cur!r} target={target!r}", flush=True)
+            return
+        if post(name, target, error) is not None:
+            print(f"16B step terminal re-reported {run_id}/{name}={target}", flush=True)
+
+    def ensure_running(name: str) -> str | None:
+        """台账 DONE/FAILED 步的 RUNNING 前置：post 失败/丢响应时按本 attempt
+        对账确认（R1-02 同口径），状态不确定返回 None（不冒进，run 详情可对账）。"""
+        cur = current.get(name)
+        if cur in (None, "QUEUED"):
+            if post(name, "RUNNING") is None:
+                try:
+                    cur = {s["step_name"]: s["status"]
+                           for s in backend.run_detail(run_id).get("steps") or []
+                           if s.get("attempt") == attempt}.get(name)
+                except Exception as exc:
+                    print(f"16B running reconcile read failed {run_id}/{name}: {exc}",
+                          flush=True)
+                    return None
+                if cur == "RUNNING":
+                    current[name] = cur
+                elif cur in (None, "QUEUED"):
+                    if post(name, "RUNNING") is None:
+                        return None
+                    cur = "RUNNING"
+                    current[name] = cur
+                elif cur in ("DONE", "FAILED"):
+                    pass  # 已越级到终态：调用方按 cur 自行核对
+                else:
+                    return None
+            else:
+                cur = "RUNNING"
+        return cur
+
     for name in STEPS:
         if name == terminal_step:
             continue  # 终态切换步：由 _report_step_single 在终态后补报（容忍 409）
         rec = steps_map.get(name) or {}
         status = str(rec.get("status") or "PENDING")
-        cur = current.get(name)
         if status == "DONE":
-            if cur in (None, "QUEUED"):
-                # H2：post 成功后局部 cur 必须刷新为 RUNNING，否则 allowed(cur,"DONE")
-                # 按 QUEUED 判定恒 False，终态 post 被静默跳过（步骤卡 RUNNING）
-                if post(name, "RUNNING") is None:
-                    continue
-                cur = "RUNNING"
+            # H2：DB 侧 QUEUED/None 必须先 RUNNING；R1-02：post 失败/丢响应
+            # 按本 attempt 对账确认，未确认不冒进终态（步骤不再静默卡 RUNNING）
+            cur = ensure_running(name)
+            if cur is None or cur == "DONE":
+                continue
             if allowed(cur, "DONE"):
-                post(name, "DONE", str(rec.get("detail") or ""))
+                if post(name, "DONE", str(rec.get("detail") or "")) is None:
+                    reconcile_terminal(name, "DONE", str(rec.get("detail") or ""))
         elif status == "FAILED":
-            if cur in (None, "QUEUED"):
-                if post(name, "RUNNING") is None:
-                    continue
-                cur = "RUNNING"
+            cur = ensure_running(name)
+            if cur is None or cur == "FAILED":
+                continue
             err = str(rec.get("detail") or "") or (
                 f"{error_step}: {error_detail}" if error_step == name else ""
             )
             if allowed(cur, "FAILED"):
-                post(name, "FAILED", err)
+                if post(name, "FAILED", err) is None:
+                    reconcile_terminal(name, "FAILED", err)
         elif status == "PENDING" and error_step is not None and STEPS.index(name) > STEPS.index(error_step):
             # 失败后的后续步：编排台账保持 PENDING（未执行）→ Backend 落 SKIPPED
-            if allowed(cur, "SKIPPED"):
+            if allowed(current.get(name), "SKIPPED"):
                 post(name, "SKIPPED", f"SKIPPED after {error_step} failure")
 
 
@@ -547,8 +622,26 @@ def _report_step_single(
             cur = "RUNNING"
         if cur != "DONE":
             backend.step(run_id, name, "DONE", attempt, lease_token, error=str(rec.get("detail") or ""))
+        # R1-02 同口径：终态写入可能失败（异常已容忍）→ 对账补报，终态必达
     except Exception as exc:
         print(f"16B terminal step report tolerated {run_id}/{name}: {exc}", flush=True)
+    try:
+        cur = {s["step_name"]: s["status"] for s in backend.run_detail(run_id).get("steps") or []
+               if s.get("attempt") == attempt}.get(name)
+    except Exception as exc:
+        print(f"16B terminal step reconcile read failed {run_id}/{name}: {exc}", flush=True)
+        return
+    if cur == "DONE":
+        return
+    try:
+        if cur in (None, "QUEUED"):
+            backend.step(run_id, name, "RUNNING", attempt, lease_token)
+            cur = "RUNNING"
+        if cur not in ("DONE", "FAILED"):
+            backend.step(run_id, name, "DONE", attempt, lease_token, error=str(rec.get("detail") or ""))
+        print(f"16B terminal step re-reported {run_id}/{name}={cur!r}->DONE", flush=True)
+    except Exception as exc:
+        print(f"16B terminal step reconcile post tolerated {run_id}/{name}: {exc}", flush=True)
 
 
 # ---------------------------------------------------------------------------
@@ -764,18 +857,52 @@ def _finish_success(cfg: ProxyConfig, backend: Backend, run_id: str, attempt: in
     ACTIVE.remove(run_id)
 
 
+def _confirm_terminal(backend: Backend, run_id: str, lease_token: str,
+                      target: str, error: str) -> bool:
+    """R1-03：终态写入确认（先对账再清恢复台账）。返回 True=已确认终态。
+
+    覆盖两种注入：
+    - 上报已提交但响应丢失：对账读 DB 已是 target（或已达其他终态）→ 确认，
+      不重复 post；
+    - 上报未提交（Backend 短时不可用/超时）：对账读非终态 → 按原身份重试
+      post 一次（幂等键保证不重复写）；再对账读确认。
+    对账读失败=状态不确定 → False（保留恢复依据，重启 recover 重新对账）。"""
+    def _read_status() -> str | None:
+        try:
+            return backend.run_detail(run_id).get("status")
+        except Exception as exc:
+            print(f"scene terminal reconcile read failed {run_id}: {exc}", flush=True)
+            return None
+
+    st = _read_status()
+    if st == target:
+        return True
+    if st in _TERMINAL_RUN_STATUSES:
+        print(f"scene run {run_id} already terminal ({st}); {target} post skipped", flush=True)
+        return True
+    if st is not None:
+        try:
+            backend.status(run_id, target, lease_token, error=error)
+        except Exception as exc:
+            print(f"scene terminal retry failed {run_id}: {exc}", flush=True)
+    return _read_status() == target
+
+
 def _finish_failure(cfg: ProxyConfig, backend: Backend, run_id: str, attempt: int,
                     lease_token: str, resource_token: str | None, spec: SceneExecSpec | None,
                     error: str, stop_cancel: threading.Event, reason: str, stage: str) -> None:
     print(f"scene run {run_id} attempt {attempt} FAILED at {stage}: {error}", flush=True)
     _stop_threads(stop_cancel)
-    try:
-        # 派发补偿同口径：SCENE_RUNNING → SCENE_FAILED（状态机允许），携带原租约
-        backend.status(run_id, "SCENE_FAILED", lease_token, error=error)
-    except Exception as exc:
-        print(f"scene failure report failed {run_id}: {exc}", flush=True)
+    # R1-03：先对账确认终态再决定清不清恢复台账——上报未提交/响应丢失时
+    # run 停 SCENE_RUNNING 且台账被删 = 重启失恢复入口（phantom run）；
+    # 未确认则保留台账留痕，recover_pending_runs 重启后按原身份重新对账续收尾
+    confirmed = _confirm_terminal(backend, run_id, lease_token, "SCENE_FAILED", error)
     _release_resource(cfg, resource_token)
-    clear_recovery_state(cfg, run_id)
+    if confirmed:
+        clear_recovery_state(cfg, run_id)
+    else:
+        print(f"scene run {run_id} SCENE_FAILED unconfirmed (Backend 不可用/未提交)：保留 recovery 台账作恢复依据",
+              flush=True)
     ACTIVE.remove(run_id)
 
 
diff --git a/tests/test_scene_host_proxy.py b/tests/test_scene_host_proxy.py
index 231c1a9..e793bcb 100644
--- a/tests/test_scene_host_proxy.py
+++ b/tests/test_scene_host_proxy.py
@@ -38,6 +38,7 @@ from scene_host_proxy import (  # noqa: E402
     ACTIVE,
     Backend,
     ProxyConfig,
+    _finish_failure,
     _process_identity,
     _report_step_single,
     _report_steps,
@@ -61,14 +62,42 @@ EFF = reg.effective_params("slope", None)
 
 
 # ---------------------------------------------------------------------------
-# 假 Backend（真实 HTTP，记录所有写调用）
+# 假 Backend（真实 HTTP，有状态：step 迁移跟踪 + run status 终态写 + 故障注入）
+# R1-01 迟到重复 /run（终态对账）、R1-02 响应丢失/未提交、R1-03 失败恢复分支
+# 需要 Backend 侧状态真实推进，静态假后端无法表达。
 # ---------------------------------------------------------------------------
+_FAKE_STEP_TRANS = {
+    # 与 app/domain/transitions.py STEP_TRANSITIONS 同口径（假后端只实现测试用到的面）
+    "QUEUED": {"RUNNING", "SKIPPED", "CANCELLED"},
+    "RUNNING": {"DONE", "FAILED", "CANCELLED"},
+    "DONE": set(), "FAILED": set(), "CANCELLED": set(), "SKIPPED": set(),
+}
+
+
 class FakeBackend:
-    def __init__(self, run_detail: dict, source_detail: dict):
-        self.run_detail = run_detail
+    def __init__(self, run_detail: dict, source_detail: dict, *, step_mode: bool = True):
         self.source_detail = source_detail
+        # step 状态：{step_name: [attempt, status]}（run_detail["steps"] 提供初始行）
+        self.steps: dict[str, list] = {}
+        for s in run_detail.get("steps") or []:
+            self.steps[str(s["step_name"])] = [int(s["attempt"]), str(s["status"])]
+        self.status = str(run_detail.get("status") or "SCENE_RUNNING")
+        self._base_detail = run_detail
         self.calls: list[tuple[str, str, dict | None]] = []
         self._lock = threading.Lock()
+        # 注入面：fail_once 一次性故障 {path_suffix: {code, body, lost, status, consumed}}
+        # status=None 匹配任意；lost=True 模拟「已提交但响应丢失」（状态已落、响应故障）
+        self.fail_once: dict[str, dict] = {}
+        # fail_status=True → 所有 /status POST 永久故障（Backend 不可用分支）
+        self.fail_status = False
+        self.fail_status_code = 500
+        self.fail_status_body = {"error": "backend unavailable"}
+        # status_fail：一次性状态定向故障 {status_or_None: {code, body, committed, consumed}}
+        # committed=True=已提交但响应丢失（DB 状态已落、HTTP 按注入故障）；False=未提交
+        self.status_fail: dict[str | None, dict] = {}
+        # step_fail：步骤级一次性故障（同 status_fail 语义，key=step payload 状态）
+        self.step_fail: dict[str | None, dict] = {}
+        self.step_mode = step_mode
         handler = self._make_handler()
         self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
         self.port = self.server.server_address[1]
@@ -83,6 +112,32 @@ class FakeBackend:
         with self._lock:
             self.calls.append((method, path, payload))
 
+    def _apply_step(self, payload: dict) -> bool:
+        """迁移合法则落状态，返回是否变更（409 拒绝时 False）。"""
+        name = str(payload.get("step_name") or "")
+        target = str(payload.get("status") or "")
+        attempt = int(payload.get("attempt") or 0)
+        row = self.steps.get(name)
+        if row is None:
+            return False
+        if not self.step_mode:
+            row[0], row[1] = attempt, target
+            return True
+        if row[1] != target and target not in _FAKE_STEP_TRANS.get(row[1], set()):
+            return False
+        row[0], row[1] = attempt, target
+        return True
+
+    def _run_detail_view(self) -> dict:
+        with self._lock:
+            d = {k: v for k, v in self._base_detail.items() if k != "steps"}
+            d["status"] = self.status
+            d["steps"] = [
+                {"step_name": name, "attempt": row[0], "status": row[1]}
+                for name, row in self.steps.items()
+            ]
+            return d
+
     def _make_handler(self):
         outer = self
 
@@ -106,28 +161,91 @@ class FakeBackend:
                 path = self.path
                 outer._record("GET", path, None)
                 if path.startswith("/api/v1/pipeline-runs/"):
-                    self._send(200, outer.run_detail)
+                    self._send(200, outer._run_detail_view())
                 elif path.startswith("/api/v1/sources/"):
                     self._send(200, outer.source_detail)
                 else:
                     self._send(404, {"error": "nf"})
 
+            def _post_once(self, path: str, payload: dict | None) -> tuple[int, dict]:
+                """处理 POST；一次性注入触发时返回故障响应。
+                inj 匹配：path 以 key 结尾，且 payload 状态等于 inj["status"]
+                （None=任意）；lost=True 模拟「已提交但响应丢失」（状态已落、响应故障）。"""
+                def _normal() -> tuple[int, dict]:
+                    if "/task-leases/" in path and path.endswith("/heartbeat"):
+                        return 200, {"ok": True}
+                    if "/api/v1/orchestrator/leases/" in path and path.endswith("/heartbeat"):
+                        return 200, {"ok": True}
+                    if "/steps/" in path:
+                        # Backend.step 把 step_name 放 URL 路径（payload 无 step_name 键）
+                        step_name = path.rsplit("/steps/", 1)[-1]
+                        step_status = str((payload or {}).get("status") or "")
+                        # 一次性步骤定向故障（R1-02 注入）：committed=True=已提交
+                        # 但响应丢失（DB 已落、HTTP 故障）；False=未提交
+                        for st, inj in outer.step_fail.items():
+                            if inj["consumed"]:
+                                continue
+                            if st is None or step_status == st:
+                                inj["consumed"] = True
+                                p2 = dict(payload or {})
+                                p2["step_name"] = step_name
+                                if inj["committed"]:
+                                    outer._apply_step(p2)
+                                return int(inj["code"]), dict(inj["body"])
+                        applied = True
+                        if payload is not None and outer.step_mode:
+                            p2 = dict(payload)
+                            p2["step_name"] = step_name
+                            applied = outer._apply_step(p2)
+                        if not applied:
+                            return 409, {"error": "step transition rejected"}
+                        return 200, {"ok": True}
+                    if path.endswith("/status"):
+                        target = str(payload.get("status") or outer.status) if payload else outer.status
+                        # 一次性状态定向故障（R1-02/R1-03 注入）：
+                        # committed=True=已提交但响应丢失（DB 状态已落、HTTP 故障）
+                        # committed=False=未提交（HTTP 故障、DB 状态不落）
+                        inj_hit = None
+                        for st, inj in outer.status_fail.items():
+                            if inj["consumed"]:
+                                continue
+                            if st is None or target == st:
+                                inj["consumed"] = True
+                                inj_hit = inj
+                                break
+                        if inj_hit is not None and inj_hit["committed"]:
+                            outer.status = target
+                        if inj_hit is not None:
+                            return int(inj_hit["code"]), dict(inj_hit["body"])
+                        outer.status = target
+                        if outer.fail_status:
+                            return int(outer.fail_status_code), dict(outer.fail_status_body)
+                        return 200, {"status": target, "ok": True}
+                    if path.endswith("/results"):
+                        return 200, {"ok": True, "run_status": "SCENE_DONE"}
+                    if path.endswith("/complete-scene"):
+                        outer.status = "SCENE_DONE"
+                        return 200, {"ok": True, "run_status": "SCENE_DONE"}
+                    return 200, {"ok": True}
+
+                with outer._lock:
+                    for key, inj in outer.fail_once.items():
+                        if not inj["consumed"] and path.endswith(key) \
+                                and (inj["status"] is None
+                                     or (payload or {}).get("status") == inj["status"]):
+                            code, resp = int(inj["code"]), dict(inj["body"])
+                            if inj["lost"]:
+                                code, resp = _normal()  # 状态已落，但响应按注入故障
+                            inj["consumed"] = True
+                            return code, resp
+                return _normal()
+
             def do_POST(self):
                 path = self.path
                 payload = self._body()
                 outer._record("POST", path, payload)
-                if "/task-leases/" in path and path.endswith("/heartbeat"):
-                    self._send(200, {"ok": True})
-                elif "/api/v1/orchestrator/leases/" in path and path.endswith("/heartbeat"):
-                    self._send(200, {"ok": True})
-                elif "/steps/" in path:
-                    self._send(200, {"ok": True})
-                elif path.endswith("/status"):
-                    self._send(200, {"status": "SCENE_DONE", "ok": True})
-                elif path.endswith("/results") or path.endswith("/complete-scene"):
-                    self._send(200, {"ok": True, "run_status": "SCENE_DONE"})
-                else:
-                    self._send(200, {"ok": True})
+                code, resp = self._post_once(path, payload)
+                self._send(code, resp)
 
             def do_DELETE(self):
                 path = self.path
@@ -498,7 +616,7 @@ def test_recovery_drops_non_running(tmp_path, vlm):
     dead = {"pid": 2**22, "process_start": "999"}
     # run 已终态（SCENE_DONE）→ recover 丢弃并清状态文件
     fb = FakeBackend(_run_detail("scene-rec-2"), _source_detail())
-    fb.run_detail["status"] = "SCENE_DONE"
+    fb.status = "SCENE_DONE"
     cfg = ProxyConfig(**{**cfg.__dict__, "backend_url": fb.base})
     backend = Backend(cfg)
     save_recovery_state(cfg, run_id="scene-rec-2", attempt=1, lease_token="tok",
@@ -660,23 +778,241 @@ def test_resolve_spec_frozen_config_hash_mismatch_fail_fast(tmp_path, monkeypatc
 
 
 def test_write_json_atomic_fsyncs_before_replace(tmp_path, monkeypatch):
-    """H6：原子写 recovery 真相源——先 flush+fsync 再 os.replace，tmp 不留残件。"""
+    """H6（R1-05 增强）：原子写 recovery 真相源——先 flush+fsync 文件，再
+    os.replace，replace 后 fsync 父目录（掉电目录项耐久）；tmp 不留残件。"""
     events: list[str] = []
     real_fsync = os.fsync
     real_replace = os.replace
+    real_open = os.open
+    dir_fds: set[int] = set()
+
+    def _recording_open(path, flags, *args, **kwargs):
+        fd = real_open(path, flags, *args, **kwargs)
+        if os.path.isdir(str(path)):
+            dir_fds.add(fd)
+        return fd
 
     def _recording_fsync(fd):
-        events.append("fsync")
+        events.append("dir_fsync" if fd in dir_fds else "file_fsync")
         return real_fsync(fd)
 
     def _recording_replace(a, b):
         events.append("replace")
         return real_replace(a, b)
 
+    monkeypatch.setattr(os, "open", _recording_open)
     monkeypatch.setattr(os, "fsync", _recording_fsync)
     monkeypatch.setattr(os, "replace", _recording_replace)
     p = tmp_path / "sub" / "x.json"
     _write_json_atomic(p, {"k": "v"})
-    assert events == ["fsync", "replace"], events
+    # 顺序：文件 fsync 先于 replace，replace 后父目录 fsync（掉电语义）
+    assert events == ["file_fsync", "replace", "dir_fsync"], events
     assert json.loads(p.read_text(encoding="utf-8")) == {"k": "v"}
-    assert not list(tmp_path.glob("sub/.*tmp"))
\ No newline at end of file
+    assert not list(tmp_path.glob("sub/.*tmp"))
+
+
+# ---------------------------------------------------------------------------
+# attempt-2-r2 回归（强审 SR-16B-R1 5 项阻塞最小返修，故障注入）
+# ---------------------------------------------------------------------------
+def _run_detail_steps(run_id: str, status: str = "SCENE_RUNNING") -> dict:
+    d = _run_detail(run_id)
+    d["status"] = status
+    return d
+
+
+def test_r1_01_late_duplicate_run_after_release_not_rerun(live_proxy):
+    """R1-01：首个 worker 结束移除 ACTIVE 后，迟到重复 /run 可再 try_reserve
+    拿到 202——保留后执行资格必须与 Backend 当前 run 状态对账，已终态 run
+    不得重执行（同 attempt 不重烧模型）。释放边界交错：in-flight 重复请求
+    命中 ACTIVE 分支（already_running，不触 Backend）。"""
+    client = live_proxy["client"]
+    fb = live_proxy["fb"]
+    cfg = live_proxy["cfg"]
+    run_id = live_proxy["run_id"]
+    payload = {"pipeline_run_id": run_id, "source_id": "SRC1", "attempt": 1,
+               "lease_token": "tok-r101", "resource_lease_token": None}
+
+    # 1) 正常 run 全链完成（模型真实调用一次）
+    code, _ = client.post("/run", payload)
+    assert code == 202, _
+    deadline = time.time() + 60
+    while time.time() < deadline and client.get("/health")[1]["active_runs"]:
+        time.sleep(0.5)
+    assert client.get("/health")[1]["active_runs"] == []
+    model_calls_1 = fb.wrote("/steps/INFER")
+
+    # 2) Backend run 已终态（SCENE_DONE）+ 释放边界交错后迟到重复 /run →
+    #    202 受理后 execute_run 在 resolve_spec 终态对账拒绝，不产生第二次
+    #    模型执行、不重复报 SCENE_FAILED
+    fb.status = "SCENE_DONE"
+    code, resp = client.post("/run", payload)
+    assert code == 202, resp  # 释放后 try_reserve 成功（=缺陷触发路径）
+    deadline = time.time() + 20
+    while time.time() < deadline and client.get("/health")[1]["active_runs"]:
+        time.sleep(0.5)
+    assert client.get("/health")[1]["active_runs"] == []
+    assert len(fb.wrote("/steps/INFER")) == len(model_calls_1), "重复 /run 不得重跑模型步"
+    # 终态 run 对账：SCENE_FAILED 上报被「已达 SCENE_DONE」分支跳过（不重复写终态），
+    # 台账清除、ACTIVE 释放、无第二次模型执行
+    failed_posts = [p for p in fb.wrote("/status") if p and p.get("status") == "SCENE_FAILED"]
+    assert len(failed_posts) == 0, (failed_posts, "终态 run 不得重报 SCENE_FAILED")
+    assert not state_path(cfg, run_id).exists()
+    assert run_id not in ACTIVE
+
+    # 3) 释放边界后再一次迟到重复 /run（同触发路径重放）：仍不得重执行
+    code3, resp3 = client.post("/run", payload)
+    assert code3 == 202, resp3
+    deadline = time.time() + 20
+    while time.time() < deadline and client.get("/health")[1]["active_runs"]:
+        time.sleep(0.5)
+    assert len(fb.wrote("/steps/INFER")) == len(model_calls_1)
+    assert len([p for p in fb.wrote("/status") if p and p.get("status") == "SCENE_FAILED"]) == 0
+
+
+def _active_or_post(cfg, run_id, attempt, lease_token) -> None:
+    with ACTIVE._lock:
+        ACTIVE._runs.clear()
+    ACTIVE.try_reserve(run_id, {"stage": "ACCEPTED", "attempt": attempt, "pid": os.getpid()})
+
+
+def test_r1_02_step_terminal_lost_response_converges(tmp_path):
+    """R1-02 分支一（已提交但响应丢失）：终态 DONE post 返回 500（DB 已落
+    DONE）→ 清理恢复状态前对账确认，不重复 post，步骤收敛到正确终态。"""
+    run_id = "scene-r102-lost"
+    fb = FakeBackend(_run_detail_steps(run_id), _source_detail())
+    fb.step_fail["DONE"] = {"code": 500, "body": {"error": "boom"},
+                            "committed": True, "consumed": False}
+    cfg = _cfg_with_backend(tmp_path, fb, run_id)
+    work_root = tmp_path / "work" / run_id / "attempt-1"
+    work_root.mkdir(parents=True)
+    (work_root / "checkpoint.json").write_text(
+        json.dumps({"steps": {"INFER": {"status": "DONE", "detail": "ok"}}}),
+        encoding="utf-8",
+    )
+    _report_steps(Backend(cfg), run_id=run_id, attempt=1, lease_token="tok",
+                  work_root=work_root)
+    # DB 收敛到 DONE；DONE 只 post 一次（500 注入），无重复写
+    assert fb.steps["INFER"][1] == "DONE", fb.steps
+    done_posts = [p for p in fb.wrote("/steps/INFER") if p and p.get("status") == "DONE"]
+    assert len(done_posts) == 1, done_posts
+    fb.stop()
+
+
+def test_r1_02_step_terminal_uncommitted_converges(tmp_path):
+    """R1-02 分支二（未提交）：RUNNING post 500（DB 仍 QUEUED）→ 对账未确认
+    → 重试一次落地；DONE post 500（未提交）→ 对账重试落地。终态必达。"""
+    run_id = "scene-r102-uncommit"
+    fb = FakeBackend(_run_detail_steps(run_id), _source_detail())
+    fb.step_fail["RUNNING"] = {"code": 500, "body": {"error": "boom"},
+                               "committed": False, "consumed": False}
+    fb.step_fail["DONE"] = {"code": 500, "body": {"error": "boom"},
+                            "committed": False, "consumed": False}
+    cfg = _cfg_with_backend(tmp_path, fb, run_id)
+    work_root = tmp_path / "work" / run_id / "attempt-1"
+    work_root.mkdir(parents=True)
+    (work_root / "checkpoint.json").write_text(
+        json.dumps({"steps": {"INFER": {"status": "DONE", "detail": "ok"}}}),
+        encoding="utf-8",
+    )
+    _report_steps(Backend(cfg), run_id=run_id, attempt=1, lease_token="tok",
+                  work_root=work_root)
+    assert fb.steps["INFER"][1] == "DONE", fb.steps  # 两分支注入后仍收敛
+    posted = [p["status"] for p in fb.wrote("/steps/INFER") if p]
+    # 未提交分支：RUNNING 失败→对账重试落地（1+1 次 post）；DONE 失败→对账补报
+    # （1+1 次 post）——重试均有界，不无限
+    assert posted.count("RUNNING") == 2, posted
+    assert posted.count("DONE") == 2, posted
+    fb.stop()
+
+
+def test_r1_03_confirm_terminal_other_terminal_no_dup_post(tmp_path):
+    """R1-03：对账读发现 run 已达其他终态（如 CANCELLED 抢先确认）→
+    不再重复 post SCENE_FAILED，按已确认处理（不覆盖终态）。"""
+    from scene_host_proxy import _confirm_terminal
+
+    run_id = "scene-r103-other"
+    fb = FakeBackend(_run_detail_steps(run_id, "CANCELLED"), _source_detail())
+    cfg = _cfg_with_backend(tmp_path, fb, run_id)
+    ok = _confirm_terminal(Backend(cfg), run_id, "tok", "SCENE_FAILED", "x")
+    assert ok is True
+    posts = [p for p in fb.wrote("/status") if p]
+    assert posts == [], posts  # 其他终态 → 零 post
+    fb.stop()
+
+
+def test_r1_03_finish_failure_uncommitted_keeps_recovery(tmp_path):
+    """R1-03 分支一（上报未提交）：SCENE_FAILED post 503 且 DB 未落地 →
+    终态未确认 → recovery 台账保留（重启失恢复入口 = phantom run 防线），
+    ACTIVE 恒清（不挡后续 /run）。"""
+    run_id = "scene-r103-uncommit"
+    fb = FakeBackend(_run_detail_steps(run_id), _source_detail())
+    fb.status_fail["SCENE_FAILED"] = {"code": 503, "body": {"error": "backend down"},
+                                      "committed": False, "consumed": False}
+    cfg = _cfg_with_backend(tmp_path, fb, run_id)
+    _active_or_post(cfg, run_id, 1, "tok-r103")
+    save_recovery_state(cfg, run_id=run_id, attempt=1, lease_token="tok-r103",
+                        resource_lease_token="res-r103", stage="EXECUTING",
+                        identity=_process_identity(), accepted_at=time.time())
+    assert state_path(cfg, run_id).exists()
+    _finish_failure(cfg, Backend(cfg), run_id, 1, "tok-r103", "res-r103", None,
+                    "INFER: MODEL_FAILED", threading.Event(), "none", stage="EXECUTING")
+    assert state_path(cfg, run_id).exists(), "未确认终态必须保留 recovery 台账"
+    assert run_id not in ACTIVE, "ACTIVE 不得残留（幽灵位挡后续 /run）"
+    # 上报未提交：DB 仍是 SCENE_RUNNING（注入不落地）
+    assert fb.status == "SCENE_RUNNING", fb.status
+    fb.stop()
+    with ACTIVE._lock:
+        ACTIVE._runs.clear()
+
+
+def test_r1_03_finish_failure_lost_response_confirms_and_clears(tmp_path):
+    """R1-03 分支二（已提交但响应丢失）：SCENE_FAILED post 500（DB 已落
+    SCENE_FAILED）→ 对账确认终态 → recovery 台账清除，不重复 post。"""
+    run_id = "scene-r103-lost"
+    fb = FakeBackend(_run_detail_steps(run_id), _source_detail())
+    fb.status_fail["SCENE_FAILED"] = {"code": 500, "body": {"error": "lost"},
+                                      "committed": True, "consumed": False}
+    cfg = _cfg_with_backend(tmp_path, fb, run_id)
+    _active_or_post(cfg, run_id, 1, "tok-r103b")
+    save_recovery_state(cfg, run_id=run_id, attempt=1, lease_token="tok-r103b",
+                        resource_lease_token=None, stage="EXECUTING",
+                        identity=_process_identity(), accepted_at=time.time())
+    assert state_path(cfg, run_id).exists()
+    _finish_failure(cfg, Backend(cfg), run_id, 1, "tok-r103b", None, None,
+                    "INFER: MODEL_FAILED", threading.Event(), "none", stage="EXECUTING")
+    assert fb.status == "SCENE_FAILED", fb.status
+    failed_posts = [p for p in fb.wrote("/status") if p and p.get("status") == "SCENE_FAILED"]
+    assert len(failed_posts) == 1, failed_posts  # 对账确认，不重复 post
+    assert not state_path(cfg, run_id).exists(), "已确认终态 → 台账清除"
+    assert run_id not in ACTIVE
+    fb.stop()
+    with ACTIVE._lock:
+        ACTIVE._runs.clear()
+
+
+def test_r1_04_unlink_error_keeps_ledger_and_releases_active(tmp_path, monkeypatch):
+    """R1-04：clear_recovery_state 的 unlink 抛非 FileNotFoundError（I/O/
+    权限错误）→ 收尾不得中断：ACTIVE 恒释放（后续 /run 不被幽灵位挡），
+    recovery 台账保留作清理失败恢复依据。"""
+    def _boom(self, *a, **k):
+        raise PermissionError(13, "read-only file system", str(self))
+
+    monkeypatch.setattr(Path, "unlink", _boom)
+    run_id = "scene-r104"
+    fb = FakeBackend(_run_detail_steps(run_id, "SCENE_FAILED"), _source_detail())
+    cfg = _cfg_with_backend(tmp_path, fb, run_id)
+    _active_or_post(cfg, run_id, 1, "tok-r104")
+    save_recovery_state(cfg, run_id=run_id, attempt=1, lease_token="tok-r104",
+                        resource_lease_token=None, stage="EXECUTING",
+                        identity=_process_identity(), accepted_at=time.time())
+    try:
+        _finish_failure(cfg, Backend(cfg), run_id, 1, "tok-r104", None, None,
+                        "ORCHESTRATION_ERROR: boom", threading.Event(), "none",
+                        stage="EXECUTING")
+    finally:
+        monkeypatch.undo()
+    assert run_id not in ACTIVE, "unlink 抛错不得中断收尾 → ACTIVE 恒释放"
+    assert state_path(cfg, run_id).exists(), "清理失败 → 台账保留作恢复依据"
+    fb.stop()
+    with ACTIVE._lock:
+        ACTIVE._runs.clear()
\ No newline at end of file

```
