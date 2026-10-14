# 派单：TASK-07B attempt-3-r3 强审查返修（最小范围）

- status: ACKED (2026-10-13 02:11 B, ack inbox/2号/TASK-07B/attempt-3-r3-ack.md)
- 派单时间：2026-10-13 02:1x +08:00（协调者 r107）
- 任务：TASK-07B attempt-3-r3（强审查 SR-07B-A2R2-20261013 返修，问题 ID 单）
- owner：B（前端功能开发群，`wt-04a-t07b` 原分支 `scene/task-07b-manual-revision-withdraw` 续 commit）
- base：`68b5188`（attempt-2-r2 交付冻结 HEAD，续 commit；原 base `502bf8e` 不变）
- 审查来源：用户 24h 强审授权（grant `31dcbabe…` 期限 2026-10-13 11:33:12）内 codex call `50c665e48cb3465c95d29da7bf1446ce`，结论 **REWORK_REQUIRED**（4 CORRECTION + 1 VERIFICATION_GAP），结果全文 `reviews/strongmodel/runs/50c665e48cb3465c95d29da7bf1446ce/result.md`，审查包 `reviews/TASK-07B/attempt-2-r2/strong-review/SR-07B-A2R2-20261013-pack.md`。

## 一、返修范围（仅 4 项代码缺陷，逐条对应问题 ID；SR-05 验证缺口不归本单，由 TESTER 在 R3 交付后按固定 target 独立取证）

**R3-1（07B-SR-01，CORRECTION 高）：纠错值持久化。**
- 现状：`corrected_label` 只进响应与幂等响应；MANUAL evidence 行、审计表、`bag_scene` 均不存修正值 → 提交 200 后无法从库还原当前人工标签（AC-04「人工纠错」核心语义缺口）。
- 最小修复：`BagSceneLabelEvidence` 增列 `corrected_label String(16) nullable`（MODEL 行恒 None；MANUAL 行存修正值）+ `SceneManualRevision` 审计表同增 `corrected_label nullable`（REVISE 存修正值、WITHDRAW 存 None）；**改未合入的原迁移 `alembic/versions/20261012_01_scene_manual.py` 直接加列（含 downgrade drop 列，07B 未合入故不另开新迁移文件）**；`revise_scene_labels` 写 MANUAL 行时落值（新建+更新路径都写）+ 审计行落值；**查询端**（07B 面内的详情/审计读取，`app/web/bags.py`/`app/api` 面）当前标签读取口径：MANUAL 行存在时以 `corrected_label` 为有效人工标签展示/返回（保留 `original_judgment_ref` 模型原值不变）。
- 验证：新增断言=提交纠错后**重新开 session** 读取 MANUAL evidence `corrected_label`==提交值 + 审计行含修正值 + MODEL 行原值不变 + 详情端返回当前人工标签。

**R3-2（07B-SR-02，CORRECTION 高）：守卫前关联 INSERT 并发抢先。**
- 现状：`revise_scene_labels` L280-281 `bag_scene` INSERT 先于 L293 守卫 UPDATE；`bag_scene` 以 (bag_id, scene_id) 为主键，子切片登记路径未预建关联时，同版本两并发请求输家可在 INSERT 处抛唯一键异常（非 409 守卫路径）。
- 最小修复：**调整顺序=先 `_guarded_bump_row_version` 再 `bag_scene` 关联 INSERT**（输家先 409 回滚，不触达 INSERT；赢家同事务内 INSERT 无冲突）。`withdraw` 路径无此 INSERT，不改。
- 验证：新增断言=**初始无 bag_scene 关联**的子切片同版本双请求（SQLite 内模拟顺序/断言顺序依赖守卫先行的代码路径）；真 MySQL 双连接口径留 TESTER（SR-05 单）。

**R3-3（07B-SR-03，CORRECTION 中）：幂等 payload 漏有效操作者。**
- 现状：payload `operator` 固定取 `operator_header`（L224），`_replay_or_none`（L228）早于 `_resolve_operator`（L240）→ 两次仅 body 传操作者（header 均 None）时第二次换人仍命中原响应；header 与 body 冲突时同绕。
- 最小修复：**先 `_resolve_operator`（依赖 bag 前可先做 header/body 解析口径，无效操作者 422 语义保持）再构造 payload**，payload `operator` 用有效操作者（resolve 后值）；revise/withdraw 两路同改。
- 验证：新增断言=body-only 换人同 key → 409（payload 不同）；原参数完全重放 → 200 原响应；header+body 冲突口径 → 409。

**R3-4（07B-SR-04，CORRECTION 中）：再纠错覆盖首次模型投影引用。**
- 现状：L274-275 `if original_ref: ev.original_judgment_ref = original_ref` → 已有 MANUAL 行再次纠错时，父包新模型证据覆盖「首次纠错时的模型投影」引用（违反不变量 4 语义=引用应锚定首次纠错时刻）。
- 最小修复：**`ev.original_judgment_ref` 已非空时不覆盖**（保留首次引用；仅 None 时写入）。
- 验证：新增断言=两次纠错之间父包模型证据变化，MANUAL 行 `original_judgment_ref` 保持首次值。

## 二、边界（冻结）

- 允许文件：`app/models.py`、`app/services/scene_manual_revision_service.py`、`alembic/versions/20261012_01_scene_manual.py`、`app/web/bags.py`（仅 07B 面内读取口径）、`app/api/scene_manual_revision.py`（仅响应字段增补）、`tests/test_task07b_r2_revision.py`（+R3 断言）/ 新 `tests/test_task07b_r3_revision.py`、`app/templates/detail.html`（仅当前人工标签展示位如有必要）。
- **顺带小修**：`app/api/scene_manual_revision.py` 文件尾换行（R2 增量 OCR 3 low 中 2 条同文件卫生项，`raise … from exc` 口径一并采纳——避免下次增量 OCR 重复报）。
- 禁：新表/新迁移文件（改未合入原迁移）、新依赖、07A/16A/16B 文件面、页面布局重构、行为面扩大（下架语义/检索语义不动）。
- AC 不变量冻结=审查包 §2（1-6），R3 只关闭 SR-01~04，不新增需求。

## 三、自测口径

- 定向：R3-1~R3-4 各 ≥1 新断言用例 + 既有 07B 用例 0 红；全量（`--ignore=tests/test_devflow.py`）0 新红（基线 836 passed + web 性能计时 1 环境性）；ruff 改动文件绿；迁移 upgrade/downgrade 往返真 MySQL 隔离库（增列口径，T03/T04 教训先例）；页面实测=纠错后详情端显示当前人工标签+原模型值并存（口径同 07A/B 自包含 uvicorn）。
- 交付：commit（`68b5188` 之上）+ 回执 `receipts/TASK-07B/attempt-3-r3.md`（REVIEW_PENDING）+ 报告 `reports/TASK-07B/attempt-3-r3.md`；真 MySQL 双连接并发取证**不属本单**（TESTER 固定 target 单，避免自证）。

## 四、停止条件与后续

- 交付后：协调者机械核验 → R3 增量 OCR（仅 diff，`--from 68b5188 --to HEAD`）→ 强审查增量复审（只看 R3-1~R3-4 问题 ID + 修复 diff，授权额度内，冻结新 target）→ 复审无阻塞 → **TESTER 07B-post-r3 独立验证单**（SR-05 口径=真 MySQL 双连接同版本无关联 200/409 + 版本只加一 + 审计/MANUAL evidence 各一行 + SR-01 持久化读回 + SR-03 换人口径）→ 全绿合入（07B 整链 `5fa0942..` 先于 16A 迁移 rebase 合入，处理 alembic 双头）→ 07B DONE → 派 07C/16C。
- 同根因两轮失败（R3 复审再出同位 CORRECTION）=升级用户，不无限返修。
- 已 ACK 前请回复 ACK（`inbox/2号/TASK-07B/attempt-3-r3-ack.md`）；开工不催单，长任务记检查点。