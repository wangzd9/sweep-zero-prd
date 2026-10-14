**结论：REWORK_REQUIRED，阻塞 TASK-16B 模块合入。** R1-03 的原失败恢复反例已关闭；R1-02 仍有真实租约语义下的残余缺陷。本次新增成功收尾链另有一项可复现缺陷。Backend 的 REGISTER 原子收尾未发现问题。

- review_id：`SR-16B-R3-DIRECT-20261013`
- 触发：`AUTHORIZED_CODEX`
- grant_id：`6b2d83fb978644b7938424e4652024ce`
- call_id：`22189dc73e9749d48d41e7ae9ae41e37`
- base：`e1524657bda1f66f03034cb72ef05cd65e0c1dfc`
- target／实际 HEAD：`15e4ef9094c7b51ec6f38832533c670d2664b985`
- 契约：冻结 v0.4、TASK-16B 原恢复要求及本包列出的 AC；独立 semantic_hash 未提供。
- 范围：两项原问题、增量代码和测试、必要编排调用链、Backend 步骤／终态／租约事务。部署文件仅核对变更清单，不裁决部署门禁；未重审 R1-01/04/05。

| 裁决对象 | 结果 |
|---|---|
| R1-02 | **未关闭**：确认结果已返回、台账会保留，但持续补报失败后主动停止续租，恢复入口可能失去有效写入资格。 |
| R1-03 原反例 | **已关闭**：`FINALIZING_FAILURE` 保存失败事实，恢复只调用补报收尾，不再进入业务编排。 |
| REGISTER 原子收尾 | **本轮定向验证通过**：QUEUED、RUNNING、缺行均可收敛；提交前异常回滚步骤、运行终态和租约。 |
| 默认参数 hash | `{}` 正规化修复成立；使用 target 代理及已接受集成候选的能力配置，spray／slope 参数值、类型和 hash 一致。 |

**R1-02｜CORRECTION｜高｜已确认，原问题残余**

对应原 H2／解除条件：补报持续失败时保留可恢复事实，故障解除后按原 attempt 收敛，且遵守真实 Backend 租约约束。

预期待收尾任务仍具有可用的补报资格。实际 [成功待收尾异常处理](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/22189dc73e9749d48d41e7ae9ae41e37/snapshot/scripts/scene_host_proxy.py:838) 和 [失败待收尾分支](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/22189dc73e9749d48d41e7ae9ae41e37/snapshot/scripts/scene_host_proxy.py:946) 都停止心跳；[_resume_finalization](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/22189dc73e9749d48d41e7ae9ae41e37/snapshot/scripts/scene_host_proxy.py:999) 仅使用旧 token 补报，没有续租或过期对账处理。

可达触发为：

1. 模型已完成，checkpoint 七步 DONE；步骤终态请求持续未提交，保存 `FINALIZING_SUCCESS`。
2. worker 退出收尾并停止续租。即使心跳接口可用，任务仍跨过现有 TTL。
3. 故障解除后恢复，旧 token 写步骤返回 `409 task lease expired`。
4. Backend 执行既有租约回收，将 run 改为 `SCENE_FAILED`；再恢复 complete，返回 `409 CONFLICT`，因为尚无已记录场景 outcome。

本轮用**实际 Backend 服务及 SQLite 内存库**复现：

```text
回收前：SCENE_RUNNING，七步 RUNNING，恢复台账保留
回收后：SCENE_FAILED，scene_outcomes 缺失
再次 complete：409 CONFLICT（None vs NO_MATCH），台账仍保留
```

后果是持久台账存在，但原 attempt 无法完成收尾；成功业务结果被租约回收判为失败。新增 `StrictBackend.lease_live` 仅为布尔值，不模拟 TTL，因而现有通过结果未覆盖此分支。

最小修复边界：让待收尾状态继续维持任务续租，并在恢复中核对真实租约资格；已过期／回收的身份须明确走受控对账，不能只反复使用旧 token，也不能全局放宽租约校验。

**阻塞模块合入。** 解除条件：注入步骤持续失败、心跳接口可用并跨过当前 TTL，随后恢复，证明原 attempt 的步骤和正确 outcome 收敛、模型调用不增加；同时验证过期／回收分支不会覆盖新 attempt 或进入永久补报循环。

**R3-01｜CORRECTION｜高｜已确认，新增成功收尾链缺陷**

对应本包冻结 AC：先持久化 `FINALIZING_SUCCESS`，成功七步确认后 complete；Backend 暂时不可达不得把已形成的成功结果改报为业务失败。

[ProxyBackendReporter.complete_scene](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/22189dc73e9749d48d41e7ae9ae41e37/snapshot/scripts/scene_host_proxy.py:338) 在保存成功意图之前，先调用 `run_detail()` 读取 attempt。该 GET 不在 `FinalizationPending` 转换范围内。异常会进入 [execute_run 的通用失败处理](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/22189dc73e9749d48d41e7ae9ae41e37/snapshot/scripts/scene_host_proxy.py:856)，持久化 `FINALIZING_FAILURE`。

触发：业务已完成、checkpoint 七步 DONE，在进入 complete 时使首个 GET 超时，随后恢复 Backend。只读内存注入实际收尾函数得到：

```text
保存阶段：RESOLVING → EXECUTING → FINALIZING_FAILURE
故障解除后：SCENE_FAILED，恢复台账删除
complete 调用次数：0
```

这属于新增调用顺序直接破坏成功收尾 AC，不是额外可用性要求。现有成功恢复测试只注入步骤或 complete 故障，没有覆盖此前新增的 GET。

最小修复边界：从原执行上下文取得已冻结的 attempt／work_root，先持久保存成功 payload 和幂等身份；其后的 Backend 读取或补报异常保持成功待收尾语义，不转入业务失败。

**阻塞模块合入。** 解除条件：覆盖此首个 GET 的一次性及持续失败，验证台账始终为 `FINALIZING_SUCCESS`；恢复后正确 complete，模型／发布不重执行，不写入错误的 `SCENE_FAILED`。

**验证与证据边界**

本轮实际执行了：

- 固定 HEAD、base 祖先关系、完整变更清单、`git diff --check` 和五个相关 Python 文件 AST 解析；工作树始终干净。
- 上述两个只读故障反例；其中租约分支调用真实 Backend 服务和租约回收逻辑，仅使用进程内 SQLite。
- Backend NO_MATCH 的 REGISTER 三种初态、终态重放及提交前异常回滚，共四组定向验证。
- target 代理配合集成候选 `6ddcbcb` 能力配置的 spray／slope 参数值、类型、hash 核对。

已读取独立回执及原日志，确认日志记录 **50 passed** 和 **24 passed**。这些是既有执行结果，**不是本轮重跑结果**。target 自身 YAML 尚无 spray 条目，24 项集成证据不能直接称为此 detached target 的独立测试结果。包内 **94 passed** 本轮未重跑。

未执行完整 pytest、MySQL、真实模型全链、生产验证、弱 OCR 或额外模型调用。既有测试需要临时文件，本轮只读验证采用内存文件替身；不把内存验证描述为真实文件恢复验收。

R1-01/04/05 沿用前轮已接受结论；本轮确认 **两项范围内 CORRECTION**，无范围外阻塞。由 16B owner 最小返修上述两项，协调者／TESTER 按关闭条件复验。集成候选及生产门禁继续独立保留。

本结果**未写文件**，由包装器保存；未修改代码、合并、部署或委派模型。可复用性检查认为现有 reviewer Skill 已覆盖流程，无需新增 Skill。token／费用、后续遗漏未知；本轮为 R3 增量复核。