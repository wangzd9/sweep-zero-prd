---
task: TASK-06B
item: attempt-1-rework
owner: 2号
status: ACCEPTED
dispatched_by: 协调者
updated: 2026-10-10 08:49
base: main 3b78736（05 强模型返修已合入；你的 76d2958 基于 8bd5618，早于 05 返修）
round: 06B 验收返修第 1 轮（有界 2 轮）
---
# 06B 返修：2 个测试与 05 #7 持久身份键语义不兼容

## 事实（协调者 08:49 验收实测，非推测）
- 76d2958 在你原 worktree（base 8bd5618）上 24 passed；合入 main 3b78736 后
  `tests/test_scene_result_report.py` 挂 **2 个**：
  `test_late_old_version_no_rollback` + `test_failed_keeps_old_current`
  （claim 循环 10 次领不到指定 run：run2 创建返回 202 但 created=False，
  拿到的是 run1 的已终态 run_id）
- 根因定位（对照实验已做）：05 强模型 #7 返修（6ce7b7a，已合入 main）把
  scene run 身份改为 **scene_identity_key 持久唯一键（终态不释放）**：
  同业务身份（源+代次+用途+冻结能力集合）**全局只创建一个 run**，同身份再建
  幂等复用既有 run（scene_slice_service.py:186-193）。
  你这两个用例的"同一 source 同场景建 run1 和 run2"在旧语义下（active 键
  终态释放）能建出第二个 run，新语义下 run2 命中 run1 终态身份被复用——
  **是测试假设过期，不是 05 返修 bug**（#7 正是强模型裁决的"只创建一次"）。
- 契约锚点：显式重新分析必须带 reanalysis_id（app/schemas/requests.py:114
  `reanalysis_id: str | None`，进身份摘要走新身份建新 run）——你的
  test_identity_gates 等用例若覆盖此路径不受影响。

## 处置（最小改法）
1. `_create_run` helper 增加可选 `reanalysis_id` 透传（body 字段，schema 已支持）；
2. 两个失败用例里 **run2 的创建带上独立 reanalysis_id**（语义上正是"重新分析
   产生新版本"，与"晚到旧版本/失败保旧 current"的测试意图一致——旧版与新版
   是两个分析实例，本就该是不同身份）；
3. 顺带核实文件内其他"同 source 多次建 run"的用例是否同样假设（grep
   `_create_run` 全部调用点），受影响的一并修；
4. 不改 05 服务代码（持久身份键是强模型裁决项，已合入 main 且 outbox 联调
   PASS 6/6，回退它=推翻已裁决契约，禁止）。

## 交付
- base 改到 main **3b78736**（rebase 或 cherry-pick 你的 76d2958 后改测试），
  wt-04a 开发；
- 定向 `tests/test_scene_result_report.py` 全绿 + 全量
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q`（devflow 3 个
  沙箱失败=已知环境性）+ ruff 绿；
- receipts/TASK-06B/attempt-1.md 追加返修段（commit/根因确认/测试/状态
  REVIEW_PENDING），群内按通报格式；
- OCR 不自跑，等协调者对修复 commit 串行代跑。