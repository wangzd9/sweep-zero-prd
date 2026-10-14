# OCR 批次账：TASK-08 / T08-C1C2 t08c-1（2号 `bf48a45`）

## 批次 C1C2-r1

- **task/attempt**：TASK-08 / T08-C1C2 t08c-1（2号 attempt）
- **base/head**：`f9bafb0..bf48a45`（单 commit；main 已推进 `98f6c88`，漂移=1 号 c3-1 纯测试 `tests/test_scene_slice_lineage.py`，与本批入选文件零交集）
- **入选文件（--preview 核实，6 app 文件 +91/-18 中 63 行）**：
  - `app/services/artifact_service.py`（105 行，+4/-1）
  - `app/services/bag_cleanup_service.py`（1213 行，+34/-9）
  - `app/services/bootstrap.py`（236 行，+1/-1）
  - `app/services/catalog_ingest.py`（112 行，+24/-2）
  - `app/services/source_service.py`（483 行，+12/-2）
  - `scripts/clone_published_dataset_records.py`（551 行，+9/-1）
- **排除**：`tests/test_bag_cleanup_concurrency.py`（default_path，纯测试先例口径，独立验证挂 TESTER/合入后复核）
- **尺寸预检（§3.6）**：最大入选文件 551 行（clone 脚本）贴 500 行阈，总 diff 仅 +91/-18 行；按先例（D3 1025 行 365s / c285e2e 134 行 2m17s）预估 5~15 分钟，单批 + `--max-tokens 60000` 留组切余量，不设跨文件拆批
- **runner**：`/home/wang/.hermes/cache/scratch/t08c-ocr/c1c2-r1-runner.py`（fcntl flock 持 `inbox/ocr.lock` + `ocr review -c bf48a45 --audience agent --max-tokens 60000`，workdir `wt-04a-t08c`）
- **启动**：2026-10-11 18:3x +08:00（协调者 cron poll 回合后台 terminal，`notify_on_complete`）
- **硬截止**：2026-10-11 19:10 +08:00（到点先查 session mtime 活跃度再裁决续等/kill+resume，§4）
- **run_id/session**：逐文件单审（本 cron 环境后台进程被回合边界 reap、前台 420s 上限，2 文件组含 bag_cleanup 1213 行必爆，改逐文件）——6/6 app 文件各一组 **全部 `Review complete: 0 finding(s)`**：
  - `bag_cleanup_service.py`（1213 行）session `6d53233c`，5m36s
  - `catalog_ingest.py`（112 行）session `692a65eb`，6m19s
  - `source_service.py`（483 行）session `1426c954`，1m23s
  - `artifact_service.py`（105 行）session `0736fd03`，48s
  - `bootstrap.py`（236 行）session `baffd04b`，37s
  - `clone_published_dataset_records.py`（551 行）session `cc427894`，3m29s
  - 日志 `/home/wang/.hermes/cache/scratch/t08c-ocr/f-*.log`（+ `p1.log`）
- **中途作废尝试**（未计入结果）：v1 `c56d992c`（PIPE 缓冲被终止）/v2 `1bfcef65`/v3（420s 超时 context canceled，各 2-3 组失败）/p2 `8e71e387`+p3（2 文件组超时）——均因单组含 1213 行文件超 420s，改逐文件后全收口
- **status**：**COMPLETED（6/6 app 文件 0 findings）**
- **result_path**：`/home/wang/.hermes/cache/scratch/t08c-ocr/c1c2-r1.log`（+ `ocr session comments <uuid>` 落盘 `c1c2-r1-comments.txt`）
- **门禁口径**：无 high/critical → 协调者 rebase `98f6c88` 复核 + 合入后 sanity → --no-ff 合入 main（推 origin，已有授权口径）；9 红文件全绿复核随 TESTER/合入后验证。有 high/critical → 回派 2号 t08c-1 返修

## 收口记录

- （待回写）