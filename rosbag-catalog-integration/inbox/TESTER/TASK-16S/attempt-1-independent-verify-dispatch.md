# TESTER TASK-16S attempt-1 独立验证派单（协调者，2026-10-15 17:4x +08:00）

- status: **TESTER_DISPATCHED**（协调者机械核验已完成；本单为行为面独立验证，与 OCR 串行不冲突——OCR 审代码，TESTER 验行为，均只读冻结 head）
- 任务：TASK-16S 原样脚本调用接入（REQ：用户 2026-10-15 直接要求"把最新 ros2_slice 当独立程序调用、不修改识别/抽帧/分段算法"；登记卡 `inbox/coordinator/TASK-16S/registration-and-candidate-freeze-20261015.md`）
- **被测固定 SHA**：`21b191cf3754225ba6453dc26c14793ebc91510e`（合并候选分支 `coord/merge-spray-script-into-16c`；拓扑 `21b191c` ← merge(16a154f+cad585a) ← merge(+1c87028)）
- 建议只读树：`/home/wang/.local/state/rosbag-scene/wt-tester-script-merge`（或自建 detached worktree 检出 `21b191c`）
- 变更面（相对 `16a154f`，11 文件 +617/−7）：`app/scene/spray/script_adapter.py`（新增）、`app/scene/spray/__init__.py`、`config/scene_capabilities.yaml`、`scripts/ros2_slice_call.py`（新增）、`scripts/scene_host_orchestrator.py`、`tests/test_spray_script_adapter.py`（新增）+ 5 文档/日志（`HANDOFF.md`、`docs/scene-script-calling.md`、`docs/deployment-snapshot.md`、`changelog/REVIEW.md`、`changelog/pending/spray-upstream-script-calling.yaml`）

## 验证要求

1. **适配器身份与认领不变量**（自造 job 夹具，`SCENE_SCRIPT_JOBS_ROOT` 指向 tmp）：
   - 五元身份（`source_id`/`source_generation`/`source_fingerprint`/`upstream_commit`）任一不符 → `SCRIPT_IDENTITY_MISMATCH`，且**不得**留下 `platform-claim.json`；
   - `job_id` 非法字符（`../x`、空、超长）→ `SCRIPT_JOB_INVALID`；`job_id` 越界目录 → `SCRIPT_JOB_UNAVAILABLE`；
   - 同作业第二个 run 认领 → `SCRIPT_JOB_ALREADY_CLAIMED`；**同一 run 重试**（同 `run_id`/`config_hash`）→ 允许接续不报错（这是幂等点，重点验）；
   - `status.source_commit` 与冻结 commit 不符 → `SCRIPT_IDENTITY_MISMATCH`；`FAILED` → `SCRIPT_FAILED`；超时（把 `SCENE_SCRIPT_TIMEOUT_SECONDS` 设 1~2s）→ `SCRIPT_TIMEOUT` 且写入 `cancel-request.json`；`is_cancelled()` → `CANCELLED` + `cancel-request.json`。
2. **结果有效性拒绝面**：`valid_images=0` / `cached_results != valid_images` / `unknown_frames>0` / `segments` 与 rows 数不符 / row label 非 `spray` / 非整数 `start,end` / `end<=start` → 各自 `SCRIPT_RESULTS_INVALID`；全通过 → `SceneOutcome.SUCCESS` 且 `start/end × 10**9` 为纳秒边界（只做单位换算，不得宣称纳秒级识别精度）。
3. **切片接收 `receive_script_slice`**（自造最小 db3+metadata 夹具）：
   - `slice_path_local` 不在 `/work/slices` 下 / 目录缺失 → `SliceWriterError`；含符号链接 → 拒绝；非单 DB3 → 拒绝；
   - DB3 名非 `rosbag2_0.db3` → 重命名且 metadata `relative_file_paths`/`files[].path|uri` 同步；metadata 与实际 DB3 不符 → 拒绝；
   - **零消息 topic 面（本线真实缺陷修复点，重点验）**：构造上游 DB3 含 18 个 topic 定义、其中 N 个消息数为 0 的切片，断言 `receive_script_slice` 返回的 topics 覆盖**全部 18 个**（含零消息）、计数与真实 DB3 一致；并做 RED 交叉证（pre-fix 口径只返回有消息 topic 时该断言失败）；
   - 接收后**原始切片与源包字节不变**（sha256 前后一致）。
4. **编排分流**：`scene_host_orchestrator` WRITE 步在 `capability_version` 为 `spray-script-deb8be8-call` 时走 `receive_script_slice`，其余（含 `spray-v1`）仍走 `slice_bag_to_staging`；断言两条路径互不误入。
5. **配置默认面**：仓内 `config/scene_capabilities.yaml` 中 `spray-script-deb8be8-call` 的 `enabled: false`、`spray-v1` 默认选择未变；不得把生产运维 overlay 的 enabled=true 当作仓内配置。
6. **零越界核**：`git diff --name-only 16a154f 21b191c` 恰为上述 11 文件（6 代码/测试 + 5 文档日志）；`app/api/`、`app/models.py`、`alembic/versions/`、`app/services/`、16C 界面面（`bag_search_service.py`/`bags.html`/`pipelines.py`/`scene_result_query.py`/`pipeline_detail.html`）**零改动**。
7. **回归**：定向 `tests/test_spray_script_adapter.py` 全绿；scene 面既有定向用例不回归（可用你此前 16D/12S 面既有口径，不必重跑全量）。

## 边界

- 只读被测 worktree（`.venv` 未跟踪可接受）；**不烧模型**、不启动任何真实上游脚本容器、不碰生产处理机、不改代码、不合并、不推送。
- 不重放生产既有 run（`scene-bd977a8fd6504b5ca7ed41fe3cee`/`scene-5abba4017f2443a3b06c2b235021`）与处理机作业目录；生产侧一致性由协调者已实测的容器内 sha256 记录承载。
- 发现失败项出 RED 证据（命令/退出码/断言原文）交协调者回派，不自行修码。
- 交付回执：`test-receipts/TASK-16S/attempt-1.md`（含命令、退出码、关键断言原文、未执行项）+ TESTER 事件。
- PASS 是本任务接受门禁之一（另一为协调者 OCR 唯一入口零 CORRECTION 级裁决）。
