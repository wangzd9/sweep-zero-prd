---
task: TASK-06B
item: attempt-1-r2-rework-3
owner: 2号
status: ACCEPTED
dispatched_by: 协调者
updated: 2026-10-10 16:14（B ACK）
base: wt-04a 9325155（你的 medium 小修之上）
round: 同返修单小修（不占新轮次）
---
# 2号小修：9325155 OCR low（dead code，1 行级）
9325155 OCR 收口（cb8ae615，5m45s，0 high/medium）出 1 条 low：`_verify_source_identity` 中
`:280` `if not manifest.source_fingerprint: raise 409` 分支不可达——M-2 新增的父包指纹 guard
（:266）+ 等值检查（:270）已覆盖"manifest 缺指纹"情形（parent 非空 + manifest 空 ⇒ 等值不成立 ⇒ :270 先 409）。
**处置**：删除 :280-281 冗余分支；若相关定向回归断言的是该分支消息，改断 :270 的 mismatch 路径
（现有 M-2 回归已覆盖"父包无指纹→409"，"manifest 空指纹"用例若有则改断等值 409 消息）。
交单 commit（9325155 之上）+ 回执 + 群内通报。OCR 不自跑（协调者增量审）。

ACK（B，2026-10-10 16:14 +08:00）：派单 inbox/2号/TASK-06B/attempt-1-r2-rework-3.md，task=06B/attempt-1-r2-rework-3（同返修单 low 小修），owner=B，base=wt-04a 9325155，分支/worktree=scene/task-06b-r2-rework / /home/wang/.local/state/rosbag-scene/wt-04a（延续本任务分支，不自建新 worktree）。范围：删 _verify_source_identity 不可达 manifest 缺指纹分支（现 :276-277），改断等值 mismatch 路径；交单 commit + 回执。
