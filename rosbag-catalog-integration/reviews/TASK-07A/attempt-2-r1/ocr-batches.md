# TASK-07A attempt-2-r1 增量 OCR 批次账（协调者串行，ocr v1.12.13，provider vllm-local Qwen3.8-27b）

- 固定快照：base `f94d006`，head `8cc6b80`（B 交付 attempt-2-r1，3 文件 +51/−5）
- 尺寸预检：bags.html 298L、bag-search.css 1373L（>500 独立成批 + `--max-tokens 60000`）、tests 排除=default_path 先例
- 排除：`tests/test_task07a_visibility.py`（default_path，独立验证挂 TESTER）
- 覆盖：2/2 入选文件全部有效收口，0 findings。

| batch_id | 输入 | 运行 | 结果 |
|---|---|---|---|
| T07A-a2r1-bagshtml | bags.html | session `8055d30e`，5m51s，~48.8k tokens | **0 findings**，EXIT=0 |
| T07A-a2r1-css-v1 | bag-search.css | session `6d72a5d7`，420s cron reap（无 manifest 不可 resume，实测 `Error: ... start a new review`） | **FAILED 不算通过**，作废 |
| T07A-a2r1-css-v2 | bag-search.css | session `b105894b`，4m9s，~78.7k tokens | **0 findings**，EXIT=0 |

- 收口时间：2026-10-12 13:56-14:0x +08:00（coord-poll-20261012-133053）
- 门禁裁决：无 high/critical → 合入条件满足（机械核验已全绿，见 decision）。