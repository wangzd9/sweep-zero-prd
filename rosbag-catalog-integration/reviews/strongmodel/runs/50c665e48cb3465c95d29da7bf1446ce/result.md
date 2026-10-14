# TASK-07B 独立审查结果

- **审查身份**：`SR-07B-A2R2-20261013`，PRE_MERGE；触发来源 `AUTHORIZED_CODEX`，grant_id `31dcbabe5720469c9fae7614188d625e`，call_id `50c665e48cb3465c95d29da7bf1446ce`。
- **基线与范围**：base `502bf8ec79690cf01e130cb0591121eb10e96af5`，target/快照 HEAD `68b51887d0ff94275f2dd9f61b1f76fa0907fd9d`；按审查包冻结的 DESIGN §7.2、§4.1 和 AC-04 不变量 1–6，审 TASK-07B 写接口。已核对 12 个变更文件清单、R2 增量、service、API、模型、查询端及定向测试。
- **结论：REWORK_REQUIRED**。仅阻塞 **TASK-07B 模块合入门禁**；不裁决 16A/16B、集成闭环或生产门禁。

## 阻塞问题

**07B-SR-01｜CORRECTION｜高｜确认。纠错值没有持久化。** 对应 AC-04 的人工纠错及有效标签投影。预期提交 `corrected_label=flat` 后，读取端能取得当前人工标签，同时保留模型原判定；实际代码只把该值放入响应和幂等响应。[service 第217、259、277、294行](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/50c665e48cb3465c95d29da7bf1446ce/snapshot/app/services/scene_manual_revision_service.py:217) 的 MANUAL evidence、审计及 `bag_scene` 均未存它；[证据模型](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/50c665e48cb3465c95d29da7bf1446ce/snapshot/app/models.py:597) 也无修正值字段。触发：把模型 `slope` 改成 `flat`；后果：返回 200，却无法从库或查询端还原当前 `flat`。最小修复是确定并写入人工标签的持久化位置，让有效读取端使用该值；保留 MODEL 行和 segment，增加提交后重新开 session 读取 `flat` 的断言。**修复及回归通过前阻塞合入。**

**07B-SR-02｜CORRECTION｜高｜代码路径确认，真 MySQL 响应待验证。守卫之前的关联 INSERT 可抢先报错。** 对应不变量 1、2。预期同代次两次纠错恰一方 200、另一方 409；实际在关联尚不存在时，两方可先读到 `linked is None`，[显式 INSERT](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/50c665e48cb3465c95d29da7bf1446ce/snapshot/app/services/scene_manual_revision_service.py:277) 先于[版本守卫](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/50c665e48cb3465c95d29da7bf1446ce/snapshot/app/services/scene_manual_revision_service.py:293)。`bag_scene` 以 `(bag_id, scene_id)` 为主键；赢家提交后，输家可能在 INSERT 处收到未捕获的唯一键异常，根本到不了 409 守卫。子切片登记路径没有预建该关联，故这是可达场景。最小修复是让版本守卫先于可能冲突的写入，或把该类竞争错误回滚并准确归为 409；用真 MySQL 双连接、初始无关联的同版本请求核验 200/409、版本只加一、审计与 MANUAL evidence 各一行。**修复及验证前阻塞合入。**

**07B-SR-03｜CORRECTION｜中｜确认。幂等重放漏比对 body 操作者。** 对应不变量 3 及“四要素”操作者证据。预期同键但操作者不同返回 409；实际 [payload 把 `operator` 固定为请求头](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/50c665e48cb3465c95d29da7bf1446ce/snapshot/app/services/scene_manual_revision_service.py:218)，[重放](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/50c665e48cb3465c95d29da7bf1446ce/snapshot/app/services/scene_manual_revision_service.py:228) 又早于 `_resolve_operator`。两次均只在 body 传操作者时，第二次改为另一人仍命中原响应；带相同请求头、第二次 body 改为冲突操作者，也绕过应有的 409。下架路径同构（第312–331行）。最小修复是先解析并校验有效操作者，再将其纳入两路幂等哈希；验证 body-only 换人、头/body 冲突、原参数重放三种情况。**修复及回归前阻塞合入。**

**07B-SR-04｜CORRECTION｜中｜确认。再次纠错可覆盖“首次纠错时的模型投影”引用。** 对应不变量 4。[模型引用查询](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/50c665e48cb3465c95d29da7bf1446ce/snapshot/app/services/scene_manual_revision_service.py:143) 取父包最新 MODEL evidence；已有 MANUAL 行再次纠错时，[非空引用直接覆盖原字段](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/50c665e48cb3465c95d29da7bf1446ce/snapshot/app/services/scene_manual_revision_service.py:271)。触发：首次纠错后父包产生新模型证据，再纠错同一子切片；后果：MANUAL 行不再指向首次纠错的模型投影。最小修复是已有首次引用时保留它，并测试两次纠错之间模型证据变化的情况。**修复及回归前阻塞合入。**

**07B-SR-05｜VERIFICATION_GAP｜高｜确认缺证据。真并发 409 尚未验证。** 对应不变量 2，也用于关闭 07B-SR-02。[R2 测试](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/50c665e48cb3465c95d29da7bf1446ce/snapshot/tests/test_task07b_r2_revision.py:117) 在发请求前已提交版本推进，请求会在读比对处返回 409，不能覆盖“两方均读到旧版本、写入时竞争”的窗口。包内也明确申报真 MySQL 双连接未执行。TESTER 应在隔离 MySQL 上覆盖初始无关联的同版本纠错，并核对响应、版本、审计、证据和关联行；**该证据到位前不解除合入门禁**。

## R1–R4 裁决

| 风险 | 裁决 |
|---|---|
| **R1 回滚与提交** | 同一数据库事务内，守卫返回零行后的 `rollback()` 可撤销此前 `Scene` flush、显式关联 INSERT 和待 flush 的 ORM 对象；守卫成功后提交失败也没有半写提交窗口。但守卫前 INSERT 的并发异常成立，见 07B-SR-02。`SessionLocal` 的 `autoflush=False` 见 [database.py](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/50c665e48cb3465c95d29da7bf1446ce/snapshot/app/database.py:13)。 |
| **R2 下架写回** | 未发现赋值与守卫写回造成双重版本推进：无键且使用新版本再次下架是一次新写入；同键同载荷重放直接返回旧响应；旧版本新请求为 409。真并发结论仍受 07B-SR-05 限制。 |
| **R3 守卫前重放** | 对合法、完全相同的请求，先返回原响应且不再校验旧 `row_version` 符合冻结幂等口径；操作者未进入有效载荷比对是确认缺陷，见 07B-SR-03。 |
| **R4 `synchronize_session="fetch"`** | 本函数后续用 `expected + 1` 构造响应，没有依赖 session 中 `bag.row_version` 的读取；未发现由会话同步引起的独立 AC 缺陷。 |

## 证据与后续

本轮执行了只读的 commit、diff 和代码核对；`git diff --check base..target` 通过，工作区干净。**未执行测试或数据库写入**：当前是只读审查快照。包内“8 passed”、全量测试和 MySQL 迁移结果属于提交材料陈述；所引回执、派单原件不在本快照内，且真 MySQL 并发测试明确未执行，不能把这些陈述当作本轮复验。

本轮确认 **4 项缺陷、1 项验证缺口**；R2 与 R4 未发现独立缺陷。返修后应按上述受影响路径验证并提交新 target 供复审；本结果不继承为新逻辑的 PASS。token 与费用未知。只读环境下**未写入**约定的 `result.md`，由调用包装器保存本结果。