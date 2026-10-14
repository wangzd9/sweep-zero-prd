# TASK-16A attempt-3-rebase ACK

- **status**: ACKED
- **task**: TASK-16A
- **attempt**: attempt-3-rebase（07B 整链合入后的既定 rebase 双头接线，口径=r107/r119 双头裁决+A 申报一致）
- **dispatch**: inbox/1号/TASK-16A/attempt-3-rebase-dispatch.md（协调者 r136，2026-10-13 08:4x）
- **owner**: 执行者 A（1号）
- **base**: 派单固定 base 不动（16A 链 base `c2018dd` 祖先链）；rebase 目标=派单口径「新 main」。
  - 派单落盘时 main=`4b9f30a`；ACK 时 main 已前移 `3d2a075`（=origin/main 双核，纯文档 changelog F-040，在 `4b9f30a` 之上）。
  - **按「rebase 到新 main」意图 rebase 到当前 main `3d2a075`**（比派单文字多一个纯文档 commit，无代码面，merge-tree 预核 0 冲突）。
- **worktree/branch**: `wt-01-t16a`@`a/task-16a-scene-intake`（复用任务专属 worktree，返修延续本任务分支，符合协议）
- **16A 链（rebase 前）**: `c2018dd → 79f6889 → c30f048 → 3aee4d1`（HEAD `3aee4d1`，未入 main）
- **迁移双头现状**: 16A `20261013_01_scene_intake` down_revision=`20261009_02_ingest_frozen`；main 新单头=`20261012_01_scene_manual`（其 down_revision 也指 `20261009_02_ingest_frozen`）→ 双头，须接线
- **时间**: 2026-10-13 08:47 +08:00

范围=仅 rebase 3 commit + 迁移 down_revision 接线 + 自测，零新功能零语义变更。rebase 触碰 07B 面或迁移语义变化→立即停并回报。