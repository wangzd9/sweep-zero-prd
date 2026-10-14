# DECISION：16C-A OCR 补审（reuse-run，等 VLM 队列缓解）

- 记录时间：2026-10-14 15:32 +08:00（协调者）
- 事实：16C-A 初 run（14:09 起）于 15:09 前后触 HARD_DEADLINE（60min 上限）：`bag_search_service.py` 审完（review_item_done，1 条 dead-code finding：`data_kind_case` 无调用者）；`scene_result_query.py` plan 请求排队 166s 被 VLM `context canceled` → review_item_failed，coverage 不完整，**不得判 AWAITING_DECISION**。
- 根因：VLM 单实例满载（15:31 实测 running=4/waiting=3），排队超时取消。非代码/参数问题。
- 授权：同一审查身份（TASK-16C-A/attempt-1）**最多初审+一次补审**；本次为唯一补审机会，再失败即 RETRY_LIMIT 升级用户，不得换 task 名/另建目录重跑。
- 下一动作（巡检接续，每 5min）：
  1. 查 VLM 队列：`running+waiting <= 2` 才起跑（满载补审=浪费唯一机会）。
  2. 起跑命令（固定入口 reuse）：
     `ocr_runtime.py prepare --project $PROJ --repo /home/wang/.local/state/rosbag-scene/wt-01-t16ca --background-file reviews/TASK-16C-A/ocr-run-20261014/background.md --output reviews/TASK-16C-A/ocr-run-20261014/retry1 --base bd0db1d2a0fc293cb4562e2079e741739bacb0de --head ff2a005 --task TASK-16C-A --attempt attempt-1 --authorization "inbox/control/V04-UI-RESUME-20261014.md" --batches-file reviews/TASK-16C-A/ocr-run-20261014/batches.json --reuse-run reviews/TASK-16C-A/ocr-run-20261014/run --retry-reason "scene_result_query.py plan 请求被 VLM 队列过载 context canceled；bag_search_service.py 已审完将复用其 finding，不重跑"` 然后 `start --run .../retry1`
     注：若 reuse 机制语义为整批重跑（含已审完文件），按 ocr-runtime.md 口径执行并核对 manifest 去重，不双计。
  3. 收口后逐条裁决（含初 run 的 dead-code finding：`data_kind_case` 是否随 C5/C6 迁移确属死代码→若是则 CORRECTION-维护面最小返修或确认无害记录）。
  4. A 补审收口 → 16C-B 叶 start（已 PREPARED，业务面仅 bags.html）。
- 期间 16C 门禁保持关闭（不裁决、不合入）；TESTER 16D 独立验证继续，不受影响。