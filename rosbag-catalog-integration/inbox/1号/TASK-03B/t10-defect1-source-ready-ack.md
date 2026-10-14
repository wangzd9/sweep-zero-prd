# ACK：t10-defect1-source-ready

- status: ACCEPTED
- 派单路径：inbox/1号/TASK-03B/t10-defect1-source-ready.md
- task：t10-defect1-source-ready（TASK-10 缺口 #1 最小返修，03B 域 source_status DISCOVERED→READY 生产路径）
- attempt：1
- owner：cron-a-poll-d5cb80cf2fc5-20261012-001230（1号 A）
- base：main `ca8730d`（= origin/main，2026-10-12 00:12 双核）
- 分支/worktree：新建任务专属 `wt-01-t10def1`（.venv 软链主仓），分支 `a/t10def1-source-ready`
- 时间：2026-10-12 00:1x +08:00

## 理解与执行口径
1. 先核既有隐式路径：确认是否已有 scanner 确认/指纹稳定机制可置 READY（有→接入；无→补最小生产置位路径）。
2. 03B 登记成功路径补 DISCOVERED→READY 置位（matched+指纹/元数据完整后由正式服务链置 READY），单 commit 最小面，只动 source_service/登记链+测试，不碰 05/06B/04B。
3. 幂等与竞争：重复登记/Scanner 重扫不得把 READY 回退 DISCOVERED；与 :459 错误态语义不冲突。
4. 测试：SQLite 定向（登记→READY + outbox 建 run 不被 :208 拦截 + 幂等不回退 + 错误态不受影响）+ 全量 SQLite（--ignore=tests/test_devflow.py）+ ruff 全绿；涉并发语义真 MySQL 8.4.11 STRICT 隔离库文件级复跑（用完即毁 0 残留）。
- 停止条件：交付 commit + 自测证据 + 回执落盘 → REVIEW_PENDING 冻结等协调者核验+OCR+合入。
- 边界：不改 06B/05/04B；不重启共享栈/不动 NAS；发现跨模块依赖→记录回派不自行扩。