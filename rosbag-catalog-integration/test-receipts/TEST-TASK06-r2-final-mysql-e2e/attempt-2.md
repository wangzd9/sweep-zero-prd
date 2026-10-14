# 回执：TASK-06 / r2-final-mysql-e2e / attempt-2（测试者，独立验证槽）

- status: TEST_REPORT_PENDING
- 派单：`inbox/TESTER/TASK-06/r2-final-mysql-e2e.md`
- 被测快照：`main 0f6aa87`（核对一致，`git status` 迁移目录+两测试文件 CLEAN）
- owner: 测试者
- 交付时间: 2026-10-10 20:04 +08:00
- 环境: 真实 MySQL 8.4.11（`6ea90827b110`，容器 `tester-r2-mysql` / 网络 `tester-r2net2`，宿主 33070，隔离库 `t_s1fresh/t_s1exist/t_r2app3`，跑完销毁 0 残留核实）

## 结论（对 attempt-1 的复测 + 一处误诊纠正）

| 项 | attempt-1 | attempt-2 | 说明 |
|----|-----------|-----------|------|
| S1 R2-01 迁移链（高） | **FAIL** 1406 | **PASS**（AC1/AC2/AC3 三 AC 全绿） | `ceeac16`/`0f6aa87` 改短 revision 25 字符解除，真实 MySQL 全新库/已有库增量/已加宽库幂等三路径 RC=0 |
| 不变式套件 40 用例 | 37 PASS / 3 FAIL | **39 PASS / 1 FAIL** | fixture `6ee858b` 让 `test_identity_gates`/`test_multi_scene` 转 PASS |
| `test_reconcile_backfills_after_publish_without_report` | FAIL（归因=child uid 截断） | **FAIL**（**非 uid 截断**，见下纠正） | 残留唯一 FAIL |

## §对 attempt-1 的纠正（关键）

attempt-1 把 reconcile 用例 FAIL 归因为"`_child_uid()` 27 字符 uid 被 MySQL 截断为 26 → 二次调用 ORM 按内存 27 字符值更新 0 行，非应用缺陷、为夹具口径问题"。**该归因经本轮探针证实不成立：**
- 实测 child uid=22 字符、parent uid=18 字符，均 `<26`，`assert len<=26` 通过，无越宽无截断；
- fixture `6ee858b` 已合入（uid 收敛+assert）后该用例**仍 FAIL**——若真是 uid 宽度问题，修复后应转绿；
- 最小复现（单用例/单全新库/`with TestClient` 触发 app lifespan）+ SQL echo：reconcile-2 在 `scene_result_report_service.py:928 db.commit()` 抛 `StaleDataError: UPDATE bag_record ... WHERE id=2 expected 1 row, 0 matched`；
- **探针**：异常后新 root 连接 `SELECT` 证实 `id=2` 子包行**确实存在**（AVAILABLE），同连接直接 `UPDATE ... WHERE id=2` **affected rows=1** → DB 行在、可更新，但 app ORM 会话内同语句 0 行。

**定性：06B reconcile 幂等重放路径在 MySQL 下的真实 app 层缺陷（非测试夹具），SQLite 全绿遮坑。建议回派 2号（06B app owner）根因，非改测试夹具。** 我 attempt-1 的"夹具口径问题、非应用缺陷"表述予以更正。

## 交付

- 报告：`reports/TASK-06/r2-final-mysql-e2e-attempt-2.md`（S1 三 AC 表 + 套件 39/40 + §纠正 + 缺陷3 + 证据索引，逐场景 SQL/RC/摘录）
- 回执：本文件
- 证据：`~/.hermes/cache/scratch/tester_r2_a2_*`（s1/suite/single_tb/t5_echo/dbg_reconcile2 脚本+日志）

## 影响 AC / 门禁

- S1 三 AC PASS → 06 聚合"迁移链 MySQL"高阻塞**解除**，03 聚合（03B）MySQL 路径验收缺口随本项收口。
- 不变式套件 39/40，残留 1 FAIL（缺陷3，06B app 代码面幂等重放）→ **06 聚合放行业务门禁仍不通过**，需缺陷3 修复 + 本用例真 MySQL 复测 PASS。
- 强模型增量复审（R2-01/02/03 必附 MySQL 结果）：缺陷3 属 R2-04/06 一致性面，建议纳入复审。

## 边界声明

- 仅测试与取证，未改仓库任何业务文件（`git status` 核对）；测试材料在 scratch。
- 隔离 MySQL 容器/网络/库本轮已销毁，0 残留。
- 不跑 OCR、不决定合入；缺陷3 定性权与建议交协调者裁决。