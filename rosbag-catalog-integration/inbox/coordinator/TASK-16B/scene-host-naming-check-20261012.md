# C TASK-16B 文件名漂移核对与处置记录（协调者 r104，2026-10-12 23:5x +08:00）

## 事实（独立实测）

- `wt-03b-t16b`@`c/task-16b-scene-host-proxy`（base `c2018dd`）零 commit；untracked=`scratch/`（t16b_orch_smoke.py/t16b_vlm_probe.py）、`scripts/scene_host_orchestrator.py`（537 行，23:36:21 落盘）、`tests/fake_vlm_server.py`（180 行，23:51:56 活跃写入）。
- 派单 §一.1 交付点名 = **`scripts/scene_host_proxy.py`（常驻本机场景代理，POST /run 台账幂等 + GET /health）**。
- 实际新建 `scene_host_orchestrator.py` = 八步执行编排库模块（PRECHECK→…→REGISTER，复用 app.scene.adapter.dispatch / slice_bag_to_staging / publish_scene_slices，不直连 DB）；其 docstring 自述「(run_id, attempt) 幂等由调用方**常驻代理 scene_host_proxy** 的接收台账保证」「真实实现见 :mod:`scripts.scene_host_proxy`」「库模块：由 scripts/scene_host_proxy.py 的常驻代理调用，不单独运行」。
- 即：C 按「先编排后代理」顺序开发，proxy 尚未开工；`app/` 与 `scripts/a100_host_proxy.py` 零改动=未碰派发面/既有文件，符合 §三边界。
- 既有测试/自测痕迹：scratch 冒烟+VLM 探针在跑，pytest cache 无 lastfailed 目录（尚未全量）。

## 处置

- 定性：**范围未扩、文件命名与派单点名不一致=交付时按派单命名收口**，不构成越界、不即时返修、不降 AC。
- **交付验收口径预先冻结**：回执落盘时协调者机械核验若 `scene_host_proxy.py` 仍缺失而能力只在 orchestrator 内，按 R2 口径最小返修（重命名/拆出，不改行为）；若 proxy 已在（哪怕后补 commit）即正常走 OCR（scripts+编排面，§3.6 预检：orchestrator 537 行>500 独立成批）。
- 不停单、不催单：C 开发在途（fake_vlm_server 23:51 活跃），本轮仅记账+预冻结验收口径。