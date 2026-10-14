# T10D1 OCR 批次账（t10-defect1-source-ready `1b92ce6`）

## T10D1-r1（2026-10-12 00:30:23 +0800 起跑，IN_FLIGHT）
- 目标：commit `1b92ce6`（`wt-01-t10def1`，base `ca8730d`，2 文件：`app/services/source_service.py` +14/-1 + `tests/test_t10def1_source_ready.py` 新增 208 行）
- §3.6 尺寸预检：2 文件均 <500 行（app 文件 diff 15 行 / 测试 208 行），单批，无需拆组
- 命令：`ocr review -c 1b92ce6 --format json --audience agent`（worktree `wt-01-t10def1`，session_id 待起跑落定）
- 进程身份：pid 3110450（后台 tracked proc_19727fe6e90d）
- 输出：`~/.hermes/cache/scratch/ocr-t10d1-r1.json`（+ `.err`/`.done`）
- 硬截止：约 15 分钟（cron 单轮时限口径）；超时/空输出/缺工具=不算通过，按 §4 监控
- 收口口径：无 high/critical → --no-ff 合入 main（推 origin）+ 合入后 sanity（alembic 单头/ruff/SQLite 定向 5）；有 high/critical → 回派 1号最小返修
## T10D1-r1（00:30:23 起跑 → **FAILED 重跑**）
- 进程 pid 3110450 于 00:30:51 退出码 1、`ocr-t10d1-r1.json` 0 字节空输出、stderr 空=按协议**不算通过**；前批 owner 会话已死（ps 独立核），A 侧 00:35 事件 `a-t10def1-attempt1-ocr-t10d1-r1-exit1-empty-output-20261012` 如实上报。

## T10D1-r1-rerun（2026-10-12 00:38 前台重跑，**COMPLETE 0 findings**）
- 目标：commit `1b92ce6`（`wt-01-t10def1`，base `ca8730d`）；§3.6 尺寸预检同前批（1 文件入选 <500 行，测试 default_path 排除=先例口径）
- 失败诊断（重跑前实测）：18002 LLM 端点 HTTP 200 可达、`ocr review -c 1b92ce6 --preview` 文件集正确（1 入选/1 排除）→ 前批空输出属进程身份层失败（tracked proc 宿主 cron 会话结束即退），非 LLM/非 diff 面问题
- 命令：`ocr review -c 1b92ce6 --format json --audience agent`（前台 222s 收口）
- 结果：**status=complete，0 finding(s)，1 file reviewed**（`app/services/source_service.py`），session `15516784-a684-4061-9520-8de6788df5a6`，工具调用 15 次 0 失败，elapsed 3m43s
- 输出：`~/.hermes/cache/scratch/ocr-t10d1-r1-rerun.json`（+ .done OCR_EXIT=0）
- 收口：无 high/critical → **--no-ff 合入 main `277e40f`（00:4x 推 origin ca8730d..277e40f）**
