# TASK-03B 强模型审查请求（attempt-2）

> 协调者生成，供强模型定向审查。所有证据均为真实命令输出/代码，未执行项已标注。
> 生成时间 2026-10-09。⚠️ 本任务**尚未合入 main**——审查对象是 worktree HEAD 14b7a64
> （/home/wang/.local/state/rosbag-scene/wt-03b，base 8e97ef1）。合入前必须过本次审查。

## 1. 任务卡摘要

- 任务 ID：TASK-03B ｜ 状态：🔁 返修完成待 OCR 收口（未合入）｜ owner：3号会话
- 交付行为：持久配置/API（IngestProfile/IngestSubmission）、Scanner 身份透传绑定、统一登记、用途事件 outbox 生产
- 验收范围：REQ-01、08、10、13 / AC-01、08、10、13
- 依赖：TASK-02 ✅、TASK-03A ✅、TASK-04A ✅（均已合入）
- 当前进度：attempt-1（34d15ac）交付完整 + attempt-2（14b7a64）返修完成；契约 5 字段与 purpose-schedule-event/v1 对齐；664 passed

## 2. 代码变更摘要

- Base：8e97ef1 → Output：14b7a64（worktree，未推送未合入）
- 变更文件（13，+2286/-8）：
  - alembic/versions/20261008_02_ingest_config.py（新增 154 行，3 表迁移）
  - app/api/ingest_submissions.py（新增 157）、app/services/ingest_service.py（新增 707）、app/services/scene_capability_read.py（新增 157）
  - app/models.py（+144）、app/api/__init__.py、app/services/bootstrap.py、app/services/source_service.py、app/scanner/{backend,runner}.py
  - tests/test_ingest_config.py（+571）、tests/test_ingest_config_api.py（+349）、tests/test_scanner_stability.py
- 高风险代码 ①——迁移 DDL（**未过 MySQL 8.4 隔离库验证**，见 §6 待裁决-1）：

```python
op.create_table("ingest_profile",
    sa.Column("id", BIGINT, nullable=False),
    sa.Column("display_name", sa.String(length=128), nullable=False, server_default=""),
    sa.Column("default_purposes_json", sa.Text(), nullable=False, server_default="[]"),
    sa.Column("default_scenes_json", sa.Text(), nullable=False, server_default="[]"),
    sa.Column("default_scene_parameters_json", sa.Text(), nullable=False, server_default="{}"),
    sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("profile_id", "version", name="uq_ingest_profile_id_version"))
# ingest_submission: relative_path 宽 1024 不进唯一索引（utf8mb4 键长上限），
# 唯一占位用 path_claim_key=sha256(profile|version|relative_path) 定长 64
# purpose_schedule_event: 唯一消费键含可空 capability_version/capability_config_hash
# （self_built 事件无 scene 字段；MySQL 唯一约束对 NULL 不生效 → event_id 唯一 + 05 幂等双保险）
# downgrade 防线: 存在 BOUND/SCHEDULED 提交或 PENDING 事件时拒绝回滚
```

- 高风险代码 ②——绑定状态机 + 占位不变式（ingest_service.py 643-686 行，attempt-2 OCR 争议焦点）：

```python
submission = _find_pending_submission(db, profile_row, entry_relative)
if submission is None:
    submission = _ensure_system_submission(db, profile_row, entry_relative)  # 同事务新建 system 行
    db.flush()
if submission.config_required or not submission.effective_config_json:
    submission.status = "BOUND"          # 同事务内立即推进终态
    submission.path_claim_key = None     # 释放占位（路径可被后续提交复用）
    db.flush(); return {...}
submission.status = "SCHEDULED"          # 正常路径
submission.path_claim_key = None
db.flush()
```

- 高风险代码 ③——attempt-2 返修（14b7a64 vs 34d15ac，仅 15 行服务改动 + 72 行回归）：

```diff
-    except Exception as exc:  # SceneConfigError → 422（UNKNOWN_SCENE/INVALID_* 等）
-        code = getattr(exc, "code", "INVALID_CONFIG")
-        raise HTTPException(422, f"{code}: {getattr(exc, 'detail', str(exc))}") from exc
+    except SceneConfigError as exc:
+        # 仅客户端配置语义错误转 422；_resolve_selection 内部的 JSONDecodeError/
+        # 注册表加载失败等是服务端故障，必须冒泡 500，不得伪装 422。
+        raise HTTPException(422, f"{exc.code}: {exc.detail}") from exc
```
  （create_submission 与 patch_submission 两处同口径）

## 3. 设计与契约对照

- 设计章节：DESIGN §3.2（提交/绑定/冻结快照/占位不变式）、§7（API 面）、§11.2（purpose-schedule-event/v1）、§9（downgrade 防线）
- 契约项 / 实现位置 / 验证方式：
  - 事件 5 字段（event_id/submission_id/source_id+gen/purpose/scene_code/capability_version/capability_config_hash/effective_config_hash/profile+frozen_at）→ _emit_purpose_events → 协调者逐字段对照 DESIGN §11.2 确认对齐
  - self_built 事件不带 scene（capability 字段 NULL）→ 571-575 行 → 05 消费端按"能力不可用/双保险"处理（交叉审查点）
  - 字段漂移适配（04A 供给侧 → 03A 消费侧唯一转换点）→ scene_capability_read.py → test_ingest_config.py 契约用例
  - 旧入口 100% 兼容（SCENE_INGEST_ENABLED=0 走 legacy）→ bootstrap/source_service → test_scanner_stability.py + 兼容矩阵
  - 占位不变式"PENDING_INPUT 行必持占位、占位必对应可绑定提交"→ §2-② → test_no_residual_pending_system_row_across_generations

## 4. 测试证据

- 命令 + 退出码（协调者独立复跑，wt-03b worktree）：
  - `pytest tests/test_ingest_config.py tests/test_ingest_config_api.py -q` → 25 passed（exit 0）
  - `pytest -q`（全量）→ 664 passed, 10 skipped, 3 failed（3 个 test_devflow 沙箱环境性失败，与改动无关）
  - `ruff format --check` + `ruff check` + `compileall` → 全过
- 关键测试用例：路径抢占 409、幂等冲突 409、版本不匹配 409、两代 bag 同路径登记（无 PENDING 残留/第二代拿新行/用户 POST 不 409）、服务端故障不伪装 422（红绿验证：撤收窄→FAILED，恢复→PASSED）、迁移 upgrade/downgrade（SQLite）
- 手动验证：SQLite 迁移 upgrade/downgrade 2 用例过；**MySQL 8.4 隔离库验证未执行**（原因见 §6）
- 未执行测试及原因：MySQL 8.4 隔离库——协调者 2026-10-08 晚间对该迁移做过隔离库实验，但实验过程因 alembic 版本链污染（曾把 03B 迁移接到 02 迁移之后增量重放）出现矛盾结果（一次 1101 失败、一次成功无 DEFAULT），**未能给出干净的 20261008_02 完整链隔离库证据**，故不声称已验证

## 5. OCR 审查结果

- 发现问题（协调者代跑 34d15ac 7 文件核心 OCR，session fe11996d，7 条）：
  - 3 critical（TEXT server_default 报 1101 ×3 处；BIGINT PK 无 autoincrement 报 1048）
  - 2 high（bind 复用 PENDING 不按 source 过滤；system 行残留 PENDING 持占位）
  - 2 medium（except Exception 过宽 ×2）
- 已修复：2 medium → attempt-2（14b7a64，§2-③）；2 high 经 owner 判定误报不修（依据 §2-② + 回归测试固化）
- 误报说明（附验证方式）：
  - 3 critical：协调者隔离库 alembic upgrade 成功 + general_log 抓真实执行 DDL——`default_purposes_json TEXT NOT NULL`（**无字面量 DEFAULT**，alembic 迁移上下文渲染丢弃了 TEXT server_default）、`id BIGINT NOT NULL AUTO_INCREMENT`、不传 id 插入返回 1。OCR 系按源码表面推断、未跑真实迁移。⚠️ 但该 general_log 抓取自"完整链（01+02）干净库"场景，而 §4 说明的增量重放实验曾见 1101——**两种场景不一致，需强模型裁决（§6-1）**
- 复审（14b7a64，3号自跑，session 34fcc8ed）：Review **partially complete**——仅 2/10 文件（scanner×2）审过 0 findings；**核心 8 文件（迁移/models/api/ingest_service/scene_capability_read/bootstrap/source_service）全部 timed out failed，未覆盖**。这不是干净通过，是覆盖缺口

## 6. 风险与待决策项

- 已知风险：
  - 核心 8 文件 OCR 覆盖缺口（复审超时），attempt-2 的 15 行返修本身未过任何一轮完整 OCR
  - 迁移 20261008_02 缺干净 MySQL 8.4 隔离库证据（见 §4）
  - 与 05 的契约交叉：self_built 事件 capability 字段 NULL，05 用 `idempotency_key=purpose-event:{event_id}` 兜底——双保险是否充分需联审
  - 占位不变式依赖"同事务内推进终态"，若未来有人在 _ensure 与 status 推进之间插入 commit/raise，不变式即破（当前代码无此路径）
- 需强模型裁决的问题（按优先级）：
  1. **迁移 MySQL 8.4 兼容性终裁**：完整链（01→02）干净库 general_log 显示 TEXT 无 DEFAULT、可升级成功；但同迁移增量重放实验曾见 1101。两种结果差异根因是什么？合入前是否需要协调者补一轮干净隔离库验证（建议：需要，裁决通过后执行）
  2. **2 high 误报判定**：_find_pending_submission 不过滤 source，是否真无风险路径？（3号依据：新建 system 行同事务推进终态；强模型可对照 §2-② 验证，或要求 3号 补"bind 中途异常回滚"场景测试）
  3. **OCR 覆盖缺口处置**：核心 8 文件未审。建议强模型直接审查 §2 高风险段 + 指定协调者对 14b7a64 核心文件补一轮错峰 OCR（单实例独占）
- 建议强模型重点关注：§2 三段高风险代码（迁移 DDL、绑定状态机/占位不变式、except 收窄）、self_built 事件 NULL 字段与 05 幂等键的交叉一致性、downgrade 防线与 02 迁移（20261008_01）的链上交互