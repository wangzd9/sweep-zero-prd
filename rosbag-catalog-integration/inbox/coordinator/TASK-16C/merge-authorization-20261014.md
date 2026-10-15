# 16C 合入持续授权（用户群内指令，18:2x +08:00）

- 用户原话：**"PASS 后可直接合入并更新测试环境"**
- 原生消息身份：chat `oc_b64dc5bf34ec1edcc8cce92ffd56604b` / user `ou_cb93c8e06b797e51a6f66a86f4c3fdaf` / message `om_x100b63c13aa398a8dd204907be97f78`
- 授权口径（协调者解析，供后续回合执行）：
  1. **TESTER 16D 联合验收对固定集成 SHA `29bd1f4` 回执 PASS 后，协调者可直接执行合入，无需再次向用户请示**：
     - `git merge --no-ff`（或按项目惯例）三叶集成候选入 main，记录 merge commit；
     - 推 github（按 AGENTS 自动提交与同步规则）。
  2. **同步更新本地测试环境**（AGENTS 定义中"本地"=开发机本地 Compose 栈）：合入后 `./scripts/local_stack.sh up` + `local_stack.sh test` 收敛，记录容器状态/健康检查/页面 API 实测。
  3. **不含生产处理机部署**：生产更新仍需用户当次明确授权 + `deploy_processing_machine.sh --apply --production`，本授权不覆盖。
  4. 联合验收**非 PASS**（任一失败）则不自动合入，回原叶 owner 最小返修，返修后重走"OCR 增量（如需要）+ TESTER 复验 + 本授权"。
- 关联授权：强审查 24h grant `32e3edfd`（至 10-15 18:17，TASK-16C 面）在途有效，返修如需强审可自动调用（0/5 已用）。
- 状态：AUTHORIZED，等待 TESTER 16D 联合验收回执。

## ⛔ 合入 HOLD（协调者，2026-10-14 18:55 +08:00）——覆盖本文件「PASS 后可直接合入」的立即执行

- TESTER 16D 对固定集成 `29bd1f4` 联合验收 PASS（18:3x–18:5x 回执在案）成立，**但协调者 OCR run `66ca40d3` b01（`bag_search_service.py`）收口裁决发现 F1（medium/bug，CONFIRMED 防御性）**：`scene_original`/`self_built_original` SQL 谓词缺 NVIDIA 排除，与 Python 标签侧单源优先级不一致（可达筛选/标签分叉，同本轮 A-OCR-2 缺陷类）。F1 属 A 叶文件、在 `29bd1f4` 集成范围内，**未修不得合入**。
- **HOLD 解除条件（全部满足前不执行本授权合入/推送/测试环境更新）**：① A 按 `inbox/1号/TASK-16C-A/ocr-r1-rework-3-dispatch-20261014.md` 最小返修冻结（仅 `bag_search_service.py`：两谓词补 `dataset_type != "nvidia_physicalai"` + line 109 docstring + line 148 注释同步，零越界）；② 协调者机械核验全绿；③ 增量 OCR 仅 `bag_search_service.py` 单文件收口零 CORRECTION 级（同 run `66ca40d3` 的 b02 `scene_result_query.py` 须先收口并逐条裁决、无新增 CORRECTION 级）；④ TESTER A 增量面（F1 组合夹具：nvidia+scene 用途原包筛 scene_original 不返回、标签仅 nvidia_original 一致性）PASS；⑤ 重建三叶固定集成候选（含 A 新 head）并 TESTER 重新联合验收 PASS。
- 本 HOLD 只挂起「立即合入」，不撤销授权本身；条件齐后仍按本授权口径直接合入+推送+更新本地测试环境（不覆盖生产）。并发协调者会话（群 chat）收到本 HOLD 后**不要先合入**，待 A F1 返修链收口。

## HOLD 条件状态更新（协调者，2026-10-14 19:41 +08:00）

- ① A R1-3 最小返修冻结 `8958291`（19:03）✓；② 机械核验全绿（19:08 b300f244）✓；③ 增量 OCR r13 `f7899cfc` 0 findings/零 CORRECTION（19:12 收口、19:14 裁决）✓；④ TESTER F1 增量独立行为面 PASS（19:26 回执 34/34+零越界+RED 交叉证+自清归零）✓ → **A 叶接受已落盘**（`TASK-16C-A/leaf-acceptance-decision-20261014.md` 19:40，OCR+TESTER 双证齐）；⑤ 三叶固定集成候选已重建 = **`44b6c07`**（相对旧 `29bd1f4` 唯一 diff=bag_search_service.py +18/−10；全仓 1174 passed、3 failed 全 seed 固有口径）✓，**TESTER 最终联合验收派单在途**（`final-integration-44b6c07-dispatch.md` 19:41）。
- **当前唯一剩余条件 = TESTER 44b6c07 联合验收回执 PASS**；PASS 后本回合/后续回合按本授权直接执行：合入 main（--no-ff 记录 merge commit）→ 推 github → `./scripts/local_stack.sh up` + `test` 本地测试环境收敛记录。不含生产处理机部署。