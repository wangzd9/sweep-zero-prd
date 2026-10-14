# 强模型定向审查包（rosbag-catalog 场景处理专项）

生成：协调者（飞书「后端功能开发」会话），2026-10-09。
用途：把 P0 高风险任务交给强模型定向审查，控制 token 消耗、提高审查质量。
**无需各任务 owner 单独提交**——本包已含全部审查材料。

## 文件清单

| 文件 | 内容 | 任务状态 | 优先级 |
|---|---|---|---|
| `01-TASK-04B-review.md` | 坡道适配/CDR/时间映射 | ✅ 已合入 main eaf632a | P0 高 |
| `02-TASK-03B-review.md` | 接收集成/配置持久化/用途事件 outbox | 🔁 未合入（worktree 14b7a64） | P0 高 |
| `03-TASK-05-review.md` | 用途事件消费/场景运行/队列/租约 | 🔧 未 commit（工作区中期快照） | P0 高 |
| `REF-DESIGN.md` | 设计契约（审查时需对照的权威来源） | — | 参考 |
| `REF-TODO.md` | 任务状态与依赖表 | — | 参考 |

建议审查顺序：`02-TASK-03B → 01-TASK-04B → 03-TASK-05`（03B 有未裁决的 MySQL 迁移矛盾 + OCR 覆盖缺口，风险最高）。

## 每份审查文档的结构（六段，强模型可直接审）

1. 任务卡摘要（ID/状态/owner/验收范围/依赖/进度）
2. 代码变更摘要（base→output、文件清单、高风险 diff 已截断 <500 行，只贴迁移 DDL/状态机/发布/时间映射等关键段）
3. 设计与契约对照（对应 DESIGN 章节、契约项、实现位置、验证方式）
4. 测试证据（真实命令+退出码、关键用例、手动验证、未执行项及原因）
5. OCR 审查结果（问题清单、已修复、误报说明附验证方式、待裁决）
6. 风险与待决策项（已知风险、需强模型裁决的问题、建议关注重点）

## 给强模型的定向指令（每份文档 §6 已列，重点复述）

**02-TASK-03B**（3 个裁决项）：
- 迁移 `20261008_02` MySQL 8.4 兼容性终裁：完整链（01→02）干净库 general_log 显示 TEXT 无字面量 DEFAULT、BIGINT 有 AUTO_INCREMENT、可升级成功；但同迁移"增量重放"实验曾见 error 1101。两种结果差异根因？合入前是否需补干净隔离库验证？
- 2 个 high（OCR 主张 bind 复用 PENDING 不按 source 过滤 / system 行残留持占位）经 owner 判误报——请对照文档 §2 的绑定状态机代码验证判定是否成立。
- 核心 8 文件 OCR 覆盖缺口（复审超时未审）如何处置。

**01-TASK-04B**（关注项）：
- CDR 封装头检测（`_encap_candidates`）误判边界：裸 CDR 回退是否可能与真实字段冲突；`_MAX_VALID_SEC=10^10` 区分充分性。
- pos 偏移修复后跨调用方（bag_io 抽帧→time_map→cdr）端到端一致性。

**03-TASK-05**（3 个裁决项）：
- 幂等是否真"双保险"：event_id 是 03B 每次 emit 的 uuid4（非确定性），仅靠 `idempotency_key=purpose-event:{event_id}`，若 03B 重放 emit 出新 event_id，05 会重复建 run。请对照 consumer 代码判断 `create_scene_run` 前是否还有按业务身份 (source,gen,purpose,scene_code,capability_config_hash) 的查重复用。
- 05↔03B 合入顺序：可先合 05（已兼容表缺失 poll 恒空）还是必须 03B 先合入再在 05 上做真实 outbox 消费回归？
- `SCENE_EXEC_HOST`（容量 1）忙时释放回队列重领，与 Phase0 宿主机租约是否可能双占同一 bag。

## 意见回执格式（强模型输出后，协调者按此逐条落实）

对每条意见请给出：
- **任务/文档编号 + §号**
- **severity**（critical/high/medium/low）
- **判定**（确认是 bug / 误报 / 需澄清）
- **依据**（引用代码行/DESIGN 章节/实验结果）
- **建议处置**（返修 patch 方向 / 补测试 / 补隔离库验证 / 可接受留痕）

协调者拿到回执后会：对照当前 HEAD 逐条核实（不盲改）、critical/high 必须给出"当前仍成立/已修复/误报"判定、返修回派对应 owner（有界 2 轮）、更新 TODO/HANDOFF/receipts。

## 敏感信息声明

本包不含密码/Token/真实环境配置；代码 diff 仅贴关键段（<500 行）；测试证据均为真实命令输出，未执行项已标注原因，无伪造退出码。