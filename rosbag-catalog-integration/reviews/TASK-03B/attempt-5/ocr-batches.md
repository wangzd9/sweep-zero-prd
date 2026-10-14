# TASK-03B attempt-5-rework-2（c285e2e）OCR 批次记录（协调者管理）

## 交付核实（cron 巡检 2026-10-10 16:48，owner cron-coord-20261010-1648）
- wt-01 HEAD = `c285e2e`（分支 t03b-r2-rework，base f088c2b），工作区干净（仅未跟踪 .venv 软链，未入 commit）。
- `git diff f088c2b..c285e2e --stat` = 2 文件 +145/-24：`app/services/scene_schedule_consumer.py` +93/-23、`tests/test_scene_r2_rework_1.py` +52/-1（ocr preview 默认排除 tests，与 B8a 口径一致）。零越界、零 .venv 产物、单 commit。
- 自测（1号回执 receipts/TASK-03B/attempt-5-rework-2.md）：定向 44 passed、全量 813 passed（3 failed = test_devflow 沙箱环境性，stash 复证非本次回归）、ruff 全绿。

## 协调者批次
| batch | base..head | 输入 | status | run |
|---|---|---|---|---|
| B9（rework-2 增量） | f088c2b..c285e2e，`ocr review -c c285e2e --audience agent` | scene_schedule_consumer.py（399 行 <500，单文件单批，无需拆组） | **RUNNING**（16:48:18 起跑，pid 480324/ocr 480346，session `cdba7e7f-79cb-441b-bc56-bd90d96d941a`，持 inbox/ocr.lock，硬截止 **17:15**；diff 仅 +93/-23，参照同规模批预计 ~5-15min） | reviews/TASK-03B/attempt-5/ocr-c285e2e-03b.log（脚本 ~/.hermes/cache/scratch/b9_ocr_03b.py 收口自动回写 status） |

## 门禁链（不变）
- B9 收口且无 high/critical → `f088c2b+c285e2e（同批 --no-ff，c285e2e 在 f088c2b 之上）+ c67600d + a07c181 + 9325155 + 86b2cc1` 合入 main（现 eff0479）→ TESTER 派单（R2-05 交错 MySQL 联调 + R2-01/02/03 终测 + 路径逃逸断言）→ 03/06B/06 聚合重验。
| B9-r2（r1 canceled 后同 commit 重跑） | f088c2b..c285e2e，`ocr review -c c285e2e --audience agent` | scene_schedule_consumer.py（399 行单文件） | **16:59 FAILED context canceled**（1m26s、1/1 item canceled、budget_exceeded=false，session `45c6b960`，vLLM capacity 拥塞排队期取消；按门禁不算通过，r3 重跑） | 同 B9 log（ocr-c285e2e-03b.log） |

| B9-r3（r2 canceled 后重跑） | f088c2b..c285e2e，`ocr review -c c285e2e --exclude 'tests/*' --audience agent --timeout 120` | scene_schedule_consumer.py（399 行单文件） | **COMPLETED 0 findings（17:11:29 收口，8m35s，session `30863ac9-9e3e-4c6d-be3b-3fd830fd208f`，1/1 completed，exit 正常）** → 03B 侧 OCR 门禁解除 | 同 B9 log（ocr-c285e2e-03b.log） |
