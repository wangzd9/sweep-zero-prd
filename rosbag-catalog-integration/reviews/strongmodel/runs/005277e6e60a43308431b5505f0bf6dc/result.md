**结论：REWORK_REQUIRED。** R1-01、R1-04、R1-05 已关闭；R1-02、R1-03 部分修复，仍存在原契约内的阻塞反例。本结论仅作用于 **TASK-16B 合入门禁**，独立 TESTER、12S-C/12S-D 及生产门禁继续保留。

- review_id：`SR-16B-R2-20261013`；类型：增量返修复审。
- 触发：`AUTHORIZED_CODEX`；grant_id：`6b2d83fb978644b7938424e4652024ce`；call_id：`005277e6e60a43308431b5505f0bf6dc`。
- base：`40ab8182c177b53fc2ff60ac6bd511b14ab4f1d9`。
- target／实际 HEAD：`e1524657bda1f66f03034cb72ef05cd65e0c1dfc`。
- 契约：冻结 v0.4、TASK-16B 原 H1/H2/H4/H6；独立 semantic_hash 未提供。
- 实际范围：两文件增量、相关恢复调用链、Backend 步骤状态机和租约边界、返修测试、开发回执及协调者 r167 验证记录。未扩审其他功能或全量历史。

**逐项关闭情况**

| 原问题 | 判定 | 证据与边界 |
|---|---|---|
| R1-01 | **已关闭** | `resolve_spec` 在执行前拒绝 Backend 已终态 run；独立内存验证覆盖 `SCENE_DONE/SCENE_FAILED/CANCELLED`，均未进入后续执行，也未覆盖已有终态。迟到请求仍返回 202，不影响本项“不得重执行”的关闭。 |
| R1-02 | **未关闭** | 单次失败后的补报已实现，但补报或对账继续失败时，调用方仍清除 recovery，步骤可永久停在 `RUNNING`。 |
| R1-03 | **未关闭** | 未确认终态时已保留 recovery；但未持久记录“待失败收尾”，重启将其恢复为业务执行，存在同 attempt 再次进入模型执行的反例。 |
| R1-04 | **已关闭** | `unlink` 的 `OSError` 被记录且不再中断收尾。独立注入 `PermissionError` 后，`ACTIVE` 正常释放，删除未成功。 |
| R1-05 | **已关闭** | 实现及测试符合 `file fsync → replace → parent directory fsync`；独立内存调用顺序验证通过。保证仍限于支持该持久化语义的文件系统，部署实际文件系统核验留在原生产门禁。 |

**R1-02｜CORRECTION｜高｜已确认，阻塞 TASK-16B 合入**

对应 H2 和原解除条件：`RUNNING` 已落库后，checkpoint 中的 `DONE/FAILED` 必须收敛；清理恢复依据前须确认或保留可继续补报的状态。

实际在 [reconcile_terminal](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/005277e6e60a43308431b5505f0bf6dc/snapshot/scripts/scene_host_proxy.py:515) 中，对账读取异常直接返回，补报再次失败也只留日志；没有向调用方传递“终态未确认”。[成功收尾](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/005277e6e60a43308431b5505f0bf6dc/snapshot/scripts/scene_host_proxy.py:850) 随后无条件清除 recovery；失败收尾也只确认 run 终态，不确认步骤终态。

独立只读内存注入复现了四个反例：

| checkpoint 目标 | 注入 | 最终步骤 | run 终态 | recovery |
|---|---|---|---|---|
| DONE | 原写入、补报均未提交 | RUNNING | SCENE_DONE | 已清除 |
| DONE | 写入未提交、对账读取超时 | RUNNING | SCENE_DONE | 已清除 |
| FAILED | 原写入、补报均未提交 | RUNNING | SCENE_FAILED | 已清除 |
| FAILED | 写入未提交、对账读取超时 | RUNNING | SCENE_FAILED | 已清除 |

这仍是原 R1-02 的“步骤卡 RUNNING 且恢复入口丢失”，没有增加新的可用性标准。现有两个新增测试只覆盖一次性故障后立即恢复，并在 `_report_steps` 返回后结束，未验证上述收尾行为。

最小修复边界：让步骤回报返回确认结果；未确认时持久保留待补报事实，并提供按原 attempt 收敛的恢复路径。补报须遵守现有 Backend 租约约束：run 终态会清租约，不能仅假定终态后重启即可补写。

解除条件：覆盖 DONE/FAILED 的已提交丢响应、未提交、补报继续失败及对账读取失败；验证未确认时恢复依据保留，故障解除后步骤正确收敛且不重新执行模型。

**R1-03｜CORRECTION｜高｜已确认，阻塞 TASK-16B 合入**

对应 H4 和原解除条件：“保留可对账恢复依据”，且两个故障分支均可收敛、不重复执行。

[_finish_failure](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/005277e6e60a43308431b5505f0bf6dc/snapshot/scripts/scene_host_proxy.py:891) 已做到未确认时不删台账，但保留的是原 `EXECUTING/RESOLVING` 台账，没有保存失败目标和错误事实。[recover_pending_runs](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/005277e6e60a43308431b5505f0bf6dc/snapshot/scripts/scene_host_proxy.py:941) 看到 Backend 仍为 `SCENE_RUNNING`，便启动 `execute_run`。编排器的 [checkpoint 恢复判断](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/005277e6e60a43308431b5505f0bf6dc/snapshot/scripts/scene_host_orchestrator.py:564) 不复用含 `INFER=FAILED` 的分析结果，因而再次进入分析执行。

可达触发：模型执行失败 → `SCENE_FAILED` 上报未提交 → 台账保留 → 代理重启且 Backend 恢复 → 原身份重新执行。

独立内存验证调用了实际 `recover_pending_runs → execute_run → SceneHostOrchestrator.run`，对文件、线程和模型边界作 stub，结果为：

```text
recovered=1
extra_model_invocations=1
saved_stages=["RESOLVING","EXECUTING"]
```

这里的计数表示再次进入模型执行函数，未发送真实模型请求。该反例违反原 R1-03“不重复执行”的解除条件。现有未提交测试只断言文件存在、`ACTIVE` 已清，未验证重启后的收敛。

最小修复边界：持久区分“执行中恢复”与“待失败终态确认”，保存原 attempt、目标终态和失败原因；后者重启时只进行对账／补报收尾。

解除条件：上报未提交后重启，在 Backend 恢复时确认原失败、正确清台账；模型执行计数不增加。保留已提交丢响应及其他终态不覆盖的现有回归。

**验证与后续**

本审查实际通过：目标 HEAD／base 祖先关系、两文件变更范围、`git diff --check`、Ruff、两文件 AST 解析，以及上述内存故障注入。工作区保持干净。

开发回执和协调者 r167 记录的 **39 passed** 已核阅；本审查未重跑 pytest，其 fixture 需要写临时文件，与当前只读沙箱不符。未执行真实栈、MySQL、真实模型、掉电验证或额外 OCR／模型审查。

本轮确认 **2 项原问题残余缺陷、关闭 3 项**，未增加范围外阻塞；未核实新的 OCR 误报，后续遗漏未知。下一步由原 owner 围绕 R1-02、R1-03 最小返修并补对应恢复验证，再由协调者及独立 TESTER 收口。

本结果未写文件，由包装器保存。未修改代码、合并、部署或委派模型；可复用性检查认为现有 reviewer Skill 已覆盖本轮流程。token、费用未知。