# OCR 批次账：TASK-09 / attempt-1（2号，坡道真实能力核验 + 生产接线）

## 批次 T09-r1（app 面 2 文件，逐文件单审）

- **task/attempt**：TASK-09 / attempt-1（2号，交付冻结 commit `a60bb81`）
- **base/head**：`0a8ca8a..a60bb81`（单 commit，base=main=origin/main，无漂移；机械核验 rev-parse 双核一致）
- **入选文件（--preview 核实，2026-10-11 21:38）**：
  - `app/scene/slope/vlm.py`（108 行，+15/-2）：DEFAULT_VLM_MODEL 完整路径默认 / max_tokens 256→2048 / enable_thinking chat_template_kwargs 透传 / model 字段可配
  - `app/scene/slope/adapter.py`（307 行，+9/-1）：_default_model_client 接线 3 个 env（SLOPE_VLM_MODEL/MAX_TOKENS/ENABLE_THINKING），fail-closed 语义不变
- **排除**：`tests/test_slope_vlm_wiring.py`（新增 162 行 9 用例，default_path 纯测试口径，独立验证已随交付自测 44 passed 复跑 RC=0）
- **尺寸预检（§3.6）**：两文件均 <500 行、diff 总量 +24/-3，无大文件合批风险；按 cron 化身口径**逐文件单审**（前台 <420s/文件），不组批
- **runner**：`/home/wang/.hermes/cache/scratch/t09-ocr/t09-r1-<file>.py`（fcntl flock 持 `inbox/ocr.lock` + `ocr review -c a60bb81 --audience agent --exclude <另一文件>,tests/*`，workdir `wt-04a-t09`，stdout 直落 log）
- **启动**：2026-10-11 21:38 +08:00（协调者 cron poll 回合，前台串行 2 批）
- **硬截止**：2026-10-11 22:30 +08:00（单文件超时则 §4 resume/降级处理，不整批重来）
- **run_id/session**（逐文件单审，2026-10-11 21:38）：
  - `vlm.py`（108 行）session `20a6cf39-c3ea-40ff-a832-68aa1c788f0d`，44s
  - `adapter.py`（307 行）session `96c83b83-a3f2-45d9-a793-59fa3d71cb89`，95s
  - 日志 `/home/wang/.hermes/cache/scratch/t09-ocr/t09-r1-vlm.log` + `t09-r1-adapter.log`
- **status**：**COMPLETED（2/2 app 文件 0 findings）**
- **result_path**：同上 log（各 `Review complete: 0 finding(s) across 1 selected item(s)`）
- **门禁口径**：无 high/critical → 合入 sanity 全绿 → --no-ff 合入 main `ca8730d`（推 origin）✅

## 收口记录

- 2026-10-11 21:42：T09-r1 逐文件 2 批全收口 0 findings，合入 `ca8730d` 完成，sanity（alembic 单头/ruff/SQLite 44）全绿。TESTER 合入后独立真 MySQL 验证挂 `inbox/TESTER/TASK-09/post-merge-ca8730d-verify-dispatch.md`，PASS 后 09 DONE。