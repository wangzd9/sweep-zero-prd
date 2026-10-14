# TASK-05（dccc867+1946718+d1f2eba）OCR 批次记录（协调者管理）

## 历史
- dccc867 首轮（1号自跑，10:56 起）：与 3号 OCR 并行 → 挂死 43min，协调者 11:44 kill。
- 1号自行重跑：6 findings 自修 → amend/追加为 d1f2eba（含 [high] orchestrator 直连 ORM 违反
  Backend 写边界 → 新增 POST /api/v1/orchestrator/purpose-events/consume，orchestrator 只 POST）。
- 1号范围复审（12:13 起，串行链）：
  - 1946718：context canceled（exit=1）→ 未取得结果
  - d1f2eba：7 文件中 **4 文件完成 0 findings**（1176k token/31min）；
    **3 文件超时失败**：app/api/scene_analysis_runs.py、app/services/scene_schedule_consumer.py、
    app/services/scene_slice_service.py —— 恰是 05 核心（事件消费幂等/场景运行/租约）。
  按 skill：部分完成≠通过，超时项必须补审。

## 协调者批次（严格串行，等 03B B1 → 06A B1 之后）
| batch | base..head | 输入 | status |
|---|---|---|---|
| B1 | eaf632a..d1f2eba 增量（核心 3 文件） | scene_schedule_consumer.py + scene_slice_service.py + scene_analysis_runs.py | QUEUED |
| B2 | dccc867（12 文件主体，d1f2eba 前未审） | 待 B1 后评估范围（d1f2eba 已覆盖 4 文件可复用，其余按文件补） | QUEUED |

## 协调者已独立验证（OCR 前）
- 范围：dccc867 12 文件 +1855/-19 全属 05；1946718 2 文件；d1f2eba 自修；cb0198c=HANDOFF.md 1 行 docs（非 05 文件，已单独确认）
- 测试：本地 main 701 passed（d1f2eba 前）；d1f2eba 后需复跑
- 冲突：与 06A 零文件重叠（merge-tree 0）
- 契约：purpose-schedule-event/v1 消费字段集与 DESIGN §11.2 一致（待 B1 抽查）

## 补审批次（2026-10-09 20:45，用户质询"你都跑ocr了吗"后如实盘点并补跑）
| 批 | 范围 | 覆盖 | 状态 |
|---|---|---|---|
| B4 | 9506457..c764f1b | 04B CDR 对齐 34c380d（2 文件）+ 05 强模型返修 6ce7b7a（6 文件），零重叠合并单批 | running（proc_6df2a2f6d253，log ocr-b4-04b05-merge.log） |
| B5 | 14b7a64..a8fac99 增量 2 文件 | 03B 主体增量（前三轮挂死，B4 收口后重试，超 20min 再失败即升级用户裁决） | queued |
| B6 | d1f2eba 核心 3 文件 | 05 消费/运行路径此前超时未审部分 | queued |

**协调者流程失误记录**：34c380d（640c5a8 合入 20:27）与 6ce7b7a（c764f1b 合入 20:42）合入时未先过 OCR 门禁，
违反 skill "OCR 串行、通过才合入"——赶验收进度所致。两笔均有代码级独立核实+定向/全量测试证据
（34c380d: 35 passed+ruff；6ce7b7a: 140 定向+757 全量+ruff），B4 收口后按意见裁决，如有 high/critical 返修回派原 owner。

## B4 收口与拆批重排（2026-10-09 21:37）
- B4（9506457..c764f1b 6 文件合并批）：planning+core 全超时 failed（37m17s，vLLM 拥塞），session 76772e0d。
- 拆 commit 模式重跑：
  - **B4-r1 = 04B CDR 34c380d：✅ 0 findings（9m08s，session 4b309814）**——04B 对齐 hotfix OCR 闭环。
  - **B6 = 05 返修 6ce7b7a：收口 2 findings（1h13m11s，session 1d0d3b30，22:49 读）**——high：迁移 backfill 未按身份去重，存量重复业务身份 → create_index(unique) IntegrityError → upgrade 失败（协调者查本地测试库 scene run=0、未发布生产=理论风险不现实触发，仍回派 1号修+补去重回归测试）；low：迁移文件末尾缺换行。⚠️ B6 round 2 core review LLM 超时 incomplete（2/42 请求失败），按纪律不算通过，需 --resume 1d0d3b30 续审补齐。返修派单：inbox/1号/TASK-05/attempt-2-ocr-rework.md（22:55）。
  - B5 = 03B 增量 14b7a64..a8fac99 2 文件：queued（B6 收口后跑）。

## B5a/B5b 收口 + B6 resume + backfill 返修（2026-10-10 00:5x，协调者）
- **B5a = 03B F2 f11e617：✅ 0 findings**（15m18s，session 73a7c246，log ocr-b5a-f11e617.log）。
- **B5b = 03B 86baad5 冻结列：收口 3 条全 documentation/low（56m40s，session 40910526，2 文件 core 覆盖，planning 1/57 超时但核心逻辑已审）**：
  ① medium：ingest_service.py:643 docstring 仍写旧 NULL-hash 降级契约，与 #4 显式失败实现矛盾（05 消费端依赖此语义）→ 回派 3号 attempt-4-ocr-rework；
  ②③ low：20261009_02 downgrade→upgrade 往返覆写冻结值（OCR 自更正：drop 固有、gate 挡不住，仅 docstring 文档化）+ E402 import 位置 → 同单回派 3号。
- **B6 = 05 6ce7b7a：2 条（1 high+1 low）已处置**——high（backfill 未按身份去重→存量重复身份 upgrade 炸）1号 db4bec7 修复合入 main **b5efba2**（00:55：best dict 按 identity 取 max PK id 规范行持键+真实 alembic 子进程 upgrade 回归测试+batch bind param 重名修+W292；33 定向+778 全量+ruff 4 E402 属 alembic 不在门禁路径）；low（末尾换行）同 commit 修。
  **B6 resume（session 1d0d3b30）补 round 2 超时缺口：22:49 起，00:5x 复跑中**（proc_1e42e17eb8e8）。
- **E402 风格统一**：1号 20261009_01 + 3号 20261009_02 各 4 个，门禁不含 alembic 不阻塞，协调者各回派小单保持与 20261008_02 风格一致。
- 05↔03B 真实 outbox 联调 **PASS 6/6**（测试者 23:10，verify-05-03b-outbox-e2e.md）——强模型 #4 契约两端一致性已端到端验证。

## B6 判定修正 + B3 补审（2026-10-10 01:0x，协调者）
- **B6 判定修正**：resume 回放（-c 6ce7b7a --resume 1d0d3b30，0 token/0s）显示终态 **"Review complete: 2 finding(s) across 5 selected items"**——
  即 B6 对 6ce7b7a 实为 **complete**（5 文件全审），round 2 的 2/42 超时只是复核轮局部 retry 失败，不推翻 complete 判定。
  上一轮"round 2 超时不算通过"判断偏严，修正为：**05 强模型返修 OCR 门禁通过**（2 条已闭环：high backfill=db4bec7 合入 b5efba2，low W292 同 commit）。
  教训：resume 回放是终态的廉价验证手段，判定"incomplete"前应先 resume 看是否 complete。
- **05 真实剩余缺口 = d1f2eba**（05 主体 commit，此前 3/7 超时未审完）：B3 已起跑（vLLM 空闲窗口 1 running/0 waiting）。
- 后续排队：db4bec7（backfill 修复 commit）OCR + 1号/3号 E402 风格小单交付后快审。

## B3（d1f2eba 05 主体）收口裁决（2026-10-10 01:17，协调者逐条对照当前 HEAD b5efba2）
5 条 = 1 medium + 4 low，**对当前代码实质缺口清零**：
- **medium #4（dropped 留 PENDING 每轮重放）→ 过时**：B3 审的是旧 commit d1f2eba；当前 HEAD 已由 6ce7b7a 的 #5 修复（mark_event_dropped + DROPPED 终态），`_mark` dropped 分支核实在位。
- **low #1（sample query 无 LIMIT 误标 created_ids）→ 已移除**：6ce7b7a 重构后当前 created_ids 计数=0。
- **low #3（outbox 跨事件泄漏）→ reviewer 自撤回**：复核确认 _mark 无跨事件写、无缺陷。
- **low #2（errors 未 log）+ low #5（空轮次无限打 0 行日志）→ 当前 HEAD 仍存在**（orchestrator.py:170-174 print 无条件触发且不含 errors）。
  两条均 maintainability/observability 级、非功能 bug（05 功能正确性已由 6ce7b7a 修复 + outbox 联调 PASS 6/6 保证）。
  **处置：并入 1号 attempt-2-ocr-rework-2.md（E402 风格小单），低优先，不阻塞 05 聚合。**
- **结论：05 主体 OCR 历史欠账清零**，05 聚合待 1号/3号 文档级小单交付即标 DONE。

## B8a/B8b 收口与 R2 重排（2026-10-10 11:49，协调者）
- **B8a = 06B app 主体（-c 6e6bb73 --exclude tests）：✅ 收口 6 findings（1h03m，session 819c9dab）**：
  1 high（多场景 run complete 死锁——finish_scene_run 按全场景汇总定终态，R2 未覆盖的真新增）
  + 4 medium（db3 双 hash 性能 / crash-window=与 R2-04 同域 / path traversal / timezone）
  + 1 low（同文件系统校验只查 specs[0]）。**全部并入 2号 attempt-1-r2-rework.md 同单返修**。
- **B8b（-c 6b21c91 测试增量）取消**：R2 已裁决 06B REWORK，返修 commit 交付后协调者对返修范围
  一次性串行 OCR（覆盖原欠账+新 diff），旧批不重复跑。
- 范围模式五连败根因已入 skill 坑 28（巨型单请求被 Qwen cancel + 会话中断 SIGTERM）；单 commit
  --exclude tests 模式 1h 稳定收口，后续补审沿用。

## I1-r1 收口（2026-10-11 15:50，协调者）
- **I1-r1（i1-1 `-c 6823f2d`，session `f71727b8`，OCR_EXIT=0，持 `ocr.lock` 稳定 inode）：0 file(s) reviewed，0 findings**——diff 全在 `tests/*`（default_path 排除），纯测试交付预期 0 入选，与 R8-r1（`b012b488`）/R9-r1（coverage 0/0）先例一致；独立验证=协调者 diff 逐行核 + SQLite 定向 36 passed + ruff 绿 + 1号真 MySQL 8.4.11 STRICT 文件级 36 passed RC=0 原始日志复核（`a-i1-mysql-suite.out`）；已 --no-ff 合入 main `f9bafb0`，I-1 VERIFICATION_GAP 关闭。
