# Decision：TASK-09 attempt-1 验收合入（2号，坡道 VLM 生产接线 + 真实样本核验）

- **时间**：2026-10-11 21:38 +08:00（协调者 cron poll 回合）
- **交付**：commit `a60bb81`（`wt-04a-t09`，分支 `scene/task-09-slope-real-verify`，3 文件 +187/-3）
- **裁决**：**ACCEPT_MERGED**（合入后验证挂 TESTER，09 暂不写 DONE）

## 机械核验（协调者独立复跑，非采信回执）

| 项 | 独立复核 | 结论 |
|---|---|---|
| base/head | rev-parse 双核 `0a8ca8a`=main=origin（合入前）；HEAD~1=base，单 commit，**无漂移** | 一致 |
| 文件集 vs 派单 2.1 枚举 | diff --name-status=vlm.py(M)/adapter.py(M)/test_slope_vlm_wiring.py(A)，与回执一致，**零越界**（2.1 仅允许客户端构造路径+新增测试） | 通过 |
| 逐行 diff vs 派单要求 | vlm.py：DEFAULT_VLM_MODEL 完整路径（=协调者前置探明的 vLLM 注册名）/max_tokens 256→2048/enable_thinking chat_template_kwargs 透传（None 不注入）/model 字段可配；adapter.py：3 env 接线+fail-closed 语义不变（endpoint 缺省=None）；**抽帧/segment/时间映射 0 改动** | 通过 |
| 派单 2.1「图像 content 非空」实证 | `scratch/t09/t09-vlm-probe.json` 独立复核：mt256 陷阱 `finish_reason=length`+`content=None`（cases[7]）复现 + mt2048 真实坡道帧 content=`坡道`（多 case）+ mt512_notk 对照 | 通过 |
| 派单 2.2 阳性/阴性/边界 | `t09-real-verify.json` 独立复核：samples[0]=**SUCCESS**（row19，publish_target=true，mapping_basis=header_stamp_ns）/samples[3,4]=**NO_MATCH**（row22/23 阴性不发布）/samples[5]=**MODEL_UNAVAILABLE**（边界不可达如实报出）；retry json row20/21 500 帧 `t09-500-probe.json` 确定性复现+相邻帧 200 对照 | 通过 |
| 自测复跑 | worktree 内 `pytest test_slope_vlm_wiring.py test_slope_adapter.py` **44 passed RC=0**（独立复跑）+ `ruff` 3 文件 All checks passed（独立复跑） | 通过 |
| 真 MySQL 8.4.11 STRICT 06B 核心 | 回执口径：隔离容器 t09-mysql，report+storage 60 passed，容器 0 残留（docker ps -a 独立核实无 t09% 残留） | 采信（合入后 TESTER 独立复验） |

## §G 待裁决项（协调者裁决）

1. **阳性覆盖口径 → 接受现证据（选项 a）**：dispatch 2.2.1 要求「阳性 slope 2-3 条」，实测 1 条 FULL SUCCESS（row19）+ row20/21 被**外部 VLM 服务确定性单帧 500** 阻塞（证据 D：3 次直发复现+相邻同尺寸帧 200，非 app 缺陷）+ 替代 row31/32 为模型假阴性（事实 C.2，方向安全）。**AC 核对以派单第三节「至少实际坡道切片样例可核对」为准，已达成**（row19 完整链路 SUCCESS+可发布区间+frame_log 逐帧证据）。剩余 2 袋（`…_105605_105620`/`…_105617_105632`）补跑**不追加**：VLM 调用量已超预算 13%（如实申报），停止条件已触发；模型假阴性/500 帧根因属**生产质量门禁 TASK-11 范围**，不借本单扩需求。
2. **500 帧归属 → 记外部服务缺陷**：vLLM 服务端 `192.168.2.45:8002`（=36.152.27.114 隧道）单图像帧确定性 Internal Server Error，**不属本单 app 范围**（app 链 fail-fast 语义正确：该帧后不继续、报 MODEL_UNAVAILABLE 不伪装 NO_MATCH）。根因需 A100 侧 SSH 查 `/tmp/vllm_qwen38.log`（执行者未越界排查，正确）——记入 TASK-11 前置事实，**不派单**（超出本单授权范围）。

## OCR（串行，协调者触发）

- 批次 T09-r1 逐文件单审（cron 化身口径）：`vlm.py` session `20a6cf39`（44s）/ `adapter.py` session `96c83b83`（95s），**均 `Review complete: 0 finding(s)`**；`tests/test_slope_vlm_wiring.py` default_path 排除（纯测试先例口径）。账 `reviews/TASK-09/attempt-1/ocr-batches.md`。

## 合入

- `--no-ff` 合入 main **`ca8730d`**（0a8ca8a..ca8730d 已推 origin），合入后 sanity 全绿：alembic 单头 `20261009_02_ingest_frozen` / ruff 3 文件 / SQLite slope 定向 44 passed RC=0。

## 门禁与后续

- **TASK-09 维持 RUNNING，合入后验证未 DONE**：TESTER 合入后独立真 MySQL 8.4.11 STRICT 验证（派单 `inbox/TESTER/TASK-09/post-merge-ca8730d-verify-dispatch.md`）PASS → 09 DONE → TASK-10 候选重算派单。
- 强审查：本单改动为 2 个客户端构造文件 +17/-3（模型 ID 默认/max_tokens/enable_thinking 接线），**NOT_REQUIRED**（无新风险面：真实样本核验已按派单完成、生产质量门禁仍属 TASK-11；不准备审查包，不自动触发）。
- TASK-11 生产启用门禁维持未放行；VLM 500 帧+假阴性事实记为 TASK-11 前置输入。