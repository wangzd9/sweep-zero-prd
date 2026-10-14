# TASK-16A attempt-3-rebase 迁移双头接线单（协调者 r136 派发，2026-10-13 08:4x）

- **角色/owner**：执行者 A（1号）｜**attempt**：attempt-3-rebase（07B 整链合入后的既定 rebase 双头接线，口径=r107/r119 双头裁决+A 申报一致）
- **背景**：07B 整链已 `--no-ff` 合入 main `4b9f30a`（changelog F-040 候选随附 `3d2a075`，已推 origin/github 双远端）。main 迁移新单头=`20261012_01_scene_manual`；你 16A 链（`79f6889`→`c30f048`→`3aee4d1`，base `c2018dd`）的迁移 `20261013_01_scene_intake.py` down_revision 仍指 `20261009_02_ingest_frozen`，与新头构成双头，必须接线。
- **固定工作区**：`wt-01-t16a`@`a/task-16a-scene-intake`，base 不动（`c2018dd` 祖先链），rebase 到新 main 后收口。
- **范围**（仅此，零新功能、零语义变更）：
  1. `git rebase` 你的 3 commit 链到 `4b9f30a`（merge-tree 预核 `app/models.py` 可自动合并，无冲突面；若 rebase 过程出现实质冲突→停止回报，不强推）。
  2. 迁移 `alembic/versions/20261013_01_scene_intake.py`：`down_revision = "20261009_02_ingest_frozen"` 改为 `"20261012_01_scene_manual"`，docstring 同步（r119 口径：单头链 20261009_02→20261012_01_scene_manual→20261013_01_scene_intake）。
  3. 自测：`alembic heads` 单头 `20261013_01_scene_intake` + 真 SQLite `upgrade head`→`downgrade -1`→`upgrade head` 三往返 RC=0（真 MySQL 8.4 全链往返留 TESTER/独立验证口径，申报即可）+ 16A 定向 56 passed 口径复跑 + ruff 变更文件 + 全量 SQLite（3 failed=test_devflow 环境性 base 复现口径，如实申报）。
- **停止条件**：rebase 完成+迁移接线+自测全绿→交付冻结 REVIEW_PENDING（回执 `receipts/TASK-16A/attempt-3-rebase.md`，列新 HEAD sha 与 rebase 后各 commit 映射）；发现 rebase 触碰 07B 面或迁移语义变化→立即停并回报协调者。
- **后续**：机械核验→增量 OCR（rebase 后迁移单文件+models 自动合并面小批）→合入 main→TESTER 16A 独立验证（target 固定=合入后 main HEAD，含真 MySQL 8.4 全链迁移往返+AC-14/AC-08 面）→16A DONE。
- **注意**：16C 已派 B、16B proxy OCR 重试在途（协调者面，不占你）；你只接本单。