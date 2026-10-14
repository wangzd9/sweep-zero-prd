# TASK-05 强模型审查请求（attempt-1，开发中）

> 协调者生成，供强模型定向审查。⚠️ 本任务**尚未 commit**——审查对象是 main worktree
> （/home/wang/work/rosbag-catalog）的在途未提交改动（8 改 + 3 新增，+188/-19 + 新文件），
> base=main eaf632a。1号开发中，本文档是中期快照，最终审查以 1号 报 REVIEW_PENDING 的 commit 为准；
> 强模型本轮意见可作为返修输入提前给到 1号，减少一轮往返。
> 测试证据为协调者对 worktree 当前态的实测（命令+退出码见 §4），非 1号 自报。

## 1. 任务卡摘要

- 任务 ID：TASK-05 ｜ 状态：🔧 开发中（未 commit）｜ owner：1号会话
- 交付行为：用途事件消费（03B outbox）、场景运行 API（POST/GET /api/v1/scene-analysis-runs）、pipeline_type=SCENE_SLICE 独立队列/状态面、执行面/步骤/租约
- 验收范围：REQ-01、03、06、08、10 / AC-01、03、06、08、10
- 依赖：TASK-02 ✅、TASK-03A ✅、TASK-04A ✅（已合入）；TASK-03B 🔁（事件生产方，**未合入**——05 已做表不存在时 poll 恒空的兼容，见 §2-③）
- 当前进度：状态机/队列/消费/取消/租约骨架已在工作区，未 commit、未报回执

## 2. 代码变更摘要

- Base：eaf632a（main）→ Output：工作区未提交（1号 commit 后更新本段）
- 变更文件：
  - 新增 app/api/scene_analysis_runs.py（52）、app/services/scene_schedule_consumer.py（215）、app/services/scene_slice_service.py（566）
  - 修改 app/domain/enums.py（+13：SCENE_SLICE_QUEUE + 6 场景状态 + SCENE_EXEC_HOST）、app/domain/transitions.py（+33：场景状态面转移表）、app/orchestrator.py（+55：Scene 执行槽 + _consume_purpose_events 主循环）、app/services/pipeline_service.py（+83）、app/config.py、app/api/__init__.py、app/schemas/{__init__,requests}.py
- 高风险代码 ①——场景状态面（transitions.py，独立于 Phase0→Phase1 链）：

```python
SCENE_TERMINAL_STATES = {SCENE_DONE, SCENE_PARTIAL_FAILED, SCENE_FAILED, CANCELLED}
STATUS_TRANSITIONS:
  SCENE_SLICE_QUEUE: {SCENE_RUNNING, SCENE_FAILED, CANCELLED, SCENE_SLICE_QUEUE}
    # SCENE_FAILED = 事件消费预检失败（能力不可用）：排队态快速失败通道
  # 运行中取消经 CANCELLING→确认子进程停写→CANCELLED（释放租约）；停写失败→SCENE_FAILED
```

- 高风险代码 ②——事件消费幂等（scene_schedule_consumer.py）：

```python
# 幂等身份（DESIGN §11.2）：同一 (source_id, source_generation, purpose, scene_code,
# capability_config_hash) 只建一次运行
spec = SceneRunCreate(..., idempotency_key=f"purpose-event:{event_id}" if event_id else None)
run, created = create_scene_run(db, spec)
# 契约违规防护：scene 事件缺 capability_version/config_hash → CONTRACT_VIOLATION 记错不建 run
# 能力不可用：仅对新建 run 快速失败（复用既有 run 时不改写其快照/终态，幂等重放无副作用）
# mark_event_consumed: UPDATE ... WHERE event_id=:eid（outbox PENDING→CONSUMED）
```

- 高风险代码 ③——对 03B 未合入的兼容（poll_outbox_events 裸 SQL）：

```python
if OUTBOX_TABLE not in sa_inspect(db).get_table_names():
    return []   # 03B 表不存在时 poll 恒空，无副作用
rows = db.execute(text(f"SELECT {columns} FROM {OUTBOX_TABLE} WHERE status='PENDING' ORDER BY id LIMIT :lim"), ...)
```
  ⚠️ 这是 05 对 03B 的**唯一数据耦合点**：裸 SQL 直接读 purpose_schedule_event，字段投影硬编码 _EVENT_FIELDS。03B 迁移未合入/字段变更时无编译期保护。

- 高风险代码 ④——执行面与取消/租约（scene_slice_service.py）：SCENE_EXEC_HOST 资源槽（P0 容量 1，忙时释放回队列不跨队列阻塞）；cancel_scene_run 走 CANCELLING→停写确认→释放租约；finish/update 全部 require_valid_task_lease 带租约+attempt 语义；单轮消费故障只记录不退出主循环，事件保持 PENDING 下轮重放

## 3. 设计与契约对照

- 设计章节：DESIGN §5（场景状态面）、§6（执行面/资源槽）、§11.2（purpose-schedule-event/v1 消费规则）、§11.3（Web 请求只建/查，长任务走队列）
- 契约项 / 实现位置 / 验证方式：
  - 事件消费幂等（同身份只建一次 run）→ scene_schedule_consumer._consume_one → 待 1号 commit 后回归（协调者将代跑 OCR + 复测）
  - self_built 用途事件不带 scene 字段、不误接 Phase0 默认链 → consumer 按 purpose != SCENE_SLICE dropped + 契约字段校验
  - 排队取消直接 CANCELLED、运行取消经 CANCELLING 停写确认 → transitions + cancel_scene_run
  - 领取任务失败补偿 → orchestrator._mark_dispatch_failed（场景 run 走 SCENE_FAILED 而非 FAILED）
  - 状态不确定先对账再重试 → finish/update 带租约校验路径
- 待确认：05 与 03B 的字段契约以 purpose-schedule-event/v1（DESIGN §11.2）为准，03B 生产侧已 5 字段对齐；05 消费侧 _EVENT_FIELDS 投影需与 03B 最终合入版逐字段核对（**交叉审查点**）

## 4. 测试证据

- 命令 + 退出码（协调者对 worktree 当前态实测）：
  - 1号 未报回执，commit 未产生 → **无 1号 自报的完整测试记录**（本段为协调者中期快照）
  - worktree 全量 `pytest -q`：未跑（工作区含 1号 在途 + 03B 未合入，全量结果不代表交付态；1号 commit 后协调者将独立复跑并补记）
- 关键测试用例（1号 应已写、commit 后核对）：同父不同用途不复用错 run、重复事件幂等、排队/运行两条取消路径、能力不可用快速失败、03B 表缺失时 poll 恒空
- 未执行测试及原因：全量回归（等待 commit）、MySQL 隔离库（05 若新增迁移，当前 diff 未见 alembic 改动——场景运行复用 pipeline_run 既有表 + pipeline_type 字段，需 1号 确认是否真无迁移；若有则合入前隔离库验证）

## 5. OCR 审查结果

- 未开始：1号 尚未 commit，无可审对象。按流程 1号 报 REVIEW_PENDING 后由协调者代跑（错峰独占单实例，避免并发挤单挂死——本次专项已 3 次遇到）
- 本轮强模型审查即作为 commit 前的定向预审：强模型对 §2 四段高风险代码的意见直接转 1号 返修

## 6. 风险与待决策项

- 已知风险：
  - **未 commit**：worktree 在途改动与 04B 已合入代码共存，1号 若误操作（如 git stash/checkout）有丢失风险；且 1号 在主工作区开发（历史教训：曾误删 .venv），commit 时协调者将核对 diff 范围
  - **裸 SQL 耦合**（§2-③）：05 消费 03B 表绕过 ORM/迁移保护，03B 未合入 main，两者合入顺序与字段一致性是主要风险
  - 场景 run 复用 pipeline_run 表（pipeline_type 区分）：需确认既有 Pipeline 查询/清理逻辑是否都按 pipeline_type 隔离，避免场景 run 被 Phase0 清理/重试逻辑误碰
- 需强模型裁决的问题（按优先级）：
  1. **05↔03B 合入顺序**：05 兼容了表缺失（poll 恒空），是否可以先合 05 再合 03B？还是必须 03B 先合入、05 在其上验证消费端到端？（建议：03B 先合入，05 在其上做真实 outbox 消费回归）
  2. **幂等身份充分性**：`purpose-event:{event_id}` 作为 idempotency_key——event_id 是 03B 每次 emit 的 uuid4（非确定性）。DESIGN §11.2 的幂等规则是"同 (source,gen,purpose,scene_code,capability_config_hash) 只建一次"，若 03B 重放 emit 出新 event_id，05 仅靠 event_id 幂等会重复建 run。请强模型对照 consumer 代码裁决是否还有第二层按业务身份的查重复用（_consume_one 中 create_scene_run 前的既有 run 查询是否覆盖）
  3. **SCENE_EXEC_HOST 容量 1 的排空语义**：忙时释放 claim 回队列，下一轮 orchestrator 重领——与现有 Phase0 宿主机租约的交互是否可能双占（同一 bag 既有 Phase0 任务又有场景任务）
- 建议强模型重点关注：§2-① 状态面转移完整性（取消/停写/快速失败三分支）、§2-② 幂等双保险是否真双、§2-③ 裸 SQL 的字段漂移风险、pipeline_type 隔离对既有清理/重试逻辑的侵入面