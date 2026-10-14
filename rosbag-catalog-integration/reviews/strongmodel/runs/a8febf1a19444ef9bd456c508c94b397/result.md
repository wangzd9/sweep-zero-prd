# 独立审查结果

- **review_id / 类型**：`SR-07B-R4-20261013`，增量复审
- **触发**：`AUTHORIZED_CODEX`；grant `31dcbabe5720469c9fae7614188d625e`，call `a8febf1a19444ef9bd456c508c94b397`
- **快照**：base `4baf79f6e1c42247a55c8554ff1e33ec8e0d2054`，target/当前 HEAD `62620a3ddc5cfa614c5e72681c852c96d60507b3`；契约为 DESIGN §7.2、§4.1 及本包冻结 AC；迁移 SHA256 为 `a13e30731a30611512ba75ce66986cfdf4b952ba9573a79a4ecb0e8119645e63`。
- **范围**：仅 R4 迁移 diff 及必要的 R3 对照、派单、回执和证据。结论 **REWORK_REQUIRED**，只作用于 **07B 模块合入门禁**；不代表集成、工程闭环或生产验收。

## 问题 R4-01

- **分类 / 严重度**：`CORRECTION` / 中，已确认。对应本包 §2 不变量 3：审计表缺失态的 downgrade **全 no-op 且不抛异常**。
- **预期 / 实际**：审计表缺失时，downgrade 不改变 schema。实际在 [迁移第 97 行](/home/wang/work/doc/prd/rosbag-catalog-integration/reviews/strongmodel/runs/a8febf1a19444ef9bd456c508c94b397/snapshot/alembic/versions/20261012_01_scene_manual.py:97) 先独立检查并删除 evidence 表的 `corrected_label`，到第 101 行才检查审计表是否存在。
- **触发与后果**：`scene_manual_revision` 缺失、`bag_scene_label_evidence.corrected_label` 存在时，downgrade 成功返回，却删除 evidence 列及其中已存的人工修正值。我用内存 SQLite 实际执行该形态，结果为 `no_exception`，执行后 evidence 表仅剩 `id`；空 schema 形态也无异常。协调者探针只断言“不抛异常”，未核验 schema 不变。
- **最小修复与关闭条件**：在审计表缺失时，于任何 drop 前返回；审计表存在时保留当前 evidence 列、索引、审计列和表的操作顺序。用 SQLite 与隔离 MySQL 分别核验“审计表缺失且 evidence 列存在”时列和值保留，并复跑正常态往返。若冻结 AC 中“全 no-op”原意仅指**审计表依赖块**，须先由契约负责人明确修正该表述；当前代码不能按字面 AC 判为通过。此项阻塞 07B 合入。

**其余裁决**：R4 的 upgrade 零改动；审计表存在时，`_indexes_of`、4 个索引、审计列和删表的顺序与 R3 逐语句一致。提升守卫覆盖 `_indexes_of` 有依据：R3 在表缺失时仍会调用它，派单 §一所称原始形态“no-op 安全”与该调用路径不符；越界申报成立，但没有发现它改变正常态顺序。新增往返风险说明与 `20261009_02` 的列丢失说明同型，未改列结构。

**证据与限制**：已核对单文件 diff、父提交、SHA256、`git diff --check`（通过）、`alembic heads`（单头），并执行上述内存 SQLite 探针。回执申报定向测试 **12 passed**、MySQL 8.4.11 正常态往返成功；本审查未复跑这两项，所引 MySQL 脚本在快照内不可用。OCR 结果文件记录 **0 findings**。R3 已接受的应用代码结论未重复审查；SR-05 真并发仍由 TESTER 07B-post-r 收口。

**本轮统计**：确认缺陷 1 项；核实派单错误前提 1 项；无范围外派单。R4 为本问题的当前返修轮，未重复通读历史应用代码。token 与费用未知。只读审查，**未写结果文件、未修改代码、未合并或部署**。