---
task: TASK-05
item: attempt-2-ocr-rework
owner: 1号
status: ACCEPTED
dispatched_by: 协调者
updated: 2026-10-09 22:55
target: 20261009_01 迁移 backfill（alembic/versions/20261009_01_scene_identity_key.py L77-85）
round: OCR 返修第 1 轮（B6 6ce7b7a：1 high + 1 low）
---
# 05 attempt-2 OCR 返修（B6 批次，1 high + 1 low）

## high：backfill 未按身份去重，存量重复业务身份会让 upgrade 失败
OCR 发现（session 1d0d3b30）：`_backfill_scene_identity` 对**每一行** SCENE_SLICE run 都重算身份并
UPDATE 写键。修复前 `active_identity_key` 终态释放，同业务身份（source+代次+用途+冻结能力集合）
在终态后重放会建第二个 run——**存量库 R1(身份 K, 已终态) 与 R2(身份 K) 可能并存**。两行拿到同一
scene_identity_key 后，紧接着 `create_index(unique=True)` 抛 IntegrityError → `alembic upgrade head`
失败（compose.yaml 在 backend 启动时执行 = 服务起不来）。

**修复**：backfill 按身份只保留一行写键（取该身份下 max(run_id) 为规范行，其余保持 NULL），
再建唯一索引。幂等重跑语义保持不变。

**风险评估（协调者已查，供你参考不豁免修复）**：本地测试库 scene run=0、scene 功能未发布生产，
当前无现实触发；但这是"存量库升级必炸"级别缺陷，且修复 10 行内，不豁免。

## low：迁移文件末尾缺换行符
`alembic/versions/20261009_01_scene_identity_key.py` 末尾补换行（W292）。

## 交付
- 从 main 533aa1c 新建修复 commit（同分支 scene/task-05-rework 或新 hotfix 分支均可，报 commit）
- 定向测试 + 回归：现有 `tests/test_scene_slice_scheduling.py`（140 基线）必须全绿；
  **补 1 个 backfill 去重回归测试**：预置同身份两条 SCENE_SLICE run（一终态一新）→ 跑迁移
  upgrade → 断言唯一索引建成、规范行=max(run_id) 持键、其余 NULL、upgrade 不抛 IntegrityError
  （SQLite 测试库内做，用 alembic API 跑单迁移或模拟 backfill 函数直接调用——选真实度高的，
  回执里写清用了哪种）
- receipts/TASK-05/attempt-2.md 追加 OCR 返修交付段（commit/测试/状态 REVIEW_PENDING）
- 完成后群内按新通报格式；OCR 不自跑，等协调者对修复 commit 复审

## 备注
B6 的 round 2 core review 因 vLLM 超时 incomplete（1h13m，2 findings 已出但覆盖未全）——
协调者会 --resume 断点续审补齐，你只需交付上述修复；若续审再出意见，合并进下一轮回派（有界 2 轮）。