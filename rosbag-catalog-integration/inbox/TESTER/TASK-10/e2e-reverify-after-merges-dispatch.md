# 派单：TASK-10 E2E 复跑（两笔返修均已合入 main 后的独立验收）

- status: TEST_REPORT_PENDING（TESTER 01:15 交付 FAIL，见 test-receipts/TEST-TASK10-e2e-reverify/attempt-1.md）

- 角色：测试者（TESTER）
- task/attempt：TASK-10 / e2e-reverify-after-merges
- 触发：协调者 00:5x 巡检收口——#1 t10-defect1-source-ready 已合入 `277e40f`（00:35 前批）、#2 t10-defect2-storage-offset `d4719f6` 本轮核验全绿→OCR T10D2-r1 0 findings→**合入 main `a77aa45`（推 origin 277e40f..a77aa45，rev-parse 双核一致）**。两笔返修均在 main。
- 被测快照：main HEAD **`a77aa45`**（= origin/main；含 scene_publish_service derive_storage_offset 中位数+100ms容差 + source_service DISCOVERED→READY）
- 基线：本单无新开发 commit，仅跑既有端到端驱动验证两笔修复协同闭环。

## 一、范围（只测、不改码、不 OCR）

跑既有端到端正式服务链驱动，验证 TASK-10 P0 收尾闭环：目录登记/配置冻结→04B 真实坡道切片（SUCCESS+可发布区间）→06B NAS+数据库登记（**derive_storage_offset 现应非 None，步骤 4 发布不再 BLOCKED**）→正式 API 获取（非空可打开+原包不变）。

- 驱动脚本：`/home/wang/.hermes/cache/scratch/t10_e2e.py`（协调者已固化为 `scratch/t10_e2e_reverify.py`，WT 改指 `/home/wang/work/rosbag-catalog` main 含两笔 merge）。
- **被测代码必须来自 main `a77aa45`**（非旧 worktree `wt-04a-t10`@ca8730d，旧 worktree 不含修复，禁用）。
- 真实 slope 袋 row19（`1165414093_slope_20260818_105105_105120`，54 帧，VLM ≤1 袋预算），VLM 端点 `http://192.168.2.45:8002/v1/chat/completions`。
- 本地 8 容器栈 backend/orchestrator/worker 需含 main 最新代码（若镜像 build 早于 `a77aa45`，须先重建/重启相关服务容器再驱动；如实记录处理，不得用旧镜像冒充）。

## 二、AC（逐项取证，不伪装成功）

1. **步骤 4 发布不再 PUBLISH_BLOCKED**：`derive_storage_offset` 对 row19 返回非 None（预期 ~100.382ms，最接近中位数真实观测值），writer 再切→`publish_scene_slices` 原子发布成功→父子/标签/当前版登记。
2. **端到端全链 SUCCESS**：登记 matched、run 冻结、analyze SUCCESS（VLM 真实调用，帧数/耗时记录）、切片可发布区间非空。
3. **原包独立复核 ALL_UNCHANGED**：源袋前后 hash/mtime 一致（只读，驱动不得修改真实 NAS 袋）。
4. **步骤 5 API 获取**：GET /bags/{child}、lineage、切片可打开，内容非空。
5. 每步落 `scratch/t10/t10-e2e.json` + `t10-run.log`，断言失败如实申报 step/原因/退出码。

## 三、停止条件

- 全链 SUCCESS + 原包 ALL_UNCHANGED + offset 非 None → 回执 **PASS**（`test-receipts/TEST-TASK10-e2e-reverify/attempt-1.md`），协调者据此判 **TASK-10 DONE→P0 收口**（停止派发，不自动转 TASK-11）。
- 任一 AC 失败 → 回执 **FAIL** + 定位（属 harness env / #1 域 / #2 域 / 04B 判定 / 其他），不跨模块改码，交协调者裁决回派。
- 不得为通过而弱化断言、跳过 VLM 真实调用、或用 mock 服务冒充。

## 四、路径

- ACK：`inbox/TESTER/TASK-10/e2e-reverify-after-merges-ack.md`（status ACCEPTED + base `a77aa45` 双核 + 容器代码面核实）
- 回执：`test-receipts/TEST-TASK10-e2e-reverify/attempt-1.md`
- 证据：`scratch/t10/t10-e2e.json` + `t10-run.log` + offset 复验输出
- 事件：`events/TESTER/`

先独立 ACK 再执行；已有派单只改 status ACK，正文不改。