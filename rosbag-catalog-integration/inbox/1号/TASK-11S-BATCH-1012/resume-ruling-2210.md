# TASK-11S-BATCH-1012 / A / 裁决续跑（ruling-doublewrite-2210）

状态：RESUME_DISPATCHED，owner=A，2026-10-13T22:10+08:00。解除你 21:52 的 BLOCKED。

先通读 `inbox/coordinator/SPRAY-BATCH-1012-20261013/ruling-doublewrite-2210.md`（含逐包目标态+你的最小纠错授权范围）。BATCH-STATUS 已同步。

要点（生产 18000 健康、active_runs=[]、3 个 date-grouped 重复 run 已 fail-closed FAILED 未烧模型，双跑风险已被车辆绑定门禁拦截）：

1. **收口滞留 op**：A `bigbags-copy` op result.json 仍 `status=RUNNING pid=2520120` 但进程已退、result.log 0 字节、staging 空=僵尸记录（C obs7）。用 `runtime_tools status`/recover 收口为终态，**不自动重跑大包 op**；16_02_03 走新的独立 op 重拷。
2. **清除污染 submission**（处理机生产 MySQL `rosbag_catalog.ingest_submission`，先 SELECT 备份到 receipt 再 DELETE）：
   - `13dc398c9301…`（14_42_48 第二写者 flat，占 flat path_claim_key，即你 409 根因）
   - `24d60fee4455…`（16_02_03 第二写者 flat，无文件无绑定）
   - `03281a51…`/`5e08e73d…`/`7f4e7b75…`（3 个 date-grouped，已 FAILED）
   - 删后核对应 flat `path_claim_key` 释放（重提交不再 409）。
3. **清除 date-grouped NAS 文件**：`ready/spray/20261012/`（4 包，删前 du -sb+逐文件 SHA 留证，确认 flat 顶层同名文件完好后再删）；`incoming/spray/20261012/` 残留一并清。
4. **续提交 flat**（A 既有 stable idempotency 格式 + source_metadata `vehicle_code=test`）：
   - `14_42_48`（NEEDS_RUNTIME_RESULT，全链验收）
   - `16_37_47`（A 尚未提交，flat 文件已在 `ready/spray/16_37_47`；TESTER 已核 flat 与源 IDENTICAL，台账缺条目按源锚定闭合）
   - `16_58_28`（确保你的 flat `518089ed` 绑定 flat ready 文件并跑，预期 NOT_APPLICABLE；TESTER 已核 flat sha 3/3 MATCH）
   - `16_02_03`（**文件全域失踪**，从源 `/home/wang/下载/1012/rosbag2_2026_10_12-16_02_03` 重拷→逐文件 SHA→原子移入 flat→提交，10.1GB 大包用 runtime_tools 冻结 op 跨夜）
5. **保持不动**：`15_58_23`(PASS)/`16_00_13`(SUCCESS)/`16_31_25`(NOT_APPLICABLE) 及其文件/submission；`16_33_10` 空包走 scanner 拒绝路径（不补造、不改文件），TESTER 核可追溯。
6. **禁止**：重提交已 PASS/SUCCESS/NOT_APPLICABLE 包；改业务代码/部署（本批无代码变更）；kill 非 A 进程（第二写者已退出）。

长机械操作（重拷/删除大目录）用 runtime_tools 冻结 spec 跨回合执行，不占模型回合等传输。完成后写 `receipts/TASK-11S-BATCH-1012/a-attempt-1.md`（含删除备份+续提交 submission_id+SHA 证据），回执 TESTER 独立验收。失败如实保留证据，未完成不 PASS。