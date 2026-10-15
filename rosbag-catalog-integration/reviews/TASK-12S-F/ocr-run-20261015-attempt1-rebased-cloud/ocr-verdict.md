# TASK-12S-F 云端 OCR 初审失败裁决（协调者，2026-10-15 16:2x +08:00）

## 运行身份

- run `77db648b45454c55b2e3577bd5dc251f`，目录 `reviews/TASK-12S-F/ocr-run-20261015-attempt1-rebased-cloud`
- unit `coordinator-ocr-77db648b45454c55b2e3577bd5dc251f.service`
- 范围：base `1e9c7de`（E attempt-2 冻结 head）→ head `96afc43`（B rebase 后 F 冻结 head）
- 7 app 文件逐文件一批（7 批），retry_depth=0 新身份（`review_identity` 前缀 `e547582cc7941312`）
- 触发：用户 2026-10-15 16:1x 指令「2」（OCR 改用协调者当前模型服务，不调本地大模型）
- 提交 16:20:40、b01 起 16:21:05Z（08:21:05Z 终），b01 duration 26.14s

## 终态与根因（本轮独立核）

- **state=REVIEW_INCOMPLETE**，gate `NOT_EVALUATED`，`results` = `INSUFFICIENT_EVIDENCE`。
- b01 `REVIEW_INCOMPLETE` rc=1，coverage `selected=1/completed=0/failed=1`，`coverage_complete=false`。
- b01 实际路由 = `hermes-sub2api` / `deepseek-v4.1-flash` / `https://sub.vankit.top/v1`（云端生效，非本地）。
- **根因 = responses 协议不兼容，非负载、非超时、非代码问题**：
  `item_error_messages`: `LLM completion error: expected destination type of 'string' or '[]byte' for responses with content-type 'text/event-stream' that is not 'application/json'`（plan_task 1 次 + main_task 1 次）。
  即 OCR 的 Go 客户端按 `application/json` 解析非流式响应，而 sub2api 对**非流式**请求（`stream:false`）仍回 `content-type: text/event-stream`。

## 独立端点复现（协调者实测，脱敏）

- `POST https://sub.vankit.top/v1/responses` `stream:false` → HTTP 200 但 `content-type: text/event-stream`，体为单条 JSON（无 `data:` 前缀、无 event 分帧）——**协议声明与实际分帧不一致**。
- `POST https://sub.vankit.top/v1/chat/completions` `stream:false` → 同样 `text/event-stream`（该中转站统一行为）。
- 对比 `POST https://x-coding.net/v1/responses` `stream:false` → `content-type: application/json; charset=utf-8`，体为标准 Response 对象——**协议正确**。
- `POST https://sub.numenume.site/v1/chat/completions` → HTTP 502（该端点当前不可用）。

## 关键旁证：用户侧 fixture 已验证

用户 Codex 会话目录 `~/.opencodereview/sessions/home-wang-work-.local-hermes-model-routing-20261015-cloud-ocr-fixture/` 两个 session（15:46、16:00）**provider 均为 `hermes-xcoding` / model `gpt-6.1-sol`**：
- 16:00 那次 `price.py` **coverage completed 1/1，elapsed 43057ms，rc=0**——云端 OCR 走 x-coding/gpt-6.1-sol 可通。
- 15:46 那次 timeout（当时 `OCR_LLM_TIMEOUT` 未调）。注意该 fixture 第一次跑的是 streaming 会话（b01.log 显示 `x-port`.

## 裁决

1. **不判通过**：零 findings、零覆盖，b02–b07 按停链规则未启动，service 已 `inactive`、无在途进程。门禁维持关闭。
2. **sub2api（deepseek-v4.1-flash / deepseek-v4-pro）不可用于 OCR**：其 responses 与 chat_completions 两条协议对非流式请求均返回 `text/event-stream`，OCR Go 客户端无法解析。**这是端点能力缺陷，不是模型能力问题，也不是负载问题。**
3. **可用云端组合（实测）**：`hermes-xcoding` / `gpt-6.1-sol`（protocol=openai-responses，正确返回 application/json，用户 fixture 已 coverage 1/1）。
4. **本 run 不补审**：同身份最多初审加一次补审，且本轮失败属端点协议能力问题——换端点即为换配置身份，须新建 run 而非 `--reuse-run`。
5. **本地 vllm 现状**：`running=4 / waiting=13`（16:26 实测），仍满载；沿用本地仍有再撞 3900s 单批硬截止的风险（已两次）。

## 下一步（待用户拍板）

- 方案甲：OCR 选择器（`ocr_model_route.py`）与 `~/.opencodereview/config.json` 的 sub2api 条目改指 `hermes-xcoding`/`gpt-6.1-sol`，新建 run 重提（用户 fixture 已证可通）。
- 方案乙：等本地 vllm 空窗（`running=0/waiting=0`）后同入口重提，走本地。
- 方案丙：维持 F 门禁关闭，暂不补审。
