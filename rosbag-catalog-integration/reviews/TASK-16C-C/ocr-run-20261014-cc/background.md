# TASK-16C-C attempt-1 OCR 背景（协调者冻结）

- 任务：TASK-16C-C（流水线详情叶，父 TASK-16C）；REQ-16/05、AC-16/05。
- 授权来源：用户 2026-10-14 恢复 v0.4 最小界面闭环（见 inbox/control/V04-UI-RESUME-20261014.md），并要求历史 OCR 未修问题入任务。
- base/head：`bd0db1d2a0fc293cb4562e2079e741739bacb0de`（未接受开发 seed，含已知缺陷）→ `522bb3f358f042160b25b5a66d55434500ab2928`（分支 `c/task-16cc-pipeline-detail`，worktree wt-c-16cc，HEAD 干净）。
- 本叶文件：`app/web/pipelines.py`、`app/templates/pipeline_detail.html`、新增 `tests/test_task16cc_scene_detail.py`（3 文件 +441/-28）。
- 关键不变量：
  - DESIGN §7.3.3：场景八步真实状态映射（EXTRACT/INFER/PRECHECK/PUBLISH/REGISTER/SEGMENT/VALIDATE/WRITE），未启动步骤保持「未开始」，不改状态机、不加 schema。
  - 场景真实终态唯一来源 `SCENE_TERMINAL_STATUSES`+`scene_terminal(run)`；INPUT_INVALID 属 Phase0，不进场景终态集，页面保持刷新。
  - CANCELLED 场景无 retry-form；尾脚本必须 DOM guard（`if (retryForm)`），不得露自建强制重试。
  - NVIDIA 契约块按 `run.pipeline_type=='NVIDIA_CHUNK'` 分流，NVIDIA 来源的场景 run 不得误露旧契约。
  - 模型身份（capability/config/summary）只取冻结快照真实字段，无记录显示「未登记」，不用当前 env 冒充历史。
  - 数据血缘兜底 `<li>` 必须在 `<ol>` 容器内闭合。
- 允许行为：仅本叶三文件增量；不部署、不生产写、不改 A/B owner 文件。
- 测试证据：新增 16 用例全绿；旧面 90 passed（2 顺序敏感失败在 seed 同序复现一致，非本增量引入）；全仓 1144 passed/4 failed 均 seed 固有复现。
- 待核实风险：真实浏览器 JS 异常取证与严格 MySQL 面归 TESTER 16D，本 OCR 不替代。
- OCR 遗留映射（本叶承担）：C1 删不可达 elif、C2 删死参数、C3+c05-03 终态唯一来源、C4 驳回回归确认、C8 DOM guard、C9 模型身份、c05-04 ol 闭合、c05-05 pipeline_type 分流。