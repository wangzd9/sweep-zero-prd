# TESTER：TASK-16D ACK（attempt-1）

ACK 2026-10-14T12:3x+08:00；owner cron-tester-poll-167580c0500b-20261014-102453。
派单：`inbox/TESTER/TASK-16D/attempt-1-dispatch.md`（2026-10-14T11:25:19+08:00）；入口 `inbox/control/V04-UI-RESUME-20261014.md`；OCR 15 项账 `reviews/TASK-16C/OCR-LEGACY-20261014.md`；验收 `ACCEPTANCE.md`（REQ/AC-16、AC-05）。

## 固定被测输入

- 独立测试树 seed：`bd0db1d2a0fc293cb4562e2079e741739bacb0de`（plan/v04-ui-resume-20261014，含已知缺陷，**未接受，不宣验收 PASS**）。
- 调查/生产基线：main `63bfcf8`、生产业务 `3c9c496`（只读参照，不测移动分支）。
- 产物：`test-receipts/TEST-TASK16D/attempt-1.md`。

## 范围确认

- 准备阶段：fixture 三类（原始/双用途/合法无血缘历史切片/当前 AVAILABLE/历史/待完成/下架/未知）、严格 MySQL 隔离库（SQLite 不外推）、真实浏览器环境（缺浏览器标 BLOCKED_BROWSER，HTTP200 不替代 DOM/Console/Network）。
- 复现 C5（双用途双标单值 CASE）、C7（日期非法值 500/边界）、C8（CANCELLED null.querySelector）及 cursor/分类风险（16C-c03-02/03/04）；旧 TESTER PASS 不覆盖新 SHA。
- 叶冻结即对冻结完整 SHA 做该面独立增量验证；最终集成 SHA 由协调者提供后再联合验收（两查询入口/浏览器三 tab/八步状态/类型分流/受控 test 首包真产物 UID 血缘获取，只读生产 API 取证，不提交/不拷包/不 retry/不烧模型/不直接写库）。
- 不改业务实现、不运行 OCR（唯一 ocr_runtime.py 归协调者）、不批准合入；缺陷回原 owner（A 查询面 / B Bag 视图 / C 流水线详情）。

## 本 ACK 后第一步

- 从 seed `bd0db1d2` 建专属 worktree `wt-tester-16d-20261014`（只读复用主仓对象，不动 seed/旧 B 冻结树/主仓脏文件），起 MySQL 隔离库与浏览器环境预检，落准备检查点。
- 原批次 TASK-11S-BATCH-1012 收尾增补卡已核销闭合，TEST_REPORT_PENDING 待大包 `4acf689f` 终态，与 16D 准备并行不冲突（16D 准备不依赖大包）。
