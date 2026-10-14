# 回执：TASK-09 attempt-1（坡道真实能力与内容核验）

- status: **REVIEW_PENDING**
- 角色：执行者B（2号）
- 派单：`inbox/2号/TASK-09/attempt-1-dispatch.md`（19:55，用户授权真实样本）
- 交付时间：2026-10-11 21:30 +08:00
- base：main `0a8ca8ac49b4610580c25b15eb8a3e762ead96d6`（= origin/main，fetch 双核）
- 交付 commit：`a60bb81`（分支 `scene/task-09-slope-real-verify`，worktree `/home/wang/.local/state/rosbag-scene/wt-04a-t09`）
- 文件清单（3 文件 +187/-3，零越界）：
  - `app/scene/slope/vlm.py`（+17/-2）：`model` 字段默认 `DEFAULT_VLM_MODEL` 完整路径；`max_tokens` 256→2048；`enable_thinking` 可选透传 `chat_template_kwargs`
  - `app/scene/slope/adapter.py`（+9/-1）：`_default_model_client` 接线 env `SLOPE_VLM_MODEL`/`SLOPE_VLM_MAX_TOKENS`/`SLOPE_VLM_ENABLE_THINKING`；endpoint fail-closed 不变
  - `tests/test_slope_vlm_wiring.py`（新增 171 行，9 用例）
- 行为：见 `reports/TASK-09/attempt-1.md`（真实样本 row19 SUCCESS/row22+23 NO_MATCH/边界 MODEL_UNAVAILABLE/时间映射 header 证据；row20+21 被外部 VLM 服务确定性 500 帧阻塞，非 app 缺陷）
- 自测（全 RC=0，环境=`wt-04a-t09` .venv）：
  - 接线+适配器 SQLite：44 passed
  - test_scene_* 定向 SQLite：232 passed
  - 全量 SQLite（ignore test_devflow）：813 passed / 10 skipped
  - ruff 3 文件：All checks passed
  - 真 MySQL 8.4.11 STRICT 06B 核心（隔离容器 t09-mysql，口径同 TESTER pm08_plug）：`test_scene_result_report.py`+`test_scene_result_storage.py` 60 passed
- VLM 实测证据：`scratch/t09/t09-vlm-probe.json`（256 陷阱真实帧复现：flat 首帧 finish_reason=length+content=None；2048 content=平地）+ `t09-real-verify*.json` + `t09-500-probe.json`（500 帧 3 次直发确定性复现，相邻同尺寸帧 200 正常）
- 未执行项（如实申报）：
  1. 替代阳性仅 row31/32（实测 NO_MATCH=模型假阴性，事实记录）；剩余 slope 袋 `…_105605_105620`/`…_105617_105632` 未跑——VLM 调用量 ~113 次已超 dispatch 预算（≤6 样本≈100）约 13%，超支来自 500 定位 retry+替代补足；补跑需协调者/用户裁决（报告 §G）
  2. 500 帧服务端根因未查（需 A100 侧 SSH 36.152.27.114 看 /tmp/vllm_qwen38.log，本机无 key，未越界）
  3. writer 再切产物未生成（2.2 核验口径=analyze 全链到 segment/frame_log，writer 落盘属 06B 职责；frame_log 证据 digest 已进 AnalysisOutput.evidence）
- 隔离资源：t09-mysql 容器/网络/库 0 残留（docker ps -a 核实）；NAS 只读 0 写入；未动 192.168.2.45 服务
- 越界申报：无（diff 仅派单允许 2 文件客户端构造路径 + 新增测试）
- 报告：`reports/TASK-09/attempt-1.md`
- 下一步：等协调者机械核验（含 2.1 图像 content 非空证据=探针 mt2048 9 case）+ 串行 OCR（app 面 2 文件）+ 裁决 §G 阳性覆盖口径