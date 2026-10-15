# TASK-12S-F attempt-1 R1 最小返修派单（协调者，2026-10-15 11:07 +08:00）

- **状态**：DISPATCHED。owner=执行者 B；task/attempt=TASK-12S-F / attempt-1 R1。
- **原交付**：工作点 head `6798059`（base `b39a3ec`，分支 `b/task-12s-f-input-reject`，wt `/home/wang/.local/state/rosbag-scene/wt-04a-t12sf`），10 文件 +939/-7，自测申报 14+91 passed、全量 1204 passed/5 failed（归属核实均非本任务）。
- **协调者独立机械核验（10:45-10:47）**：祖先链 `git merge-base --is-ancestor b39a3ec 6798059` OK、单 commit、diffstat 与回执逐项一致（10 文件 +939/-7）、工作树干净、`alembic heads` 单头 `20261014_01_ingest_rejected`。**ruff（仓配置 select E,F,I,UP，line-length=120，已按 pyproject.toml 实读确认）4×E501**：`tests/test_ingest_input_rejected.py:136/195/230/315`（122/125/141/134 > 120）——回执申报"0 error"有误（回执自述"E501 非启用规则"与仓 pyproject.toml 实际 select=["E","F","I","UP"] 不符，E501 属 E 类**已启用**）。
- **返修范围（唯一）**：修复上述 4 行超长（折行，禁止 noqa 绕过）→ ruff 本任务 10 文件 0 error → 复跑 `tests/test_ingest_input_rejected.py` 14 passed 确认无行为影响 → 在原分支续 commit。
- **冻结口径不变**：仍为工作点交付暂挂（supplement-s1）；收到"E attempt-2 冻结 head 通知"前不提前冻结正式交付；届时机械 rebase（当前 F diff 未触 `pending_binding.py`/`source_service.py`，E attempt-2 面与 F 无文件冲突，rebase 预期干净；冲突则 B 报协调者）。
- **未申报项维持如实**：真 MySQL 8.4.11 隔离探针、真并发乐观锁、NAS E2E 均留待交付冻结/TESTER 口径，本单不要求提前执行。
- **门禁**：R1 交付 → 协调者机械核验（ruff 0 error 必核，已核：HEAD `8c8bf2f` 单文件 +20/−4 折行、ruff 10 文件 All checks passed、定向 14 passed、祖先链/工作树干净）→ **OCR 范围为 F 全量 app 交付 `b39a3ec→8c8bf2f`（7 app 文件；R1 增量=测试文件折行，tests 默认排除不另起 run）** → TESTER → 接受。OCR 与 E 复验并行推进、互不阻塞；F app diff 冻结且与 E 面（`pending_binding.py`/`source_service.py`）文件不相交，rebase 至 E head 不改 F 面内容，findings 可延续。
- **边界**：仅本任务 10 文件面；不碰 E 分支/公共文件；VLM=0；不写生产。
- **时限**：ACK 30min 内（机械小单，交付预期 ≤30min）。