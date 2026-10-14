# TASK-16C-A attempt-1 OCR 补审裁决（协调者）
- 记录：2026-10-14 16:35 +08:00；run ocr-run-20261014-retry1（base bd0db1d→head ff2a005，v1.13.0）
- 2 findings 逐条核实：
  1. [low 维护] `data_kind_case` 迁移后无 .py/模板/前端调用者 → **CONFIRMED**：全仓 grep 零引用（除定义）。
     处置：**A 合入前顺手删除（1 行无行为变化），不走 OCR**（协调者机械核验 diff 即可）；非阻塞。
  2. [low] `scene_original` 未 `~_scene_slice_pred()`，与 nvidia/self_built 不对称 → **REJECTED 误报**：
     slice 子 bag 的 `bag_role=="SCENE_SLICE"`（scene_manual_revision/bag_search 在案），
     `scene_original = and_(bag_role=="ORIGINAL", _scene_basis_pred())` 靠 bag_role 维度**天然排除** slice；
     nvidia/self_built 用 dataset_type 维度（可继承自 slice）才需 `~_scene_slice_pred()`。不对称是正确设计，非缺陷。
- 裁决：**2/2 不阻塞**。data_kind_case 删除属 A 合入前清理项（不烧 OCR/VLM）。
