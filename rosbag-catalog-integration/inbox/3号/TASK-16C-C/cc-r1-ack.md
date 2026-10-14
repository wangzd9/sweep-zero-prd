# TASK-16C-C 返修单 CC-R1 — ACK（执行者C）

状态：ACKED，owner=C，2026-10-14T13:08:00+08:00（occurred=now）。

- 派单路径：`inbox/3号/TASK-16C-C/cc-r1-rework-dispatch-20261014.md`（协调者 2026-10-14 13:00 +08:00 REWORK_DISPATCHED；OCR run `e7a5580cdf9f4eed8b448aad1c61f53b` b01 唯一 finding 裁决见 `inbox/coordinator/TASK-16C-C/ocr-attempt1-adjudication-20261014.md`）
- task/attempt：TASK-16C-C / 执行者C / attempt-1 同一冻结链续 commit（不新开 attempt）
- base：续 `522bb3f358f042160b25b5a66d55434500ab2928`（wt-c-16cc 实测 HEAD=522bb3f，分支 `c/task-16cc-pipeline-detail` 干净仅未跟踪 `.venv`）
- 读写范围（C 独占两文件）：`app/templates/pipeline_detail.html` 数据血缘兜底 `{% else %}` 分支补 `<ol class="lineage">` 开始标签；`tests/test_task16cc_scene_detail.py::test_no_lineage_fallback_li_in_ol` 同步断言兜底 `<li>` 位于开始标签之后、`</ol>` 之前
- 恢复核实：attempt-1 ACK 11:30 与冻结回执 12:12 在案（head `522bb3f`）；本 ACK 为 CC-R1 返修的恢复/领取确认，不重复 attempt-1 领取；不抢占、不杀未知进程
- 自测口径：复跑 `pytest tests/test_task16cc_scene_detail.py tests/test_task16c_ui_minimal.py -q`，seed 固有失败按原口径不计本账
- 下一步：执行最小修复→续 commit 冻结→回执补 CC-R1 返修段→状态回 REVIEW_PENDING 交协调者独立核 diff（不整叶重跑 OCR）