# ACK：TASK-10 E2E 复跑（两笔返修合入后独立验收）

- 角色：测试者（TESTER）
- task/attempt：TASK-10 / e2e-reverify-after-merges / attempt-1
- status: ACCEPTED
- acked_at: 2026-10-12T01:02 +08:00

## 被测快照核实（独立双核）
- 驱动 WT=`/home/wang/work/rosbag-catalog`，`git rev-parse HEAD`= `a77aa45433`，`git fetch origin main` 后 `origin/main`= `a77aa45433`，**双核一致**。
- 两笔修复均在 HEAD：`277e40f`（defect1 DISCOVERED→READY）`git merge-base --is-ancestor`=yes；`d4719f6`（defect2 derive_storage_offset 中位数+100ms 容差）=yes。
- 旧 worktree `wt-04a-t10`@ca8730d 不含修复，**禁用**（与派单一致）。

## 环境核实
- 本地 8 容器栈 backend/orchestrator/worker 镜像 build 2026-10-08（早于 main `a77aa45`，不含 scene 路由），**不直接驱动容器**——沿用既有口径：驱动在 `a77aa45` 代码上起独立 app 实例（fresh SQLite + create_all + TestClient 正式 API），执行面由驱动驱动真实 VLM（SlopeAdapter.analyze → HttpSlopeModelClient → writer 再切 → 06B 发布）。此口径与 attempt-1 一致、被测代码=main `a77aa45`，非旧镜像冒充。
- 真实 slope 袋 row19 `/mnt/nas_backup/data_slice/1165414093/slope/1165414093_slope_20260818_105105_105120` 在位（270M，.db3+metadata.yaml+mp4 齐全，只读，前后 hash/mtime 校验对象）。
- VLM 端点 `http://192.168.2.45:8002/v1/chat/completions`（完整路径，attempt-1 404 已解口径）。
- 驱动固化版 `scratch/t10_e2e_reverify.py`（协调者 00:58 落盘，WT 指 main 仓库）；证据落 `scratch/t10/t10-e2e.json` + `t10-run.log`。

## AC 口径（逐项取证，不伪装成功）
1. 步骤 4 `derive_storage_offset` 对 row19 非 None（预期 ~100.382ms），writer 再切 → `publish_scene_slices` 原子发布成功 → 父子/标签/当前版登记，不再 PUBLISH_BLOCKED。
2. 端到端全链 SUCCESS：登记 matched、run 冻结、analyze SUCCESS（真实 VLM，帧数/耗时记录）、可发布区间非空。
3. 原包 ALL_UNCHANGED：源袋前后 hash/mtime 一致。
4. 步骤 5 API 获取：GET /bags/{child}、lineage、切片可打开、内容非空。
5. 每步落证据，断言失败如实申报 step/原因/退出码。

停止条件：全链 SUCCESS + ALL_UNCHANGED + offset 非 None → 回执 PASS；任一 AC 失败 → 回执 FAIL + 定位（harness env / #1 域 / #2 域 / 04B 判定 / 其他），不跨模块改码，交协调者裁决。

## 执行
长验证：驱动后台进程执行（VLM 真实调用，attempt-1 口径约 140s+），记 PID/日志/快照检查点后释放控制租约；巡检只核查不重复启动。