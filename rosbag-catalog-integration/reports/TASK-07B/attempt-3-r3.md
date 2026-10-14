# 回执：TASK-07B attempt-3-r3（强审查返修，R3-1~R3-4）

- status: REVIEW_PENDING
- task/attempt：TASK-07B / attempt-3-r3（强审查 SR-07B-A2R2-20261013 返修，问题 ID 单）
- owner：B（前端功能开发群）
- 派单：`inbox/2号/TASK-07B/attempt-3-r3-dispatch.md`（ACK `attempt-3-r3-ack.md` 02:11）
- 审查来源：codex call `50c665e48cb3465c95d29da7bf1446ce` REWORK_REQUIRED（4 CORRECTION + 1 VERIFICATION_GAP）
- 时间：2026-10-13 02:5x +08:00

## 一、base / head

- base：`68b5188`（attempt-2-r2 交付冻结 HEAD，续 commit；原 base `502bf8e` 不变）
- head：**`4baf79f`**（`scene/task-07b-manual-revision-withdraw` @ `wt-04a-t07b`）
- 范围：7 文件 +441/-15，零越界（全部在派单 §二允许文件清单内）

## 二、文件清单（`git diff --name-only 68b5188..4baf79f`）

| 文件 | 变更 | 对应 |
|---|---|---|
| `app/models.py` | +8 | R3-1：`BagSceneLabelEvidence.corrected_label`、`SceneManualRevision.corrected_label`（均 String(16) nullable） |
| `alembic/versions/20261012_01_scene_manual.py` | +26/-1 | R3-1：改未合入迁移双表加列含 downgrade drop（Inspector 2.0 `get_columns` 口径，部分应用重入 gate） |
| `app/services/scene_manual_revision_service.py` | +64/-21 | R3-1 MANUAL 新建+更新两路落值+审计落值+`current_manual_label` 读端口径；R3-2 守卫前置；R3-3 revise/withdraw 先 resolve 再构造 payload；R3-4 引用不覆盖 |
| `app/web/bags.py` | +6 | R3-1 详情端读 `current_manual_label` 传模板 `current_label`（仅 07B 面内读取口径） |
| `app/templates/detail.html` | +3/-1 | R3-1「当前人工标签」提示 + 审计表「修正为」列 |
| `app/api/scene_manual_revision.py` | +7/-6 | 顺带小修：尾换行 + `raise … from exc`（R2 增量 OCR 3 low 同文件卫生项，派单 §二明确授权） |
| `tests/test_task07b_r3_revision.py` | +342（新） | R3-1~R3-4 各 ≥1 新断言用例 |

## 三、行为（最小修复，冻结原 AC）

- **R3-1（07B-SR-01 高）**：提交纠错后**重开 session** 可从 `bag_scene_label_evidence` MANUAL 行 `corrected_label` 还原当前人工标签；REVISE 审计行存修正值、WITHDRAW 审计行恒 None；MODEL 行 `corrected_label` 恒 None、`original_judgment_ref` 原值不变；详情端展示当前人工标签 + 审计「修正为」列。
- **R3-2（07B-SR-02 高）**：`revise_scene_labels` 内 `_guarded_bump_row_version` 调整到 `bag_scene` 关联 INSERT **之前**——初始无关联子切片同版本两并发请求，输家在守卫处 409 回滚、不触达 INSERT 唯一键异常（非 409 守卫路径）。`withdraw` 无此 INSERT 不改。
- **R3-3（07B-SR-03 中）**：revise/withdraw 两路**先 `_resolve_operator` 再构造幂等 payload**，payload `operator` 用 resolve 后有效值（header 优先/body 兜底/冲突 409/缺失 422 语义保持）。
- **R3-4（07B-SR-04 中）**：MANUAL 行 `original_judgment_ref` **已非空不覆盖**（锚定首次纠错时刻的模型投影，仅 None 时写入）。
- AC 不变量冻结=审查包 §2(1-6)，未新增需求、未扩行为面（下架/检索语义不动）、无新表/新迁移文件/新依赖。

## 四、自测命令 / 退出码 / 环境 / 关键断言 / 证据

环境：`wt-04a-t07b` 分支 `scene/task-07b-manual-revision-withdraw` HEAD `4baf79f`，venv Python 3.10 + SQLAlchemy 2.0.41，SQLite 测试库（`tests/conftest.py` 临时库）+ 真 MySQL 8.4.11 独占容器（用完即毁，0 残留）。

1. **R3 定向**：`pytest tests/test_task07b_r3_revision.py -q` → **4 passed**（RC=0）。
   - R3-1：重开 session 断言 MANUAL 行 `corrected_label=="flat"`、`original_judgment_ref=="slope#<首次父包 MODEL 引用>"`、MODEL 行 `corrected_label is None` 且原值不变、REVISE 审计行 `corrected_label=="flat"`、`current_manual_label()=="flat"`；页面实测 `当前人工标签：<strong>flat</strong>` + 审计「修正为」列；WITHDRAW 审计行 `corrected_label is None`。
   - R3-2：源码顺序断言 `_guarded_bump_row_version(` 位置 < `bag_scene.insert()` 位置 + 初始无关联子切片端到端 200 且关联建成。
   - R3-3：body-only 提交→完全重放 200 同响应→body-only 换人同 key **409**→header+body 冲突 **409**→withdraw body-only 换人同 key **409**。
   - R3-4：两次纠错之间父包 MODEL 证据 `original_judgment_ref` 改新值，MANUAL 行引用**保持首次值**（`slope#<首次>`）、`corrected_label` 更新为新标签、仍同一 MANUAL 行不新增。
2. **07B 既有回归**：`pytest tests/test_task07b_manual_revision.py tests/test_task07b_r2_revision.py tests/test_task07b_r3_revision.py -q` → **12 passed**（RC=0）。
3. **ruff**：改动 6 文件（models/service/web-bags/api/migration/r3-test）`ruff check` → **All checks passed**。
4. **迁移往返（增列口径，T03/T04 教训先例）**：
   - SQLite：`alembic upgrade head`→`downgrade 20261009_02_ingest_frozen`→`upgrade head` 全 RC=0。
   - **真 MySQL 8.4.11 隔离库**（`docker.m.daocloud.io/mysql:8.4` 独占容器 `t07b-r3-mig-*`）：`upgrade head` 后 `SHOW COLUMNS` 校验两表均含 `corrected_label` 列 → `downgrade` 后审计表 drop + 证据表列移除 → re-`upgrade head` 后两表列恢复；**MYSQL_ROUNDTRIP_OK**，容器 0 残留（`docker ps --filter label=rosbag.t07b` 空）。
5. **全量**：`pytest --ignore=tests/test_devflow.py -q` → **840 passed / 1 failed / 10 skipped**（RC=0 收尾，57.3s）。基线 836 passed + 本单 4 新 = 840；唯一 failed=`tests/test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time`（web 性能计时环境性，**base `68b5188` 同口径复现**，派单 §三已列为环境性非功能面），无新红。
6. `alembic heads` → 单头 `20261012_01_scene_manual`（无多头）。

## 五、未执行项 / 越界申报

- **SR-05（07B-SR-05 VERIFICATION_GAP 高，真并发 409）**：**不属本单**——真 MySQL 双连接同版本无关联 200/409 口径由 TESTER 在 07B-post-r3 固定 target 单独立取证（避免自证），R3-2 本单只做源码顺序断言 + 无关联 e2e 200。
- 未执行真 MySQL 全量测试套件（本单改动面为 07B 服务/模型/迁移/web 读口径，SQLite 全量已覆盖行为面，MySQL 口径=迁移 DDL 增列往返已独立验证，业务行为真并发留 TESTER）；如协调者要求可补。
- 无越界：未改 07A/16A/16B 文件面、未建新表/新迁移文件、未加新依赖、未做页面布局重构、未扩下架/检索语义；`app/api/scene_manual_revision.py` 仅派单 §二明确授权的尾换行 + `raise from exc` 卫生项，未动响应字段。
- **本单不解除合入门禁**：交付 REVIEW_PENDING，待协调者机械核验 → R3 增量 OCR（`--from 68b5188 --to 4baf79f`）→ 强审查增量复审（只看 R3-1~R3-4，授权额度内）→ TESTER 07B-post-r3（SR-05）→ 全绿合入。

## 六、同根因轮次

- 本单为 R3（强审查 REWORK_REQUIRED 首次返修）。若 R3 增量复审再出**同位** CORRECTION，按派单 §四升级用户，不无限返修。