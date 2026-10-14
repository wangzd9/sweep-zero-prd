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