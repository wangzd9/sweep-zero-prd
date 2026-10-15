# TASK-16S 原样脚本调用接入 —— 任务登记与合并候选冻结（协调者，2026-10-15 17:50 +08:00）

- status: **REGISTERED / OCR_PENDING / TESTER_DISPATCHED**（候选冻结，未合入 main、未部署）
- 授权来源：用户 2026-10-15 17:2x「甲」（原生消息 `om_x100b623df418c4a0de1c0a9bd8f67e2`，request `d7c58fe39f0fbdd5452ae38ebd98690681e5ffcf1ce2112c46759af2cc318156`）：把脚本线合回 main 基线、跑全仓测试、补 OCR 与独立测试门禁后再谈部署。**不含生产部署授权**。

## 为什么登记

强模型（用户侧开发线）在 2026-10-15 完成 `ros2_slice` 原样调用接入，分支 `feat/spray-script-call-20261015`：
`3c9c496 → 98d0718 → 107a34d → 524fe83 → cad585a → 1c87028`（5 提交）。该线**从未进入本协作流程**：TODO/HANDOFF 零登记、零派单、零 OCR、零 TESTER 独立验证，但 `cad585a` 已随标准部署脚本成为**生产运行版本**（实测处理机 `.deployed-git-revision=cad585a`、容器内文件 sha256 与 cad585a 逐字节一致）。本卡把"事实上线但未审"的代码纳入唯一任务状态表。

## 冻结交付

| 项 | 值 |
|---|---|
| 交付分支 | `feat/spray-script-call-20261015`（head `1c87028`，已备份 github）→ 合并候选分支 `coord/merge-spray-script-into-16c` |
| base | `16a154f`（main，v0.4 最小界面闭环） |
| **冻结 head** | `21b191cf3754225ba6453dc26c14793ebc91510e` |
| 冻结 worktree | `/home/wang/.local/state/rosbag-scene/wt-coord-merge-script-20261015`（HEAD=21b191c，仅 `.venv` 未跟踪） |
| 合并拓扑 | `21b191c` ← `96716ec`(merge 16a154f+cad585a) ← `c653671`(merge +1c87028) ← `310f90e` ← `21b191c` |
| 变更面 | 11 文件 +617/−7；非文档 6 个 |
| 远端备份 | `github/coord/merge-spray-script-into-16c` = `21b191c`（ls-remote 回读一致）；`github/feat/spray-script-call-20261015` = `1c87028` |

## 变更面（相对 16a154f）

- `app/scene/spray/script_adapter.py`（新增 180 行）——`SprayScriptAdapter` 认领受控脚本作业（源UID/代次/指纹/上游 commit/config_hash 五元身份 + `platform-claim.json` 单 run 认领）、轮询 `status.json` 观察终态、取消写 `cancel-request.json`、接收 `receive_script_slice` 复制上游物理切片并复用 `_validate_slice`
- `app/scene/spray/__init__.py`（+2/−1）——注册 `SCRIPT_ADAPTER_KEY`
- `config/scene_capabilities.yaml`（+32/−1）——新增 `spray-script-deb8be8-call`，**仓内 enabled: false**（默认关闭，不改 `spray-v1` 默认）
- `scripts/ros2_slice_call.py`（新增 200 行）——调用包装：副本隔离、flock 防重复烧模型、计时、产物验证、状态记录
- `scripts/scene_host_orchestrator.py`（+5/−1）——WRITE 步按 `adapter_key` 分流到 `receive_script_slice`
- `tests/test_spray_script_adapter.py`（新增 116 行）
- 文档：`docs/scene-script-calling.md`（新增）、`HANDOFF.md`（+30）、`docs/deployment-snapshot.md`（脚本生成内容）、`changelog/REVIEW.md` + `changelog/pending/spray-upstream-script-calling.yaml`（F-042 候选）

## 合并冲突处置（共 5 处，全部为文档/日志，代码面零冲突）

1. `HANDOFF.md`（第一次合并）：脚本线 10-15 三段 vs 16C 侧历史段 → 两侧全保留。
2. `HANDOFF.md`（第二次合并 1c87028）：① 头部两条"最终回执"（1c87028 新增）与 HEAD 侧空段 → 保留 1c87028 内容；② 尾部 10-13 首包收尾段（16a154f 侧）与 10-15 原样脚本核验段（1c87028 侧）→ **两段都保留**（实测 1c87028 与 16a154f 各自独有，非重复）。
3. `docs/deployment-snapshot.md`（两次）：取 1c87028 侧（2026-10-15T16:47:23 生成，prod=`cad585a` 与实测吻合）；该文件由脚本生成、禁止手工编辑。
4. `changelog/REVIEW.md` + `spray-upstream-script-calling.yaml`：脚本线候选 `review_id: F-041` **与 main 既有水雾候选 F-041 冲突**（`changelog.py validate` 实报"审查编号 F-041 同时属于两个候选"）→ 脚本线候选**顺延为 F-042**（标题与功能点编号同步），`status` 仍 **pending**，**未批准、未发布、未写入页面时间线**；编号顺延说明记在本卡，不塞进候选字段（schema 不接受自定义键，实测拒绝）。
5. 代码面：`git diff --name-only` 交集为空，`merge-tree` 三次预检（E/F/脚本线两两）均无冲突。

## 已完成的协调者机械核验（可在 21b191c 复现）

1. **双面内容核对**（逐文件 sha256 对比两侧原点）：脚本线 6 文件与 `cad585a` **逐字节一致**；16C 六文件（`bag_search_service.py`/`bags.html`/`pipelines.py`/`bags.py`/`scene_result_query.py`/`pipeline_detail.html`）与 `16a154f` **逐字节一致** → 合并未丢任一侧功能。
2. **冲突残留**：全仓 `grep '^<<<<<<< \|^>>>>>>> '` = 0 命中。
3. **全仓 pytest**：`21b191c` = **1181 passed / 4 failed / 10 skipped**（101s）；基线 `16a154f` = **1174 passed / 4 failed / 10 skipped** → 失败集合完全相同（`test_devflow.py` ×3 环境性 sandbox-git、`test_web.py::test_bag_search_page_has_bounded_query_count_and_response_time`），新增 7 passed 全部来自脚本线自带测试，**零候选回归**。
4. **ruff**：与 `16a154f` 同为 4 errors（全在 `tests/test_task16cc_scene_detail.py` E501，16C 既有面），**零新增**。
5. **changelog**：`validate` / `render` rc=0；REVIEW.md 呈现 F-040/F-041/F-042 三段，pending 候选 13 个。
6. **alembic**：`heads` 单头 `20261013_01_scene_intake`；本合并**零迁移改动**。
7. **生产一致性**：处理机容器内 `script_adapter.py`/`ros2_slice_call.py`/`scene_host_orchestrator.py` sha256 与 `cad585a` 一致；`config/scene_capabilities.yaml` 生产侧为**运维 overlay**（`spray-script-deb8be8-call` enabled=true），仓内默认 false —— overlay 属生产运行配置，不在本卡代码面。

## 门禁与下一步

| 门禁 | 状态 |
|---|---|
| 合并冲突处置 + 机械核验 | ✅ 完成 |
| 全仓测试（与基线同口径） | ✅ 完成（零候选回归） |
| OCR（唯一入口，6 个非文档入选） | ⏳ 排队——全局 `ocr.lock` 由 12S-F run 持有，待其收口后经 `ocr_runtime.py prepare → start` 起跑，**不得并行** |
| TESTER 独立验证 | 📤 已派（`inbox/TESTER/TASK-16S/attempt-1-independent-verify-dispatch.md`，被测 `21b191c`） |
| 合入 main + 推远端 | ⛔ 未授权——等 OCR findings 裁决 + TESTER PASS 后向用户单独申请 |
| 生产部署 | ⛔ 本轮明确不在授权范围（用户口径"再谈部署"） |

## 范围与非范围

- **在范围**：把已在生产运行、但未登记未审的脚本线并入 main 并补齐全部门禁；保持 16C 界面面不变。
- **不在范围**：新增脚本能力（自动扫描启动任意源包未实现，仍为受控作业登记接入）、修改上游 `ros2_slice` 算法、放宽 Backend 完整性校验、生产部署、处理机 overlay 变更、清理生产既有 run/缓存/证据。

## 环境事实（2026-10-15 17:5x 实测）

- main = 工作区 HEAD = `16a154f` = github/main；GitLab `origin/main` 停在 `6c7d983`（落后 34 commit）。
- 生产处理机 `.deployed-git-revision = cad585a`（2026-10-15 16:04），Alembic `20261013_01_scene_intake`。
- 脚本线 5 提交本地分支 `feat/spray-script-call-20261015` head `1c87028`，已推 github 备份（此前任何远端都没有）。
