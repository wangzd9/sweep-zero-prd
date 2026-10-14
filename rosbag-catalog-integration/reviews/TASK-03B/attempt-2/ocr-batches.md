# TASK-03B attempt-2（a8fac99）OCR 批次记录（协调者管理）

## 覆盖基线
- 14b7a64（attempt-2 前版）：批 B（迁移+models）✅0 findings｜批 C（api+适配器）✅0｜批 D（__init__/bootstrap/source）✅0｜
  scanner×2 ✅0｜批 A（ingest_service.py 核心）--resume 断点续审出 3 findings（F1 high 真 bug/F2 medium/F3 low），
  3号全修 → amend 为 a8fac99；批 A 第 2 轮 deadline exceeded（1/21 请求失败，覆盖度声明在回执）。
- a8fac99 增量（14b7a64..a8fac99 = ingest_service.py + tests/test_ingest_config.py，+121/-25）：
  3号自跑 3 轮全 context canceled（30/24min+）——按 skill"同因两次失败升级"规则，
  协调者 13:35 kill 3号自跑，改协调者串行补审。

## 协调者批次
| batch | base..head | 输入 | status | run |
|---|---|---|---|---|
| B1-r1 | 14b7a64..a8fac99 | 2 文件增量 | FAILED（12m36s，input 仅 522 token 即 planning 超时=当时 vLLM 4 并发+4 waiting 拥塞，非内容问题） | proc_df52a683ea17，ocr-a8fac99-incr.log，session 9da90cab |
| B1-r2 | 14b7a64..a8fac99 | 同上（串行独占重跑） | FAILED（17m05s；根因=批次范围错：--from/--to 把 a8fac99 当新 commit 全量审 10 文件，611k input 撞上 vLLM 4+3 拥塞，planning 超时。真实增量仅 2 文件——amend 不改内容文件） | proc_b08d37d612ea，session 0f092c77 |
| B1-r3 | 14b7a64..a8fac99 | 同上（--exclude 8 个未变文件） | FAILED（19m15s，18 tool calls/17k output 后 canceled；单文件 248k input 的 planning 撞 90s 轮超时。session 5718fea4 可 --resume） | proc_396af3c963e4，ocr-a8fac99-incr-b1r3.log |

## B1 三连失败升级（14:5x，skill"同因两次失败不无限重试"）
- 根因（非内容）：① vLLM 被 claude-mem worker(37700)+chroma-mcp 等 8 个常驻 ESTAB 连接长期占 4 并发（r1 时 input 仅 522 token 即超时）；② 单文件 248k input 的 planning 请求在拥塞下必然撞轮超时；③ 3号 F2 小返修将改同一文件，现审=审旧代码，返修后须重审（skill：新 head 重审受影响批次）。
- **策略**：B1 挂起 → 03B 增量 OCR 并入 F2 小返修后的最终态一次性终审（避免重复消耗）；OCR 串行槽切给 B2(06A)。
- 用户已知晓：claude-mem 常驻流量是今日 OCR 4 次复发的共同根因，OCR 窗口期可临时 pkill worker（用户自行决定，不擅动）。

## F2 隔离库并发实测（2026-10-09 14:0x，协调者，证据 f2-isolation-evidence.log）
- 环境：mysql:8.4 + python:3.10-slim 同 docker network，pymysql 1.1.1，metadata 建 3 表
  （ingest_profile/ingest_submission/api_idempotency），双独立会话 Barrier 同拍竞争 patch_submission。
- 结果：守卫生效（恰好 1 OK，row_version 1→2，数据一致性无破口），
  **但失败方抛 StaleDataError（500）而非 409——rowcount==0 分支不可达**（synchronize_session 默认
  策略先抛异常），与 DESIGN/回执承诺的"rowcount=0→409"不符。
- 处置：回派 3号小返修（inbox/3号/TASK-03B/attempt-2-f2-rework.md，~5 行 + 隔离库复测 + monkeypatch 回归），
  不算新一轮 OCR 意见；B1-r2 收口后一起裁决合入。
- 环境坑记录：SQLAlchemy pymysql 方言吞 connect_args 的 ssl（1045 假象），用 creator 直连绕开；
  容器内 requirements.txt 装的 sqlalchemy 旧到 _ordered_columns 缺失，建表走 metadata.create_all。

## 待办
- B1-r2 收口 + 3号 F2 小返修交付 → 03B 合入 decision（合入前再独立复跑全量）
- 批次严格串行：B1 结束前不起 06A/05 批次
