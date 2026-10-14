# 派单：e2e-reverify-v2（TASK-10 / 复跑 v2，#3 合入后全链取证）

- status: TEST_REPORT_PENDING（TESTER 02:01 交付 attempt-2 PASS，回执 test-receipts/TEST-TASK10-e2e-reverify/attempt-2.md）
- task/attempt: TASK-10 / e2e-reverify / **attempt-2（复跑 v2）**
- 角色: TESTER
- 触发: 协调者 01:52 巡检收口——#3 t10-defect3-publish-bounds `0943885` 独立机械核验全绿→OCR T10D3-r1 0 findings→**--no-ff 合入 main `453da0c`（推 origin a77aa45..453da0c）**。三笔返修（#1 `277e40f` + #2 `d4719f6` + #3 `453da0c`）均在 main。
- 被测快照: main HEAD **`453da0c`**（= origin/main，含 #1 DISCOVERED→READY + #2 derive_storage_offset 中位数+100ms容差 + #3 发布记录落存储域 actual 边界 + complete-scene 区间复核改存储域界 fail-closed）。**注意：v1 attempt-1 被测 `a77aa45` 不含 #3，结果作废，v2 必须 `453da0c`。**
- 基线: 本单无新开发 commit，仅跑端到端驱动验证三笔修复协同闭环。

## 一、驱动
- 驱动脚本: `scratch/t10_e2e_reverify.py`（**协调者已按 #3 交付申报修复 step4 构造 `SlicePublishSpec` 补 `actual_start_ns/actual_end_ns`**，`:336-342`——不补则 #3 fail-closed 语义下 E2E 将 409=预期拦截，非修复未生效）。
- 被测代码必须来自 main **`453da0c`**（`git rev-parse HEAD` 双核一致；旧 worktree `wt-04a-t10`@ca8730d 禁用）。
- 本地 8 容器栈 backend/orchestrator/worker 若镜像 build 早于 `453da0c`，沿用 attempt-1 口径：驱动在 `453da0c` 代码上起独立 app 实例（fresh SQLite + create_all + TestClient 正式 API），执行面走真实 VLM（SlopeAdapter.analyze → writer 再切 → 06B 发布）。不得用旧镜像冒充，如实记录。

## 二、AC（全绿即 TASK-10 DONE）
1. 目录登记/配置冻结 → 04B 真实坡道切片 SUCCESS+可发布区间 → 06B NAS+数据库登记（**derive_storage_offset 非 None**）→ 发布（记录落 actual 边界）→ **`/results` 200** → **`/complete-scene` 200 可置 AVAILABLE**（#3 修复点：存储域区间复核通过，真包 offset≠0 不再 409）。
2. **step5 正式 API 获取**：非空可打开 + 原包独立复核 **ALL_UNCHANGED**（源袋前后 hash/mtime 一致，只读）。
3. offset 非 None + 全链 SUCCESS + 原包 ALL_UNCHANGED → 回执 **PASS**。
- 任一失败：定位 app 文件:行 + 证据（`scratch/t10/t10-e2e.json`/`t10-run.log`），回派对应域 owner 最小返修，不自行改码。

## 三、范围/越界
- 允许: 跑驱动、只读取证真实 NAS 袋、fresh 隔离 SQLite、独立 app 实例、VLM 调用 **≤1 袋**（累计 v1+v2 ≤2 袋）。
- 禁止: 改业务代码、改驱动逻辑（除协调者已落的 step4 actual 边界）、删既有断言、用旧 worktree/旧镜像冒充。

## 四、停止条件
AC 全绿交付回执 `test-receipts/TEST-TASK10-e2e-reverify/attempt-2.md`（PASS/FAIL + 全链四步证据 + 原包 ALL_UNCHANGED + VLM 袋数 + 隔离资源 0 残留声明）即停。协调者据此判 **TASK-10 DONE → P0 收口**（停止派发，不自动转 TASK-11）。

## 五、回执
- ACK: `inbox/TESTER/TASK-10/e2e-reverify-v2-ack.md`（status ACCEPTED + base `453da0c` 双核 + 容器/实例代码面核实）
- 交付: `test-receipts/TEST-TASK10-e2e-reverify/attempt-2.md`